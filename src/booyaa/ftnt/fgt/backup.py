from booyaa.ftnt.fgt import Fgt
from booyaa.common.export.save_file import save_config
from booyaa.common.fire_and_forget import fire_and_forget
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from pathlib import Path

class FgtBackup:
    def __init__(self):
        super().__init__()

        self.fgt_list = []
        tmp = {
            'addr': '',
            'user': '',
            'password': '',
            'alias': '',
            'hostname': '',
            'ssh_port': 22,
            'https_port': 443,
            'get_secondary': False,
            'backup_dir': 'fg_config',
            'progress': {
                'login': {'code': 0, 'msg': '', 'output': '', 'result': ''},
                'backup': {'code': 0, 'msg': '', 'output': '', 'result': ''},
                'logout': {'code': 0, 'msg': '', 'output': '', 'result': ''},
            }
        }

        self.backup_dir = Path('fg_config')


    def set_fgt_list(self, fgt_list):
        self.fgt_list = []
        for fgt_login_params in fgt_list:
            fgt_obj = FgtObj()
            fgt_obj.setup(**fgt_login_params)
            self.fgt_list.append(fgt_obj)

    @fire_and_forget
    def multi_bulk_run(self):
        self.backup_loop = True
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for fgt in self.fgt_list:
                results.append(executor.submit(fgt.run_backup))
                sleep(0.5)
        [r.result() for r in results]

        sleep(0.5)
        self.backup_loop = False

    # for fgt in fgtbak.fgt_list:
    #     let = fgt.run_primary_backup()
    #     print(fgt.progress['login']['msg'])
    #     print(fgt.progress['backup']['msg'])
    #     print(fgt.progress['logout']['msg'])


class FgtObj(Fgt):
    def __init__(self):
        super().__init__()
        self.progress = {
            'login': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'backup': {'code': -999, 'msg': '', 'output': '', 'result': ''},
            'logout': {'code': -999, 'msg': '', 'output': '', 'result': ''},
        }
        self.msg = ''
        self.config = []
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

        self.progress['login'] = let
        self.msg = self.progress['login']['msg']

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

        self.progress['backup'] = let
        self.msg = self.progress['backup']['msg']

        return let

    def primary_logout(self):
        let = self.api.logout()
        if let['code'] == 0:
            let['result'] = '[green]OK[/]'
        else:
            let['result'] = '[red]NG[/]'

        self.progress['logout'] = let

        return let

    def run_primary_backup(self):
        let = self.primary_login()

        if let['code'] > 0:
            return let
        let = self.primary_backup()
        if let['code'] > 0:
            return let
        let = self.primary_logout()
        if let['code'] > 0:
            return let

        return let

    def secondary_login(self):
        # Primaryにログイン
        _result = self.progress['login']['result']
        let = self.cli.login()
        if let['code'] == 0:
            let['msg'] = f'Login to Primary {self.fgt_info.addr}:{self.fgt_info.https_port}'
        else:
            let['result'] = _result + '\n[red]NG[/]'
            self.progress['login'] = let
    
            self.msg += f'\n{self.progress['login']['msg']}'

            return let

        # Secondaryにログイン
        let = self.cli.login_secondary()
        if let['code'] == 0:
            let['msg'] = f'Login to Secondary {self.fgt_info.addr}:{self.fgt_info.https_port}'
            let['result'] = _result + '\n[green]OK[/]'
        else:
            let['result'] = _result + '\n[red]NG[/]'

        self.progress['login'] = let
        self.msg += f'\n{self.progress['login']['msg']}'

        return let
    
    def secondary_backup(self):
        """"""
        _result = self.progress['backup']['result']
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
                let['result'] = _result +  '\n[g]OK[/]'
            else:
                let['result'] = _result + '\n[r]NG[/]'

        self.progress['backup'] = let
        self.msg += f'\n{self.progress['backup']['msg']}'

        return let

    def secondary_logout(self):
        # secondaryからexit
        _result = self.progress['logout']['result']
        let = self.cli.exit()
        # primaryからlogout

        let = self.cli.logout()
        if let['code'] == 0:
            let['result'] = _result + '[g]OK[/]'
        else:
            let['result'] = _result + '\n[r]NG[/]'

        self.progress['logout'] = let

        return let

    def run_secondary_backup(self):
        let = {'code': -999, 'msg': '', 'output': '', 'result': ''}
        if self.fgt_info.ha_mode == 'Standalone':
            let['code'] = -999
            let['msg'] = self.progress['login']['msg'] + '\nStandalone'
            let['result'] = self.progress['login']['result'] + '\n[red]NG[/]'
            self.msg = let['msg']
            self.progress['login'] = let

            return let

        let = self.secondary_login()
        if let['code'] > 0:
            return let
        let = self.secondary_backup()
        if let['code'] > 0:
            return let
        let = self.secondary_logout()
        if let['code'] > 0:
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
    tmp = [ 
        {
            'addr': '172.16.201.201',
            'user': 'admin',
            'password': 'P@ssw0rd',
            'alias': '',
            'hostname': '',
            'ssh_port': 22,
            'https_port': 443,
            'get_secondary': 'yes',
            'backup_dir': 'fg_config',
        },
        {
            'addr': '172.16.201.202',
            'user': 'admin',
            'password': 'P@ssw0rd',
            'alias': '',
            'hostname': '',
            'ssh_port': 22,
            'https_port': 443,
        },
    ]
    fgtbak = FgtBackup()
    fgtbak.set_fgt_list(tmp)

    fgtbak.multi_bulk_run()
