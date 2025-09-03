from rich.live import Live
from rich.table import Table

from booyaa.ftnt.msw import Msw
from booyaa.ftnt.fgt import Fgt

from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.msw.model.msw_info import MswInfo
from booyaa.ftnt.msw.model.progress import Progress


from concurrent.futures import ThreadPoolExecutor
from booyaa.common.fire_and_forget import fire_and_forget


from pathlib import Path
from time import sleep


from signal import signal, SIGINT
from traceback import format_exc


class MswBackup:
    def __init__(self):
        self.fgt = Fgt()
        self.fgt_info = FgtInfo()

        self.msw_user = ''
        self.msw_password = ''
        self.backup_dir = 'fg_config'
        self.timeout = 60

        self.msw_obj_list = []

    def setup(self,
            fgt_addr, fgt_user, fgt_password, alias='', fgt_hostname='', fgt_ssh_port=22, fgt_https_port=443,
            msw_user='', msw_password='',
            backup_dir='', timeout=60,
            **kwargs):

        self.fgt.setup(fgt_addr, fgt_user, fgt_password, alias, fgt_hostname, fgt_ssh_port, fgt_https_port)

        self.msw_user = msw_user
        self.msw_password = msw_password
        self.backup_dir = backup_dir or self.backup_dir
        self.timeout = timeout or self.timeout

        let = self.fgt.api.login(addr=fgt_addr, user=fgt_user, password=fgt_password)
        self.fgt_info = self.fgt.api.fgt_info

        return let

    def gen_msw_obj_list(self):
        self.msw_obj_list = []
        for l in msw_backup.fgt_info.msw_list:
            msw_info = MswInfo()
            msw_progress = Progress()
            msw_info.addr = l['addr']
            msw_info.user = self.msw_user
            msw_info.password = self.msw_password
            msw_info.hostname = l['hostname']
            msw_info.serial = l['serial']
            msw_info.status = l['status']
            msw_info.state = l['state']
            msw_info.model = l['model']
            msw_info.version = l['version']
            msw_info.build = l['build']
            msw_obj = MswObj(fgt_info=self.fgt_info, msw_info=msw_info, msw_progress=msw_progress)
            msw_obj.backup_dir = self.backup_dir
            self.msw_obj_list.append(msw_obj)

    def multi_backup_run(self):




class MswObj(Msw):
    def __init__(self, fgt_info: FgtInfo, msw_info: MswInfo, msw_progress: Progress):
        super().__init__(fgt_info, msw_info)
        self.progress = msw_progress

if __name__ == '__main__':
    target_info = {
        'fgt_addr': '172.16.201.201',
        'fgt_user': 'admin',
        'fgt_password': 'P@ssw0rd',
        'alias': '',
        'backup_dir': 'fgt_backup',
        'msw_user': 'admin',
        'msw_password': 'P@ssw0rd',
    }

    msw_backup = MswBackup()
    let = msw_backup.setup(**target_info)
    let = msw_backup.gen_msw_obj_list()

    for msw_obj in msw_backup.msw_obj_list:
        msw_obj.cli.display=True

        # let = msw_obj.cli.login_fgt()
        # print(let)

        # let = msw_obj.cli.login_msw(addr='10.255.1.1', user='admin', password='P@ssw0rd')
        let = msw_obj.cli.login_msw()

        let = msw_obj.cli.backup()
        
        let = msw_obj.cli.logout()
        # print(let)

        # msw_obj.cli.get.switch_physical_port.get()
        # msw_obj.cli.logout_msw()
        # msw_obj.cli.logout_fgt()


