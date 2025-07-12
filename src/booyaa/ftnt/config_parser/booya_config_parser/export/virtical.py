from booya_config_parser.export import style

from pprint import pprint


def write_table(ws, row, vdom_name, category, config_obj, field_names) -> None:
    col = 1
    end_row = 0

    # テーブルヘッダ
    for r, field_name in enumerate(field_names, start=0):
        if field_name == '__layout__':
            continue

        ws = style.write_hedder_cell(
            ws, row+r, col, field_name,
            field_names['__layout__']['header_width'])

        end_row = row + r

    # テーブルデータ
    for col, param in enumerate(config_obj, start=col+1):
        for r, field_name in enumerate(field_names, start=0):
            if field_name == '__layout__':
                continue
            try:
                if isinstance(param[field_name], str):
                    cell_value = param[field_name]
                elif isinstance(param[field_name], list):
                    cell_value = '\n'.join(map(str, param[field_name]))
                else:
                    cell_value = str(param[field_name])

                ws = style.write_cell(ws, row+r, col, cell_value,
                    width=field_names['__layout__']['value_witdh'])

                end_row = row + r

            except KeyError as e:
                print(f'[error]: {e}')

    return ws, end_row
