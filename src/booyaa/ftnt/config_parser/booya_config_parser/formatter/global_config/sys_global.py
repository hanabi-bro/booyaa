from copy import deepcopy
from pprint import pprint


# @TODO timezoneが設置されていない
class Global():
    def __init__(self) -> None:
        self.field_names = {
            '__layout__':     {'layout': 'virtical', 'header_width': 35, 'value_witdh': 25, 'sheetname': 'global', 'global': True},
            'management-vdom':                          {'width': 35, 'default_value': ['root']},
            'vdom-mode':                                {'width': 35, 'default_value': ['no-vdom']},
            'timezone':                                 {'width': 35, 'default_value': ['']},
            'virtual-switch-vlan':                      {'width': 35, 'default_value': ['disable']},
            'wireless-controller':                      {'width': 35, 'default_value': ['enable']},
            'switch-controller':                        {'width': 35, 'default_value': ['disable']},
            'gui-display-hostname':                     {'width': 35, 'default_value': ['disable']},
            'admin-scp':                                {'width': 35, 'default_value': ['disable']},
            'admintimeout':                             {'width': 35, 'default_value': ['5']},
            'gui-auto-upgrade-setup-warning':           {'width': 35, 'default_value': ['disable']},
            'gui-forticare-registration-setup-warning': {'width': 35, 'default_value': ['enable']},
            'set admin-reset-button':                   {'width': 35, 'default_value': ['enable']},
            'daily-restart':                            {'width': 35, 'default_value': ['disable']},
            'restart-time':                             {'width': 35, 'default_value': ['00:00:00']},
        }

    def format(self, addr_obj) -> list:
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
