from dataclasses import dataclass, field
from pathlib import Path


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
    export_dir: Path = field(default=Path('./export_fgt'))

    node_info_flg: bool = False
