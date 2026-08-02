# Socialization 项目开发规则（AGENTS.md）

本文件记录本项目的长期技术约束与开发规则。任何自动化开发代理（Codex 等）与人工开发者都必须遵守。规则的优先级：

1. 用户当轮给出的明确要求
2. `TASKS.md` v2.0
3. `DEVELOPMENT_PLAN.md` v2.0
4. `PRD.md`

当 PRD.md 与 v2.0 开发计划冲突时，以 TASKS.md 和 DEVELOPMENT_PLAN.md 为准；产品功能目标仍以 PRD.md 为依据。

## 固定技术约束

- 使用原生 Windows 环境开发与运行。
- 不安装、不使用 Docker。
- 不安装、不使用 WSL。
- 不使用 PostgreSQL 或 pgvector。
- 数据库使用 SQLite（Python 内置，WAL 模式 + `foreign_keys=ON` + `busy_timeout=5000`）。
- 后端：Python 3.13、FastAPI、SQLAlchemy、Alembic、Pydantic。
- 前端：React、TypeScript strict、Vite、Tailwind CSS、shadcn/ui。
- 所有服务默认只监听 `127.0.0.1`，不开放局域网。
- 不引入需要注册表写入、系统服务或系统级安装的依赖。

## 文档保护

- 不得修改 `PRD.md`、`DEVELOPMENT_PLAN.md`、`TASKS.md`、`installed-apps.txt`。
- 如需调整计划，先与用户确认，再单独提出变更方案。

## 阶段纪律

- 按 `TASKS.md` 的里程碑逐项推进（当前 M0：T0-1 至 T0-6）。
- 不得提前实现 P1、P2、P3 功能。
- 不得提前实现人物、互动、话题、AI 对话等业务功能（属于 M1 之后的里程碑）。
- 不得创建假接口、空壳功能，不得用 TODO 代替本阶段功能。
- 未实现的模块不在前端导航中出现，不创建空页面。
- 每完成一个可验证步骤，必须执行相应检查（lint、类型检查、测试、运行验证）。
- 不要一次生成整个项目；保持每个阶段可运行、可验收。

## 代码质量要求

- Python 代码必须添加类型注解（公开函数与类）。
- TypeScript 使用 strict 模式，禁止大量使用 `any`。
- 提交前必须运行：后端 ruff + pytest；前端 lint + typecheck + vitest，全部通过。
- 不允许通过删除测试、放宽类型检查、堆 `any` 或跳过命令来伪造通过。
- 遇到错误先定位并修复。

## 后端架构约定

- Router → Service → Repository → Model 分层；Router 不直接访问数据库，Service 不依赖 HTTP Request，Repository 只负责数据访问。
- 所有数据库修改必须通过 Alembic 迁移。
- 统一响应格式 `{code, message, data}`；列表统一分页 `{items, total, page, page_size}`。
- 时间一律 UTC 保存，前端按本地时区显示；核心数据使用 UUID。
- API Key 等敏感信息不得出现在日志、异常或前端响应中。

## 汇报格式

每个阶段完成后按以下 12 项汇报：

1. 本轮完成内容
2. 新增和修改的文件树
3. 安装的依赖
4. 数据库变化
5. API 列表
6. 实际执行过的命令
7. 测试结果
8. 手动启动步骤
9. 手动验收步骤
10. 已知限制
11. 尚未完成的 M0 项目
12. 下一步建议
