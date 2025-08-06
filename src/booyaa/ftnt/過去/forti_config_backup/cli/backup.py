from forti_config_backup.cli.base import FortiCli
from forti_config_backup.common.export import Export
from pathlib import Path

class CliBackup(FortiCli):
    def __init__(self):
        super().__init__()
        self.backup_dir = Path('./forti_config_backup')
        export = Export()
        self.save = export.save_file

    def get_backup_batch(self, node='all', full=False):
        """
        node: all: 全て, primary: プライマリのみ, secondary: セカンダリのみ
        """

    def get_backup(self, full=False, secondary=False):
        cmd = 'show full-configuration' if full else 'show'

        fg_hostname = self.hostname
        if secondary:
            fg_hostname = self.secondary_hostname
            let_secondary = self.login_secondary()
            if let_secondary['code'] != 0:
                let_secondary['msg'] += ' [get_backup]'
                return let_secondary

        let = self.execute_command(cmd)

        # 入力コマンドを削除
        if let['code'] == 0 and let['output'].startswith(cmd):
            output = let['output'][len(cmd):].lstrip()

        save_res = self.save(
            backup_dir=self.backup_dir,
            config_text=output,
            fg_name=fg_hostname,
            version=self.version,
            alias=self.fg_alias,)

        if save_res['code'] != 0:
            let['msg'] += ' [get_backup]'

        if secondary:
            let_secondary = self.logout_secondary()
            if let_secondary['code'] != 0:
                let_secondary['msg'] += ' [get_backup]'
                return let_secondary

        return let


if __name__ == '__main__':
    cli = CliBackup()
    cli.display = True  # デバッグ用に出力を有効化
    cli.set_target(
        user='admin',
        password='P@ssw0rd',
        target='172.16.201.6',
        alias='LABFGT01',
    )
    let = cli.login()  # ログイン
    print(let)

    let = cli.get_backup(full=False, secondary=True)  # バックアップ取得
    print(let)

    let = cli.logout()  # ログアウト
    print(let)
