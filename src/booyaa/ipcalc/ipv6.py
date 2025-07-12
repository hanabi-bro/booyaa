from re import compile, VERBOSE, IGNORECASE, sub, findall
from pathlib import Path
from csv import DictReader
import booya.ipcalc.ipv4 as ipv4

ipv6_reserved_csv = Path(__file__).parent / 'ipv6_reserved.csv'

if not ipv6_reserved_csv.exists():
    raise FileNotFoundError(f"Reserved IPv6 address CSV file not found: {ipv6_reserved_csv}")

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

def is_ip(ipv6):
    """check ipv6 host address format
    Args:
        ipv6 (str): ipv6 host address
    Returns:
        boole: valid: True, Invalid: False
    """
    if expand_ipv6(ipv6) is False:
        return False
    else:
        return True

def is_cidr(cidr):
    """check ipv6 cidr format
    Args:
        cidr (str): cidr notation
    Returns:
        boole: valid: True, Invalid: False
    """

    try:
        cidr = int(cidr)
        if 0 <= cidr <= 128:
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False
    except Exception as e:
        print(f"error: cidr value is some error in is_cidr() {e}")
        return False

def is_ipmask(ipmask):
    """check ipv6 mask format
    Args:
        ipmask (str): ipv6 mask address
    Returns:
        boole: valid: True, Invalid: False
    """
    if expand_ipv6(ipmask) is False:
        return False
    else:
        return True

def is_mask(mask):
    """check ipv4 mask address format
    Args:
        mask (str): ipv4 mask address
    Returns:
        boole: valid: True, Invalid: False
    """
    if is_cidr(mask):
        return True
    else:
        return False

def cidr2ipmask(cidr):
    """convert cidr to ipmask
    Args:
        cidr (int): cidr notation
    Returns:
        str: ipv6 mask address
    """
    if not is_cidr(cidr):
        raise False
    return ":".join(["ffff" if i < cidr // 16 else "0000" for i in range(8)]) + "::" if cidr % 16 == 0 else ":".join(["ffff" if i < cidr // 16 else "0000" for i in range(8)]) + ":" + "f" * (cidr % 16) + "::"

