from booyaa.ftnt.fg.api import FortiApi
from booyaa.ftnt.fg.cli import FortiCli

from booyaa.ftnt.msw.cli import MswCli
from booyaa.ftnt.msw.cli.get import Get as MswGet
from booyaa.ftnt.msw.cli.show import Show as MswShow

from booyaa.common.export.save_file import save_config

from pathlib import Path
from traceback import format_exc

class FgtMswCli(FortiCli):
    def __init__(self):
        super().__init__()

        self.fgt_cli = FortiCli()
        self.fgt_api = FortiApi()


    def set_target(self, target, user, password, alias=None, timeout=30, backup_dir=r'fg_config'):
        let = self.fgt_api.set_target(target=target, user=user, password=password, alias=alias, backup_dir=backup_dir)
        return super().set_target(target=target, user=user, password=password, alias=alias, backup_dir=backup_dir)

    def gen_msw_list(self, msw_port=None, msw_user=None, msw_password=None):
        let = self.fgt_api.login()
        if let['code'] != 0:
            return let
        let = self.fgt_api.login()
        if let['code'] != 0:
            return let
        # print(capi.cmdb.system_ha.get())
        # capi.get_node_info(capi)
        let = self.fgt_api.monitor.switch_controller_managed_switch.get()
        if let['code'] != 0:
            return let

        _list = self.fgt_api.monitor.switch_controller_managed_switch.msw_list
        self.msw_list = []

        for msw_info in _list:
            msw = Msw()
            msw.set_target(
                fg_addr = self.addr,
                fg_port = self.port or 22,
                fg_user = self.user,
                fg_password = self.password,
                fg_hostname = self.hostname,
                fg_serial = self.serial,
                fg_alias = self.alias,
                msw_addr = msw_info['addr'],
                msw_port = msw_port or 22,
                msw_user = msw_user or self.user,
                msw_password = msw_password or self.password,
                msw_hostname = msw_info['hostname'],
                msw_serial = msw_info['serial'],
                msw_state = msw_info['state'],
                msw_status = msw_info['status'],
                msw_model = msw_info['model'],
                msw_version = msw_info['version'],
                msw_build = msw_info['build'],
            )
            self.msw_list.append(msw)

        return let


class Msw(FortiCli):
    def __init__(self):
        super().__init__()
        self.fgt_cli = FortiCli()
        self.msw_cli = MswCli()

        self.msw_cli.show = MswShow(self)
        self.msw_cli.get = MswGet(self)

        self.fg_addr = ''
        self.fg_port = ''
        self.fg_user = ''
        self.fg_password = ''
        self.fg_hostname = ''
        self.fg_alias = ''
        self.fg_serial = ''
        self.fg_version = ''

        self.node_info_flg = True
        self.secondary_info_flg = True

    def set_target(self, 
            fg_addr, fg_port, fg_user, fg_password, fg_hostname, fg_serial, fg_alias,
            msw_addr, msw_port, msw_user, msw_password, msw_hostname, msw_serial, msw_state, msw_status, msw_model, msw_version, msw_build
        ):

        self.fg_addr = fg_addr
        self.fg_port = fg_port or 22
        self.fg_user = fg_user
        self.fg_password = fg_password
        self.fg_alias = fg_alias
        self.fg_hostname = fg_hostname
        self.fg_serial = fg_serial
        self.fg_version = fg_alias

        self.addr = msw_addr
        self.port = msw_port or 22
        self.user = msw_user
        self.password = msw_password
        self.hostname = msw_hostname
        self.serial = msw_serial
        self.state = msw_state
        self.status = msw_status
        self.model = msw_model
        self.version = msw_version
        self.build = msw_build

        self.config = ''

    def login_fgt(self):
        let = self.login(addr=self.fg_addr, user=self.fg_user, password=self.fg_password)

    def login_msw(self):
        let = self.login_fgt()
        return self.execute_ssh(self.addr, self.user, self.password)

    def logout_msw(self):
        return self.logout()

    def backup(self, full=False, cmd_strip=True, format='text', encode='utf-8', backup_dir='./fg_config'):
        let = {'code': 0, 'msg': '', 'output': ''}
        try:
            backup_dir = Path(backup_dir or self.backup_dir)
            backup_dir.mkdir(exist_ok=True)
            self.backup_dir = Path(backup_dir or self.backup_dir, self.fg_alias or self.fg_hostname)
            self.backup_dir.mkdir(exist_ok=True)
        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error]Failed backup directory {format_exc}'

        let = self.msw_cli.show.get(full=full, cmd_strip=cmd_strip)
        if let['code'] != 0:
            return let
        self.config = let['output']
        let = save_config(
            content=self.config,
            hostname=self.hostname,
            alias=None,
            version=self.version,
            export_dir=self.backup_dir,
            format=format,
            encode=encode
        )
        return let



if __name__ == '__main__':
    fgt_msw_cli = FgtMswCli()
    fgt_msw_cli.display = True  # デバッグ用に出力を有効化
    let = fgt_msw_cli.set_target(
        user='admin',
        password='P@ssw0rd',
        target='172.16.201.201',
        alias='LABFG01',
    )

    fgt_msw_cli.gen_msw_list()
    msw_list = fgt_msw_cli.msw_list

    for msw in msw_list:
        msw.display = True
        if msw.status == 'Connected':
            msw.login_msw()
            let = msw.backup()
            print(let)
            # print(msw.fg_addr)
            # print(msw.fg_port)
            # print(msw.fg_user)
            # print(msw.fg_password)
            # print(msw.fg_alias)
            # print(msw.fg_hostname)
            # print(msw.fg_serial)
            # print(msw.fg_version)
            # print(msw.addr)
            # print(msw.port)
            # print(msw.user)
            # print(msw.password)
            # print(msw.hostname)
            # print(msw.serial)
            # print(msw.state)
            # print(msw.status)
            # print(msw.model)
            # print(msw.version)
            # print(msw.build)

            msw.logout_msw()
        else:
            continue

    # fgt_msw_cli.login()
    # print(fgt_msw_cli)

    # fgt_msw_cli.login()

