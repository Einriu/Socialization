# Socialization

社会化助手 / 社交成长助手：一款面向个人的社交能力提升软件（人物信息管理 + 话题知识管理 + 社交准备 + 对话复盘 + AI 陪练 + 长期成长追踪）。

> 当前进度：**M0 初始化**（T0-1 ~ T0-6）。人物、互动、话题、AI 对话等业务功能尚未开始，属于后续里程碑。

## 技术栈

- 后端：Python 3.13 + FastAPI + SQLAlchemy + Alembic + Pydantic
- 前端：React + TypeScript（strict）+ Vite + Tailwind CSS + shadcn/ui
- 数据库：SQLite（WAL 模式，单文件，零安装）
- 运行环境：原生 Windows（无需 Docker / WSL / PostgreSQL）

## 快速开始

```powershell
# 1. 复制环境模板（可选，默认值即可运行）
Copy-Item .env.example .env

# 2. 一次性初始化：创建虚拟环境、安装依赖、初始化数据库
.\scripts\setup.ps1

# 3. 一键启动前后端
.\scripts\dev.ps1

# 4. 打开系统状态首页
# http://127.0.0.1:3000
```

健康检查：`http://127.0.0.1:8000/api/health`

## 目录结构

```text
Socialization/
├── backend/    # FastAPI 后端
├── frontend/   # React 前端
├── scripts/    # setup / dev / test / backup 脚本
├── data/       # SQLite 数据库、上传、备份、导出（gitignored）
├── docs/       # 架构与 API 文档
├── PRD.md      # 产品需求文档（只读）
├── DEVELOPMENT_PLAN.md  # 开发计划 v2.0（只读）
└── TASKS.md    # 任务清单 v2.0（只读）
```

## 文档

- [开发计划](DEVELOPMENT_PLAN.md)
- [任务清单](TASKS.md)
- [产品需求](PRD.md)

## 环境要求

- Python 3.13.5（含内置 SQLite 3.49+）
- Node.js 24.13.0 + npm 11.6+
- Git 2.55+
- 详见 [DEVELOPMENT_PLAN.md 第 8 节](DEVELOPMENT_PLAN.md)
