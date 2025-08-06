# Forti Config Backup
fortigateのバックアップを取得してファイルに保存する。
保存ディレクトリは`fg_config`(実行ディレクトリ上)

## Usage
### コマンドで直接指定
`forti_backup -t <宛先アドレス> -u <ユーザ名> -p <パスワード>`
オプションで`-n <ファイアウォール名>`を付けるとログファイルに<ファイアウォール名>を追記

### リストファイルで指定（複数可）
`forti_backup -f <宛先リストファイル>`

リストファイルフォーマット
```
<宛先アドレス>,<ユーザ名>,<パスワード>,[オプション]<FW名>
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
$app_name = "forti_backup"
$app_exe = "forti_backup.exe"
mkdir $app_dir
```

解凍してsymlinkを張る
```powershell
Expand-Archive -Path forti_backup_0.0.1_windows.zip -DestinationPath $app_dir -Force
New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_name\$app_exe"
```

## Install 補足
### windows
1. 任意のディレクトリに解凍して配置
    解凍した「forti_backup」ディレクトリを任意のディレクトリに配置する。
     例）`c:\opt\appz\forti_backup`に配置
     ```powershell
     Expand-Archive -Path forti_backup_windows.zip -DestinationPath C:\opt\appz -Force
     ```

2. 解凍したディレクトリにPathを通す
    パスは、一時的、永続化、symlink利用のいずれかが良いと思う。
    個人的には共通パスのsymlinkを使っている。

    #### 一時的なPATH追加
    ```powershell
    $env:Path += ";c:\opt\appz\forti_backup"
    ```
    確認
    ```powershell
    $ENV:Path.Split(";")
    gcm forti_backup
    ```

    #### 永続化(ユーザ環境変数)
    ```powershell
    $path = [Environment]::GetEnvironmentVariable('PATH', 'User')
    $path += ";c:\opt\appz\forti_backup"
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
    $path += ";c:\opt\appz\forti_backup"
    [Environment]::SetEnvironmentVariable("Path", $path, "Machine")
    ```
    確認
    ```powershell
    [System.Environment]::GetEnvironmentVariable("Path", "Machine").Split(";")
    ```

    #### symlink（共通パス）
    `c:\opt\bin`が共通パスの場合
    ```powersehll
    New-Item -ItemType SymbolicLink -Path "C:\opt\bin\forti_backup.exe" -Target "C:\opt\appz\forti_backup\forti_backup.exe"
    ```
    ```dos
    mklink C:\opt\bin\forti_backup.exe C:\opt\appz\forti_backup\forti_backup.exe
    ```
    確認
    ```powershell
    gcm forti_backup
    ```

### Linux
`~/.local/opt/ipcalc`に配置する場合

1. 任意のディレクトリに解凍
    ```bash
    mkdir -p ~/.local/opt
    tar zxf ipcalc_linux.tgx -C ~/.local/opt
    ```
2. パスの通ったディレクトリにsymlink
    ```bash
    ln -s ~/.local/opt/ipcalc/ipcalc ~/.local/bin/.
    ```
   `~/.local/bin`に新たにPATHを追加する場合
    ```bash
    mkdir -p ~/.local/bin
    [[ "$PATH" == *"$HOME/.local/bin"* ]] || export PATH=$PATH:$HOME/.local/bin
    ```
3. PATHの永続化
    ログインシェル(`.bash_pforile`がなければ`.profile`)が推奨だけど、分からない場合は`.bashrc`に追記でもよい
    ```bash
    [[ "$PATH" == *"$HOME/.local/bin"* ]] || export PATH=$PATH:$HOME/.local/bin
    ```

## Update
### Windows
1. 任意のディレクトリに解凍して中身を上書き
    // カスタマイズしている場合はconfig.iniを上書き変更しないように注意
    コマンドでやるならこれか(直接上書き)
    ```powershell
    Expand-Archive -Path forti_backup_windows.zip -DestinationPath C:\opt\appz -Force
    ```
    またはこっち(解凍してから上書き)
    ```powershell
    Expand-Archive -Path .\forti_backup_windows.zip -DestinationPath . -Force
    cd forti_backup
    robocopy "." "C:\opt\appz\forti_backup\" /E
    ```
### Linux
`~/.local/opt/forti_backup`に配置する場合
1. 任意のディレクトリに解凍して中身を上書き
    ```bash
    tar zxf forti_backup_linux.tgx -C ~/.local/opt
    ```

