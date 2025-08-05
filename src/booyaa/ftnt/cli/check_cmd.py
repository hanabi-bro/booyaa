from booyaa.ftnt.cli import FortiCli

fgcli = FortiCli()
let = fgcli.set_target('172.16.201.201', 'admin', 'P@ssw0rd', 'ラボFG01')
let = fgcli.login()
let = fgcli.execute.switch_controller_get_conn_status.get()
print(fgcli.execute.switch_controller_get_conn_status.fsw_list)

let = fgcli.logout()
