from booyaa.ftnt.fgt import Fgt
from booyaa.common.export.save_file import save_config
from booyaa.common.fire_and_forget import fire_and_forget

from concurrent.futures import ThreadPoolExecutor
from time import sleep
from pathlib import Path


class FgtBackup:
    def __init__(self):
        self.fgt_list = []
        self.fgt = Fgt()
        self.backup_dir = Path('fg_config')
        self.backup_loop = False


    def set_fgt_list(self, fgt_list):
        self.fgt_list = []
        for fgt_login_params in fgt_list:
            fgt_obj = FgtObj()
            fgt_obj.setup(**fgt_login_params)
            self.fgt_list.append(fgt_obj)

    # @fire_and_forget
    def run_backup(self):
        for fgt in self.fgt_list:
            fgt.run_backup()
            sleep(1)

    @fire_and_forget
    def run_backup_parallel(self):
        self.backup_loop = True
        self.futures = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for fgt in self.fgt_list:
                self.futures.append(executor.submit(fgt.run_backup))
                sleep(1)
            for future in self.futures:
                try:
                    future.result()  # 例外が発生した場合にキャッチするために必要
                except Exception as e:
                    print(f"Error occurred: {e}")

        # [r.result() for r in self.futures]
        sleep(1)
        self.backup_loop = False


class FgtObj(Fgt):
    def __init__(self):
        super().__init__()
        self.primary_progress = {
            'login': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'backup': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'logout': {'code': -999, 'msg': '', 'output': '', 'result': ''},
        }
        self.secondary_progress = {
            'login': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'backup': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'logout': {'code': -999, 'msg': '', 'output': '', 'result': ''},
        }
        self.cui_progress = {
            'login': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'backup': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'logout': {'code': -999, 'msg': '', 'output': '', 'result': ''},
        }
        self.msg = ''
        self.primary_config = ''
        self.secondary_config = ''

        self.get_secondary = ''
        self.backup_dir = ''
        self.cli.display = False

    def setup(self, addr, user, password, alias='', hostname='', ssh_port=22, https_port=443, get_secondary='', backup_dir='fg_config', **kwargs):
        let = super().setup(addr=addr, user=user, password=password, alias=alias, hostname=hostname, ssh_port=ssh_port, https_port=https_port)
        self.get_secondary = get_secondary
        self.backup_dir = backup_dir

        return let

    def login_api(self):
        return self.api.login()

    def primary_login(self):
        let = self.api.login()

        if let['code'] == 0:
            let['msg'] = f'Login to {self.fgt_info.addr}:{self.fgt_info.https_port}'
            let['result'] = '[green]OK[/]'
        else:
            let['result'] = '[red]NG[/]'

        self.primary_progress['login'] = let

        return let

    def primary_backup(self):
        let = self.api.monitor.system_config_backup.get()
        if let['code'] == 0:
            let = save_config(
                content=let['output'],
                hostname=self.fgt_info.hostname,
                alias=self.fgt_info.alias,
                version=self.fgt_info.version,
                export_dir=self.backup_dir
            )
            if let['code'] == 0:
                let['result'] = '[green]OK[/]'
            else:
                let['result'] = '[red]NG[/]'

        self.primary_progress['backup'] = let

        return let

    def primary_logout(self):
        let = self.api.logout()
        if let['code'] == 0:
            let['result'] = '[green]OK[/]'
        else:
            let['result'] = '[red]NG[/]'

        self.primary_progress['logout'] = let

        return let

    def run_primary_backup(self):
        let = self.primary_login()
        self.cui_progress['login'] = let
        self.msg = let['msg']
        if let['code'] != 0:
            return let

        let = self.primary_backup()
        self.cui_progress['backup'] = let
        self.msg = let['msg']
        if let['code'] > 0:
            return let

        let = self.primary_logout()
        self.cui_progress['logout'] = let
        if let['code'] > 0:
            return let

        return let

    def secondary_login(self):
        # Primaryにログイン
        let = self.cli.login()
        if let['code'] == 0:
            let['msg'] = f'Login to Primary {self.fgt_info.addr}:{self.fgt_info.https_port}'
            let['result'] = '[green]OK[/]'
        else:
            let['result'] = '[red]NG[/]'
            return let

        # Secondaryにログイン
        let = self.cli.login_secondary()
        if let['code'] == 0:
            let['msg'] = f'Login to Secondary {self.fgt_info.addr}:{self.fgt_info.https_port}'
            let['result'] = '[green]OK[/]'
        else:
            let['result'] = '[red]NG[/]'

        self.secondary_progress['login'] = let

        return let

    def secondary_backup(self):
        """"""
        let = self.cli.show.get()
        if let['code'] == 0:
            let = save_config(
                content=let['output'],
                hostname=self.fgt_info.secondary_hostname,
                alias=self.fgt_info.alias,
                version=self.fgt_info.version,
                export_dir=self.backup_dir,
                format='text',
                encode='utf-8',
            )

            if let['code'] == 0:
                let['result'] = '[green]OK[/]'
            else:
                let['result'] = '[red]NG[/]'

        self.secondary_progress['backup'] = let

        return let

    def secondary_logout(self):
        # secondaryからexit
        let = self.cli.exit()
        # primaryからlogout

        let = self.cli.logout()
        if let['code'] == 0:
            let['result'] = '[green]OK[/]'
        else:
            let['result'] = '[red]NG[/]'

        self.secondary_progress['logout'] = let

        return let

    def run_secondary_backup(self):
        let = {'code': -999, 'msg': '', 'output': '', 'result': ''}
        if self.fgt_info.ha_mode == 'Standalone':
            let['code'] = -999
            let['msg'] = 'Standalone'
            let['result'] = '[red]NG[/]'
            self.secondary_progress['login'] = let

            let['msg'] = f'{self.primary_progress['backup']['msg']}\n{self.secondary_progress['login']['msg']}'
            let['result'] = f'{self.primary_progress['login']['result']}\n{self.secondary_progress['login']['result']}'
            self.cui_progress['login'] = let

            self.msg = let['msg']

            return let

        let = self.secondary_login()
        if let['code'] > 0:
            let['msg'] = f'{self.primary_progress['login']['msg']}\n{self.secondary_progress['login']['msg']}'
            let['result'] = f'{self.primary_progress['login']['result']}\n{self.secondary_progress['login']['result']}'
            self.cui_progress['login'] = let
            self.msg = let['msg']
            return let

        let = self.secondary_backup()
        if let['code'] > 0:
            let['msg'] = f'{self.primary_progress['backup']['msg']}\n{self.secondary_progress['backup']['msg']}'
            let['result'] = f'{self.primary_progress['backup']['result']}\n{self.secondary_progress['backup']['result']}'
            self.cui_progress['backup'] = let
            self.msg = let['msg']
            return let
        let = self.secondary_logout()
        if let['code'] > 0:
            let['msg'] = f'{self.primary_progress['logout']['msg']}\n{self.secondary_progress['logout']['msg']}'
            let['result'] = f'{self.primary_progress['logout']['result']}\n{self.secondary_progress['logout']['result']}'
            self.cui_progress['logout'] = let
            return let

        return let

    def run_backup(self):
        let = self.run_primary_backup()
        if let['code'] > 0:
            return let

        if self.get_secondary == 'yes':
            let = self.run_secondary_backup()

        return let


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
    fgt_backup = FgtBackup()
    fgt_backup.set_fgt_list(fgt_login_list)
    fgt_backup.run_backup_parallel()
    # fgt_backup.run_backup()

