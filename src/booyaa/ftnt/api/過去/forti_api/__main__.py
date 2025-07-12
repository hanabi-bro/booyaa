from forti_api import FortiApi

from rich.console import Console
console = Console()

if __name__ == '__main__':
    fa = FortiApi()
    targets = [
        [
            '172.16.201.201',
            'admin',
            'P@ssw0rd',
            ''
        ],
        [
            '172.16.201.202',
            'admin',
            'P@ssw0rd',
            ''
        ],
    ]

    for t in targets:
        res = fa.set_target(*t)
        if res['code'] == 0:
            console.print(f'set target {t[0]}')
        else:
            console.print(f'Error! set_target {res['trace']} \nmsg:{res['msg']}\ncode: {res['code']}\noutput: {res['output']}')
            continue

        res = fa.login()
        if res['code'] == 0:
            console.print(f'login {t[0]}, {res['cookie']}')
            console.print(res['output'])
        else:
            console.print(f'Error! login {res['trace']} \nmsg:{res['msg']}\ncode: {res['code']}\noutput: {res['output']}')
            continue

        # res = fa.monitor.system_csf.get()
        # res = fa.get_node_info()
        # if res['code'] == 0:
        #     console.print(f'get node info {t[0]}, hostname: {fa.hostname}, {res['cookie']}')
        # else:
        #     console.print(f'Cookei: {res['cookie']}')
        #     console.print(f'Error! get node info {res['trace']} \nmsg:{res['msg']}\ncode: {res['code']}\noutput: {res['output']}')
        #     continue

        res = fa.monitor.system_config_backup.get()
        if res['code'] == 0:
            console.print(f'get backup {t[0]}, hostname: {fa.hostname}, {res['cookie']}')
            console.print(res['output'])
        else:
            console.print(f'Cookei: {res['cookie']}')
            console.print(f'Error! get backup {res['trace']} \nmsg:{res['msg']}\ncode: {res['code']}\noutput: {res['output']}')
            continue

        from forti_api.export.save_file import save_config
        # def save_config(self, content, fg_name, fg_alias, version, export_dir='./fg_config'):

        res = save_config(res['output'], fa.hostname, fa.fg_alias, fa.version, './fg_config')
        if res['code'] == 0:
            console.print(f'save backup {t[0]}, hostname: {fa.hostname}')
            console.print(res['output'], res['msg'])
        else:
            console.print(f'Error! save backup {res['trace']} \nmsg:{res['msg']}\ncode: {res['code']}\noutput: {res['output']}')
            continue

        res = fa.logout()
        if res['code'] == 0:
            console.print(f'logout from {t[0]}')
        else:
            console.print(f'Cookei: {res['cookie']}')
            console.print(f'Error! logout {res['trace']} \nmsg:{res['msg']}\ncode: {res['code']}\noutput: {res['output']}')
            continue
