from copy import deepcopy


class Interface:
    def __init__(self):
        self.field_names = {
            '__layout__':     {'layout': 'simple', 'sheetname': 'address', 'global': True},
            'name':           {'width': 35, 'default_value': []},
            'status':         {'width': 15, 'default_value': []},
            'alias':          {'width': 15, 'default_value': []},
            'role':           {'width': 15, 'default_value': ['']},
            'mode':           {'width': 30, 'default_value': ['static']},
            'ip':             {'width': 30, 'default_value': ['']},
            'addr_obj':       {'width': 15, 'default_value': ['']},
            'dhcp_server':    {'width': 15, 'default_value': ['']},
            'device-identification':    {'width': 15, 'default_value': ['disable']},
            'security-mode':  {'width': 15, 'default_value': ['']},

        }
