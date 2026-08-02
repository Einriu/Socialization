# Socialization 任务清单（TASKS.md）

> 版本：v2.0 ｜ 日期：2026-08-02 ｜ 配套：[DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)
>
> v2.0 依据本机 `installed-apps.txt` 的软件版本调整：原生 Windows + SQLite，无 Docker/WSL/PostgreSQL。P0 仍拆分为可逐项验收的开发任务。

## 使用说明

- 勾选 `[ ]` → `[x]` 表示完成；每项任务都有独立的“验收标准”，完成时逐条核对。
- 状态标记：`[x]` 已完成、`[~]` 进行中、`[ ]` 未开始。提交代码前必须通过质量门槛（lint/typecheck/测试）。
- 任务编号：`T0-1` 表示 M0 里程碑第 1 项，以此类推。
- 环境基线：Python 3.13.5、Node.js 24.13.0、npm 11.6.2、Git 2.55.0.2、PowerShell 7.6.3（脚本兼容 5.1）、VS Code 1.131.0、Chrome/Edge 150.x。

---

## 1. P0 里程碑总览

| 里程碑 | 目标 | 依赖 | 预估规模 |
|---|---|---|---|
| M0 初始化 | `.\scripts\dev.ps1` 一键启动前后端与 SQLite | — | M |
| M1 数据库 | 全部 P0 表与种子数据，Alembic（SQLite）迁移可升降级 | M0 | L |
| M2 人物与互动 | 人物/标签/事实/时间线/互动全链路 | M1 | L |
| M3 话题知识库 | 分类/话题/Tiptap 笔记/自动保存 | M1 | L |
| M4 AI 提供商 | 主密码加密、提供商 CRUD、适配器、模型同步 | M1 | L |
| M5 AI 对话 | 流式对话、保存历史、停止/重生成、关联面板 | M4 | L |
| M6 备份与导出 | JSON 导入导出、SQLite 备份/恢复、Markdown 导出 | M1 | M |
| M7 收尾 | README、手测、安全自查、最终验收 | M2–M6 | M |

> 并行建议：M2 与 M3 在 M1 完成后可并行；M6 与 M5 可并行（均依赖 M1/M4 的表）。

---

## 2. M0 初始化（项目可运行）

### T0-1 仓库初始化

- [x] 创建 `.gitignore`（node_modules、.venv、.env、data/、__pycache__）、`.editorconfig`、根 README 骨架、docs/ 目录。
- [x] 按 DEVELOPMENT_PLAN.md 第 5 节建立目录结构（P1/P2 目录可暂不创建）。
- [x] `data/` 目录创建并 gitignore（`socialization.db`、uploads、backups、exports 均不入库）。

**验收**：`git status` 干净可提交；目录结构与计划一致；PRD.md 与 installed-apps.txt 未被修改。

### T0-2 原生环境脚本与配置模板（替代 Docker Compose）

- [x] `scripts/setup.ps1`：创建 `.venv` → `pip install -r requirements.txt`（或 `uv pip sync`）→ `npm install` → `alembic upgrade head` → 初始化 `data/` 目录。
- [x] `scripts/dev.ps1`：并行启动后端（uvicorn 热重载）与前端（vite），Ctrl+C 一起退出；`dev-backend.ps1` / `dev-frontend.ps1` 单开脚本。
- [x] `scripts/test.ps1`：后端 ruff + pytest；前端 lint + typecheck + vitest。
- [x] `scripts/backup.ps1`：SQLite 快照（`VACUUM INTO` 或 backup API）+ JSON 导出到 `data/backups/`。
- [x] `.env.example`：`DATABASE_URL=sqlite:///E:/Socialization/data/socialization.db`、前端/后端端口、时区、`HTTPS_PROXY` 占位。
- [x] 脚本兼容 Windows PowerShell 5.1 与 PowerShell 7.6.3；路径含空格时使用引号包裹。

