import re
from collections import defaultdict
import json

def parse_yamaha_filters(config_text):
    filters = {}
    filter_sets = defaultdict(list)
    secure_filters = defaultdict(lambda: {'in': [], 'out': []})

    for line in config_text.splitlines():
        line = line.strip()

        # Static filter
        m = re.match(r'^ip filter (\d+) (\w+) (\S+) (\S+) (\S+)', line)
        if m:
            num, action, src, dst, proto = m.groups()
            filters[int(num)] = {
                "type": "static",
                "action": action,
                "src": src,
                "dst": dst,
                "protocol": proto
            }
            continue

        # Dynamic filter
        m = re.match(r'^ip filter dynamic (\d+) (\w+) (\S+) (\S+) (\S+) (.+)', line)
        if m:
            num, action, src, dst, proto, rest = m.groups()
            filters[int(num)] = {
                "type": "dynamic",
                "action": action,
                "src": src,
                "dst": dst,
                "protocol": proto,
                "details": rest
            }
            continue

        # Filter set
        m = re.match(r'^ip filter set (\S+) (.+)', line)
        if m:
            name, nums = m.groups()
            filter_sets[name] = [int(n) for n in nums.split()]
            continue

        # Secure filter
        m = re.match(r'^ip lan(\d+) secure filter (in|out) (.+)', line)
        if m:
            lan, direction, nums = m.groups()
            secure_filters[f'lan{lan}'][direction] = [int(n) for n in nums.split()]
            continue

    return {
        "filters": filters,
        "filter_sets": dict(filter_sets),
        "secure_filters": dict(secure_filters)
    }

# 使用例

config_file = 'tmp/LGWAN.txt'
with open(config_file, 'r', encoding="cp932") as f:
    config = f.read()

parsed = parse_yamaha_filters(config)
print(json.dumps(parsed, indent=2, ensure_ascii=False))
