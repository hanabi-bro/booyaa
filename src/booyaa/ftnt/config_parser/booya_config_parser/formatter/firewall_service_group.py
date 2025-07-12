from copy import deepcopy


class FirewallServiceGroup():
    def __init__(self):
        self.field_names = {
            '__layout__':     { 'layout': 'virtical', 'header_width': 25, 'value_witdh': 25, 'sheetname': 'service group', 'global': False},
            'name':           {'default_value': []},
            "member":         {'default_value': []},
            'comment':        {'default_value': []},
            'proxy':          {'default_value': []},
            'remark':         {'default_value': []},
        }

    def format(self, addr_obj):
        mod_obj = []
        for line in addr_obj:
            obj_name = list(line.keys())[0]
            tmp_line = deepcopy(line[obj_name])
            tmp_line.setdefault('member', [''])
            tmp_line.setdefault('comment', [''])
            tmp_line.setdefault('proxy', [''])
            tmp_line.setdefault('remark', [''])

            mod_line = {
                'name': obj_name,
                'member': tmp_line['member'],
                'comment': tmp_line['comment'],
                'proxy': tmp_line['proxy'],
                'remark': tmp_line['remark'],
            }

            mod_obj.append(mod_line)
        return mod_obj
