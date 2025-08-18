## FortiGate Backup

```powershell
python -m nuitka `
  --msvc=latest `
  --standalone `
  --follow-imports `
  --windows-console-mode=force `
  --output-filename=fgt_bak `
  --windows-icon-from-ico=./icon/forti_backup/FGT_BAK.ico `
  --include-data-files=./src/booyaa/ftnt/readme_fgt_bak.md=./ `
  ./src/booyaa/ftnt/fgt_backup.py
```

## ManagedSwitch Backup
```poewrshell
python -m nuitka `
  --msvc=latest `
  --standalone `
  --follow-imports `
  --windows-console-mode=force `
  --output-filename=msw_bak `
  --windows-icon-from-ico=./icon/forti_backup/MSW_BAK.ico `
  --include-data-files=./src/booyaa/ftnt/readme_msw_bak.md=./ `
  ./src/booyaa/ftnt/msw_backup.py
```

## FortiAnalyzer Backup
