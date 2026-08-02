# dev-frontend.ps1 - 单独启动前端（vite dev server）
# 兼容 Windows PowerShell 5.1 与 PowerShell 7+
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$FrontendDir = Join-Path $Root "frontend"

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Error "未安装前端依赖，请先运行 .\scripts\setup.ps1"
    exit 1
}

Push-Location $FrontendDir
try {
    & npm.cmd run dev -- --host 127.0.0.1 --port 3000
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
