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
        table.add_column("Target", style="cyan", no_wrap=True)
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

            table.add_row(
                fgt_obj.fgt_info.addr,
                fgt_obj.fgt_info.hostname,
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
    fgtbak = CuiFgtBackup()

    # fgtbak.load_list('tmp/list.csv')
    # fgtbak.set_fgt_list(fgtbak.args_fgt_list)
    fgtbak.set_fgt_list(fgt_login_list)
    fgtbak.tui_run()


    # fgtbak.multi_bulk_run()

    # for fgt in fgtbak.fgt_list:
    #     let = fgt.run_primary_backup()
    #     print(fgt.progress['login']['msg'])
    #     print(fgt.progress['backup']['msg'])
    #     print(fgt.progress['logout']['msg'])

    # for fgt in fgtbak.fgt_list:
    #     fgt.cli.display=True
    #     fgt.cli.login()
    #     fgt.cli.logout()
    #     print(fgt.__dict__)

    # for fgt in fgtbak.fgt_list:
    #     fgt.api.login()
    #     fgt.api.logout()
    #     print(fgt.__dict__)

