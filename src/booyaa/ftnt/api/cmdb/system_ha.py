from urllib.parse import urljoin

class SystemHa:
    def __init__(self, api):
        self.api = api

    def get(self):
        url = urljoin(self.api.base_url, 'cmdb/system/ha')
        let = self.api.req(url, 'get')

        if let['code'] == 0:
            let['msg'] = f'get cmdb/system/ha {self.api.fg_addr}'
            pass
        else:
            let['msg'] = f'[Error] Fail get cmdb/system/ha {self.fg_addr}'

        return let
