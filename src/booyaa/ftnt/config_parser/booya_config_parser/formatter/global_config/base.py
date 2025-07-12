#! python
from copy import deepcopy


class Base:
    def __init__(self) -> None:
        self.field_names = {
            '__layout__':     {'layout': 'virtical', 'header_width': 25, 'value_witdh': 25, 'sheetname': 'base', 'global': True},
            'model':          {'width': 35, 'default_value': []},
            'hostname':       {'width': 35, 'default_value': []},
            'version':        {'width': 15, 'default_value': []},
            'operation_mode': {'width': 15, 'default_value': ['nat']},
            'vdom_mode':      {'width': 15, 'default_value': ['']},
        }

    def format(self, header_obj) -> list:
        mod_obj = []
        # [
        #   {'none': {'uuid': ['6a33b3c4-a701-51ef-74c9-aadedb00dbb9'], 'subnet': ['0.0.0.0', '255.255.255.255']}}
        # ]
        tmp_line = deepcopy(header_obj)

        mod_line = {
            'model':             tmp_line['model'],
            'hostname':          tmp_line['hostname'],
            'version':           tmp_line['version'],
            'operation_mode':    tmp_line['operation_mode'],
            'vdom_mode':         tmp_line['vdom_mode'],
        }

        mod_obj.append(mod_line)
        return mod_obj


if __name__ == '__main__':
    pass
