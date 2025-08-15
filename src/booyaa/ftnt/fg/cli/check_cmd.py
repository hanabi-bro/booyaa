from booyaa.ftnt.fg.cli import FortiCli

fgcli = FortiCli()
fgcli.display = False
let = fgcli.set_target('172.16.201.201', 'admin', 'P@ssw0rd', 'ラボFG01')
let = fgcli.login()
let = fgcli.execute_command('get system')
print(let)
let = fgcli.logout()