**验收**：新克隆仓库后 `.\scripts\setup.ps1` 一次成功；`.\scripts\dev.ps1` 启动后前端 `http://127.0.0.1:3000` 与后端 `http://127.0.0.1:8000` 均可访问。

### T0-3 后端骨架

- [x] FastAPI 应用工厂（`app/main.py`）：配置加载（Pydantic Settings）、CORS 白名单（仅 `http://127.0.0.1:3000` / `localhost:3000`）、统一响应格式与异常处理（`exceptions.py`、`response.py`）。
- [x] `core/database.py`：SQLite 引擎，`journal_mode=WAL`、`foreign_keys=ON`、`busy_timeout=5000`、`check_same_thread=False`。
- [x] `core/logging.py`：默认过滤 `Authorization`、`api_key`、自定义请求头等敏感字段；日志不落密钥。

**验收**：`uvicorn app.main:app --reload` 可启动；访问未知路径返回统一错误 JSON；日志中无明文密钥；SQLite 文件在 `data/` 下生成且为 WAL 模式。

### T0-4 健康检查

- [x] `GET /api/health`：返回应用版本、SQLite 连通状态（`SELECT 1`）、journal_mode、组件状态。

**验收**：`Invoke-WebRequest http://127.0.0.1:8000/api/health` 返回 200 且包含 `db: ok` 与 `journal_mode: wal`。

### T0-5 前端骨架

- [x] Vite + React + TypeScript（strict）+ Tailwind + shadcn/ui 初始化（Node 24.13.0 / npm 11.6.2 环境）。
- [x] 路由与左侧导航骨架；**只显示已实现模块**（Dashboard、人物、互动、话题、AI 助手、设置）。
- [x] 浅色/深色主题切换（存 `app_settings` 或 localStorage 兜底）。
- [x] vite dev proxy：`/api` → `http://127.0.0.1:8000`。

**验收**：`npm run dev` 打开 `http://127.0.0.1:3000`，导航可切换页面，主题切换生效；无空页面（未实现模块不出现）。

### T0-6 前后端联调冒烟

- [x] 前端启动页/状态栏调用 `/api/health` 并展示后端与数据库状态。

**验收**：前后端同时运行时，前端展示“后端已连接，SQLite 正常”；后端断开时前端显示明确错误态。

---

## 3. M1 数据库（迁移与种子）

### T1-1 Alembic 初始化（SQLite）

- [ ] Alembic 接入 SQLAlchemy 模型元数据；首个 baseline 迁移。
- [ ] SQLite 类型约定：`Uuid`（存 32 位十六进制字符串）、`DateTime`（UTC ISO 字符串）、`JSON`；后续 ALTER 使用 `batch_alter_table`。
- [ ] 验证 `alembic upgrade head` 与 `alembic downgrade -1` 均可执行。

**验收**：空库执行 `alembic upgrade head` 无报错；`downgrade` 后 `upgrade` 可重复执行；`data/socialization.db` 生成。

### T1-2 人物与标签表

- [ ] `persons`（5.2 字段 + `deleted_at`）、`tags`（名称/颜色/分组/系统标记）、`person_tags`（联合唯一约束）。
- [ ] 常用索引：persons.name、tags.name、person_tags(person_id)、person_tags(tag_id)。

**验收**：迁移生成正确外键与索引；联合唯一约束阻止重复绑定。

### T1-3 人物事实、重要日期与待跟进表

- [ ] `person_facts`（fact_type/content/source_type/confidence/is_sensitive/source_id）、`important_dates`、`follow_up_tasks`（标题/截止/完成/关联互动）。
- [ ] `follow_up_tasks` 关联 persons 与 interactions（可空）。

**验收**：三表可建可删；`person_facts.confidence` 的取值校验生效。

### T1-4 互动表

- [ ] `interactions`（4.3 全部字段 + `deleted_at`）、`interaction_participants`、`interaction_topics`。

