from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.api import FgtApi


fgt_info = {
    'fgt_addr': '172.16.201.201',
    'fgt_user': 'admin',
    'fgt_password': 'P@ssw0rd',
    'fgt_alias': None,
    'fgt_hostname': None,
    'timeout': '',
}


fgtapi = FgtApi(FgtInfo())
let = fgtapi.set_target(**fgt_info)
let = fgtapi.login()
let = fgtapi.logout()
print(fgtapi.fgt_info.__dict__)


