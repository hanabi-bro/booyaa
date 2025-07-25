# Multi Ping
コマンドラインで並列でpingを実行
任意のディレクトリに配置してPathを通して使うのが推奨。
Pathを通さなくてもアプリディレクトリ上であれば実行は可能。

## Install
### Windows
1. 任意のディレクトリに解凍
    `c:\opt\appz\mping`に配置する例
    アーカイブのディレクトリに移動
    ```powershell
    cd c:\opt\tmp
    $tmpPath = [System.IO.Path]::GetTempPath()
    Expand-Archive -Path ".\mping_windows.zip" -DestinationPath "$tmpPath\mping" -Force
    robocopy "$tmpPath\mping\mping" "c:\opt\appz\mping" /E /MOVE
    Remove-Item "$tmpPath\mping\mping" -Force
    ```

2. 解凍したディレクトリにPathを通す
    #### 一時的なPATH追加
    ```powershell
    $env:Path += ";c:\opt\appz\mping"
    ```
    確認
    ```powershell
    $ENV:Path.Split(";")
    gcm mping
    ```
    #### ユーザ環境変数のPATHに追加
    ```powershell
    [Environment]::SetEnvironmentVariable("Path", "$env:Path", "User")
    ```
    確認
    ```powershell
    [System.Environment]::GetEnvironmentVariable("Path", "User").Split(";")
    ```
    #### システムグローバルのPATHに追加
    管理者権限で実行
    ```powershell
    [Environment]::SetEnvironmentVariable("Path", "$env:Path;c:\opt\appz\mping", "Machine")
    ```
    確認
    ```powershell
    [System.Environment]::GetEnvironmentVariable("Path", "Machine").Split(";")
    ```

    #### 現在のセッションにPathを反映
    ```powershell
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    ```
    ```確認
    $ENV:Path.Split(";")
    gcm mping
    ```


## Uninstall
### Windows
1. 環境変数からPathを削除
    `c:\opt\appz\mping`に配置した場合
    確認
    ```powershell
    [System.Environment]::GetEnvironmentVariable("Path", "User").Split(";")
    ```
    削除
    ```powershell
    Set-Item ENV:Path $ENV:Path.Replace("c:\opt\appz\mping", "")
    Set-Item ENV:Path $ENV:Path.Replace(";;", ";")
    [Environment]::SetEnvironmentVariable("Path", "$env:Path", "User")
    ```
    確認
    ```powershell
    [System.Environment]::GetEnvironmentVariable("Path", "User").Split(";")
    ```
    現在のセッションに反映（おまけ）
    ```powershell
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    $ENV:Path.Split(";")
    gcm mping
    ```

2. アプリをディレクトリごと削除
    パスが長いなどPowershellで消せない場合もあるのでDOS CMDで削除
    ```powershell
    cmd /c "rmdir /s /q c:\opt\appz\mping"
    ```


## Usage
Powershellまたはコマンドプロンプトで実行してください。
// Pathが通っていない場合は、フルパスまたは相対パスで直接指定すれば実行可能です。
実行ディレクトリに以下が作成されます。
* results: Ping結果ディレクトリ
* destination.csv: 宛先リスト

アプリディレクトリにある`mping.ini`でttlの変更などが可能です。

### destination_list.csvファイルで宛先指定
* デフォルトのdestination_list.csv
  - デフォルトのファイルが無い場合は自動で作成。
```powershell
mping
```

### コマンド引数で宛先指定
* 「-l」オプションの後に宛先を指定
* カンマ区切りで複数宛先の定可能
```powershell
mping -l 1.1.1.1,yahoo.co.jp
```

### 宛先ファイルを指定
* 「-f」オプションの後にファイルパスを指定
  - 実行ディレクトリからの相対パスかフルパスで指定
```powershell
mping  c:\opt\data\dst_list.csv
```

### タイムアウト指定
* 「--timeout」オプションの後に秒数を指定
* 0.5などでミリ秒指定も可能（1秒以下は非推奨）

### TTL指定
* 「--ttl」オプションの後にTTLを指定
* 1-255

