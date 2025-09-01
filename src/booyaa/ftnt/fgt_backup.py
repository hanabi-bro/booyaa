from rich.live import Live
from rich.table import Table
from pathlib import Path
from time import sleep
import csv

from booyaa.ftnt.fgt.backup import FgtBackup

class CuiFgtBackup(FgtBackup):
    def __init__(self):
        self.nomask = False
        self.msg = ''
        self.args_fgt_list = []
        super().__init__()

    def update_table(self):
        table = Table(title=f'FortiGate Backup\n{self.backup_dir.resolve()}')

        # table header
        table.add_column("Addr", style="cyan", no_wrap=True)
        table.add_column("Hostname", style="cyan", no_wrap=True)
        table.add_column("User", style="magenta")
        table.add_column("Password", style="magenta")
        table.add_column("Alias Name", style="magenta")
        table.add_column("Login", style="green")
        table.add_column("Backup", style="green")
        table.add_column("Logout", style="green")
        table.add_column("Message", style="white")

        tmp = {
            'addr': '',
            'user': '',
            'password': '',
            'alias': '',
            'hostname': '',
            'ssh_port': 22,
            'https_port': 443,
            'get_secondary': 'no',
            'backup_dir': 'fg_config',
            'progress': {
                'login': {'code': 0, 'msg': '', 'output': '', 'result': ''},
                'backup': {'code': 0, 'msg': '', 'output': '', 'result': ''},
                'logout': {'code': 0, 'msg': '', 'output': '', 'result': ''},
            }
        }


        # table body
        for fgt_obj in self.fgt_list:
            # パスワードマスク
            if self.nomask:
                passwd = fgt_obj.fgt_info.password
            else:
                passwd = '*' * len(fgt_obj.fgt_info.password)

            # secondary yes
            hostname = fgt_obj.fgt_info.hostname
            if fgt_obj.get_secondary == 'yes':
                hostname += '\n' + fgt_obj.fgt_info.secondary_hostname

            table.add_row(
                fgt_obj.fgt_info.addr,
                hostname,
                fgt_obj.fgt_info.user,
                passwd,
                fgt_obj.fgt_info.alias,
                fgt_obj.cui_progress['login']['result'],
                fgt_obj.cui_progress['backup']['result'],
                fgt_obj.cui_progress['logout']['result'],
                fgt_obj.msg
            )
        return table

    def tui_run(self):
        with Live(self.update_table(), refresh_per_second=4) as live:
            self.run_backup_parallel()
            # SIGINT (Ctrl+C)をキャッチして停止
            def signal_handler(sig, frame):
                self.backup_loop = False  # ping_loopはなぜかeventでは止まらない？？？

            # signal(SIGINT, signal_handler)

            # 実行ループ (Ctrl+Cで停止)
            while self.backup_loop:
                live.update(self.update_table())
                sleep(0.1)

            # 最終更新
            sleep(0.5)
            live.update(self.update_table())


    def load_list(self, list_csv_path, max_cols=8):
        headers = ['addr', 'user', 'password', 'alias', 'get_secondary', 'backup_direcotry', 'https_port', 'ssh_port']
        list_csv_path = Path(list_csv_path)
        if not list_csv_path.is_file():
            print(f'[Error]Can not file open {list_csv_path.resolve()}')
            exit()

        self.args_fgt_list = []

        # ファイルからリストを作成
        with open(list_csv_path, newline="", encoding="utf-8") as f:
            _args_list = csv.reader(f)
            for i, row in enumerate(_args_list):
                # 1行目がヘッダ行だったら削除する
                if i == 0 and row[0] in ['fg_addr', 'addr']:
                    continue

                # カンマずれ等を補正
                if len(row) < max_cols:
                    row.extend([""] * (max_cols - len(row)))
                # 多すぎれば切り捨てる
                elif len(row) > max_cols:
                    row = row[:max_cols]

                row_dict = dict(zip(headers, row))

                self.args_fgt_list.append(row_dict)


