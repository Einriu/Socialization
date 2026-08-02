# setup.ps1 - 一次性初始化：Python 虚拟环境、后端依赖、前端依赖、data 目录、数据库迁移
# 兼容 Windows PowerShell 5.1 与 PowerShell 7+
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$DataDir = Join-Path $Root "data"
$VenvDir = Join-Path $BackendDir ".venv"
$PyExe = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "==> Socialization setup (root: $Root)"

# 1. data 目录
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DataDir "backups") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DataDir "uploads") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DataDir "exports") | Out-Null
Write-Host "==> data 目录就绪"

# 2. Python 虚拟环境
if (-not (Test-Path $PyExe)) {
    Write-Host "==> 创建 Python 虚拟环境..."
    & python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        throw "创建 Python 虚拟环境失败"
    }
}
Write-Host "==> 虚拟环境就绪: $PyExe"

# 3. 后端依赖
Write-Host "==> 安装后端依赖..."
& $PyExe -m pip install --disable-pip-version-check -r (Join-Path $BackendDir "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "后端依赖安装失败"
}

# 4. 数据库迁移（当前仅 Alembic 空基线，M1 追加业务表）
Write-Host "==> 执行数据库迁移..."
Push-Location $BackendDir
try {
    & $PyExe -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        throw "数据库迁移失败"
    }
}
finally {
    Pop-Location
}

# 5. 前端依赖
Write-Host "==> 安装前端依赖..."
Push-Location $FrontendDir
try {
    & npm.cmd install
    if ($LASTEXITCODE -ne 0) {
        throw "前端依赖安装失败"
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "==> setup 完成。运行 .\scripts\dev.ps1 启动前后端。"
