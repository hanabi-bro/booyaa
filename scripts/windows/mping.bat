@echo off
chcp 65001 > nul
setlocal

set "APP_NAME=multi_ping"
set "APP_DIR=booyaa\mping"

set "SCRIPT_DIR=%~dp0"
set "PYTHON=%SCRIPT_DIR%..\..\.venv\Scripts\python.exe"
set "TARGET=%SCRIPT_DIR%..\..\%APP_DIR%\%APP_NAME%.py"

if not exist "%PYTHON%" (
    echo [ERROR] python.exe が見つかりません: %PYTHON%
    exit /b 1
)
if not exist "%TARGET%" (
    echo [ERROR] %APP_NAME%.py が見つかりません: %TARGET%
    exit /b 1
)

"%PYTHON%" -X utf8 "%TARGET%" %*
exit /b %ERRORLEVEL%



