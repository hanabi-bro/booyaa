from booyaa.ftnt.fg.cli import FortiCli
from booyaa.ftnt.fg.api import FortiApi
from booyaa.ftnt.msw.cli.get import Get
from booyaa.ftnt.msw.cli.show import Show

class MswCli(FortiCli):
    def __init__(self):
        super().__init__()
        self.fgtcli = FortiCli()
        self.get = Get(self)
        self.show = Show(self)
        self.msw_hostname = ''
        self.msw_serial = ''
        self.msw_addr = ''
        self.msw_version = ''
        self.msw_build = ''
        self.msw_status = ''
        self.msw_state = ''
        self.msw_user = ''
        self.msw_password = ''

        self.fgt_api = FortiApi()

    def setup(self,
            fg_addr, fg_user, fg_password, fg_alias=None,
            msw_addr=None, msw_user='admin', msw_password=None,
            timeout=30, backup_dir=r'fg_config'
        ):

        # MSWのユーザ、パスワードは指定が無ければFGと同一にする
        if msw_addr is None:
            return {
                'code': 1,
                'msg': '[Error]msw_addr is need',
            }

        self.msw_addr = msw_addr
        self.msw_user = msw_user
        self.msw_password = msw_password or self.password

        let = self.fgt_api.set_target(
            target = fg_addr,
            user = fg_user,
            password = fg_password,
            alias = fg_alias,
            timeout = timeout,
            backup_dir = backup_dir)

        return self.set_target(fg_addr, fg_user, fg_password, fg_alias, timeout, backup_dir)

    def login_fgt(self):
        self.login()
    
    def logout_fgt(self):
        self.logout()

    def msw_login(self):
        let = super().login()
        let = self.execute_ssh(
            addr = self.msw_addr,
            user = self.msw_user,
            password = self.msw_password
        )

    # def msw_logout(self):
    #     self.exit()
    #     self.logout_fgt()


if __name__ == '__main__':
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
    mswcli.setup(**target_info)
    mswcli.display = True

    let = mswcli.fgt_api.login()
    let = mswcli.fgt_api.get_node_info(mswcli.fgt_api)
    let = mswcli.fgt_api.logout()

    print(mswcli.fgt_api.__dict__)






