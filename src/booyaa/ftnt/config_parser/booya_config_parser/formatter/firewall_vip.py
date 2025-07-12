from copy import deepcopy


class FirewallVip():
    def __init__(self):
        self.field_names = {
            '__layout__':       {'layout': 'simple', 'sheetname': 'vip', 'global': False},
            'name':             {'default_value': [],  'width': 30},
            'arp-reply':        {'default_value': [],  'width': 15},
            'extip':            {'default_value': [],  'width': 30},
            'mappedip':         {'default_value': [],  'width': 30},
            'src-filter':       {'default_value': [],  'width': 15},
            'service':          {'default_value': [],  'width': 20},
            'portforward':      {'default_value': [],  'width': 15},
            'protocol':         {'default_value': [],  'width': 20},
            'extport':          {'default_value': [],  'width': 30},
            'mappedport':       {'default_value': [],  'width': 30},
            'portmapping-type': {'default_value': [],  'width': 30},
            'vip-group':        {'default_value': [],  'width': 30},
            'comment':          {'default_value': [],  'width': 30},
            'remark':           {'default_value': [],  'width': 30},
        }

    def format(self, addr_obj):
        mod_obj = []

        for line in addr_obj:
            obj_name = next(iter(line.keys()))
            tmp_line = deepcopy(line[obj_name])
            tmp_line.setdefault('type', ['static-nat'])
            tmp_line.setdefault('extip', [''])
            tmp_line.setdefault('extaddr', [''])
            tmp_line.setdefault('mappedip', [''])
            tmp_line.setdefault('mapped-addr', [''])
            tmp_line.setdefault('src-filter', [''])
            tmp_line.setdefault('service', [''])
            tmp_line.setdefault('arp-reply', ['enable'])
            tmp_line.setdefault('nat-source-vip', ['disable'])
            tmp_line.setdefault('portforward', ['disable'])
            tmp_line.setdefault('protocol', [''])
            tmp_line.setdefault('extport', [''])
            tmp_line.setdefault('mappedport', [''])
            tmp_line.setdefault('portmapping-type', [''])
            tmp_line.setdefault('comment', [''])
            tmp_line.setdefault('remark', [''])

            # ext addr
            ext_addr = tmp_line['extip'] if tmp_line['extaddr'] == [''] else tmp_line['extaddr']

            # mapped addr
            mapped_arrd = tmp_line['mappedip'] if tmp_line['mapped-addr'] == [''] else tmp_line['mapped-addr']

            # port mapping type
            if tmp_line['portforward'] == ['enable'] and tmp_line['portmapping-type'] == ['']:
                port_mapping_type = '1-to-1'
            else:
                port_mapping_type = tmp_line['portmapping-type']

            # vip_group @todo
            vip_group = ''

            mod_line = {
                'name':             obj_name,
                'arp-reply':        tmp_line['arp-reply'],
                'extip':            ext_addr,
                'mappedip':         mapped_arrd,
                'src-filter':       tmp_line['src-filter'],
                'service':          tmp_line['service'],
                'portforward':      tmp_line['portforward'],
                'protocol':         tmp_line['protocol'],
                'extport':          tmp_line['extport'],
                'mappedport':       tmp_line['mappedport'],
                'portmapping-type': port_mapping_type,
                'vip-group':        vip_group,
                'comment':          tmp_line['comment'],
                'remark':           tmp_line['remark'],
            }

            mod_obj.append(mod_line)
        return mod_obj
