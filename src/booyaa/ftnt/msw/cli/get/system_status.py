from re import search, compile, IGNORECASE

class SystemStatus:
    hostname: str                   # ホスト名
    serial: str                     # シリアル
    build: str                      # ビルド情報
    version: str                    # OSバージョン
    model: str                    # モデル

    def __init__(self, cli):
        self.cli = cli

    def get(self):
        cmd = 'get system status | grep .*'
        res = self.cli.execute_command(cmd)

        if res['code'] != 0:
            return res

        pattern_dict = {
            'versions': compile(r'Version:\s+FortiSwitch-(\S+)\s+v([\d.]+),build(\d+),.*', IGNORECASE),
            'serial': compile(r'Serial-Number:\s+(\w+)', IGNORECASE),
            'hostname': compile(r'Hostname:\s+(\S+)', IGNORECASE),
            'ng_test': compile(r'aabbss:\s+(\S+)', IGNORECASE),
        }

        for k, v in pattern_dict.items():
            matchs = v.search(res['output'])
            if matchs:
                if k == 'versions':
                    setattr(self, 'model', f'FS{matchs.group(1)}')
                    setattr(self, 'version', matchs.group(2))
                    setattr(self, 'build', matchs.group(3))
                else:
                    setattr(self, k, matchs.group(1))

            else:
                res['code'] = 1
                res['msg'] = f'[Error] {cmd} cannot get {k} value'
                return res

        return res


    def is_target(self, hostname=None, serial=None):
        let = {'code': '', }
        name_list = []
        if hostname is not None:
            name_list.append(hostname)
        if serial is not None:
            name_list.append(serial)
            
        if name_list:
            pass
        else:
            let['code'] = 1



"""
Version: FortiSwitch-224E v7.4.3,build0830,240422 (GA)
Serial-Number: S224ENTF18000490
Firmware Signature: valid
Boot: Warmboot
BIOS version: 04000004
System Part-Number: P21932-03
Burn in MAC: 70:4c:a5:a2:ea:d6
Hostname: FSW01
Security mode: none
Distribution: International
Branch point: 830
System time: Wed Jul 30 09:02:13 2025
"""

