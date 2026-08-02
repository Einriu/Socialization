# dev-backend.ps1 - 单独启动后端（热重载）
# 兼容 Windows PowerShell 5.1 与 PowerShell 7+
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PyExe = Join-Path $Root "backend\.venv\Scripts\python.exe"

if (-not (Test-Path $PyExe)) {
    Write-Error "未找到虚拟环境，请先运行 .\scripts\setup.ps1"
    exit 1
}

Push-Location (Join-Path $Root "backend")
try {
    & $PyExe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
