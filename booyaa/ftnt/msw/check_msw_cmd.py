from booyaa.ftnt.msw

mswcli = MswBackup()
mswcli.display = True

fg_addr = '172.16.201.201'
fg_user = 'admin'
fg_pass = 'P@ssw0rd'

msw_addr = '10.255.1.1'
msw_user = 'admin'
msw_pass = 'P@ssw0rd'


let = mswcli.set_target(fg_addr, fg_user, fg_pass)

let = mswcli.login_fgt()
let = mswcli.gen_msw_list()
# print(mswcli.fsw_list)

let = mswcli.logout_fgt()

let = mswcli.login_msw(msw_addr, msw_user, msw_pass)

let = mswcli.logout_msw()



