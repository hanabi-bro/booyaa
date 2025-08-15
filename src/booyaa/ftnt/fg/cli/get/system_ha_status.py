from re import search, findall

class SystemHaStatus:
    exsist_secondary: bool          # セカンダリノード有無のフラグ
    secondary_hostname: str         # セカンダリノードのホスト名
    secondary_serial: str           # セカンダリノードのシリアル
    secondary_cluster_index: str    # クラスタ番号

    def __init__(self, api):
        self.api = api

        self.exsist_secondary = False
        self.secondary_hostname = ''         # セカンダリノードのホスト名
        self.secondary_serial = ''           # セカンダリノードのシリアル


    def get(self):
        cmd = 'get system ha status | grep .*'
        # VDOMモードの場合はglobaに移動
        if self.api.vdom_mode == 'multi-vdom':
            let = self.api.config_global()
            if let['code'] != 0:
                return let

        res = self.api.execute_command(cmd)

        # コマンド実行エラー時は終了
        if res['code'] != 0:
            return let

        _ha_cluster_match = findall(r'(\S+) *, *(\w+), *HA cluster index *= *(\d+)', res['output'])
        self.exsist_secondary = len(_ha_cluster_match) == 2 or False
        if _ha_cluster_match[0][0] == self.api.hostname:
            _primary_cluster_info = _ha_cluster_match[0]
            if self.exsist_secondary:
                _secondary_cluster_info = _ha_cluster_match[1]
        else:
            _primary_cluster_info = _ha_cluster_match[1]
            if self.exsist_secondary:
                _secondary_cluster_info = _ha_cluster_match[0]

        self.cluster_index = _primary_cluster_info[2]
        if self.exsist_secondary:
            self.secondary_hostname = _secondary_cluster_info[0]
            self.secondary_serial = _secondary_cluster_info[1]
            self.secondary_cluster_index = _secondary_cluster_info[2]

        let = res

        # globalモードを終了
        if self.api.vdom_mode == 'multi-vdom':
            res = self.api.end_global()
            if res['code'] != 0:
                return let

        return let

