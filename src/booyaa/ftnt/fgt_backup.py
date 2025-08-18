from rich.live import Live
from rich.table import Table
from pathlib import Path
import sys

from booyaa.ftnt.fg.api import FortiApi
from booyaa.ftnt.fg.cli import FortiCli
from booyaa.common.export.save_file import save_config

from concurrent.futures import ThreadPoolExecutor
from booyaa.common.fire_and_forget import fire_and_forget
from signal import signal, SIGINT
from time import sleep


class FgtBackup:
    def __init__(self, config_ini=Path(Path(__file__).parent.resolve(), 'forti_backup.ini')):
        self.config_ini = config_ini

    def setup(self, target_info_list, nomask=False, backup_dir='fg_config'):
        self.target_info_list = target_info_list
        self.nomask = nomask
        for target_info in self.target_info_list:
            target_info.setdefault('progress', {})
            target_info.setdefault('hostname', '')
            target_info['progress'].setdefault('login', {'result': '', 'msg': ''})
            target_info['progress'].setdefault('backup', {'result': '', 'msg': ''})
            target_info['progress'].setdefault('save', {'result': '', 'msg': ''})
            target_info['progress'].setdefault('logout', {'result': '', 'msg': ''})
            target_info['progress'].setdefault('secondary_login', {'result': '', 'msg': ''})
            target_info['progress'].setdefault('secondary_backup', {'result': '', 'msg': ''})
            target_info['progress'].setdefault('secondary_logout', {'result': '', 'msg': ''})
        self.backup_dir = Path(backup_dir)

    def bulk_run(self):
        """"""
        for target_info in self.target_info_list:
            self.run(target_info)

    @fire_and_forget
    def multi_bulk_run(self):
        self.backup_loop = True
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for target_info in self.target_info_list:
                results.append(executor.submit(self.run, target_info))
                sleep(0.5)
        [r.result() for r in results]
        sleep(0.5)
        self.backup_loop = False


    def run(self, target_info):
        """run backup
        :param target_info: dict with keys 'target', 'user', 'password', 'alias_name'
        :return: None
        :rtype: None
        バックアップノードはAPIなどで取れないので、CLIのshowを取得
        ステータスなど確認して、HA mode a-pだったらバックアップのshowを取得

        """
        api_ftb = FortiApi()
        let = api_ftb.set_target(
            target_info['target'],
            target_info['user'],
            target_info['password'],
            target_info['alias_name'],
            backup_dir=self.backup_dir
        )

        #---------------------#
        # Primary Backup
        #---------------------#
        func_dict = {
            'login': api_ftb.login,
            'backup': api_ftb.monitor.system_config_backup.get,
            'save': save_config,
            'logout': api_ftb.logout
        }

        # primary node
        for func_name, func in func_dict.items():
            if func_name == 'save':
                func_args = [
                    target_info['config'],
                    api_ftb.hostname,
                    api_ftb.fg_alias,
                    api_ftb.version,
                    self.backup_dir
                ]
            else:
                func_args = []
            
            let = func(*func_args)

            target_info['progress'][func_name]['msg'] = let['msg']
            if let['code'] == 0:
                if func_name == 'login':
                    target_info['hostname'] = api_ftb.hostname
                elif func_name == 'backup':
                    target_info['config'] = let['output']
                target_info['progress'][func_name]['result'] = 'OK'
            else:
                target_info['progress'][func_name]['result'] = '[red]NG[/]'
                target_info['message'] = let['msg']
                return

        # HA判定
        if target_info['secondary'] is False or api_ftb.ha_mode != 'Active-Passive' or api_ftb.ha_role != 'main':
            return

        # @todo managed interfaceかどうか判定

        # secondary node
        cli_ftb = FortiCli()

        # #========debug============
        cli_ftb.display = False
        # #========debug============

        let = cli_ftb.set_target(
            target_info['target'],
            target_info['user'],
            target_info['password'],
            target_info['alias_name']
        )

        cli_func_dict = {
            'login': cli_ftb.bastion_login_secondary,
            'backup': cli_ftb.show.get,
            'save': save_config,
            'logout': cli_ftb.bastion_logout_secondary,
        }

        target_info['target'] += '\n ┗━ Standby Node'
        # Secondary node
        for func_name, func in cli_func_dict.items():
            if func_name == 'save':
                func_args = [
                    target_info['config'],
                    api_ftb.secondary_hostname,
                    api_ftb.fg_alias,
                    api_ftb.version,
                    self.backup_dir,
                    'text',
                ]
            else:
                func_args = []
            
            let = func(*func_args)

            target_info['progress'][func_name]['msg'] = let['msg']

            if let['code'] == 0:
                if func_name == 'login':
                    target_info['hostname'] += f'\n{api_ftb.secondary_hostname}'
                elif func_name == 'backup':
                    target_info['config'] = let['output']
                target_info['progress'][func_name]['result'] += '\nOK'
            else:
                target_info['progress'][func_name]['result'] += '\n[red]NG[/]'
                target_info['message'] = let['msg']
                return

        return

    def update_table(self):
        table = Table(title=f'FortiGate Backup\n{self.backup_dir.resolve()}')

        # table header
        table.add_column("Target", style="cyan", no_wrap=True)
        table.add_column("Hostname", style="cyan", no_wrap=True)
        table.add_column("User", style="magenta")
        table.add_column("Password", style="magenta")
        table.add_column("Alias Name", style="magenta")
        table.add_column("Login", style="green")
        table.add_column("Backup", style="green")
        table.add_column("Logout", style="green")
        table.add_column("Message", style="white")

        # table body
        for target_info in self.target_info_list:
            # パスワードマスク
            if self.nomask:
                passwd = target_info['password']
            else:
                passwd = '*' * len(target_info['password'])

            table.add_row(
                target_info['target'],
                target_info['hostname'],
                target_info['user'],
                passwd,
                target_info['alias_name'],
                target_info['progress']['login']['result'],
                target_info['progress']['backup']['result'],
                target_info['progress']['logout']['result'],
                target_info['message']
            )
        return table

    def tui_run(self):
        with Live(self.update_table(), refresh_per_second=4) as live:
            self.multi_bulk_run()
            # SIGINT (Ctrl+C)をキャッチして停止
            def signal_handler(sig, frame):
                self.backup_loop = False  # ping_loopはなぜかeventでは止まらない？？？

            signal(SIGINT, signal_handler)

            # 実行ループ (Ctrl+Cで停止)
            while self.backup_loop:
                live.update(self.update_table())
                sleep(0.1)


