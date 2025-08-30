from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.api.cmdb import Cmdb
from booyaa.ftnt.fgt.api.monitor import Monitor
from booyaa.ftnt.fgt.api.get_node_info import get_node_info

from httpx import Client
from httpx import TimeoutException, ConnectTimeout, ConnectError, RequestError, HTTPStatusError
from urllib.parse import urljoin
import json
from configparser import ConfigParser
from pathlib import Path
from traceback import format_exc

class FgtApi():
    def __init__(self, fgt_info: FgtInfo):
        """"""
        self.fgt_info = fgt_info
        self.timeout = 30

        self.cmdb = Cmdb(self)
        self.monitor = Monitor(self)
        self.get_node_info = get_node_info

    def read_config_ini(self, config_ini=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        cp = ConfigParser()

        if config_ini:
            self.config_ini_path = Path(config_ini)

        # config.iniがなければ作成
        if self.config_ini_path.is_file():
            cp.read(self.config_ini_path, encoding='utf-8')
        else:
            cp.add_section('default')
            cp.set('default', 'connect_timeout', '60.0')
            cp.set('default', 'read_timeout', '30.0')

            with open(self.config_ini_path, 'w', encoding='utf-8') as cf:
                cp.write(cf)

        self.timeout = (cp.getfloat('default', 'connect_timeout'), cp.getfloat('default', 'read_timeout'))
        let['msg'] = f'read config.ini self.timeout: {self.timeout}'
        return let

    def set_target(self, fgt_addr, fgt_user, fgt_password, fgt_alias='', fgt_hostname='', fgt_ssh_port=22, fgt_https_port=443, timeout=None):
        let = {'code': 0, 'msg': '', 'output': ''}
        self.fgt_info.addr = fgt_addr
        self.fgt_info.user = fgt_user
        self.fgt_info.password = fgt_password
        self.fgt_info.alias = fgt_alias
        self.fgt_info.hostname = fgt_hostname
        self.fgt_info.ssh_port = fgt_ssh_port
        self.fgt_info.https_port = fgt_https_port
        self.timeout = timeout or self.timeout

        let['msg'] = f'Set to {self.fgt_info.addr}, user: {self.fgt_info.user}'

        return let

    def login(self, addr=None, user=None, https_port=None, password=None, timeout=None, node_info=True):
        let = {'code': 0, 'msg': '', 'output': ''}

        addr = addr or self.fgt_info.addr
        https_port = https_port or self.fgt_info.https_port
        user = user or self.fgt_info.user
        password = password or self.fgt_info.password
        timeout = timeout or self.timeout

        self.session = Client(verify=False, timeout=timeout, follow_redirects=True)
        self.session.headers.update({
            'User-Agent': 'FortiAPI/1.0',
            'Content-Type': 'application/json',
        })

        # Fortigate　APIベースURL
        self.base_url = urljoin(f'https://{addr}:{https_port}', 'api/v2/')


        # ユーザ情報をセット
        login_data = {'username': user, 'secretkey': password}

        # let = self.session.post(urljoin(f'https://{self.addr}', 'logincheck'), params=login_data)

        let = self.req(
            url=urljoin(f'https://{addr}:{https_port}','logincheck'),
            method='post',
            params=login_data,
            req_format='data',
            res_format='text',
            timeout=60
        )

        # 成功時のbodyは,以下だがドキュメントによって多少違いがあるため正規表現では難しい。
                # 認証エラーなどは、Web画面のHTMLが返ってくるので、成功時はline数が少ないことで判定する。
                # <script language="javascript">
                # document.location="/prompt?viewOnly&redir=%2F";
                # </script>
        # if let['code'] == 0 and len(let['output']) == 3:
        # cookieのあるなしで成功判定に一旦仮変更して様子見
        if let['code'] == 0 and len(let['cookie']):
            let['msg'] = f'Login to {addr}'
        else:
            let['code'] = 1
            let['msg'] = f'[Error] Login Faile {addr}'
            return let

        # ログイン成功ならホスト名などnode infoを取得
        if node_info and self.fgt_info.node_info_flg is False:
            let = self.get_node_info(self)
            if let['code'] == 0:
                self.fgt_info.node_info_flg = True

        return let

    def logout(self):
        """"""
        let = self.req(
            url=urljoin(f'https://{self.fgt_info.addr}:{self.fgt_info.https_port}','logout'),
            method='post',
            res_format='text',
        )

        # logouに失敗していてもセッションはクローズする
        self.session.close()

        return let

    def req(
            self,
            url: str,
            method: str = 'post', # post | get
            params: dict | None = None,
            req_format: str = 'json',  # json | data
            res_format: str = 'json',  # json | text | bin
            timeout: float | None = None
        ) -> dict:
        let = {'code': 0, 'msg': '', 'output': '', 'trace': '', 'cookie': self.session.cookies.items()}

        # cookieにCSRFトークンが含まれていたらヘッダーにセット
        for k, v in self.session.cookies.items():
            if k.startswith('ccsrftoken_'):
                self.session.headers.update({'X-CSRFTOKEN': v.strip('"')})

        kwargs = {'timeout': timeout or self.timeout}
        try:
            if method == 'post':
                request = self.session.post
                if params and req_format == 'json':
                    kwargs['json'] = params
                elif params and req_format == 'data':
                    kwargs['params'] = params

            elif method == 'get':
                request = self.session.get
                if params:
                    kwargs['params'] = params

            res = request(url, **kwargs)

            if res_format == 'json':
                # 念のためjsonでload出来なかったら、content文字列を返す。
                try:
                    res_content = res.content.decode('utf-8')
                    let['output'] = json.loads(res_content)
                except json.JSONDecodeError:
                    let['output'] = res.content.decode('utf-8').split('\n')
            elif res_format == 'text':
                    let['output'] = res.content.decode('utf-8').split('\n')
            else:
                let['output'] = res.content

            res.raise_for_status() # status codeが200以外

        except ConnectTimeout as e:
            let['code'] = 1
            let['msg'] = f'[Error] Connection Timeout {self.fgt_info.addr},\nException: {e}'
            let['trace'] = format_exc()
        except ConnectError as e:
            let['code'] = 1
            let['msg'] = f'[Error] Connection Error {self.fgt_info.addr},\nException: {e}'
            let['trace'] = format_exc()
        except TimeoutException as e:
            let['code'] = 1
            let['msg'] = f'[Error] Session Timeout {self.fgt_info.addr},\nException: {e}'
            let['trace'] = format_exc()
        except RequestError as e:
            let['code'] = 1
            let['msg'] = f'[Error] Request Exception {self.fgt_info.addr},\nException: {e}'
            let['trace'] = format_exc()
        except HTTPStatusError as e:
            # HTTPSstatusError!!!: Client error '404 Not Found' for url 'https://172.16.201.201/api/v2/hoge'
            # For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
            let['code'] = res.status_code
            let['msg'] = f'[Error] {e}'
            let['trace'] = format_exc()
        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] Exception {self.fgt_info.addr},\nException: {e}'
            let['trace'] = format_exc()

        finally:
            return let

    def content_decode(self, content, format, encode='utf-8'):
        """
        Args:
            content (binary): output of client.content
            format (str): json, text, bin,
            encode (str): utf-8
        """
        if format == 'json':
            try:
                decode_content = content.decode(encode)
                decode_content = json.loads(decode_content)
            except json.JSONDecodeError:
                decode_content = content
        elif format == 'text':
            decode_content = content.decode(encode).replace('\r\n', '\n').replace('\r', '\n').split('\n')
        else:
            decode_content = content
        return decode_content
