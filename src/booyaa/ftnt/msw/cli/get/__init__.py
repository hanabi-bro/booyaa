from .system_status import SystemStatus
from .system_interface import SystemInterface

class Get:
    def __init__(self, cli):
        self.cli = cli
        self.system_status = SystemStatus(cli)
        self.system_interface = SystemInterface(cli)

    def get(self, sentence, timeout=60.0, cmd_strip=True):
        """get
        """
        cmd = f'get {sentence}'

        return self.cli.execute_command(cmd, cmd_strip=cmd_strip)

