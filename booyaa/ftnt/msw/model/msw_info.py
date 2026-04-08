from dataclasses import dataclass, field

@dataclass
class MswInfo:
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

    status: str = ''
    state: str = ''

    node_info_flg = False

