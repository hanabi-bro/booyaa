from datetime import datetime
from pathlib import Path

def gen_timestamp() -> str:
    """Generate a timestamp string in the format YYYYMMDD_HHMMSS."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def gen_backup_filename(hostname: str, version: str = None, alias: str = None) -> str:
    timestamp = f'_{gen_timestamp()}'
    version_str = f'_{version}' or ''
    alias_str = f'{alias}_' or ''

    return f'{alias_str}{hostname}{version_str}{timestamp}.conf'

def save_file(
        directory: str,
        hostname: str,
        content: str,
        version: str = None,
        alias: str = None,
        ) -> None:

    file_name = gen_backup_filename(hostname, version, alias)
    Path.mkdir(directory, exist_ok=True)
    file_path = Path(directory, file_name).resolve()
    try:
        with open(file_path, 'w', encoding='utf8') as file:
            file.write(content)
        flg = True
        msg = f'{file_path}'
    except Exception as e:
        flg = False
        msg = f'Error: {e}'

    return flg, msg
