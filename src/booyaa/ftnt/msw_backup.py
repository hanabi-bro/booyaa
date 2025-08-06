from rich.live import Live
from rich.table import Table

from booyaa.ftnt.msw import FgtMswCli
from booyaa.common.fire_and_forget import fire_and_forget


from pathlib import Path
from time import sleep

from signal import signal, SIGINT
from traceback import format_exc


class MswBackup:
    def __init__(self):
        self.fgtmsw_cli = FgtMswCli()
        self.target_info_list = []
        self.fg_addr = ''
        self.backup_dir = Path('./fg_config')
        self.nomask = False

    def setup(self, fg_addr, fg_user, fg_password, fg_alias=None, backup_dir='./fg_config'):
        let = self.fgtmsw_cli.set_target(
            user=fg_user,
            password=fg_password,
            target=fg_addr,
            alias=fg_alias,
            backup_dir=backup_dir,
        )
        self.backup_dir = Path(backup_dir)
        if let['code'] != 0:
            return let
        let = self.gen_target_info_list()
        return let

    @fire_and_forget
    def bulk_run(self):
        try:
            for target in self.target_info_list:
                let = self.run(target)
        except Exception as e:
            print(format_exc)
        finally:
            self.backup_loop = False

    def run(self, target):
        let = {'code': 0, 'msg': '', 'output': '', 'result': ''}
        if target['status'] != 'Connected':
            let['code'] = 1
            let['msg'] = f'{target['hostname']} is not online'
            target['message'] = let['msg']
            target['progress']['login'] = let
            return let
        
        let = target['msw_obj'].display = False

        # FG→MSWへログイン
        let = target['msw_obj'].login_msw()
        # TUI用
        if let['code'] == 0:
            let['result'] = 'OK'
        elif let['code'] > 0:
            let['result'] = '[red]NG[/]'
            return let

        target['progress']['login'] = let
        target['message'] = let['msg']

        # MSWバックアップ
        let = target['msw_obj'].backup()
        target['progress']['backup'] = let
        target['message'] = let['msg']
        # TUI用
        if let['code'] == 0:
            let['result'] = 'OK'
        elif let['code'] > 0:
            let['result'] = '[red]NG[/]'
            return let


        # MSW→FGからログアウト
        let = target['msw_obj'].logout_msw()
        target['progress']['logout'] = let
        # TUI用
        if let['code'] == 0:
            let['result'] = 'OK'
        elif let['code'] > 0:
            let['result'] = '[red]NG[/]'
            target['message'] = let['msg']
            return let

        return let

    def gen_target_info_list(self):
        let = {'code': 0 , 'msg': '', 'output': ''}
        self.target_info_list = []
        let = self.fgtmsw_cli.gen_msw_list()
        if let['code'] != 0:
            return let

        for msw in self.fgtmsw_cli.msw_list:
            self.target_info_list.append(
                {
                    'msw_obj': msw,
                    'fg_name': msw.fg_alias or msw.fg_hostname,
                    'status': msw.status,
                    'hostname': msw.hostname,
                    'addr': msw.addr,
                    'user': msw.user,
                    'password': msw.password,
                    'message': '',
                    'progress': {
                        'login': {'code': -999, 'msg': '', 'output': '', 'result': ''},
                        'backup': {'code': -999, 'msg': '', 'output': '', 'result': ''},
                        'logout': {'code': -999, 'msg': '', 'output': '', 'result': ''},
                    }
                }
            )
        
        return let

    ## Tui
    def update_table(self):
        table = Table(title=f'ManagedSwitch Backup\n{self.backup_dir.resolve()}')

        # table header
        table.add_column("FgName", style="magenta")
        table.add_column("MswName", style="cyan", no_wrap=True)
        table.add_column("User", style="magenta")
        table.add_column("Password", style="magenta")
        table.add_column("Login", style="green")
        table.add_column("Backup", style="green")
        table.add_column("Logout", style="green")
        table.add_column("Message", style="white")

        for target_info in self.target_info_list:
            # パスワードマスク
            if self.nomask:
                passwd = target_info['password']
            else:
                passwd = '*' * len(target_info['password'])

            table.add_row(
                target_info['fg_name'],
                target_info['hostname'],
                target_info['user'],
                passwd,
                target_info['progress']['login']['result'],
                target_info['progress']['backup']['result'],
                target_info['progress']['logout']['result'],
                target_info['message']
            )
        return table

    def tui_run(self):
        self.backup_loop = True
        with Live(self.update_table(), refresh_per_second=4) as live:
            self.bulk_run()
            # SIGINT (Ctrl+C)をキャッチして停止
            def signal_handler(sig, frame):
                self.backup_loop = False  # ping_loopはなぜかeventでは止まらない？？？

            signal(SIGINT, signal_handler)

            # 実行ループ (Ctrl+Cで停止)
            while self.backup_loop:
                live.update(self.update_table())
                sleep(0.1)
            
            # 最終表示
            live.update(self.update_table())



if __name__ == '__main__':
    fg_addr = '172.16.201.201'
    fg_user = 'admin'
    fg_password = 'P@ssw0rd'
    fg_alias = None

    mswbak = MswBackup()
    let = mswbak.setup(
        fg_addr=fg_addr,
        fg_user=fg_user,
        fg_password=fg_password,
        fg_alias=fg_alias,
        backup_dir='fg_config'
    )
    let = mswbak.gen_target_info_list()
    mswbak.tui_run()
