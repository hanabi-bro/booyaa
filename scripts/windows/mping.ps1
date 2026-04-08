$app_file = "mping.py"
$app_dir = "booyaa\mping"

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
$target = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot "..\..\$app_dir\$app_file"))

if (-not (Test-Path -LiteralPath $python)) {
    Write-Error "python.exe が見つかりません: $python"
    exit 1
}
if (-not (Test-Path -LiteralPath $target)) {
    Write-Error "$app_file が見つかりません: $target"
    exit 1
}
& $python -X utf8 $target @args
exit $LASTEXITCODE