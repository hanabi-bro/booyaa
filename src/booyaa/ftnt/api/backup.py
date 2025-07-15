# from booyaa.ftnt.forti_api import FortiApi
from booyaa.ftnt.api.forti_api import FortiApi


target = '172.16.201.201'
user = 'admin'
password = 'P@ssw0rd'
fg_name = 'ラボFG01'

## 前回と同じように継承クラスにしたほうがよさそう

def backup(target, user, password, fg_name):
    api = FortiApi()
    let = api.set_target(target, user, password, fg_name)
    if let ['code'] != 0:
        return let

    let = api.login(target, user, password)
    if let['code'] != 0:
        return let

    let = api.backup()


if __name__ == '__main__':
    target = '172.16.201.201'
    user = 'admin'
    password = 'P@ssw0rd'
