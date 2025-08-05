from re import search, compile, IGNORECASE

class SystemInterface:
    def __init__(self, cli):
        self.cli = cli

    def get(self):
        cmd = 'get system interface'
        return self.cli.execute_command(cmd)

    def have_ip(self, ip_addr):
        cmd = 'get system interface'
        let = self.cli.execute_command(cmd)
        re_ipaddr = compile(r'(\d+\.\d+\.\d+\.\d+)')
        match_ips = re_ipaddr.findall(let['output'])
        if ip_addr in match_ips:
            let['code'] = 0
            let['msg'] = '[{ip_addr}] in interface'
        else:
            let['code'] = 1
            let['msg'] = '[Error] Not exsit {ip_addr} in interface'

        return let

"""
FSW01 # get system interface
== [ mgmt ]
name: mgmt    dhcp-client-status: initial    mode: dhcp    ip: 0.0.0.0 0.0.0.0   status: up    type: physical   mtu-override: disable
== [ internal ]
name: internal    dhcp-client-status: connected (433764s remaining)   mode: dhcp    ip: 10.255.1.1 255.255.255.0   status: up    type: physical   mtu-override: disable
== [ rspan ]
name: rspan    dhcp-client-status: connected (433971s remaining)   mode: dhcp    ip: 10.255.12.3 255.255.255.0   status: up    type: vlan   vlanid: 4092
"""


