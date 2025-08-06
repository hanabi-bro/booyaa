## forti config backup
[アイコン](https://icooon-mono.com/00180-%e3%83%80%e3%82%a6%e3%83%b3%e3%83%ad%e3%83%bc%e3%83%89%e3%81%ae%e3%82%a2%e3%82%a4%e3%82%b3%e3%83%b3%e7%b4%a0%e6%9d%90-%e3%81%9d%e3%81%ae3/)


```powershell
python -m nuitka `
  --standalone `
  --follow-imports `
  --windows-console-mode=force `
  --output-filename=forti_backup `
  --windows-icon-from-ico=./icon/forti_config_backup/favicon.ico `
  .\src\forti_config_backup\forti_backup.py
```


## 旧ビルドメモ
```powershell
python -m nuitka `
  --standalone `
  --follow-imports `
  --enable-console `
  --output-filename=forti_config_backup `
  --force-stderr-spec="{PROGRAM_BASE}.err.log" `
  --windows-icon-from-ico=./icon/forti_config_backup/favicon.ico `
  .\booya\forti_config_backup.py
```
