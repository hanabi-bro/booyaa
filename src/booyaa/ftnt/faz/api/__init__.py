from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.api import FgtApi
from booyaa.ftnt.fgt.cli import FgtCli


class Fgt:
    def __init__(self):
        self.fgt_info = FgtInfo()
        self.api = FgtApi(self.fgt_info)
        self.cli = FgtCli(self.fgt_info)

    def setup(self, addr, user, password, alias='', hostname='', ssh_port=22, https_port=443, **kwargs):
        let = {'code': 0, 'msg': '', 'output': ''}
        self.fgt_info.addr = addr
        self.fgt_info.user = user
        self.fgt_info.password = password
        self.fgt_info.alias = alias
        self.fgt_info.hostname = hostname
        self.fgt_info.ssh_port = ssh_port
        self.fgt_info.https_port = https_port

        let['msg'] = f'Set FGT {self.fgt_info.addr}'

        return let
