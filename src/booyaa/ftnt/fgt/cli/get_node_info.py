# from booyaa.ftnt.fgt.cli import FgtCli


def get_node_info(cli):
    """ノード情報を取得"""
    let = cli.get.system_status.get()


    # コマンド実行エラー時は終了
    if let['code'] != 0:
        return let

    # ホスト名の抽出
    cli.fgt_info.hostname = cli.get.system_status.hostname

    # シリアル番号の抽出
    cli.fgt_info.serial = cli.get.system_status.serial

    # モデル, バージョン情報の抽出
    cli.fgt_info.model = cli.get.system_status.model
    cli.fgt_info.major = cli.get.system_status.major
    cli.fgt_info.minor = cli.get.system_status.minor
    cli.fgt_info.patch = cli.get.system_status.patch
    cli.fgt_info.build = cli.get.system_status.build
    cli.fgt_info.version = cli.get.system_status.version

    # manage vdom domainの抽出
    cli.fgt_info.manage_vdom = cli.get.system_status.manage_vdom

    # Virtual domain configuration
    # novdom: no-vdom, vdom: multi-vdom
    cli.fgt_info.vdom_mode = cli.get.system_status.vdom_mode

    # HAモードとHA roleの抽出
    cli.fgt_info.ha_mode = cli.get.system_status.ha_mode
    cli.fgt_info.ha_role = cli.get.system_status.ha_role

    # HAならHAノード情報の抽出
    let = cli.get.system_ha_status.get()
    if let['code'] != 0:
        return let
    
    cli.fgt_info.secondary_hostname = cli.get.system_ha_status.secondary_hostname
    cli.fgt_info.secondary_serial = cli.get.system_ha_status.secondary_serial

    # スイッチ情報取得
    let = cli.execute.switch_controller_get_conn_status.get()
    cli.fgt_info.msw_list = cli.execute.switch_controller_get_conn_status.msw_list

    # @todo ノードのエリアス取得

    # @todo 情報取得失敗時の処理
    return let

