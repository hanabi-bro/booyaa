from .config_object_parser import ConfigObjectParser
from copy import deepcopy

class FirewallPolicy(ConfigObjectParser):
    def multi_parse(self, config_block_name, config_obj, category) -> list:
        # self.load_rule(category)
        category_config_obj = deepcopy(config_obj)

        for row in category_config_obj:
            eid = next(iter(row))
            row[eid]['eid'] = eid
            for rule in self.field_rule:
                row[eid].setdefault(rule['config_name'], rule['default_value'])

            # # srcaddr
            if row[eid]['internet-service-src'] == ['enable']:
                row[eid]['srcaddr'] = row[eid]['internet-service-src-name']

            # # dstaddr
            if row[eid]['internet-service'] == ['enable']:
                row[eid]['dstaddr'] = row[eid]['internet-service-name']

        return category_config_obj

