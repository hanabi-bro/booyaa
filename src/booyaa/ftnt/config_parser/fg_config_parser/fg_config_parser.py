from dis import pretty_flags
import re, shlex, textwrap
import yaml, json
import datetime
from pathlib import Path
import sys, traceback
import csv
import socket, struct

from rich import print, pretty

pretty.install()

re_config_vdom = re.compile(r"^(config vdom) *$")
re_config = re.compile(r"^ *(config .*) *$")
re_edit = re.compile(r"^ *(edit .*) *$")
re_set = re.compile(r"^ *(set .*) *$")
re_next = re.compile(r"^ *(next)$")
re_end = re.compile(r"^ *(end)$")

class FgConfigParser:
    def __init__(self):
        self.raw = []
        self.vdom_keys = []

        ## Todo: add auto check
        self.use_vdom = False
        self.conf = []
        self.hostname = ''

        ## Fieldnames
        self.field_names = {}
        self.field_names['config firewall address'] = ['name', 'associated-interface', 'type', 'address',
            'allow-routing', 'comment', 'cache-ttl', 'remark']
        self.field_names['config firewall addrgrp'] = ['name', 'comment', 'type', 'allow-routing', "remark", "member"]
        self.field_names['config firewall vip'] = ['name', 'type', 'extip', 'mappedip', 'extintf', 'comment']
        self.field_names['config firewall vipgrp'] = ['name', 'member', 'interface', 'comments']
        self.field_names['config firewall policy'] = ['id', 'status', 'name','srcintf', 'dstintf', 'srcaddr', 'dstaddr',
            'schedule', 'service', 'action', 'nat', 'poolname', 'logtraffic',
            'av-profile', 'webfilter-profile', 'dnsfilter-profile', 'emailfilter-profile', 'dlp-sensor', 'ips-sensor', 'application-list',
            'inspection-mode', 'ssl-ssh-profile', 'comment']


        self.fw_address = []
        self.fw_addrgrp = []
        self.fw_vip = []
        self.fw_vipgrp = []
        self.fw_policy = []

        ## For NW Test
        self.nwtest_fw_policy = []
        self.field_names['test firewall policy'] = ['id', 'status', 'name','srcintf', 'dstintf', 'srcaddr', 'dstaddr',
            'schedule', 'service', 'action', 'nat', 'poolname', 'logtraffic',
            'av-profile', 'webfilter-profile', 'dnsfilter-profile', 'emailfilter-profile', 'dlp-sensor', 'ips-sensor', 'application-list',
            'inspection-mode', 'ssl-ssh-profile', 'comment', 'src_addr', 'snat_addr', 'dst_addr', 'dst_real_addr']


    def load_config(self, config_file):
        load_result = config_file
        try:
            with open(config_file, "r", encoding="utf-8-sig") as f:
                self.raw = f.readlines()

            self._parse_to_yaml_raw()
            self.json_str = json.dumps(self.conf)

            self.check_vdom()
        
        except Exception as e:
            type_, value, traceback_ = sys.exc_info()
            load_result = f"error: {value}"

        finally:
            return load_result


    def _parse_to_yaml_raw(self):
        str = ""
        indent_lv = 0

        config_count = 0
        edit_count = 0
        next_count = 0
        end_count = 0

        for line in self.raw:
            if re_config_vdom.match(line):
                indent_lv = 0
                str += f"{'    ' * indent_lv}- {line.strip()}:\n"
                indent_lv = indent_lv + 1

            elif re_config.match(line):
                str += f"{'    ' * indent_lv}- {line.strip()}:\n"

                indent_lv = indent_lv + 1
                config_count += 1

            elif re_edit.match(line):
                str += f"{'    ' * indent_lv}- {line.strip()}:\n"
                indent_lv = indent_lv + 1
                edit_count += 1

            elif re_set.match(line):
                str += f"{'    ' * indent_lv}- {line.strip()}\n"

            elif re_next.match(line):
                indent_lv = indent_lv - 1

                next_count += 1

            elif re_end.match(line):
                indent_lv = indent_lv - 1

                end_count += 1

        self.yaml_str = str
        self.conf = yaml.safe_load(str)
        self.get_hostname()

    def to_yaml(self):
        return self.yaml_str

    def to_json(self):
        return json.dumps(self.conf)

    def to_dict(self):
        return self.conf

    def check_vdom(self):
        if "config vdom" in self.conf[0].keys():
            self.use_vdom = True

        if self.use_vdom:
            for c in self.conf[0]["config vdom"]:
                self.vdom_keys.append(list(c.keys())[0])
        else:
            self.vdom_keys = ["edit root"]
    
    def get_hostname(self):
        for c in self.conf:
            if list(c.keys())[0] == "config system global":
                for params in c["config system global"]:
                    if 'set hostname' in params:
                        self.hostname = re.sub('"', '', re.sub("set hostname ","" ,params))
                        break
        
    def get_raw_config(self, category):
        raw_config_dict = {}

        if self.use_vdom:
            for i, c in enumerate(self.vdom_keys):
                for cc in self.conf[2 + i]["config vdom"][0][c]:
                    if list(cc.keys())[0] == category:
                        raw_config_dict[c] = cc[category]
        else:
            for c in self.conf:
                if list(c.keys())[0] == category:
                    raw_config_dict["edit root"] = c[category]

        return raw_config_dict
    
    def parse_config_for_csv(self, category):
        filed_names = self.field_names[category]


