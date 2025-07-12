from .config_object_parser import ConfigObjectParser
from copy import deepcopy

class FirewallAddress(ConfigObjectParser):
    def multi_parse(self, config_block_name, config_obj, category) -> list:
        # self.load_rule(category)
        category_config_obj = deepcopy(config_obj)

        for row in category_config_obj:
            eid = next(iter(row))
            row[eid]['eid'] = eid
            for rule in self.field_rule:
                row[eid].setdefault(rule['config_name'], rule['default_value'])

                if rule['view_key'] == 'interface':
                    print(rule)

            # address
            # ipmask
            if row[eid]['type'] == ['ipmask']:
                row[eid]['address'] = "/".join(row[eid]['subnet'])
            # iprange
            elif row[eid]['type'] == ['iprange']:
                row[eid]['address'] = [f"{row[eid]['start-ip'][0]}-{row[eid]['end-ip'][0]}"]

            # fqdn
            elif row[eid]['type'] == ['fqdn']:
                row[eid]['address'] = row[eid]['fqdn']

            # wildcard, 6.4 under ?
            elif row[eid]['type'] == ['wildcard']:
                row[eid]['address'] = row[eid]['wildcard']

            # geography
            elif row[eid]['type'] == ['geography']:
                row[eid]['address'] = row[eid]['country']

            # interface-subnet ??
            elif row[eid]['type'] == ['interface-subnet']:
                row[eid]['address'] = row[eid]['subnet']

            # dynamic
            elif row[eid]['type'] == ['dynamic']:
                row[eid]['address'] = row[eid]['sub-type']

            # dynamic
            elif row[eid]['type'] == ['mac']:
                row[eid]['address'] = row[eid]['macaddr']

        return category_config_obj

