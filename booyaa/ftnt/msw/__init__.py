from booyaa.ftnt.fgt.api import FgtApi
from booyaa.ftnt.msw.model.msw_info import MswInfo
from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.msw.cli import MswCli


class Msw:
    def __init__(self, fgt_info: FgtInfo | None = None, msw_info: MswInfo | None = None):
        self.fgt_info = fgt_info or FgtInfo()
        self.msw_info = msw_info or MswInfo()
        self.fgt_api = FgtApi(self.fgt_info)
        self.cli = MswCli(self.fgt_info, self.msw_info)
        self.backup_dir = 'fg_config'

    def setup(self,
            fgt_addr, fgt_user, fgt_password, alias='', fgt_hostname='', fgt_ssh_port=22, fgt_https_port=443,
            msw_addr='', msw_user='', msw_password='', msw_hostname='', msw_ssh_port=22, msw_https_port=443,
            backup_dir='', **kwargs):
        let = {'code': 0, 'msg': '', 'output': ''}

        # setup fgt info
        self.fgt_info.addr = fgt_addr
        self.fgt_info.user = fgt_user
        self.fgt_info.password = fgt_password
        self.fgt_info.alias = alias
        self.fgt_info.hostname = fgt_hostname
        self.fgt_info.ssh_port = fgt_ssh_port
        self.fgt_info.https_port = fgt_https_port

        # setup msw info
        self.msw_info.addr = msw_addr
        self.msw_info.user = msw_user
        self.msw_info.password = msw_password
        self.msw_info.hostname = msw_hostname
        self.msw_info.ssh_port = msw_ssh_port
        self.msw_info.https_port = msw_https_port

        # backup directory
        self.bacup_dir = backup_dir or self.backup_dir
        self.cli.backup_dir = self.backup_dir

        return let


if __name__ == '__main__':
    fg_info = {
        'fgt_addr': '172.16.201.201',
        'fgt_user': 'admin',
        'fgt_password': 'P@ssw0rd',
        'alias': '',
        'fgt_hostname': '',
        'get_secondary': 'yes',
        'fgt_ssh_port': 22,
        'fgt_https_port': 443,
        'backup_dir': 'fg_config',
        'timeout': 60
    }


    msw = Msw()
    msw.setup(**fg_info)
    msw.cli.display=True
    msw.cli.login_fgt()
    msw.cli.login_msw(addr='10.255.1.1', user='admin', password='P@ssw0rd')
    msw.cli.get.switch_physical_port.get()
    msw.cli.logout_msw()
    msw.cli.logout_fgt()

