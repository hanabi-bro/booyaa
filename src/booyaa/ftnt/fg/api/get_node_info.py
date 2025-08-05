def get_node_info(api):
    if api.version >= '7.2.0':
        let = api.monitor.system.cfs.get()
        if let['code'] != 0:
            let['msg'] += ' Failed get_node_info()'
            return let

        res = let['output']
        res_data = let['output']['results']['devices']['fortigate']

        api.version = res['version'].lstrip('v')
        api.major, api.minor, api.patch = api.version.split('.')
        api.build = res['build']
        api.serial = res['serial']

        api.hostname = res_data['state']['hostname']
        api.model = res_data['model']                      # "model": "FGT60F"

        ha_mode_dict = {0:'Standalone', 1: 'Active-Active', 2: 'Active-Passive'}
        api.ha_mode = ha_mode_dict[res_data['state']['ha_mode']]
        api.ha_role = 'main' if res_data['state']['is_ha_master'] == 1 else 'secondary'

        # セカンダリノード情報
        _ha_list = res_data['state']['ha_list']
        if len(_ha_list) == 2:

            secondary_info = next(
                (l for l in _ha_list if l['serial_no'] != api.serial)
            )

            api.secondary_hostname = secondary_info['hostname']
            api.secondary_serial = secondary_info['serial_no']

        api.ha_mgmt_status = ''      # mgmt statusが有効ならHAは見ない
        api.ha_mgmt_interfaces = []  # さらに念のため見るならmgmt_interfacesが1以上


    elif api.version < '7.2.0':
        let = api.monitor.web_ui_state.get()
        if let['code'] != 0:
            let['msg'] += ' Failed get_node_info()'
            return let

        res = let['output']
        res_data = let['output']['results']

        api.version = res['version'].lstrip('v')
        api.major, api.minor, api.patch = api.version.split('.')
        api.build = res['build']
        api.serial = res['serial']

        api.hostname = res_data['hostname']
        api.model = res_data['model']                      # "model": "FGT60F"

        ha_mode_dict = {0:'Standalone', 1: 'Active-Active', 2: 'Active-Passive'}
        api.ha_mode = ha_mode_dict[res_data['ha_mode']]
        api.ha_role = 'main' if res_data['is_ha_master'] == 1 else 'secondary'

        # セカンダリノード情報
        let = api.monitor.system_ha_statistics.get()
        if let['code'] != 0:
            let['msg'] += ' Failed get_node_info()'
            return let

        _ha_list = let['output']['results']
        if len(_ha_list) == 2:

            secondary_info = next(
                (l for l in _ha_list if l['serial_no'] != api.serial)
            )

            api.secondary_hostname = secondary_info['hostname']
            api.secondary_serial = secondary_info['serial_no']

    return let