$module = "booyaa.ipcalc"

# symlinkの実体パスを取得
$symlinkPath = $MyInvocation.MyCommand.Path
$realPath = (Get-Item -LiteralPath $symlinkPath).Target

# Targetが相対パスの場合があるので絶対パスに変換
if (-not [System.IO.Path]::IsPathRooted($realPath)) {
    $realPath = [System.IO.Path]::GetFullPath(
        (Join-Path (Split-Path -Parent $symlinkPath) $realPath)
    )
}

$scriptRoot = Split-Path -Parent $realPath
$python = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot "..\..\.venv\Scripts\python.exe"))

if (-not (Test-Path -LiteralPath $python)) {
    Write-Error "python.exe が見つかりません: $python"
    exit 1
}

& $python -X utf8 -m $module @args
exit $LASTEXITCODE