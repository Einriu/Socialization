# Socialization

社会化助手 / 社交成长助手：一款面向个人的本地社交能力提升软件，覆盖 **人物信息管理、话题知识管理、互动记录、AI 对话** 主闭环（P0 已全部完成）。

> 技术方案为原生 Windows + SQLite（无需 Docker / WSL / PostgreSQL），详见 [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)。

## 功能

- **人物管理**：档案（姓名/昵称/关系/熟悉度/身份/摘要）、标签、事实（来源与确认标记、敏感标记）、重要日期、待跟进事项、时间线。
- **互动记录**：多人物关联、互动方式/时长/摘要/反馈/冷场记录、后续事项自动生成跟进。
- **话题知识库**：分类树、话题（掌握等级 1–6）、Tiptap 富文本笔记（标题/加粗/高亮/表格/图片/代码/待办/列表，自动保存）。
- **AI 对话**：多提供商（DeepSeek / OpenAI / OpenAI 兼容接口）、模型同步与手动添加、SSE 流式对话、历史保存、停止/重新生成、人物与话题上下文注入（敏感与未确认信息不发送）。
- **备份与导出**：SQLite 一致性快照备份/恢复（恢复前自动安全快照）、JSON 全量导入导出、人物/话题/对话 Markdown 导出。

## 环境要求

| 软件 | 版本 | 说明 |
|---|---|---|
| Python | 3.13.5（64 位） | 内置 SQLite 3.49+ |
| Node.js / npm | 24.13.0 / 11.6+ | |
| Git | 2.55+ | 可选 |
| PowerShell | 5.1 或 7.x | 脚本兼容两者 |

## 安装与启动

```powershell
# 1.（可选）复制环境模板
Copy-Item .env.example .env

# 2. 一次性初始化：创建虚拟环境、安装依赖、初始化数据库
.\scripts\setup.ps1

# 3. 一键启动前后端（按 Enter 停止）
.\scripts\dev.ps1

# 4. 打开 http://127.0.0.1:3000
```

单独启动：`.\scripts\dev-backend.ps1`（后端 http://127.0.0.1:8000）、`.\scripts\dev-frontend.ps1`。

## 环境变量（.env）

| 变量 | 默认值 | 说明 |
|---|---|---|
| `APP_NAME` / `APP_VERSION` | Socialization / 0.1.0 | 应用信息 |
| `DATABASE_URL` | `sqlite:///data/socialization.db` | SQLite 路径（相对项目根） |
| `BACKEND_HOST` / `BACKEND_PORT` | 127.0.0.1 / 8000 | 后端监听（仅本机） |
| `FRONTEND_PORT` | 3000 | 前端端口 |
| `CORS_ORIGINS` | 本地 3000 | JSON 数组 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `HTTPS_PROXY` | 空 | 可选代理（受限网络访问 AI 接口时） |

## 使用说明

1. **人物**：新建人物 → 详情页维护标签/事实/日期/跟进；记完互动后时间线自动汇总。
2. **互动记录**：选择关联人物，填写摘要与“后续事项”，保存后自动生成待跟进。
3. **话题**：建分类与话题，详情页写笔记（自动保存，冲突会提示刷新）。
4. **AI 助手**：先在“设置”配置提供商（选择 DeepSeek/OpenAI/兼容，填入 Base URL 与 API Key，可测试连接、同步或手动添加模型）→ 新建对话 → 选择提供商/模型、关联人物/话题 → 发送消息（流式输出，可停止/重新生成/复制）。
5. **设置**：提供商与模型管理、数据备份（JSON 导入导出、快照备份、恢复、下载）。

## 数据备份与恢复

- 备份：设置页“创建备份”，生成 `data/backups/socialization-时间戳.db`（SQLite 一致性快照，可下载）。
- 恢复：设置页对备份点“恢复”，需二次确认；恢复前自动生成 `pre-restore-时间戳.db` 安全快照。
- JSON 导出/导入：导出不含 API Key 明文；导入会先清空业务数据再写入，请确认后再操作。
- 命令行备份：`.\scripts\backup.ps1`。

## API Key 与安全说明

- API Key 在服务端用本地密钥文件加密（AES-256-GCM），数据库不存明文，前端只显示掩码与末 4 位，日志自动过滤。
- 密钥文件 `data/.secret.key` 首次运行自动生成；**删除该文件等于重置全部已加密 API Key**（需重新配置，无法恢复旧密钥）。
- 服务默认仅监听 `127.0.0.1`；笔记以结构化 JSON 保存（无原生 HTML 注入面）。
- 对话上下文只发送“已确认/用户观察”且非敏感的人物事实；AI 输出带“AI 生成”标记。

## 测试与质量

```powershell
.\scripts\test.ps1   # 后端 ruff + pytest；前端 lint + typecheck + vitest
```

- 后端：FastAPI 分层（Router → Service → Repository），Alembic 迁移，统一响应 `{code,message,data}`，分页 `{items,total,page,page_size}`，UTC 时间。
- 前端：React 19 + TypeScript strict + Vite 7 + Tailwind 4 + shadcn/ui 风格组件 + 内置 hash 路由。

## 目录结构

```text
Socialization/
├── backend/    # FastAPI 后端（app/models|schemas|repositories|services|providers|api、migrations、tests）
├── frontend/   # React 前端（src/pages|components|api|lib、tests）
├── scripts/    # setup / dev / test / backup
├── data/       # SQLite、uploads、backups、exports、.secret.key（gitignored）
├── docs/       # 技术文档
├── PRD.md / DEVELOPMENT_PLAN.md / TASKS.md / installed-apps.txt   # 只读规划文档
```

## 文档

- [产品需求](PRD.md) ｜ [开发计划](DEVELOPMENT_PLAN.md) ｜ [任务清单](TASKS.md)
- 已知限制与下一步见 [TASKS.md](TASKS.md) 的 P1/P2/P3 backlog（文件知识库、社交练习、增强功能）。
