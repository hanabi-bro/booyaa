import yaml
import json
import sys
from collections import OrderedDict

from booya_config_parser.config_to_yaml import config_file_load, config_to_yaml


def config_to_obj(config_file_path, debug=True, logpath='./tmp/log'):
    print('loading config file')
    pre_parsed_lines = config_file_load(config_file_path)
    print('end loading')
    print('reformating config to yaml')
    config_yaml_lines = config_to_yaml(pre_parsed_lines)
    print('end to yaml')
    print('parse yamled config')
    config_yaml_str = '\n'.join(config_yaml_lines)

    # 順序を保持して読み込む
    yaml.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        lambda loader,
        node: OrderedDict(loader.construct_pairs(node))
    )
    config_obj = yaml.safe_load(config_yaml_str)
    print('end parse yamled config')

    if debug:
        import os
        os.makedirs(logpath, exist_ok=True)

        yaml_name = 'yamled.yaml' if config_obj['header']['vdom'] == 0 else 'multi_yamled.yaml'
        yaml_file_path = os.path.join(logpath, yaml_name)
        with open(yaml_file_path, 'w', encoding='utf-8_sig') as f:
            print(config_yaml_str, file=f)

        json_name = 'jsoned.json' if config_obj['header']['vdom'] == 0 else 'multi_jsoned.json'
        json_file_path = os.path.join(logpath, json_name)
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_obj, f, ensure_ascii=False, indent=2)

    return config_obj


if __name__ == '__main__':
    # config_file_path = 'tmp/conf/7.2_novdom.conf'
    config_file_path_list = [
        'tmp/conf/7.2_novdom.conf',
        'tmp/conf/7.2_multivdom.conf',
    ]
    for config_file_path in config_file_path_list:
        config_obj = config_to_obj(config_file_path, debug=True)



