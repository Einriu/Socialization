# test.ps1 - 后端 ruff + pytest；前端 lint + typecheck + vitest
# 兼容 Windows PowerShell 5.1 与 PowerShell 7+
$ErrorActionPreference = "Continue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PyExe = Join-Path $Root "backend\.venv\Scripts\python.exe"
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$failed = $false

if (-not (Test-Path $PyExe)) {
    Write-Error "未找到虚拟环境，请先运行 .\scripts\setup.ps1"
    exit 1
}

Write-Host "==> 后端 ruff check"
Push-Location $BackendDir
try {
    & $PyExe -m ruff check .
    if ($LASTEXITCODE -ne 0) {
        $failed = $true
    }
}
finally {
    Pop-Location
}

Write-Host "==> 后端 pytest"
Push-Location $BackendDir
try {
    & $PyExe -m pytest
    if ($LASTEXITCODE -ne 0) {
        $failed = $true
    }
}
finally {
    Pop-Location
}

Push-Location $FrontendDir
try {
    Write-Host "==> 前端 lint"
    & npm.cmd run lint
    if ($LASTEXITCODE -ne 0) {
        $failed = $true
    }

    Write-Host "==> 前端 typecheck"
    & npm.cmd run typecheck
    if ($LASTEXITCODE -ne 0) {
        $failed = $true
    }

    Write-Host "==> 前端 test"
    & npm.cmd run test
    if ($LASTEXITCODE -ne 0) {
        $failed = $true
    }
}
finally {
    Pop-Location
}

if ($failed) {
    Write-Host ""
    Write-Host "检查未全部通过，请修复后重试。" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "全部检查通过。" -ForegroundColor Green
