from typing import Optional
from pathlib import Path
from csv import DictReader

class IPv4:
    def __init__(self, args_ip_str: Optional[str] = None):
        self.reset_instance()
        if args_ip_str is not None:
            self.args_ip_str = args_ip_str.strip()

    def reset_instance(self):
        self.err_msg = []
        self.ip_version = 'IPv4'
        self.args_ip_str = None

        self.ip = None
        self.ip_long = None
        self.ip_hex = None
        self.cidr = None
        self.netmask = None

        self.nwaddr = None
        self.bcaddr = None
        self.nwaddr_long = None
        self.bcaddr_long = None
        self.nwaddr_hex = None
        self.bcaddr_hex = None

        self.host_min_addr = None
        self.host_max_addr = None
        self.num_of_hosts = None

        self.ip_class = None
        self.scope = None

        self.calc_result = self.to_dict()

    def ip_calc(self, args_ip_str: Optional[str] = None):
        if args_ip_str is None and self.args_ip_str is None:
            self.reset_instance()
            self.err_msg.append('no IP string specified')
            return self.calc_result

        if args_ip_str is not None:
            self.reset_instance()
            self.args_ip_str = args_ip_str.strip()

        if self.args_ip_str.count('/') == 0:
            self.err_msg.append(f'invalid format: {self.args_ip_str}')
            return self.calc_result
        try:
            self.ip, mask = self.args_ip_str.strip().split('/')
            self.ip = self.ip.strip()
            mask = mask.strip()
            if len(mask) == 0:
                self.err_msg.append(f'invalid format: {self.args_ip_str}')
                return self.calc_result
            self.netmask = self.cidr2ipmask(int(mask)) if mask.isdigit() else mask
        except ValueError:
            self.err_msg.append(f'invalid mask value: {self.args_ip_str}')
            return self.calc_result

        if not self.is_ip():
            self.err_msg.append(f'invalid ipv4 address: {self.ip}')
            return self.calc_result

        self.ip_long = self.ip2long()
        self.ip_hex = f"0x{self.ip_long:08X}"

        self.cidr = self.ipmask2cidr(self.netmask)
        if self.cidr is False:
            self.err_msg.append(f'invalid netmask: {self.netmask}')
            return self.calc_result

        mask_long = self.get_cidr_long(self.cidr)
        self.nwaddr_long = self.ip_long & mask_long
        self.bcaddr_long = self.ip_long | (~mask_long & 0xFFFFFFFF)

        self.nwaddr = self.long2ip(self.nwaddr_long)
        self.bcaddr = self.long2ip(self.bcaddr_long)
        self.nwaddr_hex = f"0x{self.nwaddr_long:08X}"
        self.bcaddr_hex = f"0x{self.bcaddr_long:08X}"

        self.host_min_addr = self.long2ip(self.nwaddr_long + 1)
        self.host_max_addr = self.long2ip(self.bcaddr_long - 1)
        self.num_of_hosts = (1 << (32 - self.cidr)) - 2 if self.cidr < 31 else 0

        self.ip_class, self.scope = self.get_class()

        self.calc_result = self.to_dict()

        return self.calc_result

    def is_ip(self) -> bool:
        parts = self.ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True

    def is_mask(self, mask_str: str) -> bool:
        if not isinstance(mask_str, str):
            return False
        if mask_str.count('.') != 3:
            return False
        parts = mask_str.split('.')
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True

    def is_ipaddr_format(self, ip_str: str) -> bool:
        if not isinstance(ip_str, str):
            return False
        if ip_str.count('/') != 1:
            return False
        ip, mask = ip_str.split('/')
        if not self.is_ip():
            return False
        if not mask.isdigit() or not 0 <= int(mask) <= 32:
            return False
        return True

    def ip2long(self, ip: Optional[str] = None) -> int:
        if ip is None:
            ip = self.ip
        oct1, oct2, oct3, oct4 = map(int, ip.split("."))
        return (oct1 << 24) | (oct2 << 16) | (oct3 << 8) | oct4

    def long2ip(self, ip_long: int) -> str:
        return '.'.join(map(str, [(ip_long >> (i * 8)) & 0xFF for i in range(3, -1, -1)]))

    def cidr2ipmask(self, cidr: int) -> str:
        mask = 0xFFFFFFFF & (0xFFFFFFFF << (32 - cidr))
        return f"{(mask >> 24) & 0xFF}.{(mask >> 16) & 0xFF}.{(mask >> 8) & 0xFF}.{mask & 0xFF}"

    def ipmask2cidr(self, ipmask: str) -> Optional[int]:
        if not self.is_ip():
            return False
        binary_str = ''.join([bin(int(segment))[2:].zfill(8) for segment in ipmask.split('.')])
        if '01' in binary_str:
            return False
        return binary_str.count('1')

    def get_cidr_long(self, cidr: int) -> int:
        return 0xFFFFFFFF & (0xFFFFFFFF << (32 - cidr))

    def get_class(self, ip: Optional[str] = None) -> tuple:
        if ip is None:
            ip = self.ip
        ip_class = '-'
        scope = 'Global'

        oct1 = int(ip.split('.')[0])

        if 0 <= oct1 <= 126:
            ip_class = 'A'
        elif 128 <= oct1 <= 191:
            ip_class = 'B'
        elif 192 <= oct1 <= 223:
            ip_class = 'C'
        elif 224 <= oct1 <= 239:
            ip_class = 'D'
        elif 240 <= oct1 <= 255:
            ip_class = 'E'

        ipv4_reserved_csv = Path(__file__).parent / "ipv4_reserved.csv"
        ipv4_reserved_dict = {}

        with open(ipv4_reserved_csv, newline="") as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                ip_long = self.ip2long(row["address"].split("/")[0])
                cidr = int(row["address"].split("/")[1])
                mask = self.get_cidr_long(cidr)
                nw_long = ip_long & mask
                if cidr not in ipv4_reserved_dict:
                    ipv4_reserved_dict[cidr] = {}
                ipv4_reserved_dict[cidr][nw_long] = row["scope"]

        for prefix in sorted(ipv4_reserved_dict.keys(), reverse=True):
            mask = self.get_cidr_long(prefix)
            nw_long = self.ip_long & mask
            if nw_long in ipv4_reserved_dict[prefix]:
                scope = ipv4_reserved_dict[prefix][nw_long]
                break

        return ip_class, scope

    def to_dict(self):
        return {
            'err_msg': self.err_msg,
            'args_ip': self.args_ip_str,
            'ip_version': self.ip_version,
            'ip': self.ip,
            'ip_long': self.ip_long,
            'ip_hex': self.ip_hex,
            'cidr': self.cidr,
            'netmask': self.netmask,
            'nwaddr': self.nwaddr,
            'bcaddr': self.bcaddr,
            'nwaddr_long': self.nwaddr_long,
            'bcaddr_long': self.bcaddr_long,
            'nwaddr_hex': self.nwaddr_hex,
            'bcaddr_hex': self.bcaddr_hex,
            'host_min_addr': self.host_min_addr,
            'host_max_addr': self.host_max_addr,
            'num_of_hosts': self.num_of_hosts,
            'ip_class': self.ip_class,
            'scope': self.scope
        }


if __name__ == "__main__":
    ip = IPv4()
    ip.ip_calc("192.168.1.1/32")
    print(ip.to_dict())