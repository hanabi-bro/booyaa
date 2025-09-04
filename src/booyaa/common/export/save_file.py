import json
from pathlib import Path
from booyaa.common.timestamp import timestamp

from traceback import format_exc


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


def save_config(content, hostname, alias, version, export_dir='./fg_config', format='bin', encode='utf-8'):
    major, minor, patch = version.split('.')

    if alias:
        config_file_name = f'{alias}_{hostname}_{major}_{minor}_{patch}_{timestamp()}.conf'
    else:
        config_file_name = f'{hostname}_{major}_{minor}_{patch}_{timestamp()}.conf'

    let = save_file(content, config_file_name, export_dir, format=format, encode=encode)

    return let


def save_msw_config(content, hostname='', alias='', version='', export_dir='./fg_config', format='text', encode='utf-8'):
    # MSW用にペアレントのFGのaliasかホスト名フォルダを作成
    backup_dir = Path(export_dir, alias or hostname )

    config_file_name = f'{hostname}_{timestamp()}.conf'
    if version:
        try:
            major, minor, patch = version.split('.')
            config_file_name = f'{hostname}_{major}_{minor}_{patch}_{timestamp()}.conf'
        except:
            config_file_name = f'{hostname}_{timestamp()}.conf'

    let = save_file(content, config_file_name, export_dir, format=format, encode=encode)

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

    Path.mkdir(Path(export_dir), parents=True, exist_ok=True)

    # オブジェクトのフォーマット判定
    if format is None:
        format = check_format(content)

    try:
        if format == json or format == 'text':
            with open(export_file_path, 'w', encoding=encode) as f:
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
        msg = f'[Error] file_save Error {format_exc()}'
        output = ''

    return {'code': code, 'msg': msg, 'output': output, 'trace': ''}


