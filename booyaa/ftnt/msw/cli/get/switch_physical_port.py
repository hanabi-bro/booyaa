from re import search

class SwitchPhysicalPort:
    def __init__(self, cli):
        self.cli = cli

    def get(self):
        cmd = 'get switch physical-port | grep .*'
        res = self.cli.execute_command(cmd)

        if res['code'] != 0:
            return res

        return res
