from booyaa.ftnt.api import FortiApi

from rich.console import Console
console = Console()


class CheckApiResponse:
    def __init__(self):
        self.api = FortiApi()



if __name__ == '__main__':
    target = '172.16.201.201'
    user = 'admin'
    password = 'P@ssw0rd'

    ca = CheckApiResponse()
    capi = ca.api
    capi.set_target(
        '172.16.201.201',
        'admin',
        'P@ssw0rd'
    )
    capi.login()
    # print(capi.cmdb.system_ha.get())
    print(capi.ha_mgmt_status)
    print(capi.ha_mgmt_interfaces)
    capi.logout()

