from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.api import FgtApi
from booyaa.ftnt.fgt.cli import FgtCli
from pathlib import Path

class Fgt:
    def __init__(self, fgt_info: FgtInfo | None = None):
        self.fgt_info = fgt_info or FgtInfo()
        self.api = FgtApi(self.fgt_info)
        self.cli = FgtCli(self.fgt_info)

    def setup(self, addr, user, password, alias='', hostname='', ssh_port=22, https_port=443, timeout=60, export_dir=None, **kwargs):
        let = {'code': 0, 'msg': '', 'output': ''}
        self.fgt_info.addr = addr
        self.fgt_info.user = user
        self.fgt_info.password = password
        self.fgt_info.alias = alias
        self.fgt_info.hostname = hostname
        self.fgt_info.ssh_port = ssh_port
        self.fgt_info.https_port = https_port
        self.timeout = timeout or self.timeout
        self.fgt_info.export_dir = Path(export_dir or self.fgt_info.export_dir)

        let['msg'] = f'Set FGT {self.fgt_info.addr}'

        return let
