from copy import deepcopy
from pprint import pprint


class Ha:
    def __init__(self) -> None:
        self.field_names = {
            '__layout__':     {'layout': 'virtical', 'header_width': 35, 'value_witdh': 25, 'sheetname': 'HA', 'global': True},
            'mode':                          {'width': 35, 'default_value': ['standalone']},
            'group-id':                      {'width': 35, 'default_value': ['']},
            'group-name':                    {'width': 35, 'default_value': ['']},
            'password':                      {'width': 35, 'default_value': ['']},
            'hbdev':                         {'width': 35, 'default_value': ['']},
            'monitor':                       {'width': 35, 'default_value': ['']},
            'override':                      {'width': 35, 'default_value': ['disable']},
            'priority':                      {'width': 35, 'default_value': ['120']},
            'sync-config':                   {'width': 35, 'default_value': ['enable']},
            'encryption':                    {'width': 35, 'default_value': ['disable']},
            'authentication':                {'width': 35, 'default_value': ['disable']},
            'session-pickup':                {'width': 35, 'default_value': ['disable']},
            'ha-mgmt-status':                {'width': 35, 'default_value': ['disable']},
            'ha-mgmt-interfaces':            {'width': 35, 'default_value': []},
        }

        self.ha_mgmt_interfaces = {
            '__layout__':     {'layout': 'horizontal', 'sheetname': 'HA', 'subtitle': 'Reserved Mgmt Interface','global': True},
            'id':                            {'width': 35, 'default_value': ['']},
            'interface':                     {'width': 35, 'default_value': ['']},
            'dst':                           {'width': 35, 'default_value': ['']},
            'gateway':                       {'width': 35, 'default_value': ['']},
            'gateway6':                      {'width': 35, 'default_value': ['']},
        }

    def format(self, addr_obj) -> list:
        mod_obj = []
        tmp_line = deepcopy(addr_obj)
        for k, v in self.field_names.items():
            if k == '__layout__':
                continue
            tmp_line.setdefault(k, v['default_value'])

        for param in tmp_line['ha-mgmt-interfaces']:
            num = next(iter(param))
            param[num]['id'] = num
            for k, v in self.ha_mgmt_interfaces.items():
                if k == '__layout__':
                    continue
                param[num].setdefault(k, v['default_value'])

        mod_line = tmp_line
        mod_obj.append(mod_line)

        return mod_obj
