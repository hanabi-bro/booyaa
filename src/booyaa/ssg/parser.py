from shlex import split as s_split
from writer import ExportExcel

from rich import print, pretty
pretty.install()

class ScreenosParser():
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

        self.excel_exporter = ExportExcel()

    def load(self, file_path):
        with open(file_path, 'r', encoding='utf8') as f:
            for line in f:
                self.raw.append(s_split(line.strip()))

    def parse(self):
        current_category = ""
        for line in self.raw:
            if line[0] == 'exit':
                current_category = ""

            ## hostname
            elif line[0:2] == ['set', 'hostname']:
                self.configs['basic'].append({
                    'hostname': line[2],
                    'dns': []
                })

            ## dns
            elif line[0:3] == ['set', 'dns', 'host']:
                self.configs['basic'][0]['dns'].append(line[4])

            ## vip(mip)
            elif len(line) > 10 and line[1] == 'interface' and line[3] == 'mip':
                self.configs['vip'].append(
                    {
                        'name': f'MIP({line[4]})',
                        'vip': f'{line[4]}',
                        'mapped_address': f'{line[6]}/{line[8]}',
                        'vr': line[10],
                        'comment': '',
                    }
                )

            ## interface
            elif line[0:2] == ['set', 'interface']:
                ## 存在しなければ新しく追加する
                if_exist = False
                num = ''
                for i, intf in enumerate(self.configs['interface']):
                    if intf['name'] == line[2]:
                        if_exist = True
                        num = i
                        break
                
                if not if_exist:
                    self.configs['interface'].append(
                        {
                            'name': line[2],
                            'ip': '',
                            'mode': '',
                            'zone': '',
                            'manageable': '',
                            'gateway': '',
                        }
                    )
                    num = -1

                if line[3:5] == ['ip', 'manageable']:
                    self.configs['interface'][num]['manageable'] = 'enable'
                elif line[3] == 'ip':
                    self.configs['interface'][num]['ip'] = line[4]
                elif line[3] == 'route':
                    self.configs['interface'][num]['mode'] = 'route'
                elif line[3] == 'nat':
                    self.configs['interface'][num]['mode'] = 'nat'
                elif line[3] == 'zone':
                    self.configs['interface'][num]['zone'] = line[4]
                elif line[3] == 'gateway':
                    self.configs['interface'][num]['gateway'] = line[4]

            ## route
            elif line[0:2] == ['set', 'route']:
                self.configs['route'].append(
                    {
                        'dst': line[2],
                        'gateway': line[6],
                        'interface': line[4]

                    }
                )

            ## Firewall Policy
            ### listスライスの終了位置は+1が必要、なぜだ・・・
            elif line[1:3] == ['policy', 'id']:
                id = line[3]
                current_category = "policy"

                ## Policy 最初の行
                if len(line) > 5 and line[4] == 'from':
                    tmp_params = {
                        'id': id,
                        'status': 'enable',
                        'from_sz': line[5],
                        'to_sz': line[7],
                        'src-address': [line[8]],
                        'dst-address': [line[9]],
                        'service': [line[10]],
                        'action': line[11],
                        'comment': '',
                    }
                    if len(line) > 12:
                        tmp_params['log'] = line[12:]
                    else:
                        tmp_params['log'] = 'disable'
                    
                    self.configs['policy'].append(tmp_params)

                ## Policyのstatusがdisableの場合
                elif len(line) == 5 and line[4] == 'disable':
                    self.configs['policy'][-1]['status'] = 'disable'

            # dst-addressなど追加パラメータのフォロー
            elif current_category == "policy" and len(line) == 3 and line[2]:
                if line[1] not in self.configs['policy'][-1].keys():
                    self.configs['policy'][-1][line[1]] = [line[2]]
                else:
                    self.configs['policy'][-1][line[1]].append(line[2])

            ## service
            elif line[1] == 'service':
                if line[3] == '+':
                    self.configs['service'][-1]['protocol'].append(line[4])
                    self.configs['service'][-1]['src-port'].append(line[6])
                    self.configs['service'][-1]['dst-port'].append(line[8])
                else:
                    self.configs['service'].append(
                        {
                            'name': line[2],
                            'protocol': [line[4]],
                            'src-port': [line[6]],
                            'dst-port': [line[8]],
                            'comment': '',
                        }
                    )

            ## service group
            elif line[1:3] == ['group', 'service']:
                if len(line) > 4 and line[4] == 'add':
                    self.configs['service_group'][-1]['member'].append(line[5])
                else:
                    self.configs['service_group'].append(
                        {
                            'name': line[3],
                            'member': [],
                            'comment': '',
                        }
                    )

            ## address
            elif line[1] == 'address':
                self.configs['address'].append(
                    {
                        'name': line[3],
                        'zone': line[2],
                        'address': '/'.join(line[4:6]),
                        'comment': '' if len(line) < 7 else line[6],
                    }
                )

    def export_to_excel(self, config):
        self.excel_exporter.parse_to_excel_params(self.configs)
        self.excel_exporter.export_excel_book()


if __name__ == '__main__':
    sp = ScreenosParser()
    sp.load('tmp/pci.txt')
    sp.parse()
    sp.export_to_excel(sp.configs)
