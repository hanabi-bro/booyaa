from booyaa.ftnt.fg.api import FortiApi
import json


from rich.console import Console
console = Console()
from traceback import format_exc
from urllib.parse import urljoin

class CheckApiResponse:
    def __init__(self):
        self.api = FortiApi()
    
    def setup(self, addr, user, password):
        self.api.set_target(
            '172.16.201.201',
            'admin',
            'P@ssw0rd'
        )

    def check(
            self,
            api_path: str,
            method: str = 'post', # post | get
            params: dict | None = None,
            req_format: str = 'json',  # json | data
            res_format: str = 'json',  # json | text | bin
            timeout: float | None = None
        ):
        url = urljoin(self.api.base_url, api_path)

        params = {
            'scope': 'global'
        }

        kwargs = {
            'method': 'get',
            'params': params,
            'req_format': 'data',
            'res_format': 'json'
        }


        # kwargs = {
        #     'method': method,
        #     'params': params,
        #     'req_format': 'json',
        #     'res_format': 'json'
        # }

        let = self.api.login(node_info=False)
        let = self.api.req(url, **kwargs)
        if let['code'] != 0:
            return let
        # try:
        # let = self.api.req(
        #     url,
        #     method,
        #     params,
        #     req_format,
        #     res_format,
        #     timeout,
        # )
        # except Exception as e:
            # let['msg'] = format_exc()
            # print(format_exc())
        # finally:
        self.api.logout()
        return let

if __name__ == '__main__':
    target = '172.16.201.201'
    user = 'admin'
    password = 'P@ssw0rd'

    ca = CheckApiResponse()
    ca.setup(
        '172.16.201.201',
        'admin',
        'P@ssw0rd'
    )
    api_path = 'monitor/system/csf'
    let = ca.check(
        api_path=api_path,
        method='get,'
    )

    with open('tmp/check_uri_output.txt', 'w', encoding='utf-8') as f:
        from pprint import pprint
        pprint(let['output'], stream=f)

