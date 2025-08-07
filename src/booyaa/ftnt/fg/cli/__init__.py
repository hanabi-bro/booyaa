from pathlib import Path
from configparser import ConfigParser
from paramiko import SSHClient, MissingHostKeyPolicy
from paramiko_expect import SSHClientInteraction
from re import search, findall

from booyaa.ftnt.fg.cli.get import Get
from booyaa.ftnt.fg.cli.show import Show
from booyaa.ftnt.fg.cli.execute import Execute

from booyaa.common.export.save_file import save_config

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
        self.addr = ''
        self.port = ''
        self.user = ''
        self.password = ''
        self.alias = ''

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
        self.ha_mgmt_status = ''      # @todo mgmt statusが有効ならHAは見ない
        self.ha_mgmt_interfaces = []  # @todo さらに念のため見るならmgmt_interfacesが1以上
        self.exsist_secondary = ''

        self.secondary_hostname = ''
        self.secondary_serial = ''
        self.secondary_ha_mode = ''
        self.secondary_ha_role = ''

        self.result_message = ''

        self.display = False

        self.timeout = 60
        self.interact = ''

        self.FG_PROMPT = [
            r'([\r\n]+)?([\w_\-\.]+)(\([\w_\-\.]+\))?\s*#\s*',
            r'\-\-(?i:More)\-\-',
            r'(?i:Command fail\. Return code .*)',
            r'(?i:Unknown action .*)',
        ]
        self.SSH_PROMPT = [
            r'.*(?i:password):\s*',
            r'([\r\n]+)?([\w_\-\.]+)(\([\w_\-\.]+\))?\s*#\s*',
            r'(?i:.*Could not manage member.*)',
            r'(?i: .*please try again.*)'
            r'(?i:.*No route to host.*)',
            r'(?i:.*ssh_exchange_identification: read: Connection reset by peer.*)'
            r'(?i:.*reset by peer.*)'
        ]

        self.node_info_flg = False
        self.secondary_info_flg = False

        # output_standardチェック
        self.output_standard_flg = False

        self.get = Get(self)
        self.show = Show(self)
        self.execute = Execute(self)

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

        self.addr = target
        self.port = port
        self.user = user
        self.password = password

        # エリアス指定
        if alias is not None:
            self.alias = alias

        # バックアップディレクトリ
        self.backup_dir = backup_dir        # self.base_url = f'https://{self.addr}/api/v2/'

        let['msg'] = f'Set to {self.addr}, user: {self.user}'

        return let

    def login(self, addr=None, user=None, password=None, timeout=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        addr = addr or self.addr
        _addr = addr.split(':')
        if len(_addr) == 1:
            addr = _addr[0]
            port = 22
        elif len(_addr) == 2:
            addr = _addr[0]
            port = int(_addr[1])

        user = user or self.user
        password = password or self.password
        timeout = timeout or self.timeout

        try:
            self.session = SSHClient()
            self.session.set_missing_host_key_policy(NoHostKeyCheckPolicy())
            self.session.connect(
                addr,
                port,
                user,
                self.password,
                timeout=timeout
            )
            # SSHのセッションをparamiko_expectに渡す
            self.interact = SSHClientInteraction(self.session, timeout=self.timeout, display=self.display)

            let['msg'] = f'Login successful to {self.addr} as {self.user}'
            let['output'] = self.interact.current_output_clean

        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] Session Timeout to login {self.addr} {format_exc()}'


        # ログイン成功後、output standard設定変更
        if self.output_standard_flg is False:
            self.output_standard()

        # ログイン成功後にPrimaryとSecondaryの情報を取得
        # 毎回実施しないよう取得済みフラグたてておく
        try:
            if not self.node_info_flg:
                let = self.get_node_info()
                self.node_info_flg = True
        except Exception as e:
            let['code'] = 1
            let['msg'] += f'[Error] get_node_info {self.addr} {format_exc()}'

        return let

    def exit(self, timeout=5):
        let = {'code': 0, 'msg': '', 'output': ''}

        self.interact.send('exit')
        index = self.interact.expect(self.FG_PROMPT, timeout=timeout)
        if index == 0:
            let['code'] = 0
            let['msg'] = 'exit'
        else:
            let['code'] = 1
            let['msg'] = f'[Error]Failed exit'

        return let

    def logout(self, timeout=5):
        let = {'code': 0, 'msg': '', 'output': ''}
        for i in range(3):
            try:
                self.interact.send('exit')
                index = self.interact.expect(self.FG_PROMPT, timeout=timeout)
                let['output'] = self.interact.current_output_clean

                if index == -1:
                    let['code'] = 0
                    let['msg'] = f'logout from {self.hostname}'
                    break
            except Exception as e:
                    let['code'] = 0
                    let['msg'] = f'[Error]logout Failed Force session close{format_exc()}'

        self.close()
        return let

    def close(self):
        self.interact.close()
        self.session.close()

    def execute_command(self, cmd, prompt=None, timeout=None, cmd_strip=False):
        """コマンドを実行し、結果を返す"""
        let = {'code': 0, 'msg': '', 'output': ''}

        timeout = timeout or self.timeout
        prompt = prompt or self.FG_PROMPT

        try:
            self.interact.send(cmd)
            # index = self.interact.expect(prompt, timeout=timeout)
            output = ""
            while True:
                index = self.interact.expect(prompt, timeout=timeout)
                output += self.interact.current_output_clean

                if index == 0:
                    break
                elif index == 1:
                    self.interact.send(' ')

            let['output'] = output

            if index <= 1:
                let['code'] = 0
                if cmd_strip:
                    # 入力コマンドを削除
                    if let['output'].startswith(cmd):
                        let['output'] = let['output'][len(cmd):].lstrip()

            else:
                let['code'] = 1
                let['msg'] =  f'Error: Net Expect Return: [{cmd}]\n'

        except Exception as e:
            let['code'] = 1
            let['msg'] = f'Error: execute comand [{cmd}], Exception: {e}'

        return let

    def output_standard(self):
        cmd = 'show system console'
        let = self.execute_command(cmd)
        _standard = search(r'set output standard', let['output'])
        if not _standard:
            let = self.execute_command(cmd)
            if let['code'] != 0:
                return let
            self.output_standard_flg = True
            cmds = [
                'config system console',
                'set output standard',
                'end'
            ]
            for cmd in cmds:
                let = self.execute_command(cmd)
                if let['code'] != 0:
                    return let
        return let

    def get_node_info(self):
        """ノード情報を取得"""
        let = self.get.system_status.get()

        # コマンド実行エラー時は終了
        if let['code'] != 0:
            return let

        # ホスト名の抽出
        self.hostname = self.get.system_status.hostname

        # シリアル番号の抽出
        self.serial = self.get.system_status.serial

        # モデル, バージョン情報の抽出
        self.model = self.get.system_status.model
        self.major = self.get.system_status.major
        self.minor = self.get.system_status.minor
        self.patch = self.get.system_status.patch
        self.build = self.get.system_status.build
        self.version = self.get.system_status.version

        # manage vdom domainの抽出
        self.manage_vdom = self.get.system_status.manage_vdom

        # Virtual domain configuration
        # novdom: no-vdom, vdom: multi-vdom
        self.vdom_mode = self.get.system_status.vdom_mode

        # HAモードとHA roleの抽出
        self.ha_mode = self.get.system_status.ha_mode
        self.ha_role = self.get.system_status.ha_role

        # HAならHAノード情報の抽出
        let = self.get.system_ha_status.get()
        if let['code'] != 0:
            return let
        
        self.secondary_hostname = self.get.system_ha_status.secondary_hostname
        self.secondary_serial = self.get.system_ha_status.secondary_serial

        # @todo ノードのエリアス取得

        # @todo 情報取得失敗時の処理
        return let

    def get_ha_node_info(self):
        """Secondary Nodeのホスト名、シリアル、クラスタIDを取得"""
        let = {'code': 0, 'msg': '', 'output': ''}

        # VDOMモードの場合はglobaに移動
        if self.vdom_mode == 'multi-vdom':
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
        if self.vdom_mode == 'multi-vdom':
            res = self.end_global()
            if res['code'] != 0:
                let['code'] = res['code']
                let['msg'] = f'{res['msg']} [get_ha_node_info]'
                let['output'] += res['output']
                return let

        return let

    def execute_ssh(self, addr, user, password, timeout=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        timeout = timeout or self.timeout
        #  vdomの場合は、globalに移動してSSHする
        if self.vdom_mode == 'multi-vdom':
            res = self.config_global()
            # @todo グローバルモードであることの確認とエラー処理
        
        cmd = f'execute ssh {user}@{addr}'

        self.interact.send(cmd)
        index = self.interact.expect(self.SSH_PROMPT, timeout=timeout)
        let['output'] = self.interact.current_output_clean

        if index == 0:
            # パスワード入力
            self.interact.send(password)
            index = self.interact.expect(self.FG_PROMPT, timeout=timeout)
            #
            # @todo ログインチェック
            #
            if index == 0:
                let['code'] = 0
                let['msg'] = f'ssh login to {addr}'

        if index != 0:
            let['code'] = index
            let['msg'] = f'[Error]Falied {cmd} {self.SSH_PROMPT[index]}'

        return let

    def login_secondary(self, timeout=None, secondary_user=None, secondary_pass=None):
        """セカンダリノードにログイン"""
        let = {'code': 0, 'msg': '', 'output': ''}

        secondary_user = secondary_user or self.user
        secondary_pass = secondary_pass or self.password
        timeout = timeout or self.login_timeout

        #  vdomの場合は、globalに移動してSSHする
        if self.vdom_mode == 'multi-vdom':
            res = self.config_global()
            # @todo グローバルモードであることの確認とエラー処理

        cmd = f'execute ha manage 1 {secondary_user}'
        self.interact.send(cmd)
        index = self.interact.expect(self.SSH_PROMPT, timeout=timeout)

        # Could not manage memberが返ったら、ID0にして再実施
        if index == 2:
            # セカンダリノードが存在しない場合
            cmd = f'execute ha manage 0 {secondary_user}'
            self.interact.send(cmd)
            index = self.interact.expect(self.SSH_PROMPT, timeout=timeout)
            let['output'] = self.interact.current_output_clean

        if index == 0:
            # password prompt
            self.interact.send(secondary_pass)
            self.interact.expect(self.FG_PROMPT, timeout=timeout)

            # @todo sshログイン失敗処理
            let['code'] = 0
            let['msg'] = f'Login to secondary({self.secondary_hostname})'

        else:
            let['code'] = 1
            let['msg'] = f'[Error]Failed login secondary ({self.secondary_hostname})'

        return let

    def logout_secondary(self, timeout=5.0):
        """セカンダリノードからログアウト"""
        let = self.exit()
        # @todo ログアウト確認

        # vdomの場合は、Primary側はglobalモードで実行しているので、グローバルモードを終了する
        if self.vdom_mode == 'multi-vdom':
            let = self.end_global()

        # @todo エラー処理

        return let

    def bastion_login_secondary(self, timeout=None):
        # セッションは一度クローズして、FGに再度ログイン
        if self.interact:
            self.interact.close()
        if self.session:
            self.session.close()

        let = self.login()
        if let['code'] != 0:
            return let

        let = self.login_secondary()
        return let

    def bastion_logout_secondary(self, timeout=None):
        let = self.logout_secondary()
        if let['code'] != 0:
            return let
        let = self.logout()
        return let

    def config_global(self):
        cmd = 'config global'
        let = self.execute_command(cmd)
        if let['code'] != 0:
            let['msg'] = '[Error] Failed config global'
        # #todo グローバルモードであることの確認
        return let

    def end_global(self):
        # @todo グローバルモードであることを確認
        cmd = 'end'
        let = self.execute_command(cmd)
        if let['code'] != 0:
            let['msg'] = '[Error] Failed end global'
        # #todo グローバルモード終了確認
        return let

    def config_vdom(self, vdom_name=None):
        """VDOM設定モードに入る"""
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
        cmd = 'end'
        let = self.execute_command(cmd)
        if let['code'] != 0:
            let['msg'] = '[Error] Failed end vdom'
        # @todo vdomモード囚虜確認

        return let

    def backup(self, full=False, cmd_strip=True, format='text', encode='utf-8', backup_dir=None):
        backup_dir = backup_dir or self.backup_dir
        let = self.show.get(full=full, cmd_strip=cmd_strip)
        if let['code'] != 0:
            return let
        self.config = let['output']
        let = save_config(
            content=self.config,
            hostname=self.hostname,
            alias=self.alias,
            version=self.version,
            export_dir=self.backup_dir,
            format=format,
            encode=encode
        )
        return let

    def backup_secondary(self, full=False, cmd_strip=True, format='text', encode='utf-8'):
        let = self.login_secondary()
        if let['code'] != 0:
            return let
        let = self.show.get(full=full, cmd_strip=cmd_strip)
        self.secondary_config = let['output']
        let = save_config(
            content=self.secondary_config,
            hostname=self.secondary_hostname,
            alias=self.alias,
            version=self.version,
            export_dir=self.backup_dir,
            format=format,
            encode=encode
        )
        if let['code'] != 0:
            return let
        let = self.logout_secondary()
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

    let = cli.execute_ssh(addr='10.255.1.1', user='admin', password='P@ssw0rd')
    print(let)
    let = cli.execute_command('get system status')
    let = cli.exit()

    # let = cli.backup(full=False)  # バックアップ
    # let = cli.backup_secondary()  # セカンダリノードにログイン
    
    # let = cli.config_global()  # グローバルモードに切り替え
    # print(let)

    # let = cli.end_global()  # グローバルモードを終了
    # print(let)

    # let = cli.config_vdom() # VDOM設定モードに入る
    # print(let)

    # let = cli.end_vdom()  # VDOM設定モードを終了
    # print(let)

    let = cli.logout()  # ログアウト
