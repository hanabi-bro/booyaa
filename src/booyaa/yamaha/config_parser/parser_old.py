from shlex import split as s_split
import re
# from writer import ExportExcel

from rich import print, pretty
pretty.install()

class YamahaParser():
    def __init__(self):
        self.raw = []
        self.configs = {
            'basic': [],
            'interface': [],
            'vlan': [],
            'route': [],
            'policy': [],
            'service': [],
            'service_group': [],
            'address': [],
            'vip': [],
        }

    def load(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.config_raw = f.read()        
        return self.config_raw

    def parse(self):
        self.parse_raw_to_list()
        self.parse_categories()

    def parse_raw_to_list(self):
        lines = self.config_raw
        def add_line_to_structure(line, structure, level=0):
            indent_level = len(line) - len(line.lstrip())
            if indent_level == level:
                structure.append(line.strip().split())
            else:
                if not structure or not isinstance(structure[-1], list):
                    structure.append([])
                add_line_to_structure(line, structure[-1], level + 1)

        lines = lines.strip().split('\n')
        conf_list = []
        for line in lines:
            add_line_to_structure(line, conf_list)

        self.config_pre_parsed = conf_list
        return conf_list

    def parse_categories(self):            
        """"""
        static_filter_list = []
        dynamic_filter_list = []
        static_route_list = []
        physical_interface_list = []
        pp_selector_list = []

        for line in self.config_pre_parsed:
            ### Dynamic Filter
            if ['ip', 'filter', 'dynamic'] == line[:3]:
                # inprogress filter option
                if line[6] == filter:
                    pass
                    protocol = None

                else:
                    protocol = line[6]

                dynamic_filter = {
                    'id': line[3],
                    'src_addr': line[4].split(','),
                    'dst_addr': line[5].split(','),
                    'protocol': protocol.split(','),
                    'filter': None,
                    'in_list': None,
                    'out_list': None
                }
                dynamic_filter_list.append(dynamic_filter)

            ### Static Filter
            elif ['ip', 'filter'] == line[:2]:
                static_filter = {
                    'id': line[2],
                    'action': line[3],
                    'src_addr': line[4].split(','),
                    'dst_addr': line[5].split(','),
                    'protocol': line[6].split(','),
                    'src_port': line[7].split(','),
                    'dst_port': line[8].split(','),
                }
                static_filter_list.append(static_filter)

            ### ip route
            elif ['ip', 'route'] == line[:2]:

                ## GatewayがPPの場合
                if line[4] == 'pp':
                    if_num = line[5]
                else:
                    if_num = None

                ip_route_static = {
                    'network': line[2],
                    'gateway': line[4],
                    'if_num': if_num,
                }
                static_route_list.append(ip_route_static)

            ### physical interface
            elif line[1].startswith('lan') and line[0] == 'ip':
                ## 参考
                ## fnmatchを使うとワイルドカードで判定できる。
                ## from fnmatch import fnmatch
                ## fnmatch(line[1], 'LAN*')
                {
                    'nic': None,
                    'address': None,
                    'filter_in': [],
                    'filter_out': []
                }

                #### physical_interface_listに既に入っているかを確認
                nic_dict = next(filter(lambda d: d['nic'] == line[1], physical_interface_list), None)

                #### 入っていなければ追加
                if not nic_dict:
                    nic_dict = {
                        'nic': line[1],
                        'address': None,
                        'filter_in': [],
                        'dynamic_filter_in': [],
                        'filter_out': [],
                        'dynamic_filter_out': [],
                        'mtu': 1500,
                    }
                    physical_interface_list.append(nic_dict)
                
                #### address
                if 'address' == line[2]:
                    nic_dict['address'] = line[3:]

                #### static filter in
                elif ['secure', 'filter', 'in'] == line[2:5]:
                    nic_dict['filter_in'] = line[5:]

                #### static filter in
                elif ['secure' 'filter' 'out'] == line[2:5]:
                    nic_dict['filter_out'] = line[5:]

            ### pp selector
            elif ['pp', 'select'] == line[:2]:
                pp_selector = {'id': line[3]}
                pp_selector = {
                    'id': line[1],
                    'use': None,
                    'address': None,
                    'filter_in': [],
                    'dynamic_filter_in': [],
                    'filter_out': [],
                    'dynamic_filter_out': [],
                    'mtu': 1500,
                }

                for pp_line in line[3:]:
                    #### pysical nic
                    if ['use'] == pp_line[1]:
                        pp_selector['interface'] = pp_line[2]
                    ### MTU
                    elif ['mtu'] == pp_line[2:3]:
                        pp_selector['mtu'] = pp_line[3]
                    #### filter in
                    elif ['secure', 'filter', 'in'] == pp_line[2:5]:
                        ### dynamicの位置取得
                        dynamic_index = pp_line.index('dynamic') if 'dynamic' in pp_line else -1 
                        pp_selector['filter_in'] = pp_line[5:dynamic_index]
                        pp_selector['dynamic_filter_in'] = pp_line[(dynamic_index+1):]
                    #### filter out
                    elif ['secure', 'filter', 'out'] == pp_line[2:5]:
                        dynamic_index = pp_line.index('dynamic') if 'dynamic' in pp_line else -1 
                        pp_selector['filter_out'] = pp_line[5:dynamic_index]
                        pp_selector['dynamic_filter_out'] = pp_line[(dynamic_index+1):]
                    
                pp_selector_list.append(pp_selector)

        self.dynamic_filter_list = dynamic_filter_list
        self.static_filter_list = static_filter_list
        self.static_route_list = static_route_list
        self.physical_interface_list = physical_interface_list
        self.pp_selector_list = pp_selector_list

    def gen_policy_pp_obj(self):
        """"""
        filter_in_obj = []
        dynamic_filter_in_obj = []
        filter_out_obj = []
        dynamic_filter_out_obj = []
        
        for line in self.pp_selector_list:
            id = line['id']
            for filter_in_id in line['filter_in']:
                filter_in_obj.append(
                    self.search_obj_k_v('id', filter_in_id, self.static_filter_list)
                )
            for filter_in_id in line['dynamic_filter_in']:
                dynamic_filter_in_obj.append(
                    self.search_obj_k_v('id', filter_in_id, self.dynamic_filter_list)
                )
            for filter_out_id in line['filter_in']:
                filter_out_obj.append(
                    self.search_obj_k_v('id', filter_out_id, self.static_filter_list)
                )
            for filter_out_id in line['dynamic_filter_out']:
                dynamic_filter_out_obj.append(
                    self.search_obj_k_v('id', filter_out_id, self.dynamic_filter_list)
                )
            print(dynamic_filter_out_obj)


    def search_obj_k_v(self, key, value, obj):
        """"""
        return next(filter(lambda d: d[key] == value, obj), None)




if __name__ == '__main__':
    parser = YamahaParser()
    config_raw = parser.load('tmp/pci.txt')
    parser.parse()
    print(parser.gen_policy_pp_obj())
