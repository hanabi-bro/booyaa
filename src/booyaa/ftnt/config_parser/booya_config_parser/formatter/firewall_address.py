from copy import deepcopy


class FirewallAddress:
    def __init__(self) -> None:
        self.field_names = {
            '__layout__':    {'layout': 'simple', 'sheetname': 'address', 'global': False},
            'name':          {'width': 35, 'default_value': []},
            'interface':     {'width': 15, 'default_value': []},
            'type':          {'width': 10, 'default_value': []},
            'address':       {'width': 30, 'default_value': []},
            'allow-routing': {'width': 10, 'default_value': []},
            'comment':       {'width': 30, 'default_value': []},
            'cache-ttl':     {'width':  8, 'default_value': []},
            'remark':        {'width': 15, 'default_value': []},
        }

    def format(self, addr_obj) -> list:
        mod_obj = []
        # [
        #   {'none': {'uuid': ['6a33b3c4-a701-51ef-74c9-aadedb00dbb9'], 'subnet': ['0.0.0.0', '255.255.255.255']}}
        # ]
        for line in addr_obj:
            obj_name = next(iter(line.keys()))
            tmp_line = deepcopy(line[obj_name])
            tmp_line.setdefault('type', ['ipmask'])
            tmp_line.setdefault('start-ip', [])
            tmp_line.setdefault('end-ip', [])
            tmp_line.setdefault('associated-interface', [])
            tmp_line.setdefault('allow-routing', ['disable'])
            tmp_line.setdefault('comment', [])
            tmp_line.setdefault('remark', [])
            tmp_line.setdefault('cache-ttl', ['0'])
            tmp_line.setdefault('color', ['0'])
            tmp_line.setdefault('sub-type', [])
            tmp_line.setdefault('fabric-object', ['disable'])

            # ipmask
            if tmp_line['type'] == ['ipmask']:
                tmp_line.setdefault('subnet', ['0.0.0.0', '0.0.0.0'])
                address = ["/".join(tmp_line['subnet'])]

            # iprange
            elif 'iprange' in tmp_line['type']:
                address = [f"{tmp_line['start-ip'][0]}-{tmp_line['end-ip'][0]}"]

            # fqdn
            elif 'fqdn' in tmp_line['type']:
                address = tmp_line['fqdn']

            # 6.4 under ?
            elif 'wildcard' in tmp_line['type']:
                address = tmp_line['wildcard']

            # geography
            elif 'geography' in tmp_line['type']:
                address = tmp_line['country']

            # interface-subnet ??
            elif 'interface-subnet' in tmp_line['type']:
                address = tmp_line['subnet']

            elif 'dynamic' in tmp_line['type']:
                address = tmp_line['sub-type']

            elif 'mac' in tmp_line['type']:
                address = tmp_line['macaddr']

            mod_line = {
                'name': obj_name,
                'interface': tmp_line['associated-interface'],
                'type': tmp_line['type'],
                'address': address,
                'start-ip': tmp_line['start-ip'],
                'end-ip': tmp_line['end-ip'],
                'allow-routing': tmp_line['allow-routing'],
                'comment': tmp_line['comment'],
                'remark': tmp_line['remark'],
                'color': tmp_line['color'],
                'sub-type': tmp_line['sub-type'],
                'cache-ttl': tmp_line['cache-ttl'],
                'fabric-object': tmp_line['fabric-object'],
            }

            mod_obj.append(mod_line)
        return mod_obj


if __name__ == '__main__':
    pass


