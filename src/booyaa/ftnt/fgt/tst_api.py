from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.api import FgtApi
from booyaa.common.export.save_file import save_debug_report, save_config

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
let = fgtapi.monitor.system_debug_download.get()
let = save_debug_report(
    content=let['output'],
    hostname=fgtapi.fgt_info.hostname,
    alias=fgtapi.fgt_info.alias,
    version=fgtapi.fgt_info.version,
)
print(let)

let = fgtapi.logout()
