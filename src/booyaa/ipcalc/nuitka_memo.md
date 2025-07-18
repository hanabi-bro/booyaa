nuitka ./src/booyaa/ipcalc `
  --msvc=latest `
  --standalone `
  --include-data-files=./src/booyaa/ipcalc/ipv4_reserved.csv=booyaa/ipcalc/ `
  --windows-icon-from-ico="./icon/ipcalc/ipcalc.ico" `
  --output-filename ipcalc
