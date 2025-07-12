import pandas as pd

# データの作成
nic_list = [
    {'id': 'lan1', 'filter_in': ['100', '101', '102'], 'filter_out': ['200', '201', '202']},
    {'id': 'lan2', 'filter_in': ['103', '104', '105'], 'filter_out': ['203', '204', '205']},
]

filter_list = [
    {'id': '100', 'src_addr': ['192.168.0.0/24']},
    {'id': '101', 'src_addr': ['192.168.1.0/24']},
    {'id': '102', 'src_addr': ['192.168.2.0/24']},
    {'id': '103', 'src_addr': ['192.168.3.0/24']},
    {'id': '104', 'src_addr': ['192.168.4.0/24']},
    {'id': '105', 'src_addr': ['192.168.5.0/24']},
    {'id': '200', 'src_addr': ['172.16.0.0/24']},
    {'id': '201', 'src_addr': ['172.16.1.0/24']},
    {'id': '202', 'src_addr': ['172.16.2.0/24']},
    {'id': '203', 'src_addr': ['172.16.3.0/24']},
    {'id': '204', 'src_addr': ['172.16.4.0/24']},
    {'id': '205', 'src_addr': ['172.16.5.0/24']},
]

# DataFrameへの変換
nic_df = pd.DataFrame(nic_list)
filter_df = pd.DataFrame(filter_list)


df_nic_exploded = nic_df.explode('filter_in')
df_merged = pd.merge(df_nic_exploded, filter_df, left_on='filter_in', right_on='id', how='left')

print(df_merged)

# # filter_inとfilter_outの列を展開
# nic_in_df = nic_df.explode('filter_in').merge(filter_df, left_on='filter_in', right_on='id').groupby('id_x').agg(list).reset_index()
# nic_out_df = nic_df.explode('filter_out').merge(filter_df, left_on='filter_out', right_on='id').groupby('id_x').agg(list).reset_index()

# # 結果を結合してまとめる
# policy_list = []
# for name in nic_df['id']:
#     policy_list.append({
#         'name': name,
#         'filter_in': nic_in_df[nic_in_df['id_x'] == name][['id_y', 'src_addr']].to_dict(orient='records'),
#         'filter_out': nic_out_df[nic_out_df['id_x'] == name][['id_y', 'src_addr']].to_dict(orient='records')
#     })

# print(policy_list)
