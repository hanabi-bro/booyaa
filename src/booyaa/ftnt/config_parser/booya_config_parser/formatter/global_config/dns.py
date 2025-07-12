from copy import deepcopy
from pprint import pprint

class Dns:
    def __init__(self):
        self.field_names = {
            '__layout__':     {'layout': 'virtical', 'header_width': 25, 'value_witdh': 25, 'sheetname': 'dns', 'global': True},
            'primary':                 {'width': 35, 'default_value': []},
            'secondary':               {'width': 15, 'default_value': []},
            'protocol':                {'width': 15, 'default_value': ['cleartext']},
            'server-hostname':         {'width': 15, 'default_value': ['']},
            'ssl-certificate':         {'width': 30, 'default_value': ['Fortinet_Factory']},
            'timeout':                 {'width': 30, 'default_value': ['5']},
            'retry':                   {'width': 30, 'default_value': ['2']},
            'dns-cache-limit':         {'width': 30, 'default_value': ['5000']},
            'dns-cache-ttl':           {'width': 30, 'default_value': ['1800']},
            'source-ip':               {'width': 30, 'default_value': ['']},
            'cache-notfound-responses':{'width': 30, 'default_value': ['disable']},
            'interface-select-method': {'width': 30, 'default_value': ['auto']},
            'server-select-method':    {'width': 30, 'default_value': ['least-rtt']},
            'alt-primary':             {'width': 30, 'default_value': ['0.0.0.0']},
            'alt-secondary':           {'width': 30, 'default_value': ['0.0.0.0']},
            'log':                     {'width': 30, 'default_value': ['disable']},
            'fqdn-cache-ttl':          {'width': 30, 'default_value': ['0']},
            'fqdn-min-refresh':        {'width': 30, 'default_value': ['60']},
        }

    def format(self, addr_obj):
        mod_obj = []
        # [
        #   {'none': {'uuid': ['6a33b3c4-a701-51ef-74c9-aadedb00dbb9'], 'subnet': ['0.0.0.0', '255.255.255.255']}}
        # ]
        tmp_line = deepcopy(addr_obj)
        for k, v in self.field_names.items():
            if k == '__layout__':
                continue
            tmp_line.setdefault(k, v['default_value'])

        mod_line = tmp_line
        mod_obj.append(mod_line)

        return mod_obj
