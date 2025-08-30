from booyaa.ftnt.msw.cli import MswCli
from booyaa.ftnt.fg.api import FortiApi


class MswBakup(MswCli):
    def __init__(self):
        super().__init__()
        self.msw_list = {}

    def gen_msw_lsit(self):
        let = self.fgt_api.get_node_info(self.fgt_api)



if __name__ == '__main__':
    msw_bak = MswBakup()
    target_info = {
        'fg_addr': '172.16.201.201',
        'fg_user': 'admin',
        'fg_password': 'P@ssw0rd',
        'fg_alias': 'ラボFG',
        'msw_addr': '192.0.2.1',
        'msw_user': 'admin',
        'msw_password': 'P@ssw0rd',
        'timeout': 30,
    }
    
    mswcli = MswCli()
    mswcli.set_target(**target_info)
    mswcli.display = True
    mswcli.msw_login()


