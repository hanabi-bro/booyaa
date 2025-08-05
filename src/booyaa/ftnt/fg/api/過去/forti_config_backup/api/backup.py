from forti_config_backup.api.base import FortiApi
from forti_config_backup.common.export import Export
from pathlib import Path


class Backup(FortiApi):
    def __init__(self):
        super().__init__()
        self.backup_dir = Path('./forti_config_backup')
        export = Export()
        self.save = export.save_file

    def get_backup(self, full=False, scope='global'):
        """"""
        backup_dir = self.backup_dir
        Path.mkdir(backup_dir, exist_ok=True)

        backup_uri = f'{self.base_url}/monitor/system/config/backup?scope={scope}'
        let = {'code': 0, 'msg': '', 'output': ''}
        # バックアップ取得
        try:
            # バックアップ取得
            # cookieの中身を表示
            # バックアップ画面に遷移
            self.session.get(f'{self.base_url}/ng/system/config/backup')

            if self.version >= '7.6.0':
                json_data = {
                    'destination': 'file',
                    'file_format': 'fos',
                    'scope': scope
                }
                backup_uri = f'{self.base_url}/monitor/system/config/backup'
                res = self.session.post(backup_uri, json=json_data)
            else:
                backup_uri = f'{self.base_url}/monitor/system/config/backup?scope={scope}'
                res = self.session.get(backup_uri)

            if res.status_code == 200:
                let = self.save(
                    backup_dir = self.backup_dir,
                    config_text = res.content.decode('utf-8'),
                    fg_name = self.hostname,
                    version=self.version,
                    alias = self.fg_alias,
                )

            else:
                let['code'] = 1
                let['msg'] = f'[Error] Failed api backup {self.fg_addr}'
                let['output'] = res.content.decode('utf-8')

        except Exception as e:
                let['code'] = 1
                let['msg']= f'[Error] Backup save failed: {e}'

        return let


if __name__ == '__main__':
    ba = Backup()
    ba.set_target(
        '172.16.201.202',
        'admin',
        'P@ssw0rd',
        'LABFGT01'
    )
    let = ba.login() # ログイン
    print(let)
    let = ba.get_backup() # バックアップ取得
    print(let)
    let = ba.logout() # ログアウト
    print(let)
