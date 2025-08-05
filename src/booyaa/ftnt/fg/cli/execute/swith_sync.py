from re import search

class SwitchControllerGetSyncStatus:
    fsw_list: list
    fsw_info: dict
    # {
    #     'name': sw['name'],
    #     'serial': sw['serial'],
    #     'status': sw['status'],
    #     'ip_addr': sw['connecting_from'],
    #     'state': sw['state'],
    # }



    def __init__(self, api):
        self.api = api
        # S224ENTF18000490  v7.4.3 (830)      Authorized/Up   -   10.255.1.1      Mon Jul 28 17:42:23 2025    -
        # S224EPTF20005577  v7.4.3 ()         Discovered/Down -   0.0.0.0         N/A                         -
        r'(\w+)\s+v(\d+\.\d+\.\d+)\s+(\d+)\s+(\w+)/(\w+).*(\d+\.\d+\.\d+\.\d+)'

    def get(self):
        cmd = 'execute switch-controller get-sync-status all'
        res = self.api.execute_command(cmd)

        if res['code'] != 0:
            return res


        return res