if __name__ == '__main__':
    dummy_target_list = [
        {
            'target': '172.16.201.201:443',
            'user': 'admin',
            'password': 'P@ssw0rd',
            'alias_name': 'LabFG01'
        },
        {
            'target': '172.16.201.202',
            'user': 'admin',
            'password': 'P@ssw0rd',
            'alias_name': 'LabFG02'
        },
        # {
        #     'target': '172.16.201.201',
        #     'user': 'nwadmin',
        #     'password': 'mypassword',
        #     'alias_name': 'LabFG02'
        # },
    ]


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
    fgt_bak -t 172.16.201.201 -u admin -p P@ssw0rd
    ```

    ### Primary and Secondary
    ```
    fgt_bak -t 172.16.201.201 -u admin -p P@ssw0rd -s
    ```

    ## CSV File usage
    ```
    fgt_bak -f target.csv
    ```

    ### target csv format is below
    * [optional]header line
        - fg_addr,user,password,alias,backup_secondary
    * Data Line
        - <fortigate addr>,<username>,<passwod>,[optional]<logfile prefix>,[optional]<backup secondary node(via cli show)>
    e.g.)
    ```
    fg_addr,user,password,alias,backup_secondary
    172.16.201.201,admin,P@ssw0rd,Lab-FG01,yes
    192.0.2.1,nw_admin,P@ssw0rd
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

    # パスワードマスク
    parser.add_argument('--nomask', help='[optional]No Password Mask, default is True', action='store_true')

    args = parser.parse_args()

    # 引数チェック
    if args.target and (not args.user or not args.password):
        parser.error("--u and -p are required when -t is specified.")

    target_info_list = []

    if args.target:
        target_info_list = [{
            'target': args.target,
            'user': args.user,
            'password': args.password,
            'alias_name': args.name,
            'secondary': args.secondary,
            'message': '',
        }]

    elif args.file:
        if not Path(args.file).is_file():
            print(f'Error: can not file open {Path(args.file).resolve()}')
            exit(1)

        with open(args.file, 'r', encoding='utf-8_sig') as f:
            lines = f.read().splitlines()

        for i, line in enumerate(lines):
            target_info = line.split(',')
            if i == 0 and target_info[0] == 'fg_addr':
                continue

            # Secandary Node BackupCheckk
            secondary = False
            if len(target_info) >= 5:
                secondary = True if target_info[4] == 'yes' else False

            target_info_list.append({
                'target': target_info[0],
                'hostname': '',
                'user': target_info[1],
                'password': target_info[2],
                'alias_name': target_info[3] if len(target_info) > 3 else '',
                'secondary': secondary,
                'message': '',
                'config': b'',
            })

    ftb = FgtBackup()
    ftb.setup(target_info_list, nomask=args.nomask)
    ftb.tui_run()

    sys.exit()


