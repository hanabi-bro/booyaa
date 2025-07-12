from booya_config_parser.export import style

from pprint import pprint


def write_table(ws, row, vdom_name, category, config_obj, field_names):
    """通常のテーブル上のレイアウト
    Address, Firewall Policyなど

    Args:
        ws (_type_): _description_
        row (_type_): _description_
        vdom_name (_type_): _description_
        category (_type_): _description_
        config_obj (_type_): _description_
        field_names (_type_): _description_
    """
    with open('./tmp/log/excel_config_obj.py', 'w', encoding='utf-8') as f:
        pprint(config_obj, stream=f)
    end_row = None

    # テーブルヘッダ
    for col, field_name in enumerate(field_names, start=0):
        if field_name == '__layout__':
            continue
        ws = style.write_hedder_cell(
            ws, row, col, field_name,
            field_names[field_name]['width'])
        end_row = row

    # テーブルデータ
    for r, param in enumerate(config_obj, start=row + 1):
        for col, field_name in enumerate(field_names, start=0):
            if field_name == '__layout__':
                continue
            try:
                if isinstance(param[field_name], str):
                    cell_value = param[field_name]
                elif isinstance(param[field_name], list):
                    cell_value = '\n'.join(map(str, param[field_name]))
                else:
                    cell_value = str(param[field_name])

                ws = style.write_cell(ws, r, col, cell_value)
                end_row = r

            except KeyError as e:
                print(f'[error]: {e}')

    return ws, end_row
