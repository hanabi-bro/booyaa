from booyaa.ftnt.fgt import Fgt


fgt_login_params = {
    'addr': '172.16.201.201',
    'user': 'admin',
    'password': 'P@ssw0rd',
    'alias': '',
}

fgt = Fgt()
fgt.setup(**fgt_login_params)

fgt.cli.display = True
let = fgt.api.login()
let = fgt.api.logout()
print(fgt.__dict__)

let = fgt.cli.login()
let = fgt.cli.logout()
print(fgt.__dict__)
