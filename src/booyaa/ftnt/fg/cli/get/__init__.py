from .system_status import SystemStatus
from .system_ha_status import SystemHaStatus

class Get:
    def __init__(self, cli):
        self.cli = cli
        self.system_status = SystemStatus(cli)
        self.system_ha_status = SystemHaStatus(cli)

    def get(self, sentence='', timeout=60.0, cmd_strip=True):
        """get
        """
        cmd = f'get {sentence}'

        return self.cli.execute_command(cmd, cmd_strip=cmd_strip)

