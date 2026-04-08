class Diagnose:
    def __init__(self, cli):
        self.cli = cli 

    def get(self, sentence, timeout=600.0, cmd_strip=True, output_standard=False, ignore_err_words=True):
        """
        """
        cmd = f'diagnose {sentence}'

        if '|' not in cmd:
            cmd = f'{cmd} | grep .*'

        return self.cli.execute_command(cmd, cmd_strip=cmd_strip, timeout=timeout, ignore_err_words=ignore_err_words)

