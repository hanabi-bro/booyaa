from rich.live import Live
from rich.table import Table

from booyaa.ftnt.msw import Msw
from booyaa.ftnt.fgt import Fgt

from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.msw.model.msw_info import MswInfo
from booyaa.ftnt.msw.model.progress import Progress

from concurrent.futures import ThreadPoolExecutor
from booyaa.common.fire_and_forget import fire_and_forget


from pathlib import Path
from time import sleep


from signal import signal, SIGINT
from traceback import format_exc


class MswObj(Msw):
    def __init__(self, fgt_info: FgtInfo, msw_info: MswInfo, msw_progress: Progress):
        super().__init__(fgt_info, msw_info)
        self.progress = msw_progress

    def run_backup(self):
        # Login MSW
        let = self.cli.login_msw()

        self.progress.login.code = let['code']
        self.progress.login.msg = let['msg']
        self.progress.login.output = let['output']

        if let['code'] > 0:
            self.progress.login.result = '[red]NG[/]'
            self.progress.msg = let['msg']
            return let
        else:
            self.progress.login.result = '[gree]OK[/]'
            self.progress.msg = let['msg']

        # Config Backup
        let = self.cli.backup()

        self.progress.backup.code = let['code']
        self.progress.backup.msg = let['msg']
        self.progress.backup.output = let['output']

        if let['code'] > 0:
            self.progress.backup.result = '[red]NG[/]'
            self.progress.msg = let['msg']
            return let
        else:
            self.progress.backup.result = '[gree]OK[/]'
            self.progress.msg = let['msg']

        # Logout
        let = self.cli.logout()

        self.progress.logout.code = let['code']
        self.progress.logout.msg = let['msg']
        self.progress.logout.output = let['output']

        if let['code'] > 0:
            self.progress.logout.result = '[red]NG[/]'
            return let
        else:
            self.progress.logout.result = '[gree]OK[/]'

        return let


class MswBackup:
    msw_obj: MswObj
    msw_obj_list: list[MswObj]

    def __init__(self):
        self.fgt = Fgt()
        self.fgt_info = FgtInfo()

        self.msw_user = ''
        self.msw_password = ''

        self.msw_obj_list = []

        self.backup_loop = True
        self.nomask = False
        self.backup_dir = Path('fg_config')
        self.timeout = 60

    def setup(self,
            fgt_addr, fgt_user, fgt_password, alias='', fgt_hostname='', fgt_ssh_port=22, fgt_https_port=443,
            msw_user='admin', msw_password='',
            backup_dir='', timeout=None, nomask=False,
            **kwargs):

        self.fgt.setup(fgt_addr, fgt_user, fgt_password, alias, fgt_hostname, fgt_ssh_port, fgt_https_port)

        self.msw_user = msw_user
        self.msw_password = msw_password or fgt_password
        # self.backup_dir = backup_dir or self.backup_dir
        self.backup_dir = Path(backup_dir or self.backup_dir)
        self.timeout = timeout or self.timeout
        self.nomask = nomask

        let = self.fgt.api.login(addr=fgt_addr, user=fgt_user, password=fgt_password)
        self.fgt_info = self.fgt.api.fgt_info

        return let

    def gen_msw_obj_list(self):
        self.msw_obj_list = []
        for l in self.fgt_info.msw_list:
            msw_info = MswInfo()
            msw_progress = Progress()
            msw_info.addr = l['addr']
            msw_info.user = self.msw_user
            msw_info.password = self.msw_password
            msw_info.hostname = l['hostname']
            msw_info.serial = l['serial']
            msw_info.status = l['status']
            msw_info.state = l['state']
            msw_info.model = l['model']
            msw_info.version = l['version']
            msw_info.build = l['build']
            msw_obj = MswObj(fgt_info=self.fgt_info, msw_info=msw_info, msw_progress=msw_progress)
            msw_obj.backup_dir = self.backup_dir
            self.msw_obj_list.append(msw_obj)

    def sequential_backup_run(self):
        for msw_obj in self.msw_obj_list:
            msw_obj.cli.display=True

            # let = msw_obj.cli.login_fgt()
            # print(let)

            # let = msw_obj.cli.login_msw(addr='10.255.1.1', user='admin', password='P@ssw0rd')
            msw_obj.run_backup()


    @fire_and_forget
    def multi_backup_run(self):
        self.backup_loop = True
        results = []
        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                for msw_obj in self.msw_obj_list:
                    results.append(executor.submit(msw_obj.run_backup, ))
                    sleep(1)
        except Exception as e:
            print(format_exc)
        finally:
            [r.result() for r in results]
            self.backup_loop = False

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

        for msw_obj in self.msw_obj_list:
            # パスワードマスク
            if self.nomask:
                passwd = msw_obj.msw_info.password
            else:
                passwd = '*' * len(msw_obj.msw_info.password)

            fgt_name = msw_obj.fgt_info.alias or msw_obj.fgt_info.hostname
            msw_hostname = msw_obj.msw_info.hostname
            msw_user = msw_obj.msw_info.user
            msw_password = passwd
            msw_login = msw_obj.progress.login.result
            msw_backup = msw_obj.progress.backup.result
            msw_logout = msw_obj.progress.logout.result
            msw_msg = msw_obj.progress.msg

            table.add_row(
                fgt_name,
                msw_hostname,
                msw_user,
                msw_password,
                msw_login,
                msw_backup,
                msw_logout,
                msw_msg,
            )
        return table

    def tui_run(self):
        self.backup_loop = True
        with Live(self.update_table(), refresh_per_second=1) as live:
            # self.bulk_run()
            self.multi_backup_run()
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
    `msw_bak -t <fgt_addr> -u <fgt_user> -p <fgt_password>`
    `msw_bak -t <fgt_addr> -u <fgt_user> -p <fgt_password>` --msw_user <msw_user> --msw_password <msw_password>

    e.g:
    ```
    fgt_bak -t 172.16.201.201 -u admin -p password
    fgt_bak -t 172.16.201.201 -u mswadmin -p mswpassword
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
    target_group.add_argument('-n', '--name', default='', help='[optional]logfile name, e.g.) log file prefix instead of hostname')
    target_group.add_argument('--msw_user', default='admin', help='[optional]msw user, default is admin')
    target_group.add_argument('--msw_password', help='[optional]msw password, default is same as parent FortiGate')


    # ログ出力ディレクトリ指定
    parser.add_argument('-d', '--directory', default='./fg_config', help='backup directory path default is ./fg_config')

    # パスワードマスク
    parser.add_argument('--nomask', help='[optional]No Password Mask, default is True', action='store_true')

    args = parser.parse_args()

    # 引数チェック
    if args.target and (not args.user or not args.password):
        parser.error("--u and -p are required when -t is specified.")

    if args.target:
        target_info = {
            'fgt_addr': args.target,
            'fgt_user': args.user,
            'fgt_password': args.password,
            'alias': args.name,
            'backup_dir': args.directory,
            'msw_user': args.msw_user,
            'msw_password': args.msw_password or args.password,
        }

    mswbak = MswBackup()

    # バックアップディレクトリ
    if args.directory:
        mswbak.backup_dir = args.directory

    # パスワードマスク    
    mswbak.nomask = args.nomask

    mswbak = MswBackup()
    let = mswbak.setup(**target_info)
    let = mswbak.gen_msw_obj_list()

    mswbak.tui_run()
