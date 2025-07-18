vdom_conf_categories = [
    'config system object-tagging',
    'config switch-controller traffic-policy',
    'config system settings',
    'config system replacemsg-group',
    'config firewall address',
    'config firewall multicast-address',
    'config firewall address6',
    'config firewall multicast-address6',
    'config firewall addrgrp',
    'config firewall service category',
    'config firewall service custom',
    'config firewall service group',
    'config vpn certificate ca',
    'config vpn certificate local',
    'config webfilter ftgd-local-cat',
    'config firewall shaper traffic-shaper',
    'config web-proxy global',
    'config dlp filepattern',
    'config dlp sensitivity',
    'config videofilter profile',
    'config webfilter ips-urlfilter-setting',
    'config webfilter ips-urlfilter-setting6',
    'config log threat-weight',
    'config icap profile',
    'config user setting',
    'config user group',
    'config vpn ssl web host-check-software',
    'config vpn ssl web portal',
    'config vpn ssl settings',
    'config voip profile',
    'config system sdwan',
    'config dnsfilter profile',
    'config antivirus settings',
    'config emailfilter profile',
    'config log memory setting',
    'config log null-device setting',
    'config firewall schedule recurring',
    'config firewall ssh setting',
    'config firewall profile-protocol-options',
    'config firewall ssl-ssh-profile',
    'config waf profile',
    'config firewall policy',
    'config switch-controller security-policy 802-1X',
    'config switch-controller security-policy local-access',
    'config switch-controller lldp-profile',
    'config switch-controller qos dot1p-map',
    'config switch-controller qos ip-dscp-map',
    'config switch-controller qos queue-policy',
    'config switch-controller qos qos-policy',
    'config switch-controller storm-control-policy',
    'config switch-controller auto-config policy',
    'config switch-controller initial-config template',
    'config switch-controller switch-profile',
    'config switch-controller ptp settings',
    'config switch-controller ptp policy',
    'config switch-controller dsl policy',
    'config switch-controller remote-log',
    'config wireless-controller setting',
    'config wireless-controller arrp-profile',
    'config wireless-controller wids-profile',
    'config wireless-controller ble-profile',
    'config router rip',
    'config router ripng',
    'config router ospf',
    'config router ospf6',
    'config router bgp',
    'config router isis',
    'config router multicast',
]

field_names = {}
# field_names['config firewall address'] = ['name', 'interface', 'type', 'address', 'allow-routing', 'comment', 'cache-ttl', 'remark']
# field_names['config firewall addrgrp'] = ['name', 'comment', 'type', 'allow-routing', "remark", "member"]
# field_names['config firewall vip'] = ['name', 'type', 'extip', 'mappedip', 'extintf', 'comment']
# field_names['config firewall vipgrp'] = ['name', 'member', 'interface', 'comments']
# field_names['config firewall policy'] = ['id', 'status', 'name','srcintf', 'dstintf', 'srcaddr', 'dstaddr',
#             'schedule', 'service', 'action', 'nat', 'poolname', 'logtraffic',
#             'av-profile', 'webfilter-profile', 'dnsfilter-profile', 'emailfilter-profile', 'dlp-sensor', 'ips-sensor', 'application-list',
#             'inspection-mode', 'ssl-ssh-profile', 'comments']


field_names['config firewall address'] = {
    'name':          {'width': 25},
    'interface':     {'width': 15},
    'type':          {'width': 10},
    'address':       {'width': 30},
    'allow-routing': {'width': 10},
    'comment':       {'width': 30},
    'cache-ttl':     {'width':  8},
    'remark':        {'width': 15},
}

field_names['config firewall addrgrp'] = {
    'name':          {'width': 25},
    'comment':       {'width': 30},
    'type':          {'width': 10},
    'allow-routing': {'width': 10},
    "remark":        {'width': 25},
    "member":        {'width': 30}, 
}

field_names['config firewall vip'] = {
    'name':          {'width': 25},
    'type':          {'width': 19},
    'extip':         {'width': 15},
    'mappedip':      {'width': 15},
    'extintf':       {'width': 15},
    'comment':       {'width': 30},
}

field_names['config firewall vipgrp'] = {
    'name':          {'width': 25},
    'member':        {'width': 25},
    'interface':     {'width': 15},
    'comments':      {'width': 30},
}

field_names['config firewall policy'] = {
    'id':                  {'width': 7},
    'status':              {'width': 6},
    'name':                {'width': 25},
    'srcintf':             {'width': 15},
    'dstintf':             {'width': 15},
    'srcaddr':             {'width': 25},
    'dstaddr':             {'width': 25},
    'schedule':            {'width': 8},
    'service':             {'width': 15},
    'action':              {'width': 7},
    'nat':                 {'width': 7},
    'poolname':            {'width': 25},
    'logtraffic':          {'width': 8},
    'av-profile':          {'width': 15},
    'webfilter-profile':   {'width': 15},
    'dnsfilter-profile':   {'width': 15},
    'emailfilter-profile': {'width': 15},
    'dlp-sensor':          {'width': 15},
    'ips-sensor':          {'width': 15},
    'application-list':    {'width': 15},
    'inspection-mode':     {'width': 15},
    'ssl-ssh-profile':     {'width': 15},
    'comments':            {'width': 30},
}
