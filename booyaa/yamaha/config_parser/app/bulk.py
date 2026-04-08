
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import Base
from app.db.session import engine, SessionLocal
from app.models import Nic, Filter, DynamicFilter, Address, Protocol

# データベース接続とセッションの設定

session = SessionLocal()

# 辞書からモデルインスタンスを作成する関数
def get_or_create(model, session, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

def add_filters_and_dynamic_filters(session, nic_data, filter_data, dynamic_filter_data):
    for filter_entry in filter_data:
        filter_instance = get_or_create(Filter, session, idx=filter_entry['idx'], action=filter_entry['action'], src_port=filter_entry['src_port'], dst_port=filter_entry['dst_port'])
        for addr in filter_entry['src_addr']:
            address_instance = get_or_create(Address, session, address=addr)
            filter_instance.src_addr.append(address_instance)
        for addr in filter_entry['dst_addr']:
            address_instance = get_or_create(Address, session, address=addr)
            filter_instance.dst_addr.append(address_instance)
        for proto in filter_entry['protocol']:
            protocol_instance = get_or_create(Protocol, session, protocol=proto)
            filter_instance.protocol.append(protocol_instance)

    for dynamic_filter_entry in dynamic_filter_data:
        dynamic_filter_instance = get_or_create(DynamicFilter, session, idx=dynamic_filter_entry['idx'])
        for addr in dynamic_filter_entry['src_addr']:
            address_instance = get_or_create(Address, session, address=addr)
            dynamic_filter_instance.src_addr.append(address_instance)
        for addr in dynamic_filter_entry['dst_addr']:
            address_instance = get_or_create(Address, session, address=addr)
            dynamic_filter_instance.dst_addr.append(address_instance)
        for proto in dynamic_filter_entry['protocol']:
            protocol_instance = get_or_create(Protocol, session, protocol=proto)
            dynamic_filter_instance.protocol.append(protocol_instance)

    # NICデータを処理
    for nic_entry in nic_data:
        nic_instance = get_or_create(Nic, session, idx=nic_entry['idx'], interface=nic_entry['interface'], address=nic_entry['address'], mtu=nic_entry['mtu'])
        for filter_idx in nic_entry['filter_in']:
            filter_instance = session.query(Filter).filter_by(idx=filter_idx).first()
            if filter_instance:
                nic_instance.filter_in.append(filter_instance)
        for dynamic_filter_idx in nic_entry['dynamic_filter_in']:
            dynamic_filter_instance = session.query(DynamicFilter).filter_by(idx=dynamic_filter_idx).first()
            if dynamic_filter_instance:
                nic_instance.dynamic_filter_in.append(dynamic_filter_instance)
        for filter_idx in nic_entry['filter_out']:
            filter_instance = session.query(Filter).filter_by(idx=filter_idx).first()
            if filter_instance:
                nic_instance.filter_out.append(filter_instance)
        for dynamic_filter_idx in nic_entry['dynamic_filter_out']:
            dynamic_filter_instance = session.query(DynamicFilter).filter_by(idx=dynamic_filter_idx).first()
            if dynamic_filter_instance:
                nic_instance.dynamic_filter_out.append(dynamic_filter_instance)

    session.commit()

# 実際のデータの挿入
nic_list = [
    {
        'idx': 'select 1',
        'interface': 'lan2',
        'address': None,
        'filter_in': ['101097', '101098', '101099', '101100', '101112'],
        'dynamic_filter_in': ['101100', '101101', '101102'],
        'filter_out': [101097', '101098', '101099', '101100', '101112'],
        'dynamic_filter_out': ['101100', '101101', '101102'],
        'mtu': '1454'
    }
]

filter_list = [
    {'idx': '101097', 'action': 'pass-log', 'src_addr': ['192.168.220.110', '192.168.220.111'], 'dst_addr': ['192.168.220.1', '192.168.220.2'], 'protocol': ['icmp'], 'src_port': '*', 'dst_port': '*'},
    {'idx': '101098', 'action': 'pass-log', 'src_addr': ['192.168.220.110', '192.168.220.111'], 'dst_addr': ['192.168.220.1'], 'protocol': ['*'], 'src_port': '*', 'dst_port': 'domain'},
    {'idx': '101099', 'action': 'pass-log', 'src_addr': ['192.168.220.110'], 'dst_addr': ['*'], 'protocol': ['tcp'], 'src_port': '*', 'dst_port': '*'},
    {'idx': '101100', 'action': 'pass-log', 'src_addr': ['192.168.220.9'], 'dst_addr': ['192.168.220.1'], 'protocol': ['icmp'], 'src_port': '*', 'dst_port': '*'},
]

dynamic_filter_list = [
    {'idx': '101100', 'src_addr': ['192.168.220.1'], 'dst_addr': ['*'], 'protocol': ['domain'], 'filter': None, 'in_list': None, 'out_list': None},
    {'idx': '101101', 'src_addr': ['192.168.220.110'], 'dst_addr': ['*.webconnect.hulft.com'], 'protocol': ['tcp'], 'filter': None, 'in_list': None, 'out_list': None},   
    {'idx': '101102', 'src_addr': ['192.168.220.110'], 'dst_addr': ['*.*.webconnect.hulft.com'], 'protocol': ['tcp'], 'filter': None, 'in_list': None, 'out_list': None}, 
    {'idx': '101111', 'src_addr': ['192.168.220.5', '192.168.220.200', '192.168.220.205', '192.168.220.254'], 'dst_addr': ['globalsdns.fortinet.net'], 'protocol': ['domain'], 'filter': None, 'in_list': None, 'out_list': None },
]
```

add_filters_and_dynamic_filters(session, nic_list, filter_list, dynamic_filter_list)
