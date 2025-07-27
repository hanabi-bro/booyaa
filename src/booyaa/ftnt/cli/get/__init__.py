from .system_status import SystemStatus
from .system_ha_status import SystemHaStatus

class Get:
    def __init__(self, api):
        self.system_status = SystemStatus(api)
        self.system_ha_status = SystemHaStatus(api)
