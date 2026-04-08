from .switch_controller_get_conn_status import SwitchControllerGetConnStatus
class Execute:
    def __init__(self, cli):
        self.cli = cli 
        self.switch_controller_get_conn_status = SwitchControllerGetConnStatus(cli)

    def get(self, sentence='', timeout=60.0, cmd_strip=True):
        """execute
        """
        cmd = f'execute {sentence}'

        return self.cli.execute_command(cmd, cmd_strip=cmd_strip)

