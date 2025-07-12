
from copy import deepcopy


class FirewallServiceCustom():
    def __init__(self):
        self.field_names = {
            '__layout__':      {'layout': 'simple', 'sheetname': 'service', 'global': False},
            'name':            {'width': 25, 'default_value': []},
            'category':        {'width': 25, 'default_value': []},
            'protocol':        {'width': 15, 'default_value': []},
            'address':         {'width': 30, 'default_value': []},
            'icmptype':        {'width': 10, 'default_value': []},
            'icmpcode':        {'width': 10, 'default_value': []},
            'protocol-number': {'width': 10, 'default_value': []},
            'tcp-udp':         {'width': 10, 'default_value': []},
            'dst-portrange':   {'width': 25, 'default_value': []},
            'src-portrange':   {'width': 25, 'default_value': []},
            'session-ttl':     {'width': 10, 'default_value': []},
            'comment':         {'width': 30, 'default_value': []},
            'remark':          {'width': 30, 'default_value': []},
        }
        self.range_type = [
            'tcp-portrange',
            'udp-portrange',
            'sctp-portrange',
        ]

    def format(self, addr_obj):
        mod_obj = []
        # [
        #   {'none': {'uuid': ['6a33b3c4-a701-51ef-74c9-aadedb00dbb9'], 'subnet': ['0.0.0.0', '255.255.255.255']}}
        # ]

        for line in addr_obj:
            obj_name = list(line.keys())[0]
            tmp_line = deepcopy(line[obj_name])
            tmp_line.setdefault('name', ['obj_name'])
            tmp_line.setdefault('category', [''])
            tmp_line.setdefault('protocol', ['TCP/UDP/SCTP'])
            tmp_line.setdefault('iprange', ['0.0.0.0'])
            tmp_line.setdefault('fqdn', [''])
            tmp_line.setdefault('icmptype', [''])
            tmp_line.setdefault('icmpcode', [''])
            tmp_line.setdefault('protocol-number', [''])
            tmp_line.setdefault('tcp-portrange', False)
            tmp_line.setdefault('udp-portrange', False)
            tmp_line.setdefault('sctp-portrange', False)
            tmp_line.setdefault('', [''])
            tmp_line.setdefault('', [''])
            tmp_line.setdefault('session-ttl', ['0'])
            tmp_line.setdefault('comment', [''])

            # icmp
            if tmp_line['protocol'] == ['ICMP'] or tmp_line['protocol'] == ['ICMP6']:
                if tmp_line['icmptype'] is None:
                    tmp_line['icmptype'] = 'ALL'

                if tmp_line['icmpcode'] is None:
                    tmp_line['icmpcode'] = ''


            # address
            address = tmp_line['iprange'][0]
            if not tmp_line['fqdn'][0] == '':
                address = tmp_line['fqdn'][0]

            # port range
            tcp_udp = []
            port_range_dst = []
            port_range_src = []
            for range_type in self.range_type:
                if tmp_line[range_type]:
                    for range_param in tmp_line[range_type]:
                        range = range_param.split(':')
                        if len(range) == 2:
                            port_range_dst.append(range[0])
                            port_range_src.append(range[1])
                            if not range[0] == '':
                                tcp_udp.append(range_type.split('-')[0])
                        else:
                            port_range_dst.append(range[0])
                            if not range[0] == '':
                                tcp_udp.append(range_type.split('-')[0])

            # ipmask
            # if tmp_line['type'] == ['ipmask']:
            #     tmp_line.setdefault('subnet', ['0.0.0.0', '0.0.0.0'])
            #     address = ["/".join(tmp_line['subnet'])]

            # iprange
            # elif 'iprange' in tmp_line['type']:
            #     address = [f"{tmp_line['start-ip'][0]}-{tmp_line['end-ip'][0]}"]

            mod_line = {
                'name':            obj_name,
                'category':        tmp_line['category'],
                'protocol':        tmp_line['protocol'],
                'address':         address,
                'icmptype':        tmp_line['icmptype'],
                'icmpcode':        tmp_line['icmpcode'],
                'protocol-number': tmp_line['protocol-number'],
                'tcp-udp':         tcp_udp,
                'dst-portrange':   port_range_dst,
                'src-portrange':   port_range_src,
                'session-ttl':     tmp_line['session-ttl'],
                'comment':         tmp_line['comment'],
                'remark':          '',
            }

            mod_obj.append(mod_line)
        return mod_obj


if __name__ == '__main__':
    pass

