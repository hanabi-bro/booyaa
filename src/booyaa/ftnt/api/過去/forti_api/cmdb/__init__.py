from .system_ha import SystemHa

class Cmdb:
    def __init__(self, api):
        self.system_ha = SystemHa(api)
