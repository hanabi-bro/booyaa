from pathlib import Path


# ipv4 reserved csv
ipv4_reserved_csv = Path(__file__).parent / "ipv4_reserved.csv"

if not ipv4_reserved_csv.exists():
    raise FileNotFoundError(f"ipv4 reserved csv {ipv4_reserved_csv} not found")


def is_ip(ipv4):
    """check ipv4 host address format
    Args:
        ipv4 (str): ipv4 host address
    Returns:
        boole: valid: True, Invalid: False
    """

def is_cidr(cidr):
    """checi cidr
    Args:
        cidr (str): cidr notation
        Returns:
            boole: valid: True, Invalid: False
    """

def is_ipmask(ipv4_mask):
    """check ipv4 mask address format
    Args:
        ipv4_mask (str): ipv4 mask address
    Returns:
        boole: valid: True, Invalid: False
    """

def cidr2ipmask(cidr):
    """Convert CIDR notation to IPv4 netmask.
    Args:
        cidr (int): CIDR prefix length (0-32)
    Returns:
        str: IPv4 netmask
    """

def ipmask2cidr(ipv4_mask):
    """Convert IPv4 netmask to CIDR notation.
    Args:
        ipv4_mask (str): IPv4 netmask
    Returns:
        int: CIDR prefix length (0-32)
    """

def parse_mask(mask):
    """parse mask to cidr and ipmask
    Args:
        mask (str): mask value
    Returns:
        tuple: cidr, ipmask
    """

def is_ipv4_format(ipv4_str):
    """check ipv4 format
    Args:
        ipv4_str (str): ipv4 address/mask
    Returns:
        boole: valid: True, Invalid: False
    """

def is_ip_long_size(ipv4_long):
    """size chek ipv4 decimal

    Args:
        ipv4_long (int): ipv4 decimal

    Returns:
        boole: valid: True, Invalid: False
    """

def ip2long(ipv4):
    """ipv4 to int
    Args:
        ipv4 (str): ipv4 format
    Returns:
        int: decimal ipv4 address
    """

def long2ip(ipv4_long):
    """int to ipv4
    Args:
        ipv4_long (int): decimal ipv4 address

    Returns:
        str: ipv4 format
    """

def get_cidr_long(cidr):
    """
    Convert CIDR notation to IPv4 netmask in long format.
    Args:
        cidr (int): CIDR prefix length (0-32)
    Returns:
        int: IPv4 netmask in long format
    """

def get_ipmask_long(netmask):
    """Convert IPv4 netmask to long format.
    Args:
        netmask (str): IPv4 netmask
    Returns:
        int: IPv4 netmask in long format
    """

def get_nwaddr(ipv4, cidr):
    """Get network address from IPv4 and CIDR.
    Args:
        ipv4 (str): IPv4 address
        cidr (int): CIDR prefix length (0-32)
    Returns:
        str: Network address
    """

def get_nwaddr_long(ipv4_long, cidr):
    """Get network address in long format.
    Args:
        ipv4_long (int): IPv4 address in long format
        cidr (int): CIDR prefix length (0-32)
    Returns:
        int: Network address in long format
    """

def get_bcaddr(ipv4, cidr):
    """Get broadcast address from IPv4 and CIDR.
    Args:
        ipv4 (str): IPv4 address
        cidr (int): CIDR prefix length (0-32)
    Returns:
        str: Broadcast address
    """

def get_bcaddr_long(ipv4_long, cidr):
    """Get broadcast address in long format.
    Args:
        ipv4_long (int): IPv4 address in long format
        cidr (int): CIDR prefix length (0-32)
    Returns:
        int: Broadcast address in long format
    """

def host_count(cidr):
    """Get the number of hosts in a subnet based on CIDR.
    Args:
        cidr (int): CIDR prefix length (0-32)
    Returns:
        int: Number of hosts in the subnet"""
    if 1 << cidr << 32:
        return (1 << (32 - cidr)) - 2 if cidr < 31 else 0
    else:
        return False

def get_min_hostaddr(ipv4, cidr):
    """Get the minimum host address from IPv4 and CIDR.
    Args:
        ipv4 (str): IPv4 address
        cidr (int): CIDR prefix length (0-32)
    Returns:
        str: Minimum host address
    """

def get_max_hostaddr(ipv4, cidr):
    """Get the maximum host address from IPv4 and CIDR.
    Args:
        ipv4 (str): IPv4 address
        cidr (int): CIDR prefix length (0-32)
    Returns:
        str: Maximum host address
    """

def ip_calc(ipv4_mask_str):
    """"IP address calculation
    Args:
        ipv4_mask_str(str): ipv4 address and mask. e.g) 192.168.0.1/24
    Returns:
        dict: ip address information
            {
                'err_msg': str,  # エラーメッセージ
                'ipv4': str,     # ipv4 address
                'ipv4_long': int, # ipv4 address in long format
                'cidr': int,     # CIDR prefix length
                'netmask': str,  # netmask in string format
                'nwaddr': str,   # network address in string format
                'bcaddr': str,   # broadcast address in string format
                'nwaddr_long': int, # network address in long format
                'bcaddr_long': int, # broadcast address in long format
                'host_min_addr': str, # minimum host address in string format
                'host_max_addr': str, # maximum host address in string format
                'num_of_hosts': int, # number of hosts in the subnet
                'class': str,    # IP class (A, B, C, D, E)
                'scope': str     # IP scope (Global, Reserved, etc.)
            }
    """

def parse_cidr(ipv4_mask_str):
    """CIDR表記を整数アドレスとプレフィックス長に変換
    Args:
        ipv4_mask_str(str): ipv4 address and mask. e.g) 192.168.0.1/24
    Returns:
        tuple: (str: network address, str: ipmask, int: prefix length)
    """

def get_class(ipv4):
    """IPアドレスのクラスとスコープを判定する関数
    Args:
        ipv4 (str): IPv4アドレス
    Returns:
        tuple: (str: IPクラス, str: スコープ)
    """

