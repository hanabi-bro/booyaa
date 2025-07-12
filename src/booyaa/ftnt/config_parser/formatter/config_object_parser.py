from pathlib import Path
from copy import deepcopy
from csv import DictReader
from rich import print

class ConfigObjectParser:
    def __init__(self) -> None:
        self.current_path = Path(__file__).parent
        self.data_dir = Path(self.current_path, '..', 'data')
        # self.data_dir = Path(self.current_path, 'data')
        self.global_formt_dir = Path(self.data_dir, 'global')
        self.vdom_formt_dir = Path(self.data_dir, 'vdom')

    def load_rule(self, category, obj_type) -> None:

        if obj_type == 'global':
            format_rule_csv = Path(self.data_dir, r'format_rule_global.csv')
            category_csv_path = Path(self.global_formt_dir, f'{category}.csv')

        elif obj_type == 'vdom':
            format_rule_csv = Path(self.data_dir, r'format_rule_vdom.csv')
            category_csv_path = Path(self.vdom_formt_dir, f'{category}.csv')

        with open(format_rule_csv, 'r', encoding='utf-8') as f:
            self.format_rule = next(iter([row for row in list(DictReader(f)) if row['category'] == category]))

        with open(category_csv_path, 'r', encoding='utf-8') as f:
            self.field_rule = list(DictReader(f))


    def parse(self, config_block_name, config_obj, category, obj_type) -> dict|list:
        """_summary_

        Args:
            config_block_name (str): _description_
            config_obj (_type_): _description_
            category (str): _description_
            obj_type (str): 'global' or 'vdom', (global config type or vdom config type)

        Returns:
            dict|list: _description_
        """
        category_config_obj = deepcopy(config_obj)

        # カテゴリーに対応するルールをロード
        self.load_rule(category, obj_type)

        if self.format_rule['plural'] == 'single':
            parse_result = self.single_parse(config_block_name, category_config_obj, category)

        elif self.format_rule['plural'] == 'multi':
            parse_result = self.multi_parse(config_block_name, category_config_obj, category)

        return parse_result

    def single_parse(self, config_block_name, config_obj, category) -> dict:
        # self.load_rule(category)
        category_config_obj = deepcopy(config_obj)

        for rule in self.field_rule:
            category_config_obj.setdefault(rule['config_name'], rule['default_value'])
            rule['view_key'] = rule['config_name']

        # print(category_config_obj)
        return category_config_obj

    def multi_parse(self, config_block_name, config_obj, category) -> list:
        # self.load_rule(category)
        category_config_obj = deepcopy(config_obj)

        for row in category_config_obj:
            eid = next(iter(row))
            row[eid]['eid'] = eid
            for rule in self.field_rule:
                row[eid].setdefault(rule['config_name'], rule['default_value'])
                rule['view_key'] = rule['config_name']

        return category_config_obj
