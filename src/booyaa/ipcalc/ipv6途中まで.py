from re import compile, VERBOSE, IGNORECASE, sub, findall
from pathlib import Path
from csv import DictReader

ipv6_reserved_csv = Path(__file__).parent / 'ipv6_reserved.csv'

if not ipv6_reserved_csv.exists():
    raise FileNotFoundError(f"Reserved IPv6 address CSV file not found: {ipv6_reserved_csv}")

ipv6_regex_rfc3986 = compile(r'''
^(
([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4} |                         # 1: 正規フル形式
([0-9a-fA-F]{1,4}:){1,7}: |                                     # 2: "::"で末尾省略
([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4} |                     # 3: "::"を含むさまざまな短縮形
([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2} |
([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3} |
([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4} |
([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5} |
[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6}) |
:((:[0-9a-fA-F]{1,4}){1,7}|:) |
([0-9a-fA-F]{1,4}:){6}(
    [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}                 # 4: 埋め込みIPv4
) |
([0-9a-fA-F]{1,4}:){0,5}(
    :[0-9a-fA-F]{1,4}
){0,1}:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}
)$
''', VERBOSE)


ipv6_regex_rfc5952 = compile(r'''
^(
    (?:[0-9a-f]{1,4}:){0,7}[0-9a-f]{1,4} |                         # フル形式 or 省略なし
    (?:[0-9a-f]{1,4}:){1,7}: |                                    # 末尾省略
    :(?::[0-9a-f]{1,4}){1,7} |                                    # 先頭省略
    (?:[0-9a-f]{1,4}:){1,6}::(?:[0-9a-f]{1,4}:?){0,1} |           # "::" を含む省略（中央）
    (?:[0-9a-f]{1,4}:){1,5}::(?:[0-9a-f]{1,4}:?){0,2} |
    (?:[0-9a-f]{1,4}:){1,4}::(?:[0-9a-f]{1,4}:?){0,3} |
    (?:[0-9a-f]{1,4}:){1,3}::(?:[0-9a-f]{1,4}:?){0,4} |
    (?:[0-9a-f]{1,4}:){1,2}::(?:[0-9a-f]{1,4}:?){0,5} |
    [0-9a-f]{1,4}::(?:[0-9a-f]{1,4}:?){0,6} |
    ::(?:[0-9a-f]{1,4}:?){0,7}
)$
''', IGNORECASE | VERBOSE)


def is_ip(ipv6):
    """
    Check if the given string is a valid IPv6 address format.
    """
    return bool(ipv6_regex_rfc3986.match(ipv6)) or bool(ipv6_regex_rfc5952.match(ipv6))

def is_cidr(cidr):
    """
    Check if the given string is a valid CIDR notation.
    """
    try:
        if 0 <= int(cidr) <= 128:
            return True
    except ValueError:
        return False
    return False

def is_ipmask(mask):
    """
    Check if the given string is a valid IPv6 netmask format.
    """
    if not is_ip(mask):
        return False
    # HEX形式のIPアドレスを16進数に変換し、1が連続していることを確認
    hex_mask = mask.replace(':', '')
    if len(hex_mask) == 32:
        # 1が連続していることを確認
        if '0' in hex_mask and '1' in hex_mask:
            return False
        return True

    return False

def is_mask(mask):
    if is_cidr(mask):
        return True
    return False

def cidr2ipmask(cidr):
    """
    Convert CIDR notation to IPv6 netmask.
    """
    if not is_cidr(cidr):
        return False

    # CIDRを16進数のIPアドレスに変換
    mask = '1' * int(cidr) + '0' * (128 - int(cidr))
    hex_mask = ':'.join([mask[i:i+4] for i in range(0, 128, 4)])
    return hex_mask.replace('0:', ':').rstrip(':')

def ipmask2cidr(ipmask):
    """
    Convert IPv6 netmask to CIDR notation.
    """
    if not is_ipmask(ipmask):
        return False

    # HEX形式のIPアドレスを16進数に変換し、1が連続していることを確認
    hex_mask = ipmask.replace(':', '')
    if len(hex_mask) == 128:
        return hex_mask.count('1')

    return False

def parse_mask(mask):
    mask = str(mask).strip()
    if is_cidr(mask):
        cidr = int(mask)
        ipmask = cidr2ipmask(cidr)
    elif is_ipmask(mask):
        ipmask = str(mask)
        cidr = ipmask2cidr(ipmask)
    else:
        return False, False
    return cidr, ipmask

def is_ipv6_format(ipv6_str):
    """
    Check if the given string is a valid IPv6 address format.
    """
    # "/"が含まれていない場合はFalseを返す
    if '/' not in ipv6_str:
        return False
    # host部分とprefix部分に分割
    ipv6, cidr = ipv6_str.split('/')
    return is_ip(ipv6) and is_cidr(cidr)

def ip2long(ipv6):
    """
    Convert IPv6 address to long integer.
    """
    if not is_ip(ipv6):
        return False
    # IPv6アドレスを16進数に変換し、整数に変換
    hex_ipv6 = ipv6.replace(':', '')
    return int(hex_ipv6, 16)








# ipv6はフォーマットルールが煩雑なので、プリチェックしてから
# expandして再度validateする。
def pre_validate_ipv6(ipv6: str) -> bool:
    # 最低限のチェックを行う
    return ipv6.count("::") <= 1 and ":::" not in ipv6

def expand_ipv6(ipv6: str) -> str:
    if not pre_validate_ipv6(ipv6):
        return False

    # "::"を含む場合は、左側と右側に分割、含まない場合はそのまま
    left, _, right = ipv6.partition("::")
    left_parts = left.split(":") if left else []
    right_parts = right.split(":") if right else []
    compressed_block = 8 - (len(left_parts) + len(right_parts))
    parts = left_parts + (["0000"] * compressed_block) + right_parts
    parts = [part.zfill(4) for part in parts]

    expanded_ipv6 = ":".join(parts)
    if validate_expanded_ipv6(expanded_ipv6):
        return expanded_ipv6
    return False

def validate_expanded_ipv6(expanded: str) -> bool:
    parts = expanded.split(":")
    if len(parts) != 8:
        return False
    for part in parts:
        if not (1 <= len(part) <= 4 and all(c in "0123456789abcdefABCDEF" for c in part)):
            return False
    return True



def compress_ipv6(ipv6: str) -> str:
    parts = ipv6.split(':')
    # 各パートをゼロ取り除き（ただし全部ゼロなら "0" にする）
    parts = [part.lstrip('0') or '0' for part in parts]

    # 最長連続の "0" を "::" に変換（正規表現で見つける）
    zero_runs = findall(r'(?:0:){2,}', ':'.join(parts) + ':')  # 最長マッチを探す

    if zero_runs:
        longest = max(zero_runs, key=len)
        compressed = ':'.join(parts).replace(longest[:-1], '', 1)
        # "::" の位置で "::" に変換（先頭や末尾の ":" の扱いに注意）
        compressed = sub('(^|:)0(?=::|$)', '', compressed)
        compressed = sub(':{3,}', '::', compressed)
    else:
        compressed = ':'.join(parts)

    return compressed