if __name__ == '__main__':
    fgt_login_list = [
        {
            'addr': '172.16.201.201',
            'user': 'admin',
            'password': 'P@ssw0rd',
            'alias': '',
            'hostname': '',
            'get_secondary': 'yes',
            'ssh_port': 22,
            'https_port': 443,
            'backup_dir': 'fg_config',
        },
        {
            'addr': '172.16.201.202',
            'user': 'admin',
            'password': 'P@ssw0rd',
            'alias': '',
            'hostname': '',
            'get_secondary': 'no',
            'ssh_port': 22,
            'https_port': 443,
        },
    ]
    # fgtbak = CuiFgtBackup()

    # # fgtbak.load_list('tmp/list.csv')
    # # fgtbak.set_fgt_list(fgtbak.args_fgt_list)
    # fgtbak.set_fgt_list(fgt_login_list)
    # fgtbak.tui_run()


    from argparse import ArgumentParser, RawTextHelpFormatter
    from textwrap import dedent

    class MyArgumentParser(ArgumentParser):
        def error(self, message):
            print('error occured while parsing args : '+ str(message))
            self.print_help() 
            exit()

    msg = dedent("""\
    ~~~ FortiGate Config Backup ~~~
    ## CLI usage
    ### Primary Only
    ```
    fgt_bak -t 172.16.201.201 -u admin -p my_password
    ```

    ### Primary and Secondary
    ```
    fgt_bak -t 172.16.201.201 -u admin -p my_password -s
    ```

    ## CSV File usage
    ```
    fgt_bak -f target.csv
    ```

    ### target csv format is below
    * [optional]header line
        - fg_addr,user,password,alias,get_secokdary,backup_direcotry,https_port,ssh_port
    * Data Line
        - <fortigate addr>,<username>,<passwod>,[optional]<logfile prefix>,[optional]<backup secondary node(via cli show),[optional]https port,[optional]ssh port>
    e.g.)
    ```
    fg_addr,user,password,alias,get_secokdary,backup_direcotry,https_port,ssh_port
    172.16.201.201,admin,my_password,Lab-FG01,yes
    192.0.2.1,nw_admin,nw_admin_password
    ```
    """)

    parser = MyArgumentParser(description=msg, formatter_class=RawTextHelpFormatter)
    # 直接指定とファイル指定は同時に使えない
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--target', help='ipaddr or hostname\ne.g.) forti_config_backup -t 172.16.201.201 -u admin -p P@ssw0rd')
    group.add_argument('-f', '--file', help='target csv file\ne.g.) forti_config_backup -f target.csv\ncsv fromat sample)\n172.16.201.201,admin.P@ssword\n172.16.201.202,nwadmin,MyP@ssW0rd')

    # 直接指定の場合、-t, -u, -pは必須
    target_group = parser.add_argument_group('Target Mode', '-t 指定時に必要な引数')
    target_group.add_argument('-u', '--user', help='login user name')
    target_group.add_argument('-p', '--password', help='login password')
    target_group.add_argument('-n', '--name', help='[optional]logfile name, e.g.) log file prefix instead of hostname')

    # セカンダリノード取得
    parser.add_argument('-s', '--secondary', action='store_true')

    # ログ出力ディレクトリ指定
    parser.add_argument('-d', '--directory', default='./fg_config', help='backup directory path default is ./fg_config')

    # https port
    parser.add_argument('--https_port', default=443, help='HTTPS port default is 443')

    # ssh port
    parser.add_argument('--ssh_port', default=22, help='SSH port default is 22')

    # パスワードマスク
    parser.add_argument('--nomask', help='[optional]No Password Mask, default is True', action='store_true')

    args = parser.parse_args()

    # 引数チェック
    if args.target and (not args.user or not args.password):
        parser.error("--u and -p are required when -t is specified.")

    fgt_login_list = []

    fgtbak = CuiFgtBackup()

    if args.target:
        fgt_login_list = [{
            'addr': args.target,
            'user': args.user,
            'password': args.password,
            'alias': args.name,
            'hostname': '',
            'get_secondary': 'yes' if args.secondary else 'no',
            'https_port': args.https_port,
            'ssh_port': args.ssh_port,
            'backup_dir': args.directory,
        }]
    elif args.file:
        fgtbak.load_list(args.file)
        fgt_login_list = fgtbak.args_fgt_list

    fgtbak.set_fgt_list(fgt_login_list)
    fgtbak.tui_run()
