def get_msw_list(fgtapi):
    fgtapi.fgtapi.login()
    let = fgtapi.fgtapi.monitor.switch_controller_managed_switch.get()
    fgtapi.fsw_list = fgtapi.fgtapi.monitor.switch_controller_managed_switch.fsw_list

