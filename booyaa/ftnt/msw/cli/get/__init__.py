from .system_status import SystemStatus
from .system_interface import SystemInterface
from .switch_physical_port import SwitchPhysicalPort

class Get:
    def __init__(self, cli):
        self.cli = cli
        self.system_status = SystemStatus(cli)
        self.system_interface = SystemInterface(cli)
        self.switch_physical_port = SwitchPhysicalPort(cli)

    def get(self, sentence, timeout=60.0, cmd_strip=True):
        """get
        """
        cmd = f'get {sentence} | grep .*'

        return self.cli.execute_command(cmd, cmd_strip=cmd_strip)