**验收**：一次互动可关联多个 persons 与多个 topics；删除互动不影响人物。

### T1-5 话题表

- [ ] `topic_categories`（自引用树）、`topics`（掌握等级/最后复习时间/`deleted_at`）、`topic_notes`（`content_json` + `plain_text`）、`topic_person_links`。

**验收**：分类可建父子层级；笔记 JSON 字段可存 Tiptap 文档；话题↔人物多对多。

### T1-6 AI 提供商与模型表

- [ ] `ai_providers`（17.4 阶段五字段 + 加密密钥 BLOB、自定义请求头、代理、超时/重试、最后测试时间）。
- [ ] `ai_models`（4.7 模型字段 + provider_id + 来源 sync/manual + 启用状态）。

**验收**：提供商与模型级联正确；模型可标记来源与默认模型。

### T1-7 对话表

- [ ] `conversations`（mode/provider_id/model_id/summary/pinned/`deleted_at`）、`conversation_messages`（5.2 字段 + status/generated_by_ai/metadata）、`conversation_links`（person/topic/document 三态）。

**验收**：消息外键、角色/状态校验、会话↔人物/话题关联正常。

### T1-8 支撑表与种子数据

- [ ] `app_settings`、`backup_records`、`audit_logs`、`prompt_templates`（类型/标题/正文/可编辑标志）。
- [ ] 种子：20 个预设话题分类（4.4.1）、默认设置、内置 prompt 模板（17.6 列表）。

**验收**：`alembic upgrade head` 后种子数据存在；prompt 模板可恢复默认。

### T1-9 数据访问层基座

- [ ] Repository 基类：分页、软删除过滤、`updated_at` 自动维护、审计写入（create/update/delete/restore/import）。
- [ ] 统一异常映射（NotFound、Conflict、ValidationError）。

**验收**：任意 Repository 操作自动写审计；分页返回 `{items,total,page,page_size}`。

---

## 4. M2 人物与互动

### T2-1 人物 API

- [ ] `GET /api/persons`（分页/关键词/标签筛选）、`POST`、`GET/PATCH/DELETE /api/persons/{id}`。
- [ ] 软删除 + 审计；删除返回 204；彻底删除端点（`DELETE /api/persons/{id}/permanent`，二次确认参数）。

**验收**：接口测试覆盖 CRUD、分页、筛选、软删过滤、彻底删除。

### T2-2 标签 API

- [ ] tags CRUD（颜色/分组）、`PUT /api/persons/{id}/tags` 批量设置、按标签筛选人物。

**验收**：批量设置幂等；删除标签时 `person_tags` 级联清理。

### T2-3 人物事实 API

- [ ] `GET/POST /api/persons/{id}/facts`、`PATCH/DELETE /api/person-facts/{fact_id}`。
- [ ] source_type/confidence/is_sensitive 校验；AI 来源事实必须 `confidence=ai_inference` 且前端显示“未确认”徽标。

**验收**：接口测试覆盖创建、修改、删除、敏感标记；`ai_inference` 与 `confirmed` 视觉区分。

### T2-4 重要日期与待跟进 API

- [ ] `important_dates` CRUD；`follow_up_tasks` 基础 CRUD + 按人物/状态筛选。

**验收**：生日/纪念日可录入并出现在人物详情；跟进事项可标记完成。

### T2-5 人物时间线 API

- [ ] `GET /api/persons/{id}/timeline`：合并互动、事实、重要日期，按时间倒序，分页，条目带类型标识。

**验收**：录入互动+事实+日期后，时间线按时间正确排序且分页正确。

### T2-6 互动 API

- [ ] interactions CRUD；创建/更新时维护 participants、topics；互动“后续事项”自动落 `follow_up_tasks`。
- [ ] 列表支持按人物、话题、时间范围、互动方式筛选。

**验收**：一次互动关联 2 个人 + 2 个话题保存成功；后续事项出现在跟进列表。

