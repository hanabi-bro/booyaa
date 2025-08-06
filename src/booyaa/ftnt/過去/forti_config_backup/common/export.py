from datetime import datetime
from pathlib import Path


def timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

class Export:
    def __init__(self):
        """"""

    def save_file(self, backup_dir, config_text, fg_name, version, alias=None):
        major, minor, patch = version.split('.')

        if alias:
            file_name = f'{alias}_{fg_name}_{major}_{minor}_{patch}_{timestamp()}.conf'
        else:
            file_name = f'{fg_name}_{major}_{minor}_{patch}_{timestamp()}.conf'

        Path.mkdir(Path(backup_dir), exist_ok=True)
        config_file_path = Path(backup_dir, file_name)

        with open(config_file_path, 'w', encoding='utf-8') as f:
            f.write(config_text)
        code = 0
        msg = f'Config save to {Path(config_file_path).resolve()}'
        output = f'backup_dir: {Path(backup_dir).resolve()}'

        return {'code': code, 'msg': msg, 'output': output}

