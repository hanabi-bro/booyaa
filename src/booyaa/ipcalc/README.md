# BooYaa IPcalc
* IPアドレス/マスクからNWアドレスなどを計算
* 予約済みIPアドレスリスト
* CIDR値、Netmaskリスト


## Usage
### コマンドで直接指定
#### IP Address calc
IPアドレス/マスクからNW Address、BC Address、10進値、ホスト数、クラス、スコープなどを計算
```powershell
ipcalc <IPv4>/<CIDR>
ipcalc <IPv4>/<NET_MASK>
```

#### Special-Purpose IP Address Registries List
予約済みIPアドレス一覧
```powershell
ipcalc -i
```

#### Mask List (CIDR, Netmask List)
```powershell
ipcalc -m
```

## Install
### windows
`c:\opt\bin`にパスを通してsymlinkを張る場合のサンプル。
symlink使わない場合はアプリディレクトリをパスに追加する。
* c:\opt\binが無ければ作成してパスを通しておくこと

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
アプリ配置ディレクトリ（例ではc:\opt\apps\ipcalc）に配置
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\apps"
$app_name = "ipcalc"
$app_exe = "ipcalc.exe"
mkdir $app_dir
```

解凍してsymlinkを張る
```powershell
Expand-Archive -Path ipcalc_0.0.1_windows.zip -DestinationPath $app_dir -Force
New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_name\$app_exe"
```