### T2-7 前端：人物模块

- [ ] 人物列表（分页/筛选）、详情页（概览/标签/事实/日期/时间线/跟进）、新建/编辑表单。
- [ ] 标签管理器（颜色、批量编辑）；事实编辑带来源与确认徽标；删除二次确认。

**验收**：手测路径“新建人物 → 加标签 → 加事实（含敏感标记）→ 加重要日期 → 查看时间线”全通。

### T2-8 前端：互动模块

- [ ] 互动列表与表单（多人物选择、话题选择、后续事项）、互动详情、时间线联动。

**验收**：手测“记录一次互动 → 自动生成跟进事项 → 人物时间线出现该互动”全通。

### T2-9 M2 测试

- [ ] 单元：人物保存/软删、事实确认逻辑、分页工具、审计写入。
- [ ] 集成：建人→加标签→记互动→时间线；删除人物后关联数据不残留主数据。

**验收**：`pytest` 全绿；前端 `npm test` 关键组件通过。

---

## 5. M3 话题知识库

### T3-1 话题分类 API

- [ ] topic-categories 树形 CRUD（父级校验、循环引用校验）。

**验收**：创建两级分类成功；尝试把分类设为自身后代被拒绝。

### T3-2 话题 API

- [ ] topics CRUD（简介/掌握等级/最后复习时间/关联分类）；`PUT /api/topics/{id}/persons`。

**验收**：话题可挂分类、可关联人物；掌握等级枚举校验。

### T3-3 笔记 API

- [ ] `GET/PUT /api/topics/{id}/notes`：保存 Tiptap JSON + 自动抽取纯文本（标题/段落/列表）；`updated_at` 返回给前端做并发控制。

**验收**：写入 JSON 后纯文本正确生成；重复保存不丢内容；并发冲突返回 409。

### T3-4 Tiptap 编辑器集成

- [ ] 安装 Tiptap；支持标题、粗体/斜体/高亮、引用、表格、图片、代码块、待办清单、折叠内容。
- [ ] 内部链接（话题/人物引用节点）基础实现；渲染时 HTML 消毒（DOMPurify）。
- [ ] 自动保存（防抖 1–2s + 离开页面 flush + 冲突提示）。

**验收**：编辑→等待自动保存→刷新页面内容不丢；粘贴 HTML 无脚本注入；人物/话题引用可插入。

### T3-5 前端话题页

- [ ] 分类树、话题列表（按分类/关键词）、话题详情（信息 + 笔记编辑器 + 关联人物）、新建/编辑。

**验收**：手测“建分类 → 建话题 → 写笔记自动保存 → 关联人物”全通。

### T3-6 M3 测试

- [ ] 单元：纯文本抽取、分类循环校验、笔记并发控制。
- [ ] 集成：话题笔记保存往返；分类树读取。

**验收**：测试全绿。

---

## 6. M4 AI 提供商与模型

### T4-1 主密码与加密

- [ ] `security.py`：Argon2id 哈希与验证（`argon2-cffi`，纯 pip 依赖）；`encryption.py`：AES-256-GCM（`cryptography` 库，随机 nonce，密文+nonce 存储）。
- [ ] `POST /api/security/setup-master-password`（首次）、`POST /api/security/unlock`（启动解锁）、`POST /api/security/reset-keys`（清除全部已加密密钥）。
- [ ] 解锁状态保存在后端内存（进程重启需重新解锁）；未解锁时提供商相关接口返回 403。

**验收**：设置主密码→重启后端→解锁→加解密往返一致；错误密码被拒绝；日志无密钥与主密码；重置后密钥列表为空。

### T4-2 提供商 API

- [ ] providers CRUD；API Key 写时加密、读时仅返回 `has_api_key`/`key_hint`/掩码；`PATCH` 支持 `clear_api_key`。
- [ ] 启用/停用、代理与超时字段；删除提供商前确认（关联对话显示 provider 已删除）。

