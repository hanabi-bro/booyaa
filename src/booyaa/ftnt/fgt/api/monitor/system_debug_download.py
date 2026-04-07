from urllib.parse import urljoin

class SystemDebugDownload:
    def __init__(self, api):
        self.api = api

    def get(self, dest='file', format='fos', scope='global', timeout=600):
        api_path =  'monitor/system/debug/download/'
        url = urljoin(self.api.base_url, api_path)

        params = {
            # 'destination': 'file',
            # 'file_format': 'fos',
            'scope': scope
        }

        kwargs = {
            'method': 'get',
            'params': params,
            'req_format': 'data',
            'res_format': 'bin',
            'timeout': timeout or 600
        }

        # if self.api.fgt_info.version >= '7.6.0':
        #     kwargs = {
        #         'method': 'post',
        #         'params': params,
        #         'req_format': 'data',
        #         'res_format': 'bin'
        #     }
        # else:
        #     kwargs = {
        #         'method': 'get',
        #         'params': params,
        #         'req_format': 'json',
        #         'res_format': 'bin'
        #     }

        let = self.api.req(url, **kwargs)

        return let

