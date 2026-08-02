# dev.ps1 - 一键启动前后端；按 Enter 停止（会连同子进程一起结束）
# 兼容 Windows PowerShell 5.1 与 PowerShell 7+
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LogDir = Join-Path $Root "data\logs"
$BackendScript = Join-Path $PSScriptRoot "dev-backend.ps1"
$FrontendScript = Join-Path $PSScriptRoot "dev-frontend.ps1"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Shell = "powershell.exe"
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    $Shell = "pwsh"
}

$backend = Start-Process -FilePath $Shell `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $BackendScript) `
    -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $LogDir "backend.out.log") `
    -RedirectStandardError (Join-Path $LogDir "backend.err.log")

$frontend = Start-Process -FilePath $Shell `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $FrontendScript) `
    -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $LogDir "frontend.out.log") `
    -RedirectStandardError (Join-Path $LogDir "frontend.err.log")

Write-Host "后端: http://127.0.0.1:8000/api/health (PID $($backend.Id))"
Write-Host "前端: http://127.0.0.1:3000 (PID $($frontend.Id))"
Write-Host "日志: $LogDir"
Write-Host ""
Write-Host "按 Enter 停止前后端..."

try {
    $null = Read-Host
}
finally {
    foreach ($proc in @($backend, $frontend)) {
        if ($proc -and -not $proc.HasExited) {
            & taskkill.exe /PID $proc.Id /T /F | Out-Null
        }
    }
    Write-Host "已停止前后端。"
}
