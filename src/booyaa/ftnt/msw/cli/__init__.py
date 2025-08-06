from booyaa.ftnt.fg.api import FortiApi
from booyaa.ftnt.fg.cli import FortiCli
from .get import Get
from .show import Show

class MswCli(FortiCli):
    def __init__(self):
        super().__init__()
        self.fgtapi = FortiApi()
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
        self.msw_pass = ''

    def set_target(self,
            fg_addr, fg_user, fg_pass, fg_alias=None,
            msw_uesr=None, msw_pass=None,
            timeout=30, backup_dir=r'fg_config'
        ):

        # FG API
        let = self.fgtapi.set_target(fg_addr, fg_user, fg_pass, fg_alias, timeout, backup_dir)
        if let['code'] != 0:
            return let

        # FG CLI
        let = self.fgtcli.set_target(fg_addr, fg_user, fg_pass, fg_alias, timeout, backup_dir)
        if let['code'] != 0:
            return let

        # MSWのユーザ、パスワードは指定が無ければFGと同一にする
        self.msw_uesr = msw_uesr if msw_uesr else fg_user
        self.msw_pass = msw_pass if msw_pass else fg_pass

        return super().set_target(fg_addr, fg_user, fg_pass, fg_alias, timeout, backup_dir)

    def login_fgt(self):
        self.login()
    
    def logout_fgt(self):
        self.logout()

    def get_fsw_list(self):
        self.fgtapi.login()
        let = self.fgtapi.monitor.switch_controller_managed_switch.get()
        self.fsw_list = self.fgtapi.monitor.switch_controller_managed_switch.fsw_list
        # [
        #   {'name': 'FSW01', 'serial': 'S224ENTF18000490', 'status': 'Connected', 'addr': '10.255.1.1', 'state': 'Authorized'},
        #   {'name': 'S224EPTF20005577', 'serial': 'S224EPTF20005577', 'status': 'Idle', 'addr': '-', 'state': 'DeAuthorized'}
        # ]




