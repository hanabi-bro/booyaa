# Forti Config Backup
fortigateのバックアップを取得してファイルに保存する。
Secondary NodeはCLIでコンフィグを取得。
保存ディレクトリは`fg_config`(実行ディレクトリ上)


## CLI usage
### Primary Only
```
fgt_bak -t 172.16.201.201 -u admin -p P@ssw0rd
```

### Primary and Secondary
```
fgt_bak -t 172.16.201.201 -u admin -p P@ssw0rd -s
```

### Add Logfile Prefix
```
fgt_bak -t 172.16.201.201 -u admin -p P@ssw0rd -n "LABFG01"
```

## CSV File usage
```
fgt_bak -f target.csv
```

### target csv format is below
### target csv format is below
* [optional]header line
    - addr,user,password,alias,get_secokdary,backup_direcotry,https_port,ssh_port
* Data Line
    - <fortigate addr>,<username>,<passwod>,[optional]<logfile prefix>,[optional]<backup secondary node(via cli show),[optional]https port,[optional]ssh port>
e.g.)
```
addr,user,password,alias,get_secokdary,backup_direcotry,https_port,ssh_port
172.16.201.201,admin,P@ssw0rd,Lab-FG01,yes
192.0.2.1,nw_admin,P@ssw0rd
```


## Install
### windows
`c:\opt\bin`にパスを通してsymlinkを張る場合のサンプル。
symlink使わない場合はアプリディレクトリをパスに追加する。

詳細は[Install 補足](#Install 補足)を参照

* c:\opt\binが無ければ作成してパスを通す
環境変数設定画面の開き方
```
windowsキー　>  [env]と入力　> 「環境変数を編集」
```

コマンドでも出来るがちゃんと分かっていないとリスクはある
```powershell
$bin_dir = "c:\opt\bin"
mkdir $bin_dir
$path = [Environment]::GetEnvironmentVariable('PATH', 'User')
$path += ";$bin_dir"
[Environment]::SetEnvironmentVariable("Path", $path, "User")
```

* アプリを配置してsymlinkを張る
アプリ配置ディレクトリ（例ではc:\opt\apps）などの定義
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\apps"
$app_name = "fgt_bakup"
$app_exe = "fgt_bakup.exe"
mkdir $app_dir
```

解凍してsymlinkを張る
```powershell
Expand-Archive -Path fgt_bak_*_windows.zip -DestinationPath $app_dir -Force
New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_name\$app_exe"
```

* python3xx.dllをコピー
```powershell
copy "$app_dir\$app_name\python3*?.dll" $bin_dir\.
```

### Install 補足
共通パス使わない場合
1. 任意のディレクトリに解凍して配置
    解凍した「fgt_bak」ディレクトリを任意のディレクトリに配置する。
     例）`c:\opt\apps\fgt_bak`に配置
     ```powershell
     Expand-Archive -Path fgt_bak_0.0.2_windows.zip -DestinationPath C:\opt\apps -Force
     ```

2. 解凍したディレクトリにPathを通す
    パスは、一時的、永続化、symlink利用のいずれかが良いと思う。
    個人的には共通パスのsymlinkを使っている。

    #### 一時的なPATH追加
    ```powershell
    $env:Path += ";c:\opt\apps\fgt_bak"
    ```
    確認
    ```powershell
    $ENV:Path.Split(";")
    gcm fgt_bak
    ```

    #### 永続化(ユーザ環境変数)
    ```powershell
    $path = [Environment]::GetEnvironmentVariable('PATH', 'User')
    $path += ";c:\opt\apps\fgt_bak"
    [Environment]::SetEnvironmentVariable("Path", $path, "User")
    ```
    確認
    ```powershell
    [System.Environment]::GetEnvironmentVariable("Path", "User").Split(";")
    ```
    #### 永続化(システムグローバル)
    管理者権限で実行
    ```powershell
    $path = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
    $path += ";c:\opt\apps\fgt_bak"
    [Environment]::SetEnvironmentVariable("Path", $path, "Machine")
    ```
    確認
    ```powershell
    [System.Environment]::GetEnvironmentVariable("Path", "Machine").Split(";")
    ```

    #### symlink（共通パス）
    `c:\opt\bin`が共通パスの場合
    ```powershell
    cmd /c mklink C:\opt\bin\fgt_bak.exe C:\opt\apps\fgt_bak\fgt_bak.exe
    ```

    確認
    ```powershell
    gcm fgt_bak
    ```