**验收**：接口测试确认响应体不含密钥；数据库字段为密文；日志无敏感头。

### T4-3 Provider Adapter

- [ ] `BaseAIProvider` 抽象：`test_connection` / `list_models` / `chat` / `stream_chat`。
- [ ] `OpenAICompatibleProvider` 通用实现（httpx，SSE 解析、重试、超时）；DeepSeek/OpenAI 为预设子类（不写死模型名）。
- [ ] `registry.py` 按 provider_type 实例化；业务代码不直接调用 SDK。

**验收**：用 mock 服务器验证请求体/SSE 解析/重试/超时；provider_type 路由正确。

### T4-4 模型管理

- [ ] `POST /api/providers/{id}/sync-models`（失败时给出可读错误，不覆盖手动模型）、`GET /api/providers/{id}/models`、手动添加模型、默认模型设置。

**验收**：DeepSeek 连接成功后同步到模型列表；手动添加的模型可编辑停用；断网时同步失败但不损坏已有数据。

### T4-5 前端：设置页（提供商）

- [ ] 首次启动引导（设置主密码）；提供商列表/表单（密钥输入后只显示掩码）、测试连接、同步模型、手动添加模型、默认模型选择。
- [ ] 未解锁状态显示“输入主密码解锁”界面。

**验收**：手测“配置 DeepSeek → 测试成功 → 同步模型 → 选默认模型”全通。

### T4-6 M4 测试

- [ ] 单元：加解密往返、密钥掩码、适配器请求转换、SSE 解析、日志过滤。
- [ ] 集成：创建提供商→测试连接（mock）→同步模型→默认模型保存。

**验收**：测试全绿；安全测试项（密钥不出日志）通过。

---

## 7. M5 AI 对话

### T5-1 对话 CRUD

- [ ] conversations CRUD（标题自动生成、重命名、固定、软删）；messages 分页读取。

**验收**：接口测试覆盖全生命周期；删除会话不删除关联人物/话题。

### T5-2 流式对话

- [ ] `POST /api/conversations/{id}/messages`：先持久化用户消息（status=completed）→ 调用适配器流式输出 → 逐条持久化 AI 消息（status=generating → completed）。
- [ ] AI 消息含 token/延迟/metadata；`generated_by_ai=true`；失败时用户消息保留、AI 消息 status=failed。

**验收**：SSE 分片输出到前端；刷新后历史完整；模拟模型失败时用户消息仍在且可重试。

### T5-3 停止与重新生成

- [ ] `POST /api/conversations/{id}/cancel`：取消进行中生成，AI 消息 status=stopped。
- [ ] `POST /api/conversations/{id}/messages/{mid}/regenerate`：替换同一条 AI 消息，失败原因留 metadata。

**验收**：生成中点击停止立即终止；重新生成后旧内容被新内容替换。

### T5-4 上下文组装服务

- [ ] `context_service.py`：按 4.6.3 顺序组装（全局规则→模式提示词→表达偏好→人物已确认信息→话题摘要→检索槽位(空)→会话摘要→最近消息→本次输入）。
- [ ] 敏感过滤：`is_sensitive` 或“禁止发送给外部模型”标记的事实不进上下文；未确认/`ai_inference` 不进“事实”区（可作候选提示）。
- [ ] `GET /api/conversations/{id}/context-scope`：返回将发送的类别清单与条数。

**验收**：单元测试覆盖过滤规则；人物 A 的信息不会出现在人物 B 的上下文中；context-scope 与实发内容一致。

### T5-5 对话关联

- [ ] `PUT /api/conversations/{id}/links`：关联人物/话题（文件槽位 P1）；对话页右侧面板展示当前关联与上下文范围。

**验收**：关联人物后新消息上下文包含该人物已确认事实；面板显示正确。

### T5-6 前端：对话页

