from re import search

class SystemStatus:
    hostname: str                   # ホスト名
    serial: str                     # シリアル
    model: str                      # モデル名 
    major: str                      # メジャーバージョン
    minor: str                      # マイナーバージョン
    patch: str                      # パッチバージョン
    build: str                      # ビルド情報
    version: str                    # OSバージョン
    manage_vdom: str                # 管理VDOM名
    vdom_mode: str                  # vdom名 'no-vdom', 'multi-vdom'
    ha_mode: str                    # HAモード 'standalone', 'active-passive', 'active-active'
    ha_role: str

    def __init__(self, api):
        self.api = api

    def get(self):
        cmd = 'get system status'
        res = self.api.execute_command(cmd)

        if res['code'] != 0:
            return res

        # ホスト名の抽出
        _hostname = search(r'Hostname: *(\S+)', res['output'])
        if _hostname:
            self.hostname = _hostname.group(1)

        # シリアル番号の抽出
        _serial = search(r'Serial-Number: *(\S+)', res['output'])
        if _serial:
            self.serial = _serial.group(1)

        # モデル, バージョン情報の抽出
        _versions = search(r'Version: \w+-(\w+) *v(\d+).(\d+).(\d+),build(\d+)', res['output'])
        if _versions:
            self.model, self.major, self.minor, self.patch, self.build = _versions.groups()
            self.version = f'{self.major}.{self.minor}.{self.patch}'

        # manage vdom domainの抽出
        _manage_vdom = search(r'Current virtual domain: *(\S+)', res['output'])
        if _manage_vdom:
            self.manage_vdom = _manage_vdom.group(1)

        # Virtual domain configuration
        # novdom: disable, vdom: multiple
        _vdom_mode = search(r'Virtual domain configuration: *(\S+)', res['output'])
        if _vdom_mode:
            # vdomモードの抽出 | apiの['state']['vdom_mode']の表記に合わせる
            if _vdom_mode.group(1).lower() == 'disable':
                self.vdom_mode = 'no-vdom'
            elif _vdom_mode.group(1).lower() == 'multiple':
                self.vdom_mode = 'multi-vdom'

        # HAモードとHA roleの抽出
        _ha_mode = search(r'Current HA mode: *(\S+)(?:, *(\S+))', res['output'])

        if _ha_mode:
            if _ha_mode.group(1) == 'a-a':
                self.ha_mode = 'active-active'
            elif _ha_mode.group(1) == 'a-p':
                self.ha_mode = 'active-passive'
            else:
                self.ha_mode = 'standalone'

            self.ha_role = _ha_mode.group(2) if _ha_mode.lastindex >= 2 else ''

        return res
