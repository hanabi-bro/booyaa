""" IP address calc
* int to ipv4
* ipv4 to int
* ipv6 in progress

"""
### メモ
## structのフォーマット文字列
# '!' ネットワークバイトオーダー(32bit)
# 'I' 符号なし整数(32bit, unsigned integer)
# 'B' バイト、'4B' = 'BBBB' = [0-255, 0-255, 0-255, 0-255]
# 'L' 符号なし整数(32bitまたは64bit, unsigned long)
#     プラットフォームにより変わる場合もあり、NWアドレス計算では'I'を使用したほうがよい
#
## rubyならこんな感じだったはず
# [631271850].pack('N').unpack('CCCC').join('.')
# => "37.160.113.170"
# "37.160.113.170".split(".").map(&:to_i).pack('CCCC').unpack('N')[0]
# => 631271850
#
## bit shiftで計算する場合、struct不要
# from struct import pack, unpack
from rich.live import Live
from rich.table import Table
import sys

import booyaa.ipcalc.ipv4 as ipv4_calc
from booyaa.ipcalc.ipv4 import IPv4

ipv4_calc = IPv4()

def update_table(ipinfo):
    if ipinfo['err_msg'] == '':
        ipinfo.pop('err_msg', None)
    else:
        ipinfo['err_msg'] = '\n'.join(ipinfo['err_msg'])

    table = Table(show_header=True)
    for i in ['name', 'value']:
        table.add_column(i)

    for k, v in ipinfo.items():
        table.add_row(str(k), str(v))

    return table


def tui_run(ip_str):
    if ipv4_calc.is_ipv4_format(ip_str) is True:
        ipinfo = ipv4_calc.ip_calc(ip_str)
        table = update_table(ipinfo)
    else:
        ipinfo = {'err_msg': [f'Invalid IPv4 address {ip_str}']}
        table = update_table(ipinfo)

    with Live(table, refresh_per_second=10) as live:
        live.refresh()


if __name__ == "__main__":
    from argparse import ArgumentParser, RawTextHelpFormatter
    from textwrap import dedent

    class MyArgumentParser(ArgumentParser):
        def error(self, message):
            print('error occured while parsing args : '+ str(message))
            self.print_help()
            sys.exit()

    msg = dedent("""\
    ~~~ IP Calc ~~~
    ipcalc <IPv4>/<CIDR>
    ipcalc <IPv4>/<NET_MASK>
    """)

    parser = MyArgumentParser(description=msg, formatter_class=RawTextHelpFormatter)
    parser.add_argument('ipaddr_mask', help='<ipv4>/<MASK> e.g.\nipcalc 172.16.201.10/24\n172.16.201.10/255.255.255.0')    # 必須の引数を追加
    args = parser.parse_args()    # 4. 引数を解析

    tui_run(args.ipaddr_mask)
