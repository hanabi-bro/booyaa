from urllib.parse import urljoin

class SystemHaStatistics:
    def __init__(self, api):
        self.api = api

    def get(self, scope='global'):
        api_path =  'monitor/system/ha-statistics'
        url = urljoin(self.api.base_url, api_path)

        params = {
            'scope': scope
        }

        kwargs = {
            'method': 'get',
            'params': params,
            'req_format': 'json',
            'res_format': 'json'
        }

        let = self.api.req(url, **kwargs)

        return let


"""fos7.0
{
  "http_method":"GET",
  "results":[
    {
      "hostname":"FG60F-Primary",
      "serial_no":"FGT60FTK20099VM6",
      "tnow":20858,
      "sessions":21,
      "tpacket":341525,
      "vir_usage":0,
      "net_usage":18,
      "tbyte":144913368,
      "intr_usage":0,
      "cpu_usage":0,
      "mem_usage":61,
      "per_vdom_stats":[
        {
          "vdom":"root",
          "cpu_usage":0,
          "mem_usage":43,
          "sessions":11
        }
      ],
      "uptime":11656
    },
    {
      "hostname":"FG60F-Secondary",
      "serial_no":"FGT60FTK20011089",
      "tnow":6674,
      "sessions":10,
      "tpacket":162,
      "vir_usage":0,
      "net_usage":16,
      "tbyte":29125,
      "intr_usage":0,
      "cpu_usage":0,
      "mem_usage":56,
      "per_vdom_stats":[
        {
          "vdom":"root",
          "cpu_usage":0,
          "mem_usage":40,
          "sessions":0
        }
      ],
      "uptime":11651
    }
  ],
  "vdom":"root",
  "path":"system",
  "name":"ha-statistics",
  "action":"",
  "status":"success",
  "serial":"FGT60FTK20099VM6",
  "version":"v7.0.17",
  "build":682
}                                                                                                                                                                                                            ✓
"""