## FortiGate Backup

```powershell
python -m nuitka `
  --msvc=latest `
  --standalone `
  --follow-imports `
  --windows-console-mode=force `
  --output-filename=fgt_backup `
  --windows-icon-from-ico=./icon/forti_backup/FGT_BAK.ico `
  --include-data-files=./src/booyaa/ftnt/readme_fgt_backup.md=./ `
  ./src/booyaa/ftnt/fgt_backup.py
```

## ManagedSwitch Backup
```poewrshell
python -m nuitka `
  --msvc=latest `
  --standalone `
  --follow-imports `
  --windows-console-mode=force `
  --output-filename=msw_backup `
  --windows-icon-from-ico=./icon/forti_backup/MSW_BAK.ico `
  --include-data-files=./src/booyaa/ftnt/readme_msw_backup.md=./ `
  ./src/booyaa/ftnt/msw_backup.py
```

## FortiAnalyzer Backup
