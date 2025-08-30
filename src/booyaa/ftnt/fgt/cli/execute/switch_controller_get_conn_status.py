import re

class SwitchControllerGetConnStatus:
    fsw_list: list
    # fsw_info: dict
    # {
    #     'name': sw['name'],
    #     'serial': sw['serial'],
    #     'status': sw['status'],
    #     'ip_addr': sw['connecting_from'],
    #     'state': sw['state'],
    # }


    def __init__(self, cli):
        self.cli = cli

        self.msw_list = []

        self.pattern = re.compile(r"""
            ^(S\w+)\s+                         # シリアル
            v(\d+\.\d+\.\d)\s*                 # バージョン
            \((\d*)\)\s+                       # ビルド
            (\w+)/                             # 認証
            (\w+)\s+                           # ステータス
            (\S+)\s+                           # フラグ
            ([\d\.]+)\s+                       # IPアドレス
            \w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+\s+ # 日付
            ([\w_\-\.]+)\s*                    # ホスト名
        """, re.VERBOSE)

    def get(self):
        cmd = 'execute switch-controller get-conn-status'
        res = self.cli.execute_command(cmd)

        if res['code'] != 0:
            return res

        self.fsw_list = []
        for l in res['output'].splitlines():
            match = self.pattern.match(l.strip())
            if match:
                self.msw_list.append({
                    'name': match.group(1),
                    'version': match.group(2),
                    'build': match.group(3),
                    'state': match.group(4),
                    'status': match.group(5),
                    'flag': match.group(6),
                    'addr': match.group(7),
                    'serial': match.group(8),
                })

        return res
