from urllib.parse import urljoin

class SystemCsf:
    def __init__(self, api):
        self.api = api

    def get(self):
        url = urljoin(self.api.base_url, 'monitor/system/csf')
        let = self.api.req(url, method='get')

        if let['code'] == 0:
            let['msg'] = f'monitor/system/csf {self.api.fg_addr}'
            pass
        else:
            let['msg'] = f'[Error] Fail monitor/system/csf {self.api.fg_addr}'

        return let

    def __sample(self):
        sample_response = {
        "http_method": "GET",
        "revision": "20.1.1216463408",
        "results": {
            "devices": {
            "fortigate": [
                {
                "appliance_info": [],
                "firmware_license": True,
                "path": "FGT60FTK20011089",
                "mgmt_ip_str": "",
                "mgmt_port": 0,
                "sync_mode": 1,
                "object_unification": 0,
                "saml_role": "disable",
                "ipam_status": "disable",
                "admin_port": 443,
                "serial": "FGT60FTK20011089",
                "fabric_uid": "",
                "host_name": "FG60F-Secondary",
                "firmware_version_major": 7,
                "firmware_version_minor": 4,
                "firmware_version_patch": 8,
                "firmware_version_build": 2795,
                "firmware_version_branch": 2795,
                "firmware_version_maturity": "M",
                "firmware_version_release_type": "GA",
                "device_type": "fortigate",
                "forticloud_id": "Confidential",
                "authorization_type": "serial",
                "model_name": "FortiGate",
                "model_number": "60F",
                "model": "FGT60F",
                "model_subtype": "",
                "model_level": "low",
                "eos": False,
                "limited_ram": True,
                "is_vm": False,
                "state": {
                    "hostname": "FG60F-Secondary",
                    "fext_enabled": True,
                    "fext_vlan_mode": False,
                    "snapshot_utc_time": 1748839586000,
                    "utc_last_reboot": 1748838977000,
                    "time_zone_offset": -540,
                    "time_zone_text": "(GMT+9:00) Asia/Tokyo",
                    "time_zone_db_name": "Asia/Tokyo",
                    "is_dst_observed": False,
                    "is_dst_timezone": False,
                    "date_format": "yyyy/MM/dd",
                    "date_format_device": "system",
                    "fortimanager_configured": False,
                    "centrally_managed": False,
                    "fortimanager_backup_mode": False,
                    "fips_cc_enabled": False,
                    "fips_ciphers_enabled": False,
                    "vdom_mode": "",
                    "management_vdom": "root",
                    "conserve_mode": False,
                    "bios_security_level": 1,
                    "image_sign_status": "certified",
                    "forticare_registration_level": 1,
                    "has_hyperscale_license": False,
                    "need_fs_check": False,
                    "carrier_mode": False,
                    "csf_enabled": False,
                    "csf_group_name": "",
                    "csf_upstream_ip": "",
                    "csf_sync_mode": "default",
                    "csf_object_sync_mode": "local",
                    "ha_mode": 0,
                    "is_ha_master": 1,
                    "ngfw_mode": "profile-based",
                    "forced_low_crypto": False,
                    "has_log_disk": False,
                    "has_local_config_revisions": True,
                    "lenc_mode": False,
                    "usg_mode": False,
                    "stateramp_mode": False,
                    "admin_https_redirection": True,
                    "config_save_mode": "automatic",
                    "usb_mode": False,
                    "security_rating_run_on_schedule": True,
                    "features": {
                    "gui-ipv6": False,
                    "gui-replacement-message-groups": False,
                    "gui-local-out": False,
                    "gui-certificates": False,
                    "gui-custom-language": False,
                    "gui-wireless-opensecurity": False,
                    "gui-app-detection-sdwan": False,
                    "gui-display-hostname": True,
                    "gui-fortigate-cloud-sandbox": False,
                    "gui-firmware-upgrade-warning": True,
                    "gui-forticare-registration-setup-warning": True,
                    "gui-auto-upgrade-setup-warning": False,
                    "gui-workflow-management": False,
                    "gui-cdn-usage": True,
                    "switch-controller": True,
                    "wireless-controller": True,
                    "fortiextender": True,
                    "fortitoken-cloud-service": True
                    }
                },
                "vdoms": [
                    "root"
                ],
                "vdom_info": {
                    "root": {
                    "central_nat_enabled": False,
                    "transparent_mode": False,
                    "ngfw_mode": "profile-based",
                    "features": {
                        "gui-proxy-inspection": False,
                        "gui-icap": False,
                        "gui-implicit-policy": True,
                        "gui-dns-database": False,
                        "gui-load-balance": False,
                        "gui-multicast-policy": False,
                        "gui-dos-policy": False,
                        "gui-object-colors": True,
                        "gui-route-tag-address-creation": False,
                        "gui-voip-profile": False,
                        "gui-ap-profile": True,
                        "gui-security-profile-group": False,
                        "gui-local-in-policy": False,
                        "gui-explicit-proxy": False,
                        "gui-dynamic-routing": False,
                        "gui-policy-based-ipsec": False,
                        "gui-threat-weight": True,
                        "gui-spamfilter": False,
                        "gui-file-filter": True,
                        "gui-application-control": True,
                        "gui-ips": True,
                        "gui-dhcp-advanced": True,
                        "gui-vpn": True,
                        "gui-sslvpn": False,
                        "gui-wireless-controller": True,
                        "gui-advanced-wireless-features": False,
                        "gui-switch-controller": True,
                        "gui-fortiap-split-tunneling": False,
                        "gui-webfilter-advanced": False,
                        "gui-traffic-shaping": True,
                        "gui-wan-load-balancing": True,
                        "gui-antivirus": True,
                        "gui-webfilter": True,
                        "gui-videofilter": False,
                        "gui-dnsfilter": True,
                        "gui-waf-profile": False,
                        "gui-dlp-profile": False,
                        "gui-virtual-patch-profile": False,
                        "gui-casb": False,
                        "gui-fortiextender-controller": True,
                        "gui-advanced-policy": False,
                        "gui-allow-unnamed-policy": False,
                        "gui-email-collection": False,
                        "gui-multiple-interface-policy": False,
                        "gui-policy-disclaimer": False,
                        "gui-ztna": False,
                        "gui-ot": False,
                        "gui-dynamic-device-os-id": False
                    },
                    "virtual_wire_pair_count": 0,
                    "is_admin_type_vdom": False,
                    "is_lan_extension_vdom": False,
                    "is_management_vdom": True,
                    "resolve_hostnames": True
                    }
                },
                "vdom_mode": False,
                "fweb_build": "eNp1kctO6zAQhnkWr5FoyqVJduPESQ2+HV/Sg4Q0SkuR2EJZob47Tgt1UsTGsr9/ZvzPzCeptGp4S8rP7xtSC6paotFceVLOF8Xt5UkKXNSogqTMnkmVa9Bq7VFwyT2rSbl7+9ie5DZwVJqUJH/O874oNrP1Nnvpb26zTVEsrq/7l1m2Ldb9mkxSTKCCV2jAL2Pu09X7rt+9blKMhHttB0OkXCTI1Q+8SVDXTMQaTevxbtaQqYCCdcOpV2e+489xFoda+QlakDhv6Vmoc6Iz6gj3l8QI8I22cjRZoNSy7mhi4uE4VwH0YLGFc0WCD5b7xyjKqC2hYwgd/gsQd+W5YqTMvnEFJniDUE3QCqaoVg4ds92wxh+2hHTnxqEMNU1EcPWA0LaWteBH/wldgcDYFkbH3moxkjw7TFeiC8Zo65N0wOmpmEdlwghE/d6N3rF/qmPMXWIGqoeYF7uL4siRW/FhZ86bxIIbtRICr39b6rj1IbZSawlc/ebHsn9xzGdzzP7/KXcChpr7/cUXoiXzWQ==",
                "fsw_version": 0,
                "fsw_list": [],
                "fap_version": 0,
                "fap_list": [],
                "fext_version": 0,
                "fext_list": [],
                "ha_mode": "active-passive",
                "is_ha_master": 1,
                "ha_list": [
                    {
                    "serial_no": "FGT60FTK20011089",
                    "hostname": "FG60F-Secondary",
                    "is_ha_primary": True
                    },
                    {
                    "serial_no": "FGT60FTK20099VM6",
                    "hostname": "FG60F-Primary",
                    "is_ha_primary": False
                    }
                ],
                "upgrade_status": "disabled",
                "upgrade_id": 0,
                "upgrade_path_index": 0,
                "device_upgrade_summary": {
                    "disabled": 0,
                    "initialized": 0,
                    "downloading": 0,
                    "device-disconnected": 0,
                    "ready": 0,
                    "coordinating": 0,
                    "staging": 0,
                    "cancelled": 0,
                    "final-check": 0,
                    "upgrade-devices": 0,
                    "confirmed": 0,
                    "done": 0,
                    "failed": 0
                },
                "subtree_members": [],
                "forticloud_id_list": {},
                "tree_has_multi_vdom": False,
                "ha_group_name": "labfg01",
                "ha_group_id": 255,
                "fabric_approval_support": False
                }
            ]
            },
            "protocol_enabled": False
        },
        "vdom": "root",
        "path": "system",
        "name": "csf",
        "status": "success",
        "serial": "FGT60FTK20011089",
        "version": "v7.4.8",
        "build": 2795
        }
