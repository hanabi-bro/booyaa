class Show:
    def __init__(self, cli):
        self.cli = cli 

    def get(self, sentence='', full=False, timeout=120.0, cmd_strip=True):
        """show
        コンフィグ取得用, showコマンドだけ体系が違うので例外的にここで取得する。
        任意コマンド実行可能（未実装のコマンドのsentenceで実行可能）
        """
        if sentence == '':
            cmd = 'show full-configuration' if full else 'show'
        else:
            cmd = f'show {sentence}'

        return self.cli.execute_command(cmd, cmd_strip=cmd_strip)

