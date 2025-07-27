from pathlib import Path
from configparser import ConfigParser
from paramiko import SSHClient, MissingHostKeyPolicy
from paramiko_expect import SSHClientInteraction
from re import search, findall

from traceback import format_exc


from rich.console import Console
console = Console()

class NoHostKeyCheckPolicy(MissingHostKeyPolicy):
    """ホストキー無視ポリシー"""
    def missing_host_key(self, client, hostname, key):
        # print(f"{hostname} key: {key.get_name()} {key.get_base64()}")
        return

class FortiCli():
    def __init__(self):
        self.fg_addr = ''
        self.fg_port = ''
        self.fg_user = ''
        self.fg_pass = ''
        self.fg_alias = ''
        self.fg_hostname = ''

        self.session = ''
        self.root_dir = Path(__file__).parent.resolve()
        config_ini = 'config.ini'
        self.config_ini_path = Path(Path(__file__).parent.parent.resolve(), config_ini)
        self.read_config_ini(config_ini)

        # node info
        self.hostname = ''
        self.serial = ''
        self.version = ''
        self.major = ''
        self.minor = ''
        self.patch = ''
        self.build = ''

        self.model = ''

        self.config = ''

        self.manage_vdom = 'root'
        self.vdom_mode = ''

        self.ha_mode = ''
        self.ha_role = ''
        self.ha_mgmt_status = ''      # mgmt statusが有効ならHAは見ない
        self.ha_mgmt_interfaces = []  # さらに念のため見るならmgmt_interfacesが1以上
        self.exsist_secondary = ''

        self.secondary_hostname = ''
        self.secondary_serial = ''
        self.secondary_ha_mode = ''
        self.secondary_ha_role = ''

        self.result_message = ''
        self.error = None

        self.display = False

        self.timeout = 60.0

        self.interact = ''
        self.PROMPT = [
            r'[\r\n][\w_\-\.\(\) ]+#\s*',
            r'[\w_\-\.\(\) ]+#\s*',
            r'(?i:Command fail\. Return code .*)',
            r'(?i:Unknown action .*)',
        ]
        self.SSH_PROMPT = [
            r'.*(?i:password):\s*',
            r'(?i:.*Could not manage member.*)',
            r'[\w_\-\.\(\) ]+#\s*'
        ]

        self.primary_info_flg = False
        self.secondary_info_flg = False

    def read_config_ini(self, config_ini=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        cp = ConfigParser()

        if config_ini:
            self.config_ini_path = Path(config_ini)

        # config.iniがなければデフォルト値
        if self.config_ini_path.is_file():
            cp.read(self.config_ini_path, encoding='utf-8')
        else:
            cp.add_section('cli')
            cp.set('cli', 'login_timeout', '10.0')
            cp.set('cli', 'read_timeout', '600.0')

            with open(self.config_ini_path, 'w', encoding='utf-8') as cf:
                cp.write(cf)

        self.login_timeout = cp.getfloat('cli', 'login_timeout', fallback=10.0)
        self.timeout = cp.getfloat('default', 'read_timeout', fallback=600.0)
        let['msg'] = f'read config.ini login_timeout: {self.login_timeout}, timeout: {self.timeout}'
        return let

    def set_target(self, target, user, password, alias=None, timeout=30.0, backup_dir=r'fg_config'):
        """ターゲットをセット
        Args:
            traget:
            user:
            password:
            alias:
            port:
        """
        let = {'code': 0, 'msg': '', 'output': ''}

        # ポート指定がある場合
        if ':' in target:
            _, port = target.split(':')
            port = int(port)
        else:
            port = 22

        self.fg_addr = target
        self.fg_port = port
        self.fg_user = user
        self.fg_pass = password

        # エリアス指定
        if alias is not None:
            self.fg_alias = alias

        # バックアップディレクトリ
        self.backup_directory = backup_dir        # self.base_url = f'https://{self.fg_addr}/api/v2/'

        let['msg'] = f'Set to {self.fg_addr}, user: {self.fg_user}'

        return let

    def login(self):
        let = {'code': 0, 'msg': '', 'output': ''}

        try:
            self.session = SSHClient()
            self.session.set_missing_host_key_policy(NoHostKeyCheckPolicy())
            self.session.connect(self.fg_addr, self.fg_port, self.fg_user, self.fg_pass, timeout=self.login_timeout)
            # SSHのセッションをparamiko_expectに渡す
            self.interact = SSHClientInteraction(self.session, timeout=self.timeout, display=self.display)

            let['msg'] = f'Login successful to {self.fg_addr} as {self.fg_user}'
            let['output'] = self.interact.current_output_clean

        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] Session Timeout to login {self.fg_addr}'
            self.error = format_exc()
            print(e)


        # ログイン成功後にPrimaryとSecondaryの情報を取得
        # 毎回実施しないよう取得済みフラグたてておく
        try:
            if not self.primary_info_flg:
                let = self.get_node_info()
                self.primary_info_flg = True
        except Exception as e:
            let['code'] = 1
            let['msg'] += f' get_node_info {self.fg_addr}'
            self.error = format_exc()

        return let

    def logout(self):
        """ログアウト処理"""
        let = {'code': 0, 'msg': '', 'output': ''}

        if self.session:
            try:
                self.interact.send('exit')
                self.interact.expect()
                let['msg'] = f'logout from {self.fg_addr}'

            except Exception as e:
                let['code'] = 1
                let['msg'] = f'[Error] logout fail {self.fg_addr}, Force session closed'

            finally:
                self.interact.close()
                self.session.close
        else:
            let['code'] = 1
            let['msg'] = f'[Error] No active session {self.fg_addr}, Force session closed'

        return let

if __name__ == '__main__':
    cli = FortiCli()
    cli.display = True  # デバッグ用に出力を有効化
    cli.set_target(
        user='admin',
        password='P@ssw0rd',
        target='172.16.201.201',
        alias='LABFG01',
    )
    let = cli.login()  # ログイン
    print(let)

    let = cli.logout()  # ログアウト
    print(let)

