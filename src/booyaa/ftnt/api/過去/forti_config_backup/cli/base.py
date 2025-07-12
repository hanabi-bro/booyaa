from pathlib import Path
from configparser import ConfigParser
from paramiko import SSHClient, MissingHostKeyPolicy
from paramiko_expect import SSHClientInteraction
from re import search, findall

# from sys import exc_info
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

        self.manage_vdom = 'root'
        self.vdom_mode = ''

        self.ha_mode = ''
        self.ha_role = ''
        self.exsist_secondary = ''

        self.secondary_hostname = ''
        self.secondary_serial = ''
        self.secondary_ha_mode = ''
        self.secondary_ha_role = ''

        self.result_message = ''
        self.error = None

        self.display = False

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

    def set_target(self, target, user, password, alias=None, port=22):
        """ターゲットをセット
        Args:
            traget:
            user:
            password:
            alias:
            port:
        """
        let = {'code': 0, 'msg': '', 'output': ''}

        self.fg_addr = target
        self.fg_port = port
        self.fg_user = user
        self.fg_pass = password

        # エリアス指定
        if alias is not None:
            self.fg_alias = alias

        # バックアップディレクトリ
        self.backup_directory = r'./fg_config'        # self.base_url = f'https://{self.fg_addr}/api/v2/'

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

            # ログイン成功後にPrimaryとSecondaryの情報を取得
            # 毎回実施しないよう取得済みならスキップ
        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] Session Timeout to login {self.fg_addr}'
            self.error = format_exc()
            print(e)

        try:
            if not self.primary_info_flg:
                let = self.get_node_info()
                self.primary_info_flg = True
        except Exception as e:
            let['code'] = 1
            let['msg'] += f' get_node_info {self.fg_addr}'
            self.error = format_exc()
            print(e)


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

    def execute_command(self, cmd, prompt=None, timeout=None):
        """コマンドを実行し、結果を返す"""
        let = {'code': 0, 'msg': '', 'output': ''}

        timeout = timeout or self.timeout
        prompt = prompt or self.PROMPT

        try:
            self.interact.send(cmd)
            index = self.interact.expect(prompt, timeout=timeout)
            let['output'] = self.interact.current_output_clean

            if index == 0 or index == 1:
                let['code'] = 0
            else:
                let['code'] = 1
                let['msg'] =  f'Error: Net Expect Return: {cmd}\n'

        except Exception as e:
            let['code'] = 1
            let['msg'] = f'Error: execute comand [{self.cmd}], Exception: {e}'

        return let

    def get_node_info(self):
        """ノード情報を取得"""
        let = {'code': 0, 'msg': '', 'output': ''}

        cmd = 'get system status'
        res = self.execute_command(cmd)

        # コマンド実行エラー時は終了
        if res['code'] != 0:
            let['code'] = res['code']
            let['msg'] = f'{res['msg']}[get_node_info]'
            let['output'] = res['output']
            return let

        let = res

        # バージョン情報の抽出
        _versions = search(r'Version: *\S+ *v(\d+).(\d+).(\d+),build(\d+)', res['output'])
        if _versions:
            self.major, self.minor, self.patch, self.build = _versions.group(1,2,3,4)
            self.version = f'{self.major}.{self.minor}.{self.patch}'

        # シリアル番号の抽出
        _serial = search(r'Serial-Number: *(\S+)', res['output'])
        if _serial:
            self.serial = _serial.group(1)

        # ホスト名の抽出
        _hostname = search(r'Hostname: *(\S+)', res['output'])
        if _hostname:
            self.hostname = _hostname.group(1)

        # manage vdom domainの抽出
        _manage_vdom = search(r'Current virtual domain: *(\S+)', res['output'])
        if _manage_vdom:
            self.manage_vdom = _manage_vdom.group(1)

        # Virtual domain configuration
        # novdom: disable, vdom: multiple
        _vdom_mode = search(r'Virtual domain configuration: *(\S+)', res['output'])
        if _vdom_mode:
            # vdomモードの抽出
            if _vdom_mode.group(1).lower() == 'disable':
                self.vdom_mode = 'novdom'
            elif _vdom_mode.group(1).lower() == 'multiple':
                self.vdom_mode = 'multiple'

        # HAモードとHA roleの抽出
        _ha_mode = search(r'Current HA mode: *(\S+)(?:, *(\S+))', res['output'])

        if _ha_mode:
            if _ha_mode.group(1) == 'a-a':
                self.ha_mode = 'active-active'
            elif _ha_mode.group(1) == 'a-p':
                self.ha_mode = 'active-passive'
            else:
                self.ha_mode = 'standalone'

            self.ha_role = _ha_mode.group(2) if _ha_mode.lastindex >= 2 else None

            res = self.get_ha_node_info()
            if res['code'] != 0:
                return res
            else:
                let['code'] = 0
                let['msg'] = 'get node info {selfe.fg_addr}'
                let['output'] += res['output']

        # @todo ノードのエリアス取得

        # @todo 情報取得失敗時の処理
        return let

    def get_ha_node_info(self):
        """Secondary Nodeのホスト名、シリアル、クラスタIDを取得"""
        let = {'code': 0, 'msg': '', 'output': ''}

        # VDOMモードの場合はglobaに移動
        if self.vdom_mode == 'multiple':
            let = self.config_global()
            if let['code'] != 0:
                let['msg'] = f'{let['msg']} [get_ha_node_info]'
                return let

        cmd = 'get system ha status'
        res = self.execute_command(cmd)

        # コマンド実行エラー時は終了
        if res['code'] != 0:
            let['code'] = res['code']
            let['msg'] = f'{res['msg']} [get_ha_node_info]'
            let['output'] = res['output']
            return let

        _ha_cluster_match = findall(r'(\S+) *, *(\w+), *HA cluster index *= *(\d+)', res['output'])
        self.exsist_secondary = len(_ha_cluster_match) == 2 or False
        if _ha_cluster_match[0][0] == self.hostname:
            _primary_cluster_info = _ha_cluster_match[0]
            if self.exsist_secondary:
                _secondary_cluster_info = _ha_cluster_match[1]
        else:
            _primary_cluster_info = _ha_cluster_match[1]
            if self.exsist_secondary:
                _secondary_cluster_info = _ha_cluster_match[0]

        self.cluster_index = _primary_cluster_info[2]
        if self.exsist_secondary:
            self.secondary_hostname = _secondary_cluster_info[0]
            self.secondary_serial = _secondary_cluster_info[1]
            self.secondary_cluster_index = _secondary_cluster_info[2]

        let = res

        # globalモードを終了
        if self.vdom_mode == 'multiple':
            res = self.end_global()
            if res['code'] != 0:
                let['code'] = res['code']
                let['msg'] = f'{res['msg']} [get_ha_node_info]'
                let['output'] += res['output']
                return let

        return let

    def login_secondary(self, timeout=None, secondary_user=None, secondary_pass=None):
        """セカンダリノードにログイン"""
        let = {'code': 0, 'msg': '', 'output': ''}

        secondary_user = secondary_user or self.fg_user
        secondary_pass = secondary_pass or self.fg_pass
        timeout = timeout or self.login_timeout

        #  vdomの場合は、globalに移動してSSHする
        if self.vdom_mode == 'multiple':
            res = self.config_global()
            # @todo グローバルモードであることの確認とエラー処理

        cmd = f'execute ha manage 1 {secondary_user}'
        self.interact.send(cmd)
        index = self.interact.expect(self.SSH_PROMPT, timeout=timeout)

        # Could not manage memberが返ったら、ID0にして再実施
        if index == 1:
            # セカンダリノードが存在しない場合
            cmd = f'execute ha manage 0 {secondary_user}'
            self.interact.send(cmd)
            index = self.interact.expect(self.SSH_PROMPT, timeout=timeout)
            let['output'] = self.interact.current_output_clean

        if index == 0:
            self.interact.send(secondary_pass)
            self.interact.expect(self.PROMPT, timeout=timeout)
            let['code'] = 0
            let['msg'] = f'Login to secondary({self.secondary_hostname})'

        else:
            let['code'] = 1
            let['msg'] = f'[Error]Failed login secondary ({self.secondary_hostname})'

        return let

    def logout_secondary(self, timeout=None):
        """セカンダリノードからログアウト"""
        let = {'code': 0, 'msg': '', 'output': ''}
        timeout = timeout or self.login_timeout

        # @todoセカンダリであることを確認

        cmd = 'exit'
        res = self.execute_command(cmd, timeout=timeout)

        # @todo ログアウト確認

        # vdomの場合は、Primary側はglobalモードで実行しているので、グローバルモードを終了する
        if self.vdom_mode == 'multiple':
            res = self.end_global()

        # @todo エラー処理

        let = res

        return let

    def config_global(self):
        let = {'code': 0, 'msg': '', 'output': ''}
        cmd = 'config global'
        let = self.execute_command(cmd)
        if let['code'] != 0:
            let['msg'] = '[Error] Failed config global'
        # #todo グローバルモードであることの確認
        return let

    def end_global(self):
        # @todo グローバルモードであることを確認
        let = {'code': 0, 'msg': '', 'output': ''}
        cmd = 'end'
        let = self.execute_command(cmd)
        if let['code'] != 0:
            let['msg'] = '[Error] Failed end global'
        # #todo グローバルモード終了確認
        return let

    def config_vdom(self, vdom_name=None):
        """VDOM設定モードに入る"""
        let = {'code': 0, 'msg': '', 'output': ''}
        vdom_name = vdom_name or self.manage_vdom
        cmd = f'config vdom {vdom_name}'
        let = self.execute_command(cmd)
        if let['code'] != 0:
            let['msg'] = f'[Error] Failed config vdom {vdom_name}'
        # @todo コンフィグモード確認

        return let

    def end_vdom(self):
        """VDOM設定モードを終了"""
        # @todo vdomモードにいることを確認
        let = {'code': 0, 'msg': '', 'output': ''}
        cmd = 'end'
        let = self.execute_command(cmd)
        if let['code'] != 0:
            let['msg'] = '[Error] Failed end vdom'
        # @todo vdomモード囚虜確認

        return let

if __name__ == '__main__':
    cli = FortiCli()
    cli.display = True  # デバッグ用に出力を有効化
    cli.set_target(
        user='admin',
        password='P@ssw0rd',
        target='172.16.201.6',
        alias='LABFG0LABFG01',
    )
    let = cli.login()  # ログイン
    print(let)

    let = cli.login_secondary()  # セカンダリノードにログイン

    if let['code'] == 0:
        let = cli.logout_secondary()  # セカンダリノードからログアウト
        print(let)

    let = cli.config_global()  # グローバルモードに切り替え
    print(let)

    let = cli.end_global()  # グローバルモードを終了
    print(let)

    let = cli.config_vdom() # VDOM設定モードに入る
    print(let)

    let = cli.end_vdom()  # VDOM設定モードを終了
    print(let)

    let = cli.logout()  # ログアウト
    print(let)
