from booya_config_parser.config_to_obj import config_to_obj
from pprint import pprint
from pathlib import Path
from booya_config_parser.formatter.global_config.base import Base
from booya_config_parser.formatter.global_config.dns import Dns
from booya_config_parser.formatter.global_config.sys_global import Global
from booya_config_parser.formatter.global_config.ha import Ha
from booya_config_parser.formatter.firewall_address import FirewallAddress
from booya_config_parser.formatter.firewall_addrgrp import FirewallAddrgrp
from booya_config_parser.formatter.firewall_service_custom import FirewallServiceCustom
from booya_config_parser.formatter.firewall_service_group import FirewallServiceGroup
from booya_config_parser.formatter.firewall_vip import FirewallVip
from booya_config_parser.formatter.firewall_vipgrp import FirewallVipgrp
from booya_config_parser.formatter.firewall_ippool import FirewallIppool
from booya_config_parser.formatter.firewall_policy import FirewallPolicy


class ConfigParser():
    def __init__(self, debug=True, debug_path='./tmp/log/') -> None:
        self.debug = debug
        self.debug_path = debug_path
        self.config_file_path = ''
        self.config_obj = ''
        self.formatted_params = {}
        self.parsed_obj = {'header': '', 'global': {}}

        self.global_formatter = {
            'base': Base(),
            'system_global': Global(),
            'system_ha': Ha(),
            'system_dns': Dns(),
        }

        self.global_field_names = {k: v.field_names for k, v in self.global_formatter.items()}

        self.formatter = {
            'firewall_address': FirewallAddress(),
            'firewall_addrgrp': FirewallAddrgrp(),
            'firewall_service_custom': FirewallServiceCustom(),
            'firewall_service_group': FirewallServiceGroup(),
            'firewall_vip': FirewallVip(),
            'firewall_vipgrp': FirewallVipgrp(),
            'firewall_ippool': FirewallIppool(),
            'firewall_policy': FirewallPolicy(),
        }

        self.field_names = {k: v.field_names for k, v in self.formatter.items()}

    def debug_print(self, debug_data, filename):
        with open(Path(self.debug_path, filename), 'w', encoding='utf-8') as f:
            pprint(debug_data, stream=f)

    def config_load(self, config_file_path):
        self.config_file_path = config_file_path
        self.config_obj = config_to_obj(config_file_path)
        self.vdom_mode = 'novdom' if self.config_obj['header']['vdom'] == 0 else 'multivdom'

    def parse_header(self):
        self.config_obj['header']['vdom']

        if self.config_obj['header']['vdom'] == 0:
            vdom_mode = 'novdom'
        elif self.config_obj['header']['vdom'] == 1:
            vdom_mode = 'multivdom'
        else:
            vdom_mode = 'no support'

        if vdom_mode == 'novdom':
            global_key = 'root'
        else:
            global_key = 'global'

        config_version = self.config_obj['header']['config-version'].split('-')
        model = config_version[0]
        version = config_version[1]
        major = version.split('.')[0]
        minor = version.split('.')[1]
        patch = version.split('.')[2]

        if self.config_obj['header']['opmode'] == 0:
            operation_mode = 'nat'
        else:
            operation_mode = 'transparent'

        self.parsed_obj['header'] = {
            'version': version,
            'model': model,
            'major': major,
            'minor': minor,
            'patch': patch,
            'conf_file_ver': self.config_obj['header']['conf_file_ver'],
            'opmode': self.config_obj['header']['opmode'],
            'operation_mode': operation_mode,
            'user': self.config_obj['header']['user'],
            'vdom_mode': vdom_mode,
            'vdom': self.config_obj['header']['vdom'],
            'global_vdom': self.config_obj['header']['global_vdom'],
            'hostname': self.config_obj[global_key]['system_global']['hostname'][0],
        }

    def parse_categories(self, fileld_names=None):
        if fileld_names is None:
            filed_names = self.field_names

        # global系
        self.pre_format_global()

        # vdom系
        for category in filed_names:
            self.parse_category(category)

    def parse_category(self, category_key='firewall_address') -> None:
        """"""
        # parsed_obj = OrderedDict()
        pre_format_objects = self.pre_format_config_obj(category_key)
        for vdom_name, v in pre_format_objects.items():
            self.parsed_obj.setdefault(vdom_name, {})
            self.parsed_obj[vdom_name][category_key] = self.formatter[category_key].format(v[category_key])

        if self.debug:
            self.debug_print(self.parsed_obj, 'parsed_obj.py')

    def pre_format_global(self):
        if self.config_obj['header']['vdom'] == 1:
            global_key = 'global'
        else:
            global_key = 'root'

        for k, v in self.global_formatter.items():
            if k == 'base':
                self.parsed_obj['global'][k] = v.format(self.parsed_obj['header'])
                # v.format(self.parsed_obj['header'])
            else:
                self.parsed_obj['global'][k] = v.format(self.config_obj[global_key][k])

    def pre_format_config_obj(self, category_key):

        tmp_objects = []
        pre_fmt_objects = {}
        # multivdomとnovdomの構造の違いを吸収
        if self.config_obj['header']['vdom'] == 1:
            self.vdom_mode = 'multivdom'
            tmp_objects = self.config_obj['vdom']
        else:
            tmp_objects = [{'root': self.config_obj['root']}]

        for vdom_obj in tmp_objects:
            # vdom_name = list(vdom_obj.keys())[0]
            vdom_name = next(iter(vdom_obj.keys()))

            # vdom名のdict作っておく
            pre_fmt_objects.setdefault(vdom_name, {})
            # 設定が元々ない場合は空のオブジェクト作っておく
            vdom_obj[vdom_name].setdefault(category_key, {})
            # 対象カテゴリをコピー
            pre_fmt_objects[vdom_name][category_key] = vdom_obj[vdom_name][category_key]

        if self.debug:
            self.debug_print(pre_fmt_objects, 'pre_format.py')

        return pre_fmt_objects


if __name__ == '__main__':
    # config_file_path = './tmp/conf/7.2_novdom.conf'
    config_file_path = './tmp/conf/7.2_multivdom.conf'
    # config_file_path = r'C:\opt\work\tmp\paser_test_data\multi_vdom_test.conf'

    fcp = ConfigParser()
    fcp.config_load(config_file_path)
    # print(fcp.config_obj['header'])

    fcp.parse_header()

    fcp.parse_categories()

    from booya_config_parser.export.excel import ExportExcel
    ee = ExportExcel()
    ee.export_book(fcp.parsed_obj, fcp.field_names, fcp.global_field_names)

