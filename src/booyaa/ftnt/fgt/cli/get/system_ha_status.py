from re import search, findall

class SystemHaStatus:
    exsist_secondary: bool          # セカンダリノード有無のフラグ
    secondary_hostname: str         # セカンダリノードのホスト名
    secondary_serial: str           # セカンダリノードのシリアル
    secondary_cluster_index: str    # クラスタ番号

    def __init__(self, cli):
        self.cli = cli

        self.exsist_secondary = False
        self.secondary_hostname = ''         # セカンダリノードのホスト名
        self.secondary_serial = ''           # セカンダリノードのシリアル
        self.secondary_cluster_index = ''

    def get(self):
        cmd = 'get system ha status | grep .*'
        # VDOMモードの場合はglobaに移動
        if self.cli.fgt_info.vdom_mode == 'multi-vdom':
            let = self.cli.config_global()
            if let['code'] != 0:
                return let

        let = self.cli.execute_command(cmd)

        # コマンド実行エラー時は終了
        if let['code'] != 0:
            return let

        # globalモードを終了
        if self.cli.fgt_info.vdom_mode == 'multi-vdom':
            let = self.cli.end_global()
            if let['code'] != 0:
                return let

        # HA index取得
        _ha_cluster_match = findall(r'\n(Primary|Secondary) *: (\S+| \s+) *, (\S+), HA cluster index = (\d+)', let['output'])
        for _ha in _ha_cluster_match:
            if _ha[0] == 'Primary':
                self.primary_hostname = _ha[1].strip()
                self.primary_serial = _ha[2].strip()
                self.primary_cluster_index = _ha[3].strip()
            elif _ha[0] == 'Secondary':
                self.secondary_hostname = _ha[1].strip()
                self.secondary_serial = _ha[2].strip()
                self.secondary_cluster_index = _ha[3].strip()

                if self.secondary_hostname and self.secondary_serial and self.secondary_cluster_index:
                    self.secondary_exist = True

        self.exsist_secondary = len(_ha_cluster_match) == 2 or False

        return let

