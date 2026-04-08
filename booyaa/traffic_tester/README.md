# BooYaa Traffic Tester
* サーバ、クライアント間で指定ポートでトラフィックの送受信が可能
* Iperf3やNTTTCPのように、管理通信用のポートは不要
* TCP, UDP, HTTP, HTTPSで任意のポートで待ち受け可能


## Usage
* サーバクライアント共通
  第一引数でサーバ・クライアントを指定
  - http-server
  - http-client
  - https-server
  - https-client
  - tcp-server 
  - tcp-client 
  - udp-server 
  - udp-client
* サーバ
  - 起動
    `traffc_tester 'mode' 'port'`
  - 停止
  　`Ctrl + c`
* クライアント
  - 起動
    `traffc_tester 'mode' 'server ip' 'port'`
    - `--duration`オプションで実行時間を指定可能、デフォルトは0で無停止
  - 停止
  　`Ctrl + c`

* サーバオプション
    ```
    --bind ADDR       Bind address (default: 0.0.0.0)
    --timeout SEC     Client idle timeout in seconds (default: 30)
    --interval SEC    Stats log interval in seconds (default: 1)
    --blocksize N     Send block size in bytes (default: 65536)
    --mode MODE       download | upload | both (default: download)
    --logdir DIR      Log directory (default: ./log_traffic)
    ```
* クライアントオプション
    ```
    --timeout SEC     Connection/idle timeout in seconds (default: 30)
    --interval SEC    Stats log interval in seconds (default: 1)
    --duration SEC    Run duration in seconds, 0=unlimited (default: 0)
    --blocksize N     Send block size in bytes (default: 65536)
    --mode MODE       download | upload | both (default: download)
    --logdir DIR      Log directory (default: ./log_traffic)
    ```

