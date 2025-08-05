from .system_csf import SystemCsf
from .system_config_backup import SystemConfigBackup


class Monitor:
    def __init__(self, api):
        self.system_csf = SystemCsf(api)
        self.system_config_backup = SystemConfigBackup(api)
