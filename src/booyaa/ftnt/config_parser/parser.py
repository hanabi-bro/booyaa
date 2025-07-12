#! python
from pathlib import Path
import json
from logging import basicConfig, getLogger, DEBUG, FileHandler
from rich.logging import RichHandler
from rich import print
from csv import DictReader
from config_parser.formatter.config_object_parser import ConfigObjectParser
from config_parser.formatter.firewall_policy import FirewallPolicy
from config_parser.formatter.firewall_address import FirewallAddress

# ログ設定
def setup_logger() -> getLogger:
    basicConfig(
        level=DEBUG,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(rich_tracebacks=True),
            # logging.FileHandler("app.log", mode="w", encoding="utf-8")
        ],
    )
    return getLogger(__name__)


log = setup_logger()


class Formatter:
    def __init__(self) -> None:
        """"""
        self.config_obj = ''
        self.vdom_mark = 'vdom'
        self.global_mark = 'global'
        self.formatted_config = {'header': {}, 'global': {}, 'vdom': {}}
        self.current_path = Path(__file__).parent
        self.rule_dir = Path(self.current_path, 'data')

    def json_load(self, json_path) -> None:
        with open(json_path, 'r', encoding='utf-8') as f:
            self.config_obj = json.load(f)

        self.check_base_info()

    def check_base_info(self) -> None:
        self.base_info = self.config_obj['header']
        # no-vdomの場合、globalもroot配下になっている
        if self.config_obj['header']['vdom'] == 0:
            self.vdom_mark = 'root'
            self.global_mark = 'root'
        # multivdomのvdomの場合
        elif self.config_obj['header']['vdom'] == 1:
            self.vdom_mark = 'vdom'
            self.global_mark = 'global'
        # 未実装、6.2とかであったmanagement-vdom構成(2)などは今のところ未サポート
        else:
            self.vdom_mark = 'vdom'
            self.global_mark = 'global'

        # FGT60F-7.2.10-FW-build1706-240918
        _ver_info = self.base_info['config-version'].split('-', 3)

        self.base_info['model'] = _ver_info[0]
        self.base_info['version'] = _ver_info[1]
        self.base_info['majore'], self.base_info['minor'], self.base_info['patch'] = _ver_info[1].split('.')
        self.base_info['build_num'] = _ver_info[3]

        self.formatted_config['header']['model'] = _ver_info[0]
        self.formatted_config['header']['version'] = _ver_info[1]
        self.formatted_config['header']['majore'], self.formatted_config['header']['minor'], self.formatted_config['header']['patch'] = _ver_info[1].split('.')
        self.formatted_config['header']['build_num'] = _ver_info[3]

        # vdom mode
        self.formatted_config['header']['vdom_mode']= self.config_obj[self.global_mark]['system_global']['vdom-mode'][0]

        # hostname
        self.formatted_config['header']['hostname'] = self.config_obj[self.global_mark]['system_global']['hostname'][0]

    def global_parse(self) -> None:
        format_rule_global_csv = Path(self.rule_dir, r'format_rule_global.csv')
        with open(format_rule_global_csv, 'r', encoding='utf-8') as f:
            self.format_rule_global = list(DictReader(f))

        global_config_obj = self.config_obj[self.global_mark]
        formatted_global_obj = self.formatted_config['global']

        for row in self.format_rule_global:
            category = row['category']
            try:
                if row['parser'] == 'ConfigObjectParser':
                    global_parser = ConfigObjectParser()
                else:
                    global_parser = ConfigObjectParser()

                # カテゴリーキーが存在しない場合は空の値を追加
                if category in global_config_obj:
                    formatted_global_obj[category] = global_parser.parse(
                        self.global_mark, global_config_obj[category], category, 'global'
                    )
                else:
                    formatted_global_obj[category] = ''

            except Exception as e:
                log.exception()
                exit()

        # formatted_global_obj = {
        #     row['category']: global_parser.parse(self.global_mark, global_config_obj[row['category']], row['category'], 'global')
        #     for row in self.format_rule_global
        # }

    def vdom_parse(self) -> None:
        format_rule_vdom_csv = Path(self.rule_dir,  r'format_rule_vdom.csv')
        with open(format_rule_vdom_csv, 'r', encoding='utf-8') as f:
            self.format_vdom_rule = list(DictReader(f))

        vdom_config_obj = self.config_obj[self.vdom_mark]
        formatted_vdom_obj = self.formatted_config['vdom']

        for vdom_obj_dict in vdom_config_obj:
            vdom_name = next(iter(vdom_obj_dict))
            vdom_obj = vdom_obj_dict[vdom_name]
            formatted_vdom_obj[vdom_name] = {}


            for row in self.format_vdom_rule:
                category = row['category']
                if row['parser'] == 'FirewallPolicy':
                    vdom_parser = FirewallPolicy()
                elif row['parser'] == 'FirewallAddress':
                    vdom_parser = FirewallAddress()
                else:
                    vdom_parser = ConfigObjectParser()

                # カテゴリーキーが存在しない場合は空の値を追加
                if category in vdom_obj:
                    formatted_vdom_obj[vdom_name][category] = vdom_parser.parse(
                        vdom_name, vdom_obj[category], category, 'vdom'
                    )
                else:
                    formatted_vdom_obj[vdom_name][category] = ''
            # formatted_vdom_obj[vdom_name] = {
            #     row['category']: vdom_parser.parse(vdom_name, vdom_obj[row['category']], row['category'], 'vdom')
            #     for row in self.format_vdom_rule
            # }


if __name__ == '__main__':
    current_path = Path(__file__).parent
    # json_path = Path(current_path, 'log', 'multi_jsoned.json')
    json_path = r'C:\opt\work\phy\booya_config_parser\tmp\log\multi_jsoned.json'

    ft = Formatter()
    ft.json_load(json_path)
    ft.global_parse()
    ft.vdom_parse()

    import json
    with open('new_parser_vdom.json', 'w', encoding='utf-8') as f:
        json.dump(ft.formatted_config, f, indent=2)

    # from config_parser.export.excel import ExportExcel
    # excel = ExportExcel()
    # excel.export(ft.formatted_config)
