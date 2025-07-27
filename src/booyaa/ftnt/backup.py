from rich.live import Live
from rich.table import Table
from pathlib import Path
import sys

from booyaa.ftnt.api import FortiApi
from booyaa.common.export.save_file import save_config

from concurrent.futures import ThreadPoolExecutor
from booyaa.common.fire_and_forget import fire_and_forget
from signal import signal, SIGINT
from time import sleep


class FortiBackup:
    def __init__(self, config_ini=Path(Path(__file__).parent.resolve(), 'forti_backup.ini')):
        self.config_ini = config_ini

    def setup(self, target_info_list, nomask=False):
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
        ftb = FortiApi()
        self.backup_dir = Path('fg_config')

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
        let = api_ftb.set_target(target_info['target'], target_info['user'], target_info['password'], target_info['alias_name'], backup_dir=self.backup_dir)

        #---------------------#
        # Primary Backup
        #---------------------#
        func = [
            api_ftb.login,
            api_ftb.monitor.system_config_backup.get,
            save_config,
            api_ftb.logout,
        ]
        func_name = ['login', 'backup', 'save', 'logout']

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
        # if api_ftb.ha_mode != 'active-passive' or api_ftb.ha_mode == 'a-p':
        #     return

        # # secondary node
        # cli_ftb = CliBackup()

        # #========debug============
        # cli_ftb.display = True
        # #========debug============

        # let = cli_ftb.set_target(target_info['target'], target_info['user'], target_info['password'], target_info['alias_name'])

        # func = [
        #     cli_ftb.login,
        #     cli_ftb.get_backup,
        #     cli_ftb.logout,
        # ]
        # func_name = ['login', 'backup', 'logout']

        # for i, f in enumerate(func):
        #     if func_name[i] == 'backup':
        #         let = f(full=False, secondary=True)
        #     else:
        #         let = f()
        #     target_info['progress'][func_name[i]]['msg'] += let['msg']
        #     if let['code'] == 0:
        #         if func_name[i] == 'login':
        #             target_info['hostname'] += f'\n{cli_ftb.secondary_hostname}'
        #         target_info['progress'][func_name[i]]['result'] += '\nOK'
        #     else:
        #         target_info['progress'][func_name[i]]['result'] = '\n[red]NG[/]'
        #         target_info['message'] = let['msg']
        #         return

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
    ## set target
    forti_config_backup -t 172.16.201.201 -u admin -p P@ssw0rd

    ## target file csv
    forti_config_backup -f target.csv
    ### target csv format is below
    <fortigate addr>,<username>,<passwod>,[optional]<logfile prefix>
    e.g.)
    ```
    172.16.201.201,admin,P@ssword,
    172.16.201.202,nwadmin,mypassword,LabFG01
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
    parser.add_argument('-b', '--both', action='store_true')

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
        target_info_list = [{'target': args.target, 'user': args.user, 'password': args.password, 'alias_name': args.name, 'message': ''}]

    elif args.file:
        if not Path(args.file).is_file():
            print(f'Error: can not file open {Path(args.file).resolve()}')
            exit(1)

        with open(args.file, 'r', encoding='utf-8_sig') as f:
            lines = f.read().splitlines()

        for line in lines:
            target_info = line.split(',')
            target_info_list.append({
                'target': target_info[0],
                'hostname': '',
                'user': target_info[1],
                'password': target_info[2],
                'alias_name': target_info[3] if len(target_info) > 3 else '',
                'message': '',
                'config': b'',
            })

    ftb = FortiBackup()
    ftb.setup(target_info_list, nomask=args.nomask)
    ftb.tui_run()

    sys.exit()


'''
* 7.0には/system/cfsはまだない？7.0でGUI時のデバッグする。
* get node checkで500で帰ってきてるけどエラー拾えていないので、見直し必要
  2025-07-27   15:08.26   /home/mobaxterm  curl -k -b cookie.txt -X GET https://${FGADDR}/api/v2/monitor/system/csf?scope=global | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   224  100   224    0     0   5893      0 --:--:-- --:--:-- --:--:--  6054
{
  "http_method": "GET",
  "revision": "0.0.1",
  "status": "error",
  "http_status": 500,
  "vdom": "root",
  "path": "system",
  "name": "csf",
  "action": "",
  "serial": "FG100FTK22027480",
  "version": "v7.0.11",
  "build": 489
}
'''