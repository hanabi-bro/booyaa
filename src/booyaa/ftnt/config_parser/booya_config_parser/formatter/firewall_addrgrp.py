from copy import deepcopy


class FirewallAddrgrp:
    def __init__(self) -> None:
        self.field_names = {
            '__layout__':     {'layout': 'virtical', 'header_width': 25, 'value_witdh': 25, 'sheetname': 'address group', 'global': False},
            'name':           {'default_value': []},
            'comment':        {'default_value': []},
            'type':           {'default_value': []},
            'allow-routing':  {'default_value': []},
            "remark":         {'default_value': []},
            "member":         {'default_value': []},
            "exclude-member": {'default_value': []},
        }

    def format(self, addr_obj) -> list:
        mod_obj = []
        # [
        #   {'none': {'uuid': ['6a33b3c4-a701-51ef-74c9-aadedb00dbb9'], 'subnet': ['0.0.0.0', '255.255.255.255']}}
        # ]
        for line in addr_obj:
            obj_name = next(iter(line.keys()))
            tmp_line = deepcopy(line[obj_name])
            tmp_line.setdefault('type', ['default'])
            tmp_line.setdefault('category', [''])
            tmp_line.setdefault('member', [''])
            tmp_line.setdefault('comment', [''])
            tmp_line.setdefault('remark', [''])
            tmp_line.setdefault('allow-routing', ['disable'])
            tmp_line.setdefault('exclude', ['disable'])
            tmp_line.setdefault('member', [''])
            tmp_line.setdefault('exclude-member', [''])

            mod_line = {
                'name': obj_name,
                'comment': tmp_line['comment'],
                'type': tmp_line['type'],
                'allow-routing': tmp_line['allow-routing'],
                'remark': tmp_line['remark'],
                'member': tmp_line['member'],
                'exclude-member': tmp_line['exclude-member'],
            }

            mod_obj.append(mod_line)
        return mod_obj
