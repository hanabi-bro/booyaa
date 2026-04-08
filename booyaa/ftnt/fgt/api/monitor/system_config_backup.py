from urllib.parse import urljoin

class SystemConfigBackup:
    def __init__(self, api):
        self.api = api

    def get(self, dest='file', format='fos', scope='global'):
        api_path =  'monitor/system/config/backup'
        url = urljoin(self.api.base_url, api_path)

        params = {
            'destination': 'file',
            'file_format': 'fos',
            'scope': scope
        }

        if self.api.fgt_info.version >= '7.6.0':
            kwargs = {
                'method': 'post',
                'params': params,
                'req_format': 'data',
                'res_format': 'bin'
            }
        else:
            kwargs = {
                'method': 'get',
                'params': params,
                'req_format': 'json',
                'res_format': 'bin'
            }

        let = self.api.req(url, **kwargs)

        return let