#////////////////////

    def get_fw_address(self):
        use_vdom = False
        address_dict = {}
        if "config vdom" in self.conf[0].keys():
            use_vdom = True

        if use_vdom:
            for i, c in enumerate(self.vdom_keys):
                for cc in self.conf[2 + i]["config vdom"][0][c]:
                    if list(cc.keys())[0] == "config firewall address":
                        address_dict[c] = cc["config firewall address"]

        else:
            for c in self.conf:
                if list(c.keys())[0] == "config firewall address":
                    address_dict["edit root"] = c["config firewall address"]

        return address_dict

    def get_fw_addrgrp(self):
        use_vdom = False
        addrgrp_dict = {}
        if "config vdom" in self.conf[0].keys():
            use_vdom = True

        if use_vdom:
            for i, c in enumerate(self.vdom_keys):
                for cc in self.conf[2 + i]["config vdom"][0][c]:
                    if list(cc.keys())[0] == "config firewall addrgrp":
                        addrgrp_dict[c] = cc["config firewall addrgrp"]

        else:
            for c in self.conf:
                if list(c.keys())[0] == "config firewall addrgrp":
                    addrgrp_dict["edit root"] = c["config firewall addrgrp"]

        return addrgrp_dict

    def get_fw_vip(self):
        use_vdom = False
        vip_dict = {}
        if "config vdom" in self.conf[0].keys():
            use_vdom = True

        if use_vdom:
            for i, c in enumerate(self.vdom_keys):
                for cc in self.conf[2 + i]["config vdom"][0][c]:
                    if list(cc.keys())[0] == "config firewall vip":
                        vip_dict[c] = cc["config firewall vip"]

        else:
            for c in self.conf:
                if list(c.keys())[0] == "config firewall vip":
                    vip_dict["edit root"] = c["config firewall vip"]

        return vip_dict

    def get_fw_vipgrp(self):
        use_vdom = False
        vipgrp_dict = {}
        if "config vdom" in self.conf[0].keys():
            use_vdom = True

        if use_vdom:
            for i, c in enumerate(self.vdom_keys):
                for cc in self.conf[2 + i]["config vdom"][0][c]:
                    if list(cc.keys())[0] == "config firewall vipgrp":
                        vipgrp_dict[c] = cc["config firewall vipgrp"]

        else:
            for c in self.conf:
                if list(c.keys())[0] == "config firewall vipgrp":
                    vipgrp_dict["edit root"] = c["config firewall vipgrp"]

        return vipgrp_dict


    def get_fw_policy(self):
        use_vdom = False
        policy_dict = {}
        if "config vdom" in self.conf[0].keys():
            use_vdom = True

        if use_vdom:
            for i, c in enumerate(self.vdom_keys):
                for cc in self.conf[2 + i]["config vdom"][0][c]:
                    if list(cc.keys())[0] == "config firewall policy":
                        policy_dict[c] = cc["config firewall policy"]

        else:
            for c in self.conf:
                if list(c.keys())[0] == "config firewall policy":
                    policy_dict["edit root"] = c["config firewall policy"]

        return policy_dict

    def convert_fw_address(self):
        fw_address_dict = self.get_fw_address()

        self.fw_address = []

        field_names = self.field_names['config firewall address']

        for l in fw_address_dict["edit root"]:
            fw_addr = {}
            tmp_addr = {}
            for k, v in l.items():
                tmp_addr['name'] = re.sub("edit ","" ,k).strip('"')
                for p in v:
                    params = shlex.shlex(p)
                    params.whitespace_split = True
                    ll = [x.strip('"') for x in list(params)]
                    tmp_addr[ll[1]] = "\n".join(ll[2:])

                # mod ip range
                if not 'type' in tmp_addr.keys():
                    if not 'subnet' in tmp_addr.keys():
                        tmp_addr['type'] = 'subnet'
                        tmp_addr['address'] = ''
                    else:
                        tmp_addr['type'] = 'subnet'
                        tmp_addr['address'] = tmp_addr['subnet']
                elif tmp_addr['type'] == 'iprange':
                    tmp_addr['address'] = f"{tmp_addr['start-ip']}-{'end-ip'}"
                elif tmp_addr['type'] == 'fqdn':
                    tmp_addr['address'] = tmp_addr['fqdn']
                elif tmp_addr['type'] == 'tmp_addr':
                    tmp_addr['address'] = tmp_addr['tmp_addr']
                elif tmp_addr['type'] == 'geography':
                    tmp_addr['address'] = tmp_addr['country']
                elif tmp_addr['type'] == 'wildcard':
                    tmp_addr['address'] = tmp_addr['wildcard']
                elif tmp_addr['type'] == 'interface-subnet':
                    tmp_addr['address'] = tmp_addr['subnet']
                    tmp_addr['associated-interface'] = tmp_addr['interface']
                elif tmp_addr['type'] == 'dynamic':
                    tmp_addr['address'] = tmp_addr['sub-type']
                elif tmp_addr['type'] == 'mac':
                    tmp_addr['address'] = tmp_addr['macaddr']
                
                # csvにするときにエラーになったりするので、空の値を入れておく
                for k in field_names:
                    if not k in tmp_addr.keys():
                        fw_addr[k] = ''
                    else:
                        fw_addr[k] = tmp_addr[k]

            self.fw_address.append(fw_addr)

    def to_csv_fw_address(self, export_dir='tmp'):
        if len(self.fw_address) == 0:
            self.convert_fw_address()

        export_result = self.to_csv(
            self.field_names['config firewall address'],
            self.fw_address, export_dir,
            'address'
        )

        return export_result

    def convert_fw_addrgrp(self):
        fw_address_dict = self.get_fw_addrgrp()

        self.fw_addrgrp = []

        field_names = self.field_names['config firewall addrgrp']

        for l in fw_address_dict["edit root"]:
            fw_addrgrp = {}
            tmp_addrgrp = {}
            for k, v in l.items():
                tmp_addrgrp['name'] = re.sub("edit ","" ,k).strip('"')
                for p in v:
                    params = shlex.shlex(p)
                    params.whitespace_split = True
                    ll = [x.strip('"') for x in list(params)]
                    if ll[1] == "member":
                        # tmp_addrgrp[ll[1]] = re.sub('"', '', "\n".join(ll[2:]))
                        tmp_addrgrp[ll[1]] = "\n".join(ll[2:])
                    else:
                        tmp_addrgrp[ll[1]] = " ".join(ll[2:])

                # csvにするときにエラーになったりするので、空の値を入れておく
                for k in field_names:
                    if not k in tmp_addrgrp.keys():
                        fw_addrgrp[k] = ''
                    else:
                        fw_addrgrp[k] = tmp_addrgrp[k]

            self.fw_addrgrp.append(fw_addrgrp)

    def to_csv_fw_addrgrp(self, export_dir='tmp'):
        if len(self.fw_addrgrp) == 0:
            self.convert_fw_addrgrp()

        export_result = self.to_csv(
            self.field_names['config firewall addrgrp'],
            self.fw_addrgrp, export_dir,
            'addrgrp'
        )
        return export_result

    def convert_fw_vip(self):
        fw_vip_dict = self.get_fw_vip()

        self.fw_vip = []

        field_names = self.field_names['config firewall vip']

        for l in fw_vip_dict["edit root"]:
            fw_vip = {}
            tmp_vip = {}
            for k, v in l.items():
                if not 'type' in tmp_vip.keys():
                    tmp_vip['type'] = 'static-nat'
                tmp_vip['name'] = re.sub("edit ","" ,k).strip('"')
                for p in v:
                    params = shlex.shlex(p)
                    params.whitespace_split = True
                    ll = [x.strip('"') for x in list(params)]
                    if ll[1] == "member":
                        tmp_vip[ll[1]] = "\n".join(ll[2:])
                    else:
                        tmp_vip[ll[1]] = " ".join(ll[2:])

                # csvにするときにエラーになったりするので、空の値を入れておく
                for k in field_names:
                    if not k in tmp_vip.keys():
                        fw_vip[k] = ''
                    else:
                        fw_vip[k] = tmp_vip[k]

            self.fw_vip.append(fw_vip)

    def to_csv_fw_vip(self, export_dir='tmp'):
        if len(self.fw_vip) == 0:
            self.convert_fw_vip()

        export_result = self.to_csv(
            self.field_names['config firewall vip'],
            self.fw_vip, export_dir,
            'vip'
        )
        return export_result

    def convert_fw_vipgrp(self):
        fw_vipgrp_dict = self.get_fw_vipgrp()

        self.fw_vipgrp = []

        field_names = self.field_names['config firewall vipgrp']

        for l in fw_vipgrp_dict["edit root"]:
            fw_vipgrp = {}
            tmp_vipgrp = {}
            for k, v in l.items():
                if not 'type' in tmp_vipgrp.keys():
                    tmp_vipgrp['type'] = 'static-nat'
                tmp_vipgrp['name'] = re.sub("edit ","" ,k).strip('"')
                for p in v:
                    params = shlex.shlex(p)
                    params.whitespace_split = True
                    ll = [x.strip('"') for x in list(params)]
                    if ll[1] == "member":
                        # tmp_addrgrp[ll[1]] = re.sub('"', '', "\n".join(ll[2:]))
                        tmp_vipgrp[ll[1]] = "\n".join(ll[2:])
                    else:
                        tmp_vipgrp[ll[1]] = " ".join(ll[2:])


                # csvにするときにエラーになったりするので、空の値を入れておく
                for k in field_names:
                    if not k in tmp_vipgrp.keys():
                        fw_vipgrp[k] = ''
                    else:
                        fw_vipgrp[k] = tmp_vipgrp[k]

            self.fw_vipgrp.append(fw_vipgrp)

    def to_csv_fw_vipgrp(self, export_dir='tmp'):
        if len(self.fw_vipgrp) == 0:
            self.convert_fw_vipgrp()

        export_result = self.to_csv(
            self.field_names['config firewall vipgrp'],
            self.fw_vipgrp, export_dir,
            'vipgrp'
        )
        return export_result
    
    def convert_fw_policy_vdom(self):
        fw_policy_dict = self.get_fw_policy()
        field_names = self.field_names['config firewall policy']

        vdoms = []
        for v in self.vdom_keys:
            vdoms.append(v.replace('vdom', 'edit'))
        
        for v in fw_policy_dict:
            print(v)


        pass

    def convert_fw_policy(self):
        fw_policy_dict = self.get_fw_policy()

        self.fw_policy = []
        field_names = self.field_names['config firewall policy']

        for l in fw_policy_dict["edit root"]:
            fw_policy = {}
            tmp_policy = {}
            for k, v in l.items():
                tmp_policy['id'] = re.sub("edit ","" ,k)
                for p in v:
                    params = shlex.shlex(p)
                    params.whitespace_split = True
                    ll = [x.strip('"') for x in list(params)]
                    tmp_policy[ll[1]] = "\n".join(ll[2:])
                
                if not ('status', 'disable') in tmp_policy.items():
                    tmp_policy['status'] = 'enable'

                if ('nat', 'enable') in tmp_policy.items():
                    if ('ippool', 'enable') in tmp_policy.items():
                        tmp_policy['nat'] = 'ip pool'
                    else:
                        tmp_policy['nat'] = 'interface ip'

                if not ('inspection-mode', 'proxy') in tmp_policy.items():
                    tmp_policy['inspection-mode'] = 'flow'

                # csvにするときにエラーになったりするので、空の値を入れておく
                for k in field_names:
                    if not k in tmp_policy.keys():
                        fw_policy[k] = ''
                    else:
                        fw_policy[k] = tmp_policy[k]

                self.fw_policy.append(fw_policy)

    def to_csv_fw_policy(self, export_dir='tmp'):
        if len(self.fw_policy) == 0:
            self.convert_fw_policy()

        export_result = self.to_csv(
            self.field_names['config firewall policy'],
            self.fw_policy, export_dir,
            'policy'
        )
        return export_result

    def to_csv(self, field_names, params, export_dir, category):
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        dt = now.strftime('%Y%m%d%H%M%S')
        export_name = f"{self.hostname}_{category}_{dt}.csv"

        export_path = Path(export_dir)
        export_path.joinpath(export_name)
        export_path = export_path.joinpath(export_name).resolve()

        try:
            with open(export_path,'w',encoding='utf-8',newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames = field_names)
                writer.writeheader()
                writer.writerows(params)

            export_result = export_path

        except Exception as e:
            type_, value, traceback_ = sys.exc_info()
            export_result = f"error: {value}"

        finally:
            return export_result

    # For NW Test
    def gen_policy_test_list(self):
        ## still in progress
        self.convert_fw_policy()
        self.convert_fw_address()
        self.convert_fw_addrgrp()
        self.convert_fw_vip()
        self.convert_fw_vipgrp()

        self.nwtest_fw_policy = []

        for p in self.fw_policy:
            p['src_addr'] = ''
            p['snat_addr'] = ''
            p['dst_addr'] = ''
            p['dst_real_addr'] = ''
            srcaddr_names = p['srcaddr'].split('\n')
            tmp_src_addrs = []

            for srcaddr in srcaddr_names:
                self.addr_test_perse(srcaddr)
        
        # export_dir = 'tmp'

        # export_result = self.to_csv(
        #     self.field_names['test firewall policy'],
        #     self.nwtest_fw_policy, export_dir,
        #     'nwtest_policy'
        # )
        # return export_result


    ### 

    def addr_test_perse(self, addr_str):
        split_addrs = []
        tmp_addrs = []
        addr_ips = []

        if addr_str == '':
            split_addrs.append('')
        else:
            split_addrs = addr_str.split('\n')

        for addr_name in split_addrs:
            ## addresグループかVIPグループに入ってるか見る。
            for addr_obj in self.fw_addrgrp:
                if addr_obj.get(addr_name):
                    tmp_addrs.append(addr_obj['member'].split('\n'))
                    print(addr_obj['member'])
                    break
            for addr_obj in self.fw_vipgrp:
                if addr_obj.get(addr_name):
                    tmp_addrs.append(addr_obj['member'].split('\n'))
                    break
            

        # return addr_ips




    def addr_format(self, addr_str):
        fgt_ipformat = r'\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+'

        if re.match(fgt_ipformat, addr_str):
            tmp_addr = shlex.split(addr_str)
            if tmp_addr[1] == '255.255.255.255':
                tmp_addr.pop()
            else:
                tmp_addr[1] = self.mask2cidr(tmp_addr[1])

            addr = "/".join(map(str, tmp_addr))
        else:
            addr = addr_str
        
        return addr



    def mask2cidr(self, netmask):
        return sum(bin(int(x)).count('1') for x in netmask.split('.'))





if __name__ == "__main__":
    cp = FgConfigParser()
    cp.load_config("tmp/FG_SAMPLE_CONFIG.conf")

    # print(cp.to_csv_fw_policy())
    # print(cp.to_csv_fw_address())
    # print(cp.to_csv_fw_addrgrp())
    # print(cp.to_csv_fw_vip())
    # print(cp.to_csv_fw_vipgrp())

    # print(cp.get_raw_config("config firewall address"))

    import json
    print(json.dumps(cp.conf, indent=2))

