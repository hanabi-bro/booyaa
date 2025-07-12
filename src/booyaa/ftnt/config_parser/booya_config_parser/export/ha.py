from booya_config_parser.export import style, virtical, horizontal_sub
from booya_config_parser.formatter.global_config.ha import Ha
from pprint import pprint
from copy import deepcopy

ha = Ha()

def write_table(ws, row, vdom_name, category, config_obj, field_names):

    sub_filed_name01 = 'ha-mgmt-interfaces'
    tmp_field_names = deepcopy(field_names[category])
    tmp_field_names.pop(sub_filed_name01)


    # 基本パラメータ
    ws, row = virtical.write_table(
        ws, row, vdom_name, category,
        config_obj[vdom_name][category],
        tmp_field_names)

    row = row + 2
    # 管理インタフェース
    ws, row = horizontal_sub.write_table(
        ws, row, vdom_name, category,
        config_obj[vdom_name][category][0][sub_filed_name01],
        ha.ha_mgmt_interfaces)


    # 管理インタフェース
    return ws, row
