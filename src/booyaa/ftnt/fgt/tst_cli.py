from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.cli import FgtCli

fgt_info = {
    'fgt_addr': '172.16.201.201',
    'fgt_user': 'admin',
    'fgt_password': 'P@ssw0rd',
    'fgt_alias': None,
    'fgt_hostname': None,
    'timeout': '',
}


fgtcli = FgtCli(FgtInfo())
fgtcli.display = True
let = fgtcli.set_target(**fgt_info)
let = fgtcli.login()

# let = fgtcli.execute_command('show system interface | grep .*')
# let = fgtcli.config_global()
# let = fgtcli.end_global()
# let = fgtcli.config_vdom()
# let = fgtcli.end_vdom()

let = fgtcli.login_secondary()
print(let)
let = fgtcli.logout_secondary()
print(let)


let = fgtcli.logout()