- [ ] 对话列表/新建/重命名/删除；消息流式渲染（Markdown、代码块、引用展示）；复制、编辑用户消息重发、停止、重新生成。
- [ ] 提供商/模型选择；未配置提供商时的空状态引导；错误提示与重试按钮。

**验收**：手测“新建对话 → 选 DeepSeek → 提问 → 流式输出 → 刷新保留 → 停止/重新生成 → 关联人物查看上下文面板”全通。

### T5-7 M5 测试

- [ ] 单元：上下文组装、敏感过滤、消息状态机、SSE 事件序列。
- [ ] 集成：提供商→流式对话→历史保存；失败→保留→重新生成；隔离性测试（跨人物不泄漏）。

**验收**：测试全绿。

---

## 8. M6 备份与导出

### T6-1 JSON 全量导出/导入

- [ ] `POST /api/export`：导出全部核心数据为 JSON（不含密钥明文）；`POST /api/import`：先校验（schema + 外键引用）后导入，可选“覆盖/合并”模式。

**验收**：导出→清库→导入→数据完整一致；非法文件被拒绝并返回具体错误。

### T6-2 SQLite 备份与恢复

- [ ] `GET/POST /api/backups`：用 Python `sqlite3` backup API 生成一致性快照到 `data/backups/`（如 `socialization-20260802-1330.db`）；`backup_records` 记录路径/大小/状态。
- [ ] `POST /api/backups/{id}/restore`：恢复前需二次确认（参数 `confirm=true`），流程为“停止写连接 → 替换数据库文件 → 重建连接”；恢复前自动再生成一份安全快照。

**验收**：备份→删数据→恢复→数据回来；恢复按钮无确认参数时返回 400；恢复过程不破坏备份文件本身。

### T6-3 Markdown 导出

- [ ] `GET /api/export/persons/{id}.md`、`GET /api/export/topics/{id}.md`、`GET /api/export/conversations/{id}.md`（含元信息与 AI 标记）。

**验收**：导出的 Markdown 在本地可正常打开阅读，AI 内容带 `generated_by_ai` 标记。

### T6-4 前端：设置-备份页

- [ ] 导出/导入（含导入结果预览）、备份列表、创建备份、恢复确认流程、下载按钮。

**验收**：手测全流程；恢复前弹窗需输入确认词。

### T6-5 M6 测试

- [ ] 集成：备份→清库→恢复一致性；JSON 导入校验失败路径。

**验收**：测试全绿。

---

## 9. M7 收尾与最终验收

### T7-1 README

- [ ] 完整安装（依赖 installed-apps.txt 版本清单）、启动（`setup.ps1` + `dev.ps1`）、环境变量说明、使用说明、备份恢复步骤、主密码说明（含遗忘处理）。

**验收**：新环境（同版本软件）按 README 从零可复现。

### T7-2 端到端手测清单

- [ ] 按 M2–M6 手测路径完整执行一遍并记录结果。

**验收**：所有手测路径通过，无阻断性问题。

### T7-3 安全自查

- [ ] API Key/主密码不出现在日志、异常、前端响应；文件路径防穿越；笔记 HTML 消毒；删除二次确认；敏感事实不发送模型。

**验收**：安全测试用例通过（第 14 章 P0 适用项）。

### T7-4 体验与性能检查

- [ ] 所有列表分页；路由懒加载；错误提示与重试按钮；加载态/空态完整；删除确认全覆盖。

**验收**：首屏 < 2s（本地）；无未处理的 500。

### T7-5 最终验收（对照 PRD 17.1）

- [ ] 1 人物管理 ｜ 2 标签管理 ｜ 3 互动记录 ｜ 4 话题知识库 ｜ 5 Tiptap 笔记 ｜ 6 AI 提供商管理 ｜ 7 三种提供商接口 ｜ 8 模型同步+手动添加 ｜ 9 AI 流式对话 ｜ 10 对话历史保存 ｜ 11 人物/话题/对话关联 ｜ 12 API Key 加密保存 ｜ 13 导入导出与备份 ｜ 14 原生一键启动（替代 Docker Compose，见 DEVELOPMENT_PLAN.md 第 0 节偏差声明）。

