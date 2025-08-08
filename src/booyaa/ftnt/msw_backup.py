from rich.live import Live
from rich.table import Table

from booyaa.ftnt.msw import FgtMswCli

from concurrent.futures import ThreadPoolExecutor
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
        self.backup_loop = True
        try:
            for target in self.target_info_list:
                let = self.run(target)
        except Exception as e:
            print(format_exc)
        finally:
            self.backup_loop = False

    @fire_and_forget
    def multi_bulk_run(self):
        self.backup_loop = True
        results = []
        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                for target_info in self.target_info_list:
                    results.append(executor.submit(self.run, target_info))
                    sleep(0.5)
        except Exception as e:
            print(format_exc)
        finally:
            [r.result() for r in results]
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

        target['progress']['login'] = let
        target['message'] = let['msg']

        if let['code'] > 0:
            return let

        # MSWバックアップ
        let = target['msw_obj'].backup()

        # TUI用
        if let['code'] == 0:
            let['result'] = 'OK'
        elif let['code'] > 0:
            let['result'] = '[red]NG[/]'

        target['progress']['backup'] = let
        target['message'] = let['msg']

        if let['code'] > 0:
            return let


        # MSW→FGからログアウト
        let = target['msw_obj'].logout_msw()

        # TUI用
        if let['code'] == 0:
            let['result'] = 'OK'
        elif let['code'] > 0:
            let['result'] = '[red]NG[/]'

        target['progress']['logout'] = let

        if let['code'] > 0:
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
        with Live(self.update_table(), refresh_per_second=1) as live:
            # self.bulk_run()
            self.multi_bulk_run()
            # SIGINT (Ctrl+C)をキャッチして停止
            def signal_handler(sig, frame):
                self.backup_loop = False

            signal(SIGINT, signal_handler)

            # 実行ループ (Ctrl+Cで停止)
            while self.backup_loop:
                live.update(self.update_table())
                sleep(0.1)
            
            # 最終表示
            live.update(self.update_table())


if __name__ == '__main__':
    # fg_addr = '172.16.201.201'
    # fg_user = 'admin'
    # fg_password = 'P@ssw0rd'
    # fg_alias = None

    # mswbak = MswBackup()
    # let = mswbak.setup(
    #     fg_addr=fg_addr,
    #     fg_user=fg_user,
    #     fg_password=fg_password,
    #     fg_alias=fg_alias,
    #     backup_dir='fg_config'
    # )
    # let = mswbak.gen_target_info_list()

    # mswbak.tui_run()

    #==========================

    from argparse import ArgumentParser, RawTextHelpFormatter
    from textwrap import dedent

    class MyArgumentParser(ArgumentParser):
        def error(self, message):
            print('error occured while parsing args : '+ str(message))
            self.print_help() 
            exit()

    msg = dedent("""\
    ~~~ Forti MangedSwitch Config Backup ~~~
    ## CLI usage
    `msw_bak -t <fg_addr> -u <fg_user> -p <fg_password>`

    e.g:
    ```
    fgt_bak -t 172.16.201.201 -u admin -p P@ssw0rd
    ```
    """)

    parser = MyArgumentParser(description=msg, formatter_class=RawTextHelpFormatter)

    # 直接指定とファイル指定は同時に使えない
    # 現時点では直接指定のみ
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--target', help='ipaddr or hostname\ne.g.) forti_config_backup -t 172.16.201.201 -u admin -p P@ssw0rd')
    # group.add_argument('-f', '--file', help='target csv file\ne.g.) forti_config_backup -f target.csv\ncsv fromat sample)\n172.16.201.201,admin.P@ssword\n172.16.201.202,nwadmin,MyP@ssW0rd')

    # 直接指定の場合、-t, -u, -pは必須
    target_group = parser.add_argument_group('Target Mode', '-t 指定時に必要な引数')
    target_group.add_argument('-u', '--user', help='login user name')
    target_group.add_argument('-p', '--password', help='login password')
    target_group.add_argument('-n', '--name', help='[optional]logfile name, e.g.) log file prefix instead of hostname')

    # ログ出力ディレクトリ指定
    parser.add_argument('-d', '--directory', default='./fg_config', help='backup directory path default is ./fg_config')

    # パスワードマスク
    parser.add_argument('--nomask', help='[optional]No Password Mask, default is True', action='store_true')

    args = parser.parse_args()

    # 引数チェック
    if args.target and (not args.user or not args.password):
        parser.error("--u and -p are required when -t is specified.")

    if args.target:
        parent_fg = {
            'fg_addr': args.target,
            'fg_user': args.user,
            'fg_password': args.password,
            'fg_alias': args.name,
            'backup_dir': args.directory,
        }

    mswbak = MswBackup()
    let = mswbak.setup(
        **parent_fg
    )
    let = mswbak.gen_target_info_list()
    mswbak.tui_run()
