## Install

### 事前準備
gitの改行変換は必ず無効にすること
* windows
```powershell
scoop isntall git
git config --global core.autocrlf false
scoop isntall uv git
uv python install 3.13.7
```

* linux
```bash
sudo apt-get install -y git
git config --global core.autocrlf false
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### リポジトリパス
```
https://github.com/hanabi-bro/booyaa.git
```

### clone
これを任意のディレクトリにclone
例）/opt/配下にする場合
* windows
```powershell
mkdir /opt/booyaa
cd /opt/booyaa
git clone https://github.com/hanabi-bro/booyaa.git .
uv sync
uv pip install -e .
```

* linux
```bash
mkdir -p ~/.local
cd ~/.local
git clone https://github.com/hanabi-bro/booyaa.git
cd booyaa
uv sync
sudo setcap 'cap_net_bind_service=+ep' $(readlink -f .venv/bin/python)
uv pip install -e .
```

### symlink
* windows
共通binディレクトリの利用を推奨、無ければ作成する。
```powershell
mkdir "c:\opt\bin"
```
パスを追加する
```
winキー押下 > `env`を入力 > `環境変数を編集`
```
ユーザ環境変数の`PATH`に共通binディレクトリを追加

**fgt_backup**
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa\scripts\windows"
$app_name = "fgt_backup"
$app_exe = "$app_name.ps1"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```

**msw_backup**
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa\scripts\windows"
$app_name = "msw_backup"
$app_exe = "$app_name.ps1"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```

**traffic_tester**
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa\scripts\windows"
$app_name = "traffic_tester"
$app_exe = "$app_name.ps1"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```

**ipcalc**
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa\scripts\windows"
$app_name = "ipcalc"
$app_exe = "$app_name.ps1"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```

**mping**
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa\scripts\windows"
$app_name = "mping"
$app_exe = "$app_name.ps1"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```

* linux
最近のディストリビューションなら~/.local/binは定義済みだと思うけど一応メモ
共通binディレクトリの利用を推奨、無ければ作成する。
```PATH
mkdir -p "$HOME/.local/bin"
```

PATHの追加, 永続化するなら~/.profileか~/.bashrcに追記。
より汎用的なLinuxのPATH追加は別途整理中
```bash
export PATH=$HOME/.local/bin:$PATH
```

**fgt_backup**
```bash
bin_dir="$HOME/.local/bin"
app_dir="$HOME/.local/booyaa/scripts/linux"
app_name="fgt_backup"
app_exe="$app_name.sh"

ln -fs $app_dir/$app_exe $bin_dir/$app_name
```

**msw_backup**
```bash
bin_dir="$HOME/.local/bin"
app_dir="$HOME/.local/booyaa/scripts/linux"
app_name="msw_backup"
app_exe="$app_name.sh"

ln -fs $app_dir/$app_exe $bin_dir/$app_name
```

**traffic_tester**
```bash
bin_dir="$HOME/.local/bin"
app_dir="$HOME/.local/booyaa/scripts/linux"
app_name="traffic_tester"
app_exe="$app_name.sh"

ln -fs $app_dir/$app_exe $bin_dir/$app_name
```

**ipcalc**
```bash
bin_dir="$HOME/.local/bin"
app_dir="$HOME/.local/booyaa/scripts/linux"
app_name="ipcalc"
app_exe="$app_name.sh"

ln -fs $app_dir/$app_exe $bin_dir/$app_name
```

**mping**
```bash
bin_dir="$HOME/.local/bin"
app_dir="$HOME/.local/booyaa/scripts/linux"
app_name="mping"
app_exe="$app_name.sh"

ln -fs $app_dir/$app_exe $bin_dir/$app_name
```


## 実行
任意のディレクトリに移動実行

### msw_backup
* symlinkあり
```
msw_backup -t 172.16.201.201 -u admin -p P@ssw0rd --msw_user admin --msw_password P@ssw0rd
```
* symlink無し
```
c:\opt\booyaa\.venv\Scripts\python.exe c:\opt\booyaa\msw_backup.py -t 172.16.201.201 -u admin -p P@ssw0rd --msw_user admin --msw_password P@ssw0rd
```

### fgt_backup
* symlinkあり
```
fgt_backup -t 172.16.201.201 -u admin -p P@ssw0rd
```
* symlink無し
```
c:\opt\booyaa\.venv\Scripts\python.exe c:\opt\booyaa\fgt_backup.py -t 172.16.201.201 -u admin
```

### traffic_tester
```
traffic_tester http-server 80
```
```
traffic_tester http-client 127.0.0.1 80 --duration 5
```

## 更新
```
cd /opt/booyaa
git pull origin main
```


## その他
### ipcalc
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa"
$app_name = "ipcalc"
$app_exe = "ipcalc.bat"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```

### mping
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa"
$app_name = "mping"
$app_exe = "mping.bat"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```

### Traffic Tester
```powershell
$bin_dir = "c:\opt\bin"
$app_dir = "c:\opt\booyaa"
$app_name = "traffic_tester"
$app_exe = "traffic_tester.ps1"

New-Item -ItemType SymbolicLink -Path "$bin_dir\$app_exe" -Target "$app_dir\$app_exe" -force
```
