from urllib.parse import urljoin

class SystemHa:
    def __init__(self, api):
        self.api = api

    def get(self):
        api_path = 'cmdb/system/ha'
        url = urljoin(self.api.base_url, api_path)
        let = self.api.req(url, 'get')

        if let['code'] == 0:
            let['msg'] = f'get {api_path} {self.api.fg_addr}'
            pass
        else:
            let['msg'] = f'[Error] Fail get {api_path} {self.api.fg_addr}'

        return let


"""
{
  "http_method":"GET",
  "revision":"4f036a22ff65e85d36c7eadc1c25a73b",
  "results":{
    "group-id":100,
    "group-name":"lab_ha01",
    "mode":"a-p",
    "sync-packet-balance":"disable",
    "password":"",
    "key":"",
    "hbdev":"\"wan2\" 100 ",
    "session-sync-dev":"",
    "route-ttl":10,
    "route-wait":0,
    "route-hold":10,
    "multicast-ttl":600,
    "load-balance-all":"disable",
    "sync-config":"enable",
    "encryption":"disable",
    "authentication":"disable",
    "hb-interval":2,
    "hb-interval-in-milliseconds":"100ms",
    "hb-lost-threshold":6,
    "hello-holddown":20,
    "gratuitous-arps":"enable",
    "arps":5,
    "arps-interval":8,
    "session-pickup":"disable",
    "session-pickup-connectionless":"disable",
    "session-pickup-expectation":"disable",
    "session-pickup-nat":"disable",
    "session-pickup-delay":"disable",
    "link-failed-signal":"disable",
    "uninterruptible-upgrade":"enable",
    "uninterruptible-primary-wait":30,
    "standalone-mgmt-vdom":"disable",
    "ha-mgmt-status":"disable",
    "ha-mgmt-interfaces":[
    ],
    "ha-eth-type":"8890",
    "hc-eth-type":"8891",
    "l2ep-eth-type":"8893",
    "ha-uptime-diff-margin":300,
    "standalone-config-sync":"disable",
    "logical-sn":"disable",
    "vcluster-id":0,
    "override":"enable",
    "priority":200,
    "override-wait-time":0,
    "schedule":"round-robin",
    "weight":"40 ",
    "cpu-threshold":"5 0 0",
    "memory-threshold":"5 0 0",
    "http-proxy-threshold":"5 0 0",
    "ftp-proxy-threshold":"5 0 0",
    "imap-proxy-threshold":"5 0 0",
    "nntp-proxy-threshold":"5 0 0",
    "pop3-proxy-threshold":"5 0 0",
    "smtp-proxy-threshold":"5 0 0",
    "monitor":"",
    "pingserver-monitor-interface":"",
    "pingserver-failover-threshold":0,
    "pingserver-secondary-force-reset":"enable",
    "pingserver-flip-timeout":60,
    "vdom":"",
    "vcluster2":"disable",
    "secondary-vcluster":{
      "vcluster-id":1,
      "override":"enable",
      "priority":128,
      "override-wait-time":0,
      "monitor":"",
      "pingserver-monitor-interface":"",
      "pingserver-failover-threshold":0,
      "pingserver-secondary-force-reset":"enable",
      "vdom":""
    },
    "ha-direct":"disable",
    "memory-compatible-mode":"disable",
    "memory-based-failover":"disable",
    "memory-failover-threshold":0,
    "memory-failover-monitor-period":60,
    "memory-failover-sample-rate":1,
    "memory-failover-flip-timeout":6,
    "failover-hold-time":0
  },
  "vdom":"root",
  "path":"system",
  "name":"ha",
  "status":"success",
  "http_status":200,
  "serial":"FGT60FTK20099VM6",
  "version":"v7.0.17",
  "build":682
}                                                                                                                                                                                                            ✓
"""