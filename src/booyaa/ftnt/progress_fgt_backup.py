from booyaa.ftnt.fgt.backup import FgtObj

class FgtBackup:
    fgtobj: FgtObj
    fgtobj_list: list[FgtObj]

    def __init__(self):
        self.fgtobj_list = []
        self.fgt_target_list = []
    

    def setup(self, fgt_target_list):
        self.fgt_target_list = fgt_target_list
        for fgt_target_info in fgt_target_list:
            fgtobj = FgtObj()
            fgtobj.setup(
                **fgt_target_info
            )
            self.fgtobj_list.append(fgtobj)

    def sequential_backup_run(self):


if __name__ == '__main__':
    fgt_target_list = [
        {
            'addr': '172.16.201.201',
            'user': 'admin',
            'password': 'P@ssw0rd',
            'ssh_port': 22,
            'https_port': 443,
            'timeout': 60,
            'export_dir': 'fgt_export',
        }
    ]

    fgtbakup = FgtBackup()
    fgtbakup.setup(fgt_target_list)
