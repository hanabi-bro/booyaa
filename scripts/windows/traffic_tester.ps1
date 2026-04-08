param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet(
        'http-server',
        'http-client',
        'https-server',
        'https-client',
        'tcp-server',
        'tcp-client',
        'udp-server',
        'udp-client'
    )]
    [string]$Mode,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

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

$moduleMap = @{
    'http-server'  = 'booyaa.traffic_tester.http.server'
    'http-client'  = 'booyaa.traffic_tester.http.client'
    'https-server' = 'booyaa.traffic_tester.https.server'
    'https-client' = 'booyaa.traffic_tester.https.client'
    'tcp-server'   = 'booyaa.traffic_tester.tcp.server'
    'tcp-client'   = 'booyaa.traffic_tester.tcp.client'
    'udp-server'   = 'booyaa.traffic_tester.udp.server'
    'udp-client'   = 'booyaa.traffic_tester.udp.client'
}

$module = $moduleMap[$Mode]

if (-not $module) {
    throw "Unknown mode: $Mode"
}

& $python -m $module @Rest
exit $LASTEXITCODE
