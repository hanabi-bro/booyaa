"""
## 概要
* pexpectでFortiGateの設定をバックアップ
  - pexpectでFortiGateにsshでログイン
  - 「get system console」を実行し結果を取得
  - 以下の様にoutputがstandardかmoreを判断
    ```
    output              : more
    ```
  - outputがmoreの場合は以下コマンドでstandardに変更
    ```
    config system console
    set output standard
    end
    ```
  - 「show」コマンドを実行し表示されるコンフィグをファイルに保存
  - コンフィグ出力の終了を確認
  - output standardに変更した場合は、元の設定に戻す
    ```
    config system console
    set output more
    end
    ```
  - ログアウトして終了
"""
import paramiko
import time
import re

HOST = '172.16.201.6'
USER = 'admin'
PASSWORD = 'P@ssw0rd'
BACKUP_FILE = 'fgt_backup.conf'

def wait_prompt(channel, prompt=r'[\r\n].*# ', timeout=30):
    """指定のプロンプトが返るまで待機して出力を返す"""
    buffer = ''
    start = time.time()
    while time.time() - start < timeout:
        if channel.recv_ready():
            data = channel.recv(1024).decode('utf-8')
            buffer += data
            if re.search(prompt, buffer):
                return buffer
        time.sleep(0.1)
    raise TimeoutError('プロンプト待ちタイムアウト')

def send_cmd(channel, cmd):
    """コマンド送信 + プロンプトまで出力を取得"""
    channel.send(cmd + '\n')
    return wait_prompt(channel)

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, look_for_keys=False)

    chan = client.invoke_shell()
    send_cmd(chan, '')  # コンソール設定モードに入る

    # 現在の output 設定を確認
    output = send_cmd(chan, 'get system console')
    match = re.search(r'output\s*:\s*(\w+)', output)
    original_output = match.group(1) if match else 'standard'
    print(f'Current output mode: {original_output}')

    # output が more の場合は standard に変更
    if original_output.lower() == 'more':
        send_cmd(chan, 'config system console')
        send_cmd(chan, 'set output standard')
        send_cmd(chan, 'end')

    # 「show」コマンドで全設定取得
    chan.send('show\n')
    config_data = ''
    while True:
        if chan.recv_ready():
            out = chan.recv(4096).decode('utf-8')
            config_data += out
            print
            if re.search(r'end[\r\n].*# ', out):  # 設定出力の終端（"end" + プロンプト）
                break
        time.sleep(0.2)

    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        f.write(config_data)

    print(f'Backup saved to {BACKUP_FILE}')

    # 出力モードを戻す
    if original_output.lower() == 'more':
        send_cmd(chan, 'config system console')
        send_cmd(chan, 'set output more')
        send_cmd(chan, 'end')

    # ログアウト
    chan.send('exit\n')
    chan.close()
    client.close()

if __name__ == '__main__':
    main()
