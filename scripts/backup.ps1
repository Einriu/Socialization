# backup.ps1 - 使用 SQLite backup API 生成一致性快照
# 兼容 Windows PowerShell 5.1 与 PowerShell 7+
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DbPath = Join-Path $Root "data\socialization.db"
$BackupDir = Join-Path $Root "data\backups"

if (-not (Test-Path $DbPath)) {
    Write-Error "数据库不存在: $DbPath（请先运行 setup.ps1 并至少启动过一次后端）"
    exit 1
}

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupPath = Join-Path $BackupDir "socialization-$Timestamp.db"

$PyExe = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $PyExe)) {
    $PyExe = "python"
}

& $PyExe -c 'import sqlite3, sys; src, dst = sys.argv[1], sys.argv[2]; s = sqlite3.connect(src); d = sqlite3.connect(dst); s.backup(d); d.close(); s.close(); print("OK")' $DbPath $BackupPath
if ($LASTEXITCODE -ne 0) {
    throw "SQLite 备份失败"
}

$Size = (Get-Item $BackupPath).Length
Write-Host "备份完成: $BackupPath ($Size bytes)"
