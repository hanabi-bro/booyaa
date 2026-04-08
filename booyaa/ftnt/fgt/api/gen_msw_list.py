def gen_msw_list(fgtapi):
    fgtapi.fgtapi.login()

    let = fgtapi.fgt_api.login()
    if let['code'] != 0:
        return let

    if fgtapi.fgt_api.version < '7.0.0':
        let = fgtapi.fgt_api.monitor.switch_controller_managed_switch.get()
        _list = fgtapi.fgt_api.monitor.switch_controller_managed_switch.msw_list
    elif '7.0.0' <= fgtapi.fgt_api.version:
        let = fgtapi.fgt_api.monitor.switch_controller_managed_switch_status.get()
        _list = fgtapi.fgt_api.monitor.switch_controller_managed_switch_status.msw_list

    fgtapi.fg_info.msw_list = _list

    return let

