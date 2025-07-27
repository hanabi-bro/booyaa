# import requests
# from requests.exceptions import Timeout, ConnectTimeout, ConnectionError, RequestException, HTTPError
from httpx import Client
from httpx import TimeoutException, ConnectTimeout, ConnectError, RequestError, HTTPStatusError
from urllib.parse import urljoin
import json
from configparser import ConfigParser
from pathlib import Path
from traceback import format_exc
from booyaa.ftnt.api.cmdb import Cmdb
from booyaa.ftnt.api.monitor import Monitor


class FortiApi():
    def __init__(self):
        """"""
        self.fg_addr = ''
        self.fg_port = ''
        self.fg_user = ''
        self.fg_pass = ''
        self.fg_alias = ''

        self.base_url = ''
        self.session = ''

        self.root_dir = Path(__file__).parent.resolve()
        config_ini = 'config.ini'
        self.config_ini_path = Path(Path(__file__).parent.parent.resolve(), config_ini)


        self.cmdb = Cmdb(self)
        self.monitor = Monitor(self)

        # self.read_config_ini(config_ini)

        # node info
        self.hostname = ''
        self.serial = ''
        self.version = ''
        self.major = ''
        self.minor = ''
        self.patch = ''
        self.build = ''

        self.model = ''

        self.config = b''

        self.manage_vdom = 'root'
        self.vdom_mode = ''

        self.ha_mode = ''
        self.ha_role = ''
        self.ha_mgmt_status = ''      # mgmt statusが有効ならHAは見ない
        self.ha_mgmt_interfaces = []  # さらに念のため見るならmgmt_interfacesが1以上

        self.secondary_hostname = ''
        self.secondary_serial = ''
        self.secondary_ha_mode = ''
        self.secondary_ha_role = ''

        self.result_message = ''

        self.error = None

        self.timeout = 60.0

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

    def set_target(self, target, user, password, alias=None, timeout=30.0, backup_dir=r'fg_config'):
        """ターゲットをセット
        Args:
            traget:
            user:
            password:
            alias:
        """
        let = {'code': 0, 'msg': '', 'output': ''}

        # ポート指定があったら、一応取っておく
        if ':' in target:
            _, port = target.split(':')
            port = int(port)
        else:
            port = 443

        self.fg_addr = target
        self.fg_port = port
        self.fg_user = user
        self.fg_pass = password

        # エリアス指定
        if alias is not None:
            self.fg_alias = alias

        # バックアップディレクトリ
        self.backup_directory = Path(backup_dir)

        # Fortigate　APIベースURL
        self.base_url = urljoin(f'https://{self.fg_addr}', 'api/v2/')

        self.session = Client(verify=False, timeout=timeout, follow_redirects=True)
        self.session.headers.update({
            'User-Agent': 'FortiAPI/1.0',
            'Content-Type': 'application/json',
        })

        let['msg'] = f'Set to {self.fg_addr}, user: {self.fg_user}'

        return let

    def login(self, node_info=True):
        """"""
        # ユーザ情報をセット
        login_data = {'username': self.fg_user, 'secretkey': self.fg_pass}

        # let = self.session.post(urljoin(f'https://{self.fg_addr}', 'logincheck'), params=login_data)

        let = self.req(
            url=urljoin(f'https://{self.fg_addr}','logincheck'),
            method='post',
            params=login_data,
            req_format='data',
            res_format='text',
            timeout=60)

        # 成功時のbodyは,以下だがドキュメントによって多少違いがあるため正規表現では難しい。
                # 認証エラーなどは、Web画面のHTMLが返ってくるので、成功時はline数が少ないことで判定する。
                # <script language="javascript">
                # document.location="/prompt?viewOnly&redir=%2F";
                # </script>
        # if let['code'] == 0 and len(let['output']) == 3:
        # cookieのあるなしで成功判定に一旦仮変更して様子見
        if let['code'] == 0 and len(let['cookie']):
            let['msg'] = f'Login to {self.fg_addr}'
        else:
            let['code'] = 1
            let['msg'] = f'[Error] Login Faile {self.fg_addr}'

        # ログイン成功ならホスト名などnode infoを取得
        if let['code'] == 0 and node_info:
            res = self.get_node_info()
            if res['code'] == 0:
                let['msg'] = f'Login and get node info {self.fg_addr}, hostname {self.hostname}'
            else:
                # node info取得失敗
                let['code'] == 1
                let['msg'] = f'[Error] Login but Failed get node info {self.fg_addr}'

        return let

    def logout(self):
        """"""
        let = self.req(
            url=urljoin(f'https://{self.fg_addr}','logout'),
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

        except TimeoutException as e:
            let['code'] = 1
            let['msg'] = f'[Error] Session Timeout {self.fg_addr},\nException: {e}'
            let['trace'] = format_exc()
        except ConnectTimeout as e:
            let['code'] = 1
            let['msg'] = f'[Error] Connection Timeout {self.fg_addr},\nException: {e}'
            let['trace'] = format_exc()
        except ConnectError as e:
            let['code'] = 1
            let['msg'] = f'[Error] Connection Error {self.fg_addr},\nException: {e}'
            let['trace'] = format_exc()
        except RequestError as e:
            let['code'] = 1
            let['msg'] = f'[Error] Request Exception {self.fg_addr},\nException: {e}'
            let['trace'] = format_exc()
        except HTTPStatusError as e:
            # HTTPSstatusError!!!: Client error '404 Not Found' for url 'https://172.16.201.201/api/v2/hoge'
            # For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
            let['code'] = res.status_code
            let['msg'] = f'[Error] {e}'
            let['trace'] = format_exc()
        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] Exception {self.fg_addr},\nException: {e}'
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

    def get_node_info(self):
        let = self.monitor.system_csf.get()

        if let['code'] != 0:
            return let

        res_data = let['output']['results']['devices']['fortigate'][0]

        self.hostname = res_data['host_name']
        self.serial = res_data['serial']
        self.major = res_data['firmware_version_major']
        self.minor = res_data['firmware_version_minor']
        self.patch = res_data['firmware_version_patch']
        self.build = res_data['firmware_version_build']
        self.version = f'{self.major}.{self.minor}.{self.patch}'
        self.model = res_data['model']

        if res_data['state']['vdom_mode'] == "":
            self.vdom_mode = "no-vdom"
        else:
            self.vdom_mode = "multi-vdom"
        self.manage_vdom = res_data['state']['management_vdom']

        self.ha_mode = res_data['ha_mode']

        if self.ha_mode == 'active-passive' or self.ha_mode == 'a-p':
            self.ha_role = 'master' if res_data['is_ha_master'] == 1 else 'slave'
            ha_list = res_data['ha_list']
            for ha_info in ha_list:
                if ha_info['hostname']  == self.hostname:
                    next
                else:
                    self.secondary_hostname = ha_info['hostname']
                    self.secondary_serial = ha_info['serial_no']
                    self.secondary_ha_role = 'primary' if ha_info['is_ha_primary'] else 'secondary'
                    break

        let = self.cmdb.system_ha.get()
        if let['code'] != 0:
            return let
        self.ha_mgmt_status = let['output']['results']['ha-mgmt-status']
        self.ha_mgmt_interfaces = let['output']['results']['ha-mgmt-interfaces']


        let['msg'] = f'get node info {self.fg_addr}'


        return let