**验收**：13 项功能 + 原生一键启动逐项演示通过，并对照 PRD 第 15 章 P0 适用项（1、2、3、4、7、8、9、10、11、13、14、15）全部满足。

---

## 10. P1/P2/P3 功能 backlog（随阶段细化）

### P1 知识库版本

- [ ] 文件上传（大小/类型限制、进度、哈希去重、版本管理）
- [ ] 解析器插件化：PDF、DOCX、PPTX、XLSX、TXT、Markdown、HTML（含消毒）
- [ ] 文本切分（500–800 字、80–150 重叠、保留标题/页码、表格独立）
- [ ] 嵌入提供商独立配置（OpenAI/兼容/本地嵌入模型）
- [ ] 向量检索：优先 `sqlite-vec`（pip 轮子，Windows/cp313）；轮子不可用则回退纯 Python（numpy）余弦相似度（个人知识库规模足够）
- [ ] 混合检索评分（6.4 权重入配置）+ 回答引用（片段 ID、页码）
- [ ] FTS5 全文搜索（人物/标签/字段/互动/话题/笔记/文件/对话/待办 + 筛选）
- [ ] 文档解析后台任务：FastAPI 进程内 asyncio 队列（无 Celery/Redis）
- [ ] 自定义字段（4.2.2 十种类型）
- [ ] CSV 人物导入、Markdown 笔记导入、文件夹批量上传
- [ ] 长对话压缩（阶段摘要、摘要历史、手动修改）
- [ ] `ai_usage_logs` 用量统计
- [ ] 人物关系基础 CRUD（`person_relationships`）

### P2 社交能力版本

- [ ] 聊天前简报（`/api/persons/{id}/briefing`，含开场/冷场/边界内容）
- [ ] 互动信息自动提取与“待确认”区域（提取→勾选→写入）
- [ ] 聊天复盘（AI 复盘 + 不自动写事实）
- [ ] AI 模拟聊天（13 种练习模式 + 角色参数）
- [ ] 多维度评分（10 维度，必须带对话证据）
- [ ] 社交目标设置与每周成长报告
- [ ] 间隔复习（1/3/7/14/30 天 + 四级反馈）
- [ ] 长期记忆与审批（保存/修改/仅本次/忽略）
- [ ] 待跟进提醒闭环（首页/人物详情）
- [ ] `users` / `user_profiles`（表达偏好、社交目标）

### P3 增强版本

- [ ] 人物关系图可视化
- [ ] OCR（图片文字识别）
- [ ] 音频转文字、视频字幕提取
- [ ] 网页收藏/浏览器扩展
- [ ] 移动端适配
- [ ] Tauri/Electron 桌面打包
- [ ] 本地模型（Ollama）接入
- [ ] 可选云同步

---

## 11. P0 测试矩阵（覆盖第 14 章 P0 适用项）

| 层级 | 覆盖点 | 对应任务 |
|---|---|---|
| 单元 | 人物保存、事实确认、标签批量、分页 | T2-9 |
| 单元 | 笔记纯文本抽取、并发控制 | T3-6 |
| 单元 | API Key 加解密、掩码、日志过滤 | T4-6 |
| 单元 | 适配器请求转换、SSE 解析、重试超时 | T4-6 |
| 单元 | 上下文组装、敏感过滤、状态机 | T5-7 |
| 集成 | 人物→互动→时间线 | T2-9 |
| 集成 | 提供商→流式对话→历史保存 | T5-7 |
| 集成 | SQLite 备份→恢复一致性、JSON 导入校验 | T6-5 |
| 集成 | 跨人物上下文隔离 | T5-7 |
| 安全 | 密钥不出日志、路径穿越、恶意 HTML、删除确认 | T7-3 |
