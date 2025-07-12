import re
import shlex
from logging import getLogger, DEBUG, INFO

logger = getLogger("config_to_yaml")
logger.setLevel(INFO)


def config_file_load(file_path, encode='utf-8_sig') -> list:
    """_summary_

    Args:
        file_path (_type_): _description_
        encode (_type_): _description_
    """
    tmp_line = ''
    multi_line_flg = False
    mod_config_list = []

    with open(file_path, 'r', encoding=encode) as f:
        for i, l in enumerate(f):
            ls = l.rstrip('\r\n')
            if multi_line_flg:
                tmp_line += ls
                # 末尾が「\"」ではなく、「"」だった場合はマルチライン終了判定
                if not ls.endswith(r'\"') and ls.endswith(r'"'):
                    multi_line_flg = False
                else:
                    continue
            else:
                tmp_line = ls

            try:
                shlex.split(tmp_line)
                mod_config_list.append(tmp_line)
            except ValueError as e:
                multi_line_flg = True
                if str(e) != 'No closing quotation':
                    logger.exception('value_error')

            except Exception:
                logger.exception('Unknown Error')

        return mod_config_list


def count_indent_level(line) -> int:
    match = re.match(r"^(\s*)", line)
    if match:
        return len(match.group(1)) // 4
    return 0


def parse_header(line) -> list:
    parts = re.split(':', re.sub('^#', '', line))
    parsed_line = []
    for word in parts:
        val = re.split('=', word)
        parsed_line.append(f'  {val[0]}: {val[1]}')
    return parsed_line


def config_to_yaml(config_list) -> list:
    yamled_config_list = ['header:']
    parent = ''
    config_vdom_count = 0
    mod_indent = 2

    vdom_mode = 'multi_vdom'

    for i, l in enumerate(config_list):

        strip_l = l.strip()
        array_l = shlex.split(strip_l)

        orig_space_count = len(l) - len(l.lstrip())
        orig_indent = 0 if orig_space_count == 0 else int(orig_space_count / 2)

        ## Header
        if l.startswith('#'):
            # novdom判定
            if re.search(r':vdom=0:', l):
                vdom_mode = 'novdom'

            headres_parmas = parse_header(l)
            for params in headres_parmas:
                yamled_config_list.append(params)

        # 空白行はスキップ
        elif l == '':
            continue

        # novdomの場合
        elif l == 'config system global':
            if vdom_mode == 'novdom':
                yamled_config_list.append('root:')

            yamled_config_list.append(f'{" " * orig_indent}{" " * mod_indent}{'_'.join(array_l[1:])}:')

        elif re.match('config vdom', strip_l):
            parent = 'vdom'
            mod_indent = 2
            if config_vdom_count < 2:
                yamled_config_list.append(f'{array_l[1]}:')
            config_vdom_count += 1

        elif re.match('config global', strip_l):
            yamled_config_list.append(f'{array_l[1]}:')
            parent = 'global'
            mod_indent = 2

        # vdom名のeditの場合の処理
        elif array_l[0] == 'edit' and parent == 'vdom' and orig_indent == 0:
            yamled_config_list.append(f'  - {array_l[1]}:')
            mod_indent = 6

        # vdom名以外のedit
        elif array_l[0] == 'edit':
            yamled_config_list.append(f'{" " * orig_indent}{" " * mod_indent}- "{'_'.join(array_l[1:])}":')
            mod_indent = mod_indent + 2

        elif strip_l == 'next':
            mod_indent = mod_indent - 2
        elif strip_l == 'end':
            continue

        elif array_l[0] == 'set':
            # コメント、バッファの場合yamlの制御文字が入る場合があるので、リテラルスカラーを利用する
            if array_l[1] == 'comment' or array_l[1] == 'buffer':
                yamled_config_list.append(f'{" " * orig_indent}{" " * mod_indent}{array_l[1]}: |')
                yamled_config_list.append(f'{" " * orig_indent}{" " * mod_indent}  {array_l[2]}')
            else:
                yamled_config_list.append(f'{" " * orig_indent}{" " * mod_indent}{array_l[1]}: {array_l[2:]}')

        elif array_l[0] == 'unset':
            yamled_config_list.append(f'{" " * orig_indent}{" " * mod_indent}{array_l[1]}: ~')

        elif array_l[0] == 'config':
            yamled_config_list.append(f'{" " * orig_indent}{" " * mod_indent}{'_'.join(array_l[1:])}:')

        else:
            logger.info('unsupport')
            logger.debug(l)

    return yamled_config_list


if __name__ == '__main__':
    # file_path = r'tmp/conf/7.2_novdom.conf'
    file_path = r'tmp/conf/7.2_multivdom.conf'
    # file_path = r'tmp/conf/NEPNWFW01_7-0_0523_202307191702.conf'
    logger.setLevel(DEBUG)
    pre_parsed_lines = config_file_load(file_path)
    yamled_lines = config_to_yaml(pre_parsed_lines)

