from copy import deepcopy


class FirewallIppool():
    def __init__(self):
        self.field_names = {
            '__layout__':             {'layout': 'simple', 'sheetname': 'ippool', 'global': False},
            'name':                   {'default_value': [],  'width': 30},
            'type':                   {'default_value': ['overload'],  'width': 30},
            'startip':                {'default_value': [],  'width': 30},
            'endip':                  {'default_value': [],  'width': 30},
            'arp-reply':              {'default_value': ['enable'],  'width': 30},
            'arp-intf':               {'default_value': [],  'width': 30},
            'associated-interface':   {'default_value': [],  'width': 30},
            'source-startip':         {'default_value': [],  'width': 30},
            'source-endip':           {'default_value': [],  'width': 30},
            'port-per-user':          {'default_value': [],  'width': 30},
            'block-size':             {'default_value': [],  'width': 30},
            'num-blocks-per-user':    {'default_value': [],  'width': 30},
            'comment':                {'default_value': [],  'width': 30},
            'remark':                 {'default_value': [],  'width': 30},
        }

    def format(self, addr_obj):
        mod_obj = []
        for line in addr_obj:
            obj_name = list(line.keys())[0]
            tmp_line = deepcopy(line[obj_name])
            tmp_line.setdefault('type', ['overload'])
            tmp_line.setdefault('startip', [''])
            tmp_line.setdefault('endip', [''])
            tmp_line.setdefault('arp-reply', ['disable'])
            tmp_line.setdefault('arp-intf', [''])
            tmp_line.setdefault('associated-interface', [''])
            tmp_line.setdefault('source-startip', [''])
            tmp_line.setdefault('source-endip', [''])
            tmp_line.setdefault('port-per-user', [''])
            tmp_line.setdefault('block-size', [''])
            tmp_line.setdefault('num-blocks-per-user', [''])
            tmp_line.setdefault('comment', [''])
            tmp_line.setdefault('remark', [''])

            mod_line = {
                'name':                 obj_name,
                'type':                 tmp_line['type'],
                'startip':              tmp_line['startip'],
                'endip':                tmp_line['endip'],
                'arp-reply':            tmp_line['arp-reply'],
                'arp-intf':             tmp_line['arp-intf'],
                'associated-interface': tmp_line['associated-interface'],
                'source-startip':       tmp_line['source-startip'],
                'source-endip':         tmp_line['source-endip'],
                'port-per-user':        tmp_line['port-per-user'],
                'block-size':           tmp_line['block-size'],
                'num-blocks-per-user':  tmp_line['num-blocks-per-user'],
                'comment':              tmp_line['comment'],
                'remark':               tmp_line['remark'],
            }

            mod_obj.append(mod_line)
        return mod_obj
