from dataclasses import dataclass, field

@dataclass
class FgtInfo:
    hostname: str = ''
    addr: str = ''
    user: str = ''
    password: str = ''
    alias: str = ''
    ssh_port: int = 22
    https_port: int = 443

    serial: str = ''
    version: str = ''
    major: str = ''
    minor: str = ''
    patch: str = ''
    build: str = ''

    model: str = ''
    config: str = ''

    manage_vdom: str = 'root'
    vdom_mode: str = 'no-vdom'

    ha_mode: str = ''
    ha_role: str = ''
    ha_mgmt_status: str = ''
    ha_mgmt_interfaces: list = field(default_factory=list)
    exsist_secondary: str = ''

    secondary_hostname: str = ''
    secondary_serial: str = ''
    secondary_ha_mode: str = ''
    secondary_ha_role: str = ''

    msw_list: list = field(default_factory=list)

    node_info_flg = False

    def set_target(self, fgt_addr, fgt_user, fgt_password, fgt_alias='', fgt_hostname='', fgt_ssh_port=22, fgt_https_port=443, timeout=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        addr = fgt_addr
        user = fgt_user
        password = fgt_password
        alias = fgt_alias
        hostname = fgt_hostname
        ssh_port = fgt_ssh_port
        https_port = fgt_https_port

        let['msg'] = f'CLI Set to {addr}, user: {user}'

        return let
