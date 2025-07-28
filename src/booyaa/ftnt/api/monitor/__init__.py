from .system_csf import SystemCsf
from .system_config_backup import SystemConfigBackup
from .web_ui_state import WebUiState
from .system_ha_statistics import SystemHaStatistics

class Monitor:
    def __init__(self, api):
        self.system_csf = SystemCsf(api)
        self.system_config_backup = SystemConfigBackup(api)
        self.web_ui_state = WebUiState(api)
        self.system_ha_statistics = SystemHaStatistics(api)
