# 构建 Socialization 单文件 EXE（含前端静态资源与后端服务）
# 兼容 Windows PowerShell 5.1 与 7+
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$FrontendDir = Join-Path $Root "frontend"
$BackendDir = Join-Path $Root "backend"
$DesktopDir = Join-Path $Root "desktop"
$PyExe = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $PyExe)) {
    throw "未找到虚拟环境，请先运行 .\scripts\setup.ps1"
}

Write-Host "==> 构建前端静态资源..."
Push-Location $FrontendDir
try {
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) {
        throw "前端构建失败"
    }
}
finally {
    Pop-Location
}

Write-Host "==> PyInstaller 打包 EXE..."
Push-Location $DesktopDir
try {
    & $PyExe -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name Socialization `
        --paths $BackendDir `
        --add-data "$FrontendDir\dist;frontend_dist" `
        --add-data "$BackendDir\migrations;migrations" `
        --add-data "$BackendDir\alembic.ini;." `
        (Join-Path $DesktopDir "entry.py")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller 打包失败"
    }
}
finally {
    Pop-Location
}

$ExePath = Join-Path $DesktopDir "dist\Socialization.exe"
Write-Host "==> 构建完成: $ExePath"
