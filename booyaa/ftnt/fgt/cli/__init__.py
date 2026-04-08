from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.cli.get import Get
from booyaa.ftnt.fgt.cli.show import Show
from booyaa.ftnt.fgt.cli.execute import Execute
from booyaa.ftnt.fgt.cli.diagnose import Diagnose
from booyaa.ftnt.fgt.cli.get_node_info import get_node_info
from booyaa.common.export.save_file import save_config, save_debug_report

from pathlib import Path

from paramiko import SSHClient, MissingHostKeyPolicy
from paramiko_expect import SSHClientInteraction
from re import search

from traceback import format_exc

class NoHostKeyCheckPolicy(MissingHostKeyPolicy):
    """ホストキー無視ポリシー"""
    def missing_host_key(self, client, hostname, key):
        # print(f"{hostname} key: {key.get_name()} {key.get_base64()}")
        return

class FgtCli:
    session: SSHClient | None
    interact: SSHClientInteraction | None

    def __init__(self, fgt_info: FgtInfo):
        self.fgt_info = fgt_info
        self.timeout = 30
        self.display = False

        self.FGT_PROMPT = [
            r'([\r\n]+)?([\w_\-\.]+)\s*(\([\w_\-\.]+\))?\s*#\s*',
        ]

        self.ERROR_PROMPT = [
            r'([\r\n]+)?.*(?i:Command fail)\s*',
            r'([\r\n]+)?.*(?i:Return code)\s*',
            r'([\r\n]+)?.*(?i:Unknown action)\s*',
            r'([\r\n]+)?.*(?i:Could not manage member).*',
            r'([\r\n]+)?.*(?i:please try again).*',
            r'([\r\n]+)?.*(?i:Connection closed).*',
            r'([\r\n]+)?.*(?i:No route to host).*',
            r'([\r\n]+)?.*(?i:reset by peer).*',
        ]

        self.SSH_PROMPT = [
            r'.*(?i:password):\s*',
            r'([\r\n]+)?([\w_\-\.]+)\s*(\([\w_\-\.]+\))?\s*#\s*',
        ]

        self.session = None
        self.interact = None

        self.get = Get(self)
        self.show = Show(self)
        self.execute = Execute(self)
        self.diagnose = Diagnose(self)

        self.get_node_info = get_node_info

    def set_target(self, fgt_addr, fgt_user, fgt_password, fgt_alias='', fgt_hostname='', fgt_ssh_port=22, fgt_https_port=443, timeout=None, export_dir=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        self.fgt_info.addr = fgt_addr
        self.fgt_info.user = fgt_user
        self.fgt_info.password = fgt_password
        self.fgt_info.alias = fgt_alias
        self.fgt_info.hostname = fgt_hostname
        self.fgt_info.ssh_port = fgt_ssh_port
        self.fgt_info.https_port = fgt_https_port
        self.timeout = timeout or self.timeout
        self.fgt_info.export_dir = Path(export_dir or self.fgt_info.export_dir)

        let['msg'] = f'CLI Set to {self.fgt_info.addr}, user: {self.fgt_info.user}'

        return let

    def login(self, addr=None, user=None, ssh_port=None, password=None, timeout=None, node_info=True):
        let = {'code': 0, 'msg': '', 'output': ''}

        addr = addr or self.fgt_info.addr
        user = user or self.fgt_info.user
        ssh_port = ssh_port or self.fgt_info.ssh_port
        password = password or self.fgt_info.password
        timeout = timeout or self.timeout

        try:
            self.session = SSHClient()
            self.session.set_missing_host_key_policy(NoHostKeyCheckPolicy())
            self.session.connect(
                addr,
                ssh_port,
                user,
                self.fgt_info.password,
                timeout=timeout
            )
            # SSHのセッションをparamiko_expectに渡す
            self.interact = SSHClientInteraction(self.session, timeout=self.timeout, display=self.display)

            let['output'] = self.interact.current_output_clean
            _output = self.interact.current_output

        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] Session Timeout to login {self.fgt_info.addr} {format_exc()}'
            return let

        # ログイン成功後、output standard設定変更
        # '| grep .*'で回避可能そうなので一旦無効化しておいて様子見
        # if self.output_standard_flg is False:
        #     self.output_standard()

        # ログイン成功ならホスト名などnode infoを取得
        if node_info and self.fgt_info.node_info_flg is False:
            let = self.get_node_info(self)
            if let['code'] == 0:
                self.fgt_info.node_info_flg = True

        return let

    def exit(self, timeout=5):
        let = {'code': 0, 'msg': '', 'output': ''}

        self.interact.send('exit')
        index = self.interact.expect(self.FGT_PROMPT, timeout=timeout)
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
                index = self.interact.expect(self.FGT_PROMPT, timeout=timeout)
                let['output'] = self.interact.current_output_clean

                if index == -1:
                    let['code'] = 0
                    let['msg'] = f'logout from {self.fgt_info.hostname}'
                    break
            except Exception as e:
                    let['code'] = 0
                    let['msg'] = f'[Error]logout Failed Force session close{format_exc()}'

        self.close()
        return let

    def close(self):
        if self.interact:
            self.interact.close()
        if self.session:
            self.session.close()

    def execute_command(self, cmd, prompt=None, error_words=None, timeout=None, cmd_strip=False, ignore_err_words=False):
        """コマンドを実行し、結果を返す"""
        let = {'code': 0, 'msg': '', 'output': ''}

        timeout = timeout or self.timeout
        prompt = prompt or self.FGT_PROMPT
        error_words = error_words or self.ERROR_PROMPT

        try:
            self.interact.send(cmd)
            index = self.interact.expect(prompt, timeout=timeout)
            let['output'] = self.interact.current_output_clean

            # エラーワードが含まれていないかチェック
            if ignore_err_words is False:
                for err_word in error_words:
                    match = search(err_word, let['output'])
                    if match:
                        let['code'] = 1
                        let['msg'] = f'[Error] {cmd} is {err_word} in {let['output']}'
                        break

            if let['code'] == 0 and cmd_strip:
                # 入力コマンドを削除
                if let['output'].startswith(cmd):
                    let['output'] = let['output'][len(cmd):].lstrip()

        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] execute comand [{cmd}], Exception: {e}'

        return let

    def execute_ssh(self, addr, user, password, port=22, timeout=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        timeout = timeout or self.timeout
        #  vdomの場合は、globalに移動してSSHする
        if self.fgt_info.vdom_mode == 'multi-vdom':
            let = self.config_global()
            # @todo グローバルモードであることの確認とエラー処理
        
        cmd = f'execute ssh {user}@{addr} {port}'

        self.interact.send(cmd)
        index = self.interact.expect(self.SSH_PROMPT, timeout=timeout)
        let['output'] = self.interact.current_output_clean

        if index != 0:
            let['code'] = index
            let['msg'] = f'[Error]Falied {cmd} {let['output']}'
            return let

        # パスワード入力
        self.interact.send(password)
        index = self.interact.expect(self.FGT_PROMPT, timeout=timeout)
        _output = self.interact.current_output
        let['output'] = self.interact.current_output_clean

        let['msg'] = f'ssh login to {addr}'

        # エラーの再チェック
        for check_word in self.SSH_PROMPT[2:]:
            match = search(check_word, _output)
            if match:
                let['code'] = 1
                let['msg'] = f'[Error] Login failed {_output}'

        # 念のためプロンプトが自身（FG）のホスト名じゃない事も確認しておく
        my_prompt = rf'([\r\n]+)?({self.fgt_info.hostname})(\([\w_\-\.]+\))?\s*#\s*'
        match = search(my_prompt, _output)

        if match:
                let['code'] = 1
                let['msg'] = f'[Error] Login failed. Prompt is {self.fgt_info.hostname}: {_output}'

        return let

    def ssh_error_check(self, output):
        let = {'code': 0, 'msg': '', 'output': output}
        for err_word in self.ERROR_PROMPT:
            match = search(err_word, output)

            if match:
                let['msg'] = f'[Error] Secondary Login Failed {match.group()}'
                break
        return let

    def prompt_check(self, hostname):
        let = {'code': 0, 'msg': '', 'output': ''}
        # プロンプト確認のためEnter
        self.interact.send('')
        index = self.interact.expect(self.FGT_PROMPT, timeout=self.timeout)
        let['output'] = self.interact.current_output

        # プロンプトからホスト名を取得
        re_hostname_prompt = r'([\r\n]+)?([\w_\-\.]+)\s*(\([\w_\-\.]+\))?\s*#\s*'
        match = search(re_hostname_prompt, let['output'])

        # プロンプトからホスト名を抜き出す
        match_hostname = ''
        if match:
            match_hostname = match.group(2)
        else:
            let['code'] = -1
            let['msg'] = '[Error] prompt is not expect'

        # ホスト名が想定と違っていたらエラー
        if match_hostname != hostname:
            let['code'] = -1
            let['msg'] = '[Error] prompt is not {hostname}, current prompt is {match_hostname}'
            return let
        else:
            let['code'] = 0
            let['msg'] = 'prompt is {hostname}'

        return let

    def login_secondary(self, timeout=None, secondary_user=None, secondary_password=None):
        """セカンダリノードにログイン"""
        let = {'code': 0, 'msg': '', 'output': ''}

        secondary_user = secondary_user or self.fgt_info.user
        secondary_password = secondary_password or self.fgt_info.password
        timeout = timeout or self.timeout

        #  vdomの場合は、globalに移動してSSHする
        if self.fgt_info.vdom_mode == 'multi-vdom':
            res = self.config_global()
            # @todo グローバルモードであることの確認とエラー処理

        # cluster id 取得
        let = self.get.system_ha_status.get()
        if let['code'] != 0:
            let['msg'] = f'[Error]Failed get cluster index'
            return let

        if self.get.system_ha_status.exsist_secondary is False:
            let['msg'] = f'[Error]Secondary node is not available'
            return let

        secondary_cluster_index = self.get.system_ha_status.secondary_cluster_index
        # Secondary Nodeにログイン
        cmd = f'execute ha manage {secondary_cluster_index} {secondary_user}'
        self.interact.send(cmd)
        index = self.interact.expect(self.SSH_PROMPT, timeout=timeout)
        let['output'] = self.interact.current_output

        # ssh成功
        if index == 0:
            # エラーチェック
            let = self.ssh_error_check(let['output'])
            if let['code'] != 0:
                return let

            # パスワード入力
            self.interact.send(secondary_password)
            index = self.interact.expect(self.FGT_PROMPT, timeout=timeout)
            let['output'] = self.interact.current_output

            if index == 0:
                # パスワード入力後のエラーチェック
                let = self.ssh_error_check(let['output'])
                if let['code'] != 0:
                    return let

                # プロンプトのチェック
                let = self.prompt_check(self.fgt_info.secondary_hostname)

                if let['code'] == 0:
                        let['code'] = 0
                        let['msg'] = f'Login to secondary {self.fgt_info.secondary_hostname}'
                else:
                    let['code'] = -1
                    let['msg'] = f'[Error ] Login Failed secondary {self.fgt_info.secondary_hostname}'

            else:
                let['code'] = 1
                let['msg'] = f'[Error] Login failed {let['output']}'

        return let

    def logout_secondary(self, timeout=5.0):
        """セカンダリノードからログアウト"""
        let = self.exit()
        # @todo ログアウト確認

        # vdomの場合は、Primary側はglobalモードで実行しているので、グローバルモードを終了する
        if self.fgt_info.vdom_mode == 'multi-vdom':
            let = self.end_global()

        # @todo エラー処理

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
        vdom_name = vdom_name or self.fgt_info.manage_vdom
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

    def export_debug_report(self, secondary=False, export_dir=None):
        if secondary:
            hostname = self.fgt_info.secondary_hostname
        else:
            hostname = self.fgt_info.hostname
        export_dir = Path(export_dir or self.fgt_info.export_dir)

        # デバッグレポート取得
        let = self.diagnose.get('debug report')

        if let['code'] != 0:
            return let

        # ファイルへエクスポート
        let = save_debug_report(
            content=let['output'],
            hostname=hostname,
            alias=self.fgt_info.alias,
            version=self.fgt_info.version,
            export_dir=export_dir,
        )

        return let

    def export_backup(self, secondary=False, export_dir=None):
        if secondary:
            hostname = self.fgt_info.secondary_hostname
        else:
            hostname = self.fgt_info.hostname
        export_dir = Path(export_dir or self.fgt_info.export_dir)

        # バックアップ取得
        let = self.show.get()

        if let['code'] != 0:
            return let

        # ファイルへエクスポート
        let = save_config(
            content=let['output'],
            hostname=hostname,
            alias=self.fgt_info.alias,
            version=self.fgt_info.version,
            export_dir=export_dir,
            format='text',
            encode='utf-8'
        )

        return let


if __name__ == '__main__':
    tmp = {
        'fgt_addr': '172.16.201.201',
        'fgt_user': 'admin',
        'fgt_password': 'P@ssw0rd',
    }

    fgtcli = FgtCli(FgtInfo())
    fgtcli.set_target(**tmp)
    fgtcli.display=True

    let = fgtcli.login()
    let = fgtcli.login_secondary()
    let = fgtcli.export_backup(secondary=True)
    let = fgtcli.logout_secondary()

    fgtcli.logout()
