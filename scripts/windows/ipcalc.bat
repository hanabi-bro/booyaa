@echo off
chcp 65001 > nul
setlocal

set "APP_NAME=ipcalc"
set "MODULE=booyaa.ipcalc"

set "SCRIPT_DIR=%~dp0"
set "PYTHON=%SCRIPT_DIR%..\..\.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] python.exe が見つかりません: %PYTHON%
    exit /b 1
)


"%PYTHON%" -X utf8 -m "%MODULE%" %*
exit /b %ERRORLEVEL%
