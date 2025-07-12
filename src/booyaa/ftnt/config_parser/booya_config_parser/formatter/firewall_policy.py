from copy import deepcopy


class FirewallPolicy:
    def __init__(self):
        self.field_names = {
            '__layout__':          {'layout': 'simple', 'sheetname': 'policy', 'global': False},
            'id':                  {'width': 7,  'default_value': []},
            'status':              {'width': 6,  'default_value': []},
            'name':                {'width': 25, 'default_value': []},
            'srcintf':             {'width': 15, 'default_value': []},
            'dstintf':             {'width': 15, 'default_value': []},
            'srcaddr':             {'width': 25, 'default_value': []},
            'dstaddr':             {'width': 25, 'default_value': []},
            'schedule':            {'width': 8,  'default_value': []},
            'service':             {'width': 15, 'default_value': []},
            'action':              {'width': 7,  'default_value': []},
            'nat':                 {'width': 7,  'default_value': []},
            'poolname':            {'width': 25, 'default_value': []},
            'logtraffic':          {'width': 8,  'default_value': []},
            'av-profile':          {'width': 15, 'default_value': []},
            'webfilter-profile':   {'width': 15, 'default_value': []},
            'dnsfilter-profile':   {'width': 15, 'default_value': []},
            'emailfilter-profile': {'width': 15, 'default_value': []},
            'dlp-sensor':          {'width': 15, 'default_value': []},
            'ips-sensor':          {'width': 15, 'default_value': []},
            'application-list':    {'width': 15, 'default_value': []},
            'inspection-mode':     {'width': 15, 'default_value': []},
            'ssl-ssh-profile':     {'width': 15, 'default_value': []},
            'comments':            {'width': 30, 'default_value': []},
        }

    def format(self, policy_obj):
        mod_obj = []

        for line in policy_obj:
            obj_id = list(line.keys())[0]
            tmp_line = deepcopy(line[obj_id])
            tmp_line.setdefault('name', [obj_id])
            tmp_line.setdefault('status', ['enable'])
            tmp_line.setdefault('logtraffic', ['utm'])
            tmp_line.setdefault('action', ['deny'])
            tmp_line.setdefault('inspection-mode', ['flow'])
            tmp_line.setdefault('service', [''])
            tmp_line.setdefault('nat', ['disable'])
            tmp_line.setdefault('ippool', ['disable'])
            tmp_line.setdefault('poolname', [''])
            tmp_line.setdefault('match-vip', ['disable'])
            tmp_line.setdefault('internet-service', ['disable'])
            tmp_line.setdefault('internet-service-name', [''])
            tmp_line.setdefault('internet-service-src', ['disable'])
            tmp_line.setdefault('internet-service-src-name', [''])
            tmp_line.setdefault('utm-status', ['disable'])
            tmp_line.setdefault('ssl-ssh-profile', [''])
            tmp_line.setdefault('av-profile', [''])
            tmp_line.setdefault('webfilter-profile', [''])
            tmp_line.setdefault('dnsfilter-profile', [''])
            tmp_line.setdefault('file-filter-profile', [''])
            tmp_line.setdefault('dlp-sensor', [''])
            tmp_line.setdefault('ips-sensor', [''])
            tmp_line.setdefault('application-list', [''])
            tmp_line.setdefault('emailfilter-profile', [''])
            tmp_line.setdefault('email-collect', ['disable'])
            tmp_line.setdefault('comments', [''])

            # srcaddr
            if tmp_line['internet-service-src'] == ['enable']:
                srcaddr = tmp_line['internet-service-src-name']
            else:
                srcaddr = tmp_line['srcaddr']
            
            # dstaddr
            if tmp_line['internet-service'] == ['enable']:
                dstaddr = tmp_line['internet-service-name']
            else:
                dstaddr = tmp_line['dstaddr']
            
            # format
            mod_line = {
                'id':                  obj_id,
                'status':              tmp_line['status'],
                'name':                tmp_line['name'],
                'srcintf':             tmp_line['srcintf'],
                'dstintf':             tmp_line['dstintf'],
                'srcaddr':             srcaddr,
                'dstaddr':             dstaddr,
                'schedule':            tmp_line['schedule'],
                'service':             tmp_line['service'],
                'action':              tmp_line['action'],
                'nat':                 tmp_line['nat'],
                'poolname':            tmp_line['poolname'],
                'logtraffic':          tmp_line['logtraffic'],
                'av-profile':          tmp_line['av-profile'],
                'webfilter-profile':   tmp_line['webfilter-profile'],
                'dnsfilter-profile':   tmp_line['dnsfilter-profile'],
                'emailfilter-profile': tmp_line['emailfilter-profile'],
                'dlp-sensor':          tmp_line['dlp-sensor'],
                'ips-sensor':          tmp_line['ips-sensor'],
                'application-list':    tmp_line['application-list'],
                'inspection-mode':     tmp_line['inspection-mode'],
                'ssl-ssh-profile':     tmp_line['ssl-ssh-profile'],
                'comments':            tmp_line['comments'],
            }
            mod_obj.append(mod_line)

        return mod_obj

if __name__ == '__main__':
    pass
