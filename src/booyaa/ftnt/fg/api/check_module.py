from booyaa.ftnt.fg.api import FortiApi

from rich.console import Console
console = Console()
from traceback import format_exc
from urllib.parse import urljoin


if __name__ == '__main__':
    target = '172.16.201.201'
    user = 'admin'
    password = 'P@ssw0rd'

    api = FortiApi()
    api.set_target(
        '172.16.201.201',
        'admin',
        'P@ssw0rd'
    )
    api.login()
    let = api.monitor.switch_controller_managed_switch.get()

    with open('tmp/check_module_output.txt', 'w', encoding='utf-8') as f:
        from pprint import pprint
        pprint(let['output'], stream=f)

