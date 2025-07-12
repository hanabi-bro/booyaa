from copy import deepcopy


class FirewallVipgrp():
    def __init__(self):
        self.field_names = {
            '__layout__':       {'layout': 'simple', 'sheetname': 'vip group', 'global': False},
            'name':             {'default_value': [],  'width': 30},
            'interface':        {'default_value': [],  'width': 30},
            'member':           {'default_value': [],  'width': 30},
            'comment':          {'default_value': [],  'width': 30},
            'remark':           {'default_value': [],  'width': 30},
        }

    def format(self, addr_obj):
        mod_obj = []
        for line in addr_obj:
            obj_name = list(line.keys())[0]
            tmp_line = deepcopy(line[obj_name])
            tmp_line.setdefault('interface', ['any'])
            tmp_line.setdefault('member', [''])
            tmp_line.setdefault('comment', [''])
            tmp_line.setdefault('remark', [''])

            mod_line = {
                'name':             obj_name,
                'interface':        tmp_line['interface'],
                'member':           tmp_line['member'],
                'comment':          tmp_line['comment'],
                'remark':           tmp_line['remark'],
            }

            mod_obj.append(mod_line)
        return mod_obj
