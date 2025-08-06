from booyaa.ftnt.msw import FgtMswCli


if __name__ == '__main__':
    fgt_msw_cli = FgtMswCli()
    fgt_msw_cli.display = True  # デバッグ用に出力を有効化
    let = fgt_msw_cli.set_target(
        user='admin',
        password='P@ssw0rd',
        target='172.16.201.201',
    )

    fgt_msw_cli.gen_msw_list()
    msw_list = fgt_msw_cli.msw_list

    for msw in msw_list:
        msw.display = True
        if msw.status == 'Connected':
            msw.login_msw()
            let = msw.backup(backup_dir='./fg_config')
            # print(msw.fg_addr)
            # print(msw.fg_port)
            # print(msw.fg_user)
            # print(msw.fg_password)
            # print(msw.fg_alias)
            # print(msw.fg_hostname)
            # print(msw.fg_serial)
            # print(msw.fg_version)
            # print(msw.addr)
            # print(msw.port)
            # print(msw.user)
            # print(msw.password)
            # print(msw.hostname)
            # print(msw.serial)
            # print(msw.state)
            # print(msw.status)
            # print(msw.model)
            # print(msw.version)
            # print(msw.build)

            msw.logout_msw()
        else:
            continue

    # fgt_msw_cli.login()
    # print(fgt_msw_cli)

    # fgt_msw_cli.login()

