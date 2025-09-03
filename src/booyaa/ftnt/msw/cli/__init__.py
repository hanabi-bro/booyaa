from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.msw.model.msw_info import MswInfo
from booyaa.ftnt.fgt.cli import FgtCli

from booyaa.ftnt.fgt.cli.get import Get as FgtGet
from booyaa.ftnt.fgt.cli.show import Show as FgtShow
from booyaa.ftnt.fgt.cli.execute import Execute as FgtExecute

from booyaa.ftnt.msw.cli.get import Get as MswGet
from booyaa.ftnt.msw.cli.show import Show as MswShow

from booyaa.common.export.save_file import save_config

from pathlib import Path


class MswCli(FgtCli):
    def __init__(self, fgt_info: FgtInfo, msw_info: MswInfo):
        super().__init__(fgt_info)
        self.msw_info = msw_info
        self.backup_dir = 'fg_config'

    def set_cli_fgt(self):
        self.get = FgtGet(self)
        self.show = FgtShow(self)
        self.execute = FgtExecute(self)

    def set_cli_msw(self):
        self.get = MswGet(self)
        self.show = MswShow(self)


    def set_target(self,
            fgt_addr, fgt_user, fgt_password, alias='', fgt_hostname='', fgt_ssh_port=22, fgt_https_port=443,
            msw_addr='', msw_user='', msw_password='', msw_hostname='', msw_ssh_port=22, msw_https_port=443,
            backup_dir='', **kwargs):

        let = super().set_target(fgt_addr, fgt_user, fgt_password, alias, fgt_hostname, fgt_ssh_port, fgt_https_port)

        self.msw_info.addr = msw_addr
        self.msw_info.user = msw_user
        self.msw_info.password = msw_password
        self.msw_info.alias = alias
        self.msw_info.hostname = msw_hostname
        self.msw_info.ssh_port = msw_ssh_port
        self.msw_info.https_port = msw_https_port

        self.backup_dir = backup_dir or self.backup_dir

        let['msg'] = f'Set FGT {self.fgt_info.addr}'

        return let

    def login_fgt(self):
        let = super().login()
        self.set_cli_fgt()
        return let

    def logout_fgt(self):
        let = super().logout()
        return let

    def login_msw(self, addr='', user='', password='', hostname='', port=22, timeout=None):

        if not self.session:
            let = self.login_fgt()
            if let['code'] != 0:
                return let

        self.msw_info.addr = addr or self.msw_info.addr
        self.msw_info.user = user or self.msw_info.user
        self.msw_info.password = password or self.msw_info.password
        self.msw_info.hostname = hostname or self.msw_info.hostname
        self.msw_info.ssh_port = port or self.msw_info.ssh_port
        let = self.execute_ssh(self.msw_info.addr, self.msw_info.user, self.msw_info.password, self.msw_info.ssh_port, timeout)
        if let['code'] != 0:
            return let
        self.set_cli_msw()

        if not self.msw_info.hostname:
            let = self.get_msw_info()

        return let

    def logout_msw(self):
        let = self.exit()
        if let['code'] != 0:
            return let
        self.set_cli_fgt()
        return let

    def backup(self, backup_dir=''):
        let = self.show.get()
        if let['code'] != 0:
            return let

        backup_dir = backup_dir or self.backup_dir

        # MSW用にペアレントのFGのaliasかホスト名フォルダを作成
        backup_dir = Path(backup_dir, self.fgt_info.alias or self.fgt_info.hostname )

        if let['code'] == 0:
            let = save_config(
                content=let['output'],
                hostname=self.msw_info.hostname,
                alias=self.fgt_info.alias,
                version=self.msw_info.version,
                export_dir=backup_dir,
                format='text',
                encode='utf-8',
            )
        
        return let

    def get_msw_info(self):
        let = self.get.system_status.get()
        try:
            self.msw_info.hostname = self.get.system_status.hostname
            self.msw_info.model = self.get.system_status.model
            self.msw_info.serial = self.get.system_status.serial
            self.msw_info.version = self.get.system_status.version
        except Exception as e:
            let['code'] = -1
            let['msg'] = f'[Error]get mws info error {e}'

        return let


if __name__ == '__main__':
    fg_info = {
        'fgt_addr': '172.16.201.201',
        'fgt_user': 'admin',
        'fgt_password': 'P@ssw0rd',
        'alias': 'ラボFG01',
        'fgt_hostname': '',
        'get_secondary': 'yes',
        'fgt_ssh_port': 22,
        'fgt_https_port': 443,
        'backup_dir': 'fg_config',
        'timeout': 60,
        'msw_addr': '10.255.1.1',
        'msw_user': 'admin',
        'msw_password': 'P@ssw0rd',
    }

    msw = MswCli(FgtInfo(), MswInfo())
    msw.set_target(**fg_info)
    print(msw.fgt_info)
    print(msw.msw_info)
    msw.display=True
    # msw.login_fgt()
    msw.login_msw(addr='10.255.1.1', user='admin', password='P@ssw0rd')
    msw.backup()
    msw.logout_msw()
    msw.logout_fgt()
