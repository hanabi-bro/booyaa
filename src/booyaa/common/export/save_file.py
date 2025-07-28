import json
from pathlib import Path
from booyaa.common.timestamp import timestamp


def check_format(self, content):
    if isinstance(content, str):
        try:
            # JSONエラーになったらテキストと判定
            json.loads(content)
            return "json"
        except json.JSONDecodeError:
            # JSONでなければテキスト文字列とみなす
            return "text"
    elif isinstance(content, bytes):
        return "bin"
    else:
        return "unknown"


def save_config(content, fg_name, fg_alias, version, export_dir='./fg_config', format='bin'):
    major, minor, patch = version.split('.')

    if fg_alias:
        config_file_name = f'{fg_alias}_{fg_name}_{major}_{minor}_{patch}_{timestamp()}.conf'
    else:
        config_file_name = f'{fg_name}_{major}_{minor}_{patch}_{timestamp()}.conf'

    let = save_file(content, config_file_name, export_dir, format=format, encode='utf-8')

    return let


def save_file(content, export_name, export_dir='.', format=None, encode='utf-8'):
    """
    Args:
        content (binary): output of client.content
        format (str): json, text, bin,
        encode (str): utf-8

    Todo:
        エラーハンドリング
    """
    export_file_path = Path(export_dir, export_name)

    Path.mkdir(Path(export_dir), exist_ok=True)

    # オブジェクトのフォーマット判定
    if format is None:
        format = check_format(content)

    try:
        if format == json or format == 'text':
            with open(export_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format == 'bin':
            with open(export_file_path, 'wb') as f:
                f.write(content)
        else:
            with open(export_file_path, 'w') as f:
                f.write(content)
        code = 0
        msg = f'Config save to {Path(export_file_path).resolve()}'
        output = f'export_dir: {Path(export_dir).resolve()}'
    except Exception as e:
        code = 1
        msg = f'[Error] file_save Error {e}'
        output = e

    return {'code': code, 'msg': msg, 'output': output, 'trace': ''}

