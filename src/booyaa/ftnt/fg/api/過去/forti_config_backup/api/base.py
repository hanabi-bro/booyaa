import requests
from requests.exceptions import Timeout, ConnectTimeout, ConnectionError, RequestException, HTTPError
import json
from configparser import ConfigParser
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from logging import basicConfig, getLogger
from pathlib import Path
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)
console = Console()

class FortiApi():
    def __init__(self, log_level='DEBUG'):
        """"""
        self.fg_addr = ''
        self.fg_port = ''
        self.fg_user = ''
        self.fg_pass = ''
        self.fg_alias = ''
        self.fg_hostname = ''

        self.base_url = f'https://{self.fg_addr}/api/v2/'
        self.session = requests.Session()
        self.session.verify = False
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
        self.ha_mgmt_status = ''  # mgmt statusが有効ならHAは見ない

        self.secondary_hostname = ''
        self.secondary_serial = ''
        self.secondary_ha_mode = ''
        self.secondary_ha_role = ''
        self.result_message = ''
        self.error = None

        install()
        basicConfig(
            level=log_level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)]
        )
        self.log = getLogger('FortiApi_base')


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
            cp.set('default', 'connect_timeout', '10.0')
            cp.set('default', 'read_timeout', '30.0')

            with open(self.config_ini_path, 'w', encoding='utf-8') as cf:
                cp.write(cf)

        self.timeout = (cp.getfloat('default', 'connect_timeout'), cp.getfloat('default', 'read_timeout'))
        let['msg'] = f'read config.ini self.timeout: {self.timeout}'
        return let

    def set_target(self, target, user, password, alias=None):
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
        self.backup_directory = r'./fg_config'

        # Fortigate　APIベースURL
        self.base_url = f'https://{self.fg_addr}/api/v2/'

        let['msg'] = f'Set to {self.fg_addr}, user: {self.fg_user}'

        return let

    def login(self):
        """"""
        let = {'code': 0, 'msg': '', 'output': ''}

        # ユーザ情報をセット
        login_data = {'username': self.fg_user, 'secretkey': self.fg_pass}

        try:
            # APIでログイン（token使わないため6.2以降とかはRead Onlyになると思われる。どのバージョンからは定かではない）
            res = self.session.post(f'https://{self.fg_addr}/logincheck', data=login_data, timeout=self.timeout)
            # ステータスコードだけではログイン成功とは判定できない。
            # こういうところもFTNTは、抜群にいけてない

            # cookieの中身を表示
            cookie_dict = self.session.cookies.get_dict()
            for k, v in cookie_dict.items():
                if k.startswith('ccsrftoken_'):
                    self.session.headers.update({'X-CSRFTOKEN': v.strip('"')})

            let['output'] = res.content.decode('utf-8').split('\n')
            if res.status_code == 200:
                if len(let['output']) < 5:
                    let['msg'] = f'Login to {self.fg_addr}'
                    # 成功時のbodyは,以下だがドキュメントによって多少違いがあるため正規表現では難しい。
                    # 認証エラーなどは、Web画面のHTMLが返ってくるので、成功時はline数が少ないことで判定する。
                    # <script language="javascript">
                    # document.location="/prompt?viewOnly&redir=%2F";
                    # </script>

                else:
                    let['code'] = 1
                    let['msg'] = f'[Error] Failed to login {self.fg_addr}'
            else:
                # ステータスコードが200以外の場合
                let['code'] = 1
                let['msg'] = f'[Error] Login Failed {self.fg_addr}, code:{res.status.code}'

            # 成功ならホスト名などnode infoを取得
            if let['code'] == 0:
                res = self.get_node_info()
                if res['code'] == 0:
                    let['msg'] = f'login to {self.fg_addr}, hostname {self.hostname}'
                else:
                    # node info取得失敗
                    let['code'] == 1
                    let['msg'] = f'[Error] Login to {self.fg_addr}, But Failed get node info'

        except Timeout as e:
            let['code'] = 1
            let['msg'] = f'[Error] Session Timeout to login {self.fg_addr}'
            self.error = e
        except ConnectTimeout as e:
            let['code'] = 1
            let['msg'] = f'[Error] Connection Timeout to login {self.fg_addr}'
            self.error = e
        except ConnectionError as e:
            let['code'] = 1
            let['msg'] = f'[Error] Connection Error to {self.fg_addr}'
            self.error = e
        except RequestException as e:
            let['code'] = 1
            let['msg'] = f'[Error] Request Exception to {self.fg_addr}'
            self.error = e
        except HTTPError as e:
            let['code'] = 1
            let['msg'] = f'[Error] HTTP Error in  {self.fg_addr}'
            self.error = e
        except Exception as e:
            let['code'] = 1
            let['msg'] = f'[Error] Failed to login {self.fg_addr}, Exception: {e}'
            self.error = e

        return let

    def logout(self):
        """"""
        let = {'code': 0, 'msg': '', 'output': ''}
        res = self.session.post(f'https://{self.fg_addr}/logout', timeout=self.timeout)
        let['output'] = res.content.decode('utf-8').split('\n')
        if res.status_code == 200:
            let['msg'] = f'logout from {self.fg_addr}'
        else:
            let['code'] = 1
            let['msg'] = f'[Error] logout fail {self.fg_addr}, Force session closed'

        # logouに失敗してもセッションはクローズする
        self.session.close()

        return let

    def get_node_info(self):
        """
        '/monitor/system/csf'がかなり一度に多くの情報が取れることを発見したので差し替え
        """

        let = {'code': 0, 'msg': '', 'output': ''}
        uri = f'{self.base_url}/monitor/system/csf'

        res = self.session.get(uri, timeout=self.timeout)
        let['output'] = res.content.decode('utf-8').split('\n')

        if res.status_code == 200:
            res_data = json.loads(res.content.decode('utf-8'))

            # --------------------- for debug ---------------------
            with open(Path('./tmp', 'debug.json'), 'w', encoding='utf-8') as f:
                json.dump(res_data, f, indent=2, ensure_ascii=False)
            # --------------------- for debug ---------------------

            res_data = res_data['results']['devices']['fortigate'][0]

            self.hostname = res_data['host_name']
            self.serial = res_data['serial']
            self.major = res_data['firmware_version_major']
            self.minor = res_data['firmware_version_minor']
            self.patch = res_data['firmware_version_patch']
            self.build = res_data['firmware_version_build']
            self.version = f'{self.major}.{self.minor}.{self.patch}'
            self.model = res_data['model']

            self.vdom_mode = res_data['state']['vdom_mode']
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

            let['msg'] = f'get node info {self.fg_addr}'

        else:
            let['code'] = 1
            let['msg'] = f'[Error] Fail get node info {self.fg_addr}'

        return let

        sample_response = {
        "http_method": "GET",
        "revision": "20.1.1216463408",
        "results": {
            "devices": {
            "fortigate": [
                {
                "appliance_info": [],
                "firmware_license": True,
                "path": "FGT60FTK20011089",
                "mgmt_ip_str": "",
                "mgmt_port": 0,
                "sync_mode": 1,
                "object_unification": 0,
                "saml_role": "disable",
                "ipam_status": "disable",
                "admin_port": 443,
                "serial": "FGT60FTK20011089",
                "fabric_uid": "",
                "host_name": "FG60F-Secondary",
                "firmware_version_major": 7,
                "firmware_version_minor": 4,
                "firmware_version_patch": 8,
                "firmware_version_build": 2795,
                "firmware_version_branch": 2795,
                "firmware_version_maturity": "M",
                "firmware_version_release_type": "GA",
                "device_type": "fortigate",
                "forticloud_id": "Confidential",
                "authorization_type": "serial",
                "model_name": "FortiGate",
                "model_number": "60F",
                "model": "FGT60F",
                "model_subtype": "",
                "model_level": "low",
                "eos": False,
                "limited_ram": True,
                "is_vm": False,
                "state": {
                    "hostname": "FG60F-Secondary",
                    "fext_enabled": True,
                    "fext_vlan_mode": False,
                    "snapshot_utc_time": 1748839586000,
                    "utc_last_reboot": 1748838977000,
                    "time_zone_offset": -540,
                    "time_zone_text": "(GMT+9:00) Asia/Tokyo",
                    "time_zone_db_name": "Asia/Tokyo",
                    "is_dst_observed": False,
                    "is_dst_timezone": False,
                    "date_format": "yyyy/MM/dd",
                    "date_format_device": "system",
                    "fortimanager_configured": False,
                    "centrally_managed": False,
                    "fortimanager_backup_mode": False,
                    "fips_cc_enabled": False,
                    "fips_ciphers_enabled": False,
                    "vdom_mode": "",
                    "management_vdom": "root",
                    "conserve_mode": False,
                    "bios_security_level": 1,
                    "image_sign_status": "certified",
                    "forticare_registration_level": 1,
                    "has_hyperscale_license": False,
                    "need_fs_check": False,
                    "carrier_mode": False,
                    "csf_enabled": False,
                    "csf_group_name": "",
                    "csf_upstream_ip": "",
                    "csf_sync_mode": "default",
                    "csf_object_sync_mode": "local",
                    "ha_mode": 0,
                    "is_ha_master": 1,
                    "ngfw_mode": "profile-based",
                    "forced_low_crypto": False,
                    "has_log_disk": False,
                    "has_local_config_revisions": True,
                    "lenc_mode": False,
                    "usg_mode": False,
                    "stateramp_mode": False,
                    "admin_https_redirection": True,
                    "config_save_mode": "automatic",
                    "usb_mode": False,
                    "security_rating_run_on_schedule": True,
                    "features": {
                    "gui-ipv6": False,
                    "gui-replacement-message-groups": False,
                    "gui-local-out": False,
                    "gui-certificates": False,
                    "gui-custom-language": False,
                    "gui-wireless-opensecurity": False,
                    "gui-app-detection-sdwan": False,
                    "gui-display-hostname": True,
                    "gui-fortigate-cloud-sandbox": False,
                    "gui-firmware-upgrade-warning": True,
                    "gui-forticare-registration-setup-warning": True,
                    "gui-auto-upgrade-setup-warning": False,
                    "gui-workflow-management": False,
                    "gui-cdn-usage": True,
                    "switch-controller": True,
                    "wireless-controller": True,
                    "fortiextender": True,
                    "fortitoken-cloud-service": True
                    }
                },
                "vdoms": [
                    "root"
                ],
                "vdom_info": {
                    "root": {
                    "central_nat_enabled": False,
                    "transparent_mode": False,
                    "ngfw_mode": "profile-based",
                    "features": {
                        "gui-proxy-inspection": False,
                        "gui-icap": False,
                        "gui-implicit-policy": True,
                        "gui-dns-database": False,
                        "gui-load-balance": False,
                        "gui-multicast-policy": False,
                        "gui-dos-policy": False,
                        "gui-object-colors": True,
                        "gui-route-tag-address-creation": False,
                        "gui-voip-profile": False,
                        "gui-ap-profile": True,
                        "gui-security-profile-group": False,
                        "gui-local-in-policy": False,
                        "gui-explicit-proxy": False,
                        "gui-dynamic-routing": False,
                        "gui-policy-based-ipsec": False,
                        "gui-threat-weight": True,
                        "gui-spamfilter": False,
                        "gui-file-filter": True,
                        "gui-application-control": True,
                        "gui-ips": True,
                        "gui-dhcp-advanced": True,
                        "gui-vpn": True,
                        "gui-sslvpn": False,
                        "gui-wireless-controller": True,
                        "gui-advanced-wireless-features": False,
                        "gui-switch-controller": True,
                        "gui-fortiap-split-tunneling": False,
                        "gui-webfilter-advanced": False,
                        "gui-traffic-shaping": True,
                        "gui-wan-load-balancing": True,
                        "gui-antivirus": True,
                        "gui-webfilter": True,
                        "gui-videofilter": False,
                        "gui-dnsfilter": True,
                        "gui-waf-profile": False,
                        "gui-dlp-profile": False,
                        "gui-virtual-patch-profile": False,
                        "gui-casb": False,
                        "gui-fortiextender-controller": True,
                        "gui-advanced-policy": False,
                        "gui-allow-unnamed-policy": False,
                        "gui-email-collection": False,
                        "gui-multiple-interface-policy": False,
                        "gui-policy-disclaimer": False,
                        "gui-ztna": False,
                        "gui-ot": False,
                        "gui-dynamic-device-os-id": False
                    },
                    "virtual_wire_pair_count": 0,
                    "is_admin_type_vdom": False,
                    "is_lan_extension_vdom": False,
                    "is_management_vdom": True,
                    "resolve_hostnames": True
                    }
                },
                "vdom_mode": False,
                "fweb_build": "eNp1kctO6zAQhnkWr5FoyqVJduPESQ2+HV/Sg4Q0SkuR2EJZob47Tgt1UsTGsr9/ZvzPzCeptGp4S8rP7xtSC6paotFceVLOF8Xt5UkKXNSogqTMnkmVa9Bq7VFwyT2rSbl7+9ie5DZwVJqUJH/O874oNrP1Nnvpb26zTVEsrq/7l1m2Ldb9mkxSTKCCV2jAL2Pu09X7rt+9blKMhHttB0OkXCTI1Q+8SVDXTMQaTevxbtaQqYCCdcOpV2e+489xFoda+QlakDhv6Vmoc6Iz6gj3l8QI8I22cjRZoNSy7mhi4uE4VwH0YLGFc0WCD5b7xyjKqC2hYwgd/gsQd+W5YqTMvnEFJniDUE3QCqaoVg4ds92wxh+2hHTnxqEMNU1EcPWA0LaWteBH/wldgcDYFkbH3moxkjw7TFeiC8Zo65N0wOmpmEdlwghE/d6N3rF/qmPMXWIGqoeYF7uL4siRW/FhZ86bxIIbtRICr39b6rj1IbZSawlc/ebHsn9xzGdzzP7/KXcChpr7/cUXoiXzWQ==",
                "fsw_version": 0,
                "fsw_list": [],
                "fap_version": 0,
                "fap_list": [],
                "fext_version": 0,
                "fext_list": [],
                "ha_mode": "active-passive",
                "is_ha_master": 1,
                "ha_list": [
                    {
                    "serial_no": "FGT60FTK20011089",
                    "hostname": "FG60F-Secondary",
                    "is_ha_primary": True
                    },
                    {
                    "serial_no": "FGT60FTK20099VM6",
                    "hostname": "FG60F-Primary",
                    "is_ha_primary": False
                    }
                ],
                "upgrade_status": "disabled",
                "upgrade_id": 0,
                "upgrade_path_index": 0,
                "device_upgrade_summary": {
                    "disabled": 0,
                    "initialized": 0,
                    "downloading": 0,
                    "device-disconnected": 0,
                    "ready": 0,
                    "coordinating": 0,
                    "staging": 0,
                    "cancelled": 0,
                    "final-check": 0,
                    "upgrade-devices": 0,
                    "confirmed": 0,
                    "done": 0,
                    "failed": 0
                },
                "subtree_members": [],
                "forticloud_id_list": {},
                "tree_has_multi_vdom": False,
                "ha_group_name": "labfg01",
                "ha_group_id": 255,
                "fabric_approval_support": False
                }
            ]
            },
            "protocol_enabled": False
        },
        "vdom": "root",
        "path": "system",
        "name": "csf",
        "status": "success",
        "serial": "FGT60FTK20011089",
        "version": "v7.4.8",
        "build": 2795
        }


if __name__ == '__main__':
    fa = FortiApi()
    targets = [
        [
            '172.16.201.201',
            'admin',
            'P@ssw0rd',
            ''
        ],
        [
            '172.16.201.202',
            'admin',
            'P@ssw0rd',
            ''
        ],
    ]

    for t in targets:
        res = fa.set_target(*t)
        console.print(f'set target {t[0]}')
        if res['code'] != 0:
            console.print(f'[Error] Failed set target {t[0]}')
            console.print(fa.error)
            continue

        console.print(f'login to {t[0]}')
        res = fa.login()
        if res['code'] != 0:
            console.print(f'{res['msg']}, {res['code']}, {res['output']}')
            console.print(fa.error)
            continue

        console.print(f'logout from {t[0]}')
        res = fa.logout()
        if res['code'] != 0:
            console.print(f'{res['msg']}, {res['code']}, {res['output']}')
            console.print(fa.error)
            continue
