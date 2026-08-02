# Socialization 任务清单（TASKS.md）

> 版本：v3.0 ｜ 日期：2026-08-02 ｜ 配套：[DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)
>
> v3.0（个人自用版）：将原 M0–M7 八个里程碑合并为 **R1–R3 三个大阶段**（决策 D16），任务按“功能块”粒度验收，减少对话轮次；并按 D15/D17 简化加密与企业级细节。

## 使用说明

- 勾选 `[ ]` → `[x]` 表示完成；每项任务都有独立“验收标准”。
- 状态标记：`[x]` 已完成、`[~]` 进行中、`[ ]` 未开始。提交前必须通过质量门槛（后端 ruff+pytest；前端 lint+typecheck+vitest）。
- 任务编号：`A1-1` 表示 R1 阶段第 1 项，以此类推。
- 环境基线：Python 3.13.5、Node.js 24.13.0、npm 11.6.2、Git 2.55.0.2、PowerShell 7.6.3（脚本兼容 5.1）、VS Code 1.131.0、Chrome/Edge 150.x。

---

## 1. 阶段总览

| 阶段 | 内容（合并自原里程碑） | 关键交付 | 验收主线 |
|---|---|---|---|
| R1 基础平台与人物/互动 | M0+M1+M2 | 一条命令启动、SQLite 全量 P0 表、人物/标签/事实/日期/跟进/互动/时间线（前后端） | 建人→加标签→记互动→看时间线 |
| R2 话题笔记与 AI 对话 | M3+M4+M5 | 话题分类/话题/Tiptap 笔记；提供商管理（简化加密）；SSE 流式对话与历史；关联人物/话题 | 建话题写笔记→配置 DeepSeek→流式对话可保存 |
| R3 备份与收尾 | M6+M7 | JSON 导入导出、SQLite 备份/恢复、Markdown 导出、README、端到端手测与安全自查 | 备份→清库→恢复成功；对照 17.1 全部通过 |

---

## 2. 已完成：M0 初始化（T0-1 ~ T0-6，提交 `410f70b`）

- [x] 仓库初始化：AGENTS.md、.gitignore、.editorconfig、README 骨架、docs/、data/（gitignored）。
- [x] 原生环境脚本：setup.ps1、dev.ps1、dev-backend.ps1、dev-frontend.ps1、test.ps1、backup.ps1；.env.example。
- [x] 后端骨架：FastAPI 应用工厂、Pydantic Settings、SQLite（WAL/foreign_keys/busy_timeout）、统一异常响应、敏感日志过滤。
- [x] `GET /api/health`：应用版本、SELECT 1、journal_mode。
- [x] 前端骨架：Vite + React 19 + TS strict + Tailwind 4 + shadcn/ui 配置、浅/深主题、/api 代理、系统状态首页。
- [x] 前后端联调冒烟（前端调用 /api/health 展示连接状态与错误重试）。
- [x] 基础测试：后端 pytest 12 项、前端 vitest 3 项全部通过；健康检查 200、WAL=wal 实测通过。

---

## 3. R1 基础平台与人物/互动

### A1-1 数据库：一次性建全部 P0 表 + 种子

- [ ] Alembic 迁移创建全部 P0 表：persons、tags、person_tags、person_facts、important_dates、follow_up_tasks、interactions、interaction_participants、interaction_topics、topic_categories、topics、topic_notes、topic_person_links、ai_providers、ai_models、conversations、conversation_messages、conversation_links、app_settings、backup_records、audit_logs、prompt_templates。
- [ ] 类型约定：UUID（存 32 位十六进制）、UTC 时间、JSON 字段；常用索引；`deleted_at` 软删除列。
- [ ] 种子数据：20 个预设话题分类、默认设置、内置 prompt 模板。

**验收**：`alembic upgrade head` / `downgrade -1` / `upgrade head` 均可执行；种子数据存在；无业务表遗漏。

### A1-2 数据访问基座

- [ ] Repository 基类：分页 `{items,total,page,page_size}`、软删除过滤、`updated_at` 维护、audit_logs 基础写入。
- [ ] 统一异常映射（NotFound/Conflict/ValidationError）。

**验收**：任一 Repository 操作自动写审计；分页与软删行为有测试覆盖。

### A1-3 人物与标签 API

- [ ] persons CRUD（列表分页/关键词筛选、软删+彻底删除、审计）。
- [ ] tags CRUD（颜色/分组）+ 人物标签批量设置。
- [ ] person_facts CRUD（source_type/confidence/is_sensitive）+ important_dates + follow_up_tasks 基础 CRUD。

**验收**：接口测试覆盖 CRUD、分页、软删、事实确认标记；前端可完成“新建人物→加标签→加事实→加重要日期”。

### A1-4 互动与时间线 API

- [ ] interactions CRUD：多人物、多话题关联；“后续事项”自动落 follow_up_tasks；列表按人物/话题/时间筛选。
- [ ] `GET /api/persons/{id}/timeline`：合并互动+事实+重要日期，时间倒序，分页。

**验收**：一次互动关联 2 人+2 话题；后续事项出现在跟进列表；时间线排序正确。

### A1-5 前端：人物与互动页面

- [ ] 人物列表/详情/表单（标签、事实带来源与确认徽标、重要日期、跟进、时间线）。
- [ ] 互动记录列表/表单（多人物/话题选择、后续事项）；删除二次确认。

**验收**：手测“建人→加标签→加事实→记互动→看时间线”全通。

### A1-6 R1 测试与验收

- [ ] 后端 pytest（人物/标签/事实/互动/时间线/分页/审计）+ 前端 vitest 关键组件；lint/typecheck 全绿。
- [ ] 运行 `.\scripts\dev.ps1` 完成 R1 端到端手测。

**验收**：全部检查通过；R1 验收主线可完整演示。

---

## 4. R2 话题笔记与 AI 对话

### A2-1 话题 API

- [ ] topic_categories 树形 CRUD（循环引用校验）；topics CRUD（掌握等级/最后复习时间）；话题↔人物关联。

**验收**：两级分类可建；话题可挂分类、关联人物。

### A2-2 话题笔记（Tiptap）

- [ ] 笔记 API：Tiptap JSON 存取 + 自动抽取纯文本 + 并发控制（updated_at）。
- [ ] Tiptap 编辑器：标题/粗斜体/高亮/引用/表格/图片/代码块/待办/折叠；渲染 HTML 消毒（DOMPurify）。
- [ ] 自动保存（防抖 + 离开页面 flush + 冲突提示）。

**验收**：编辑→自动保存→刷新不丢；粘贴 HTML 无脚本注入。

### A2-3 API Key 简化加密与提供商管理

- [ ] 本地密钥文件：首次运行自动生成 `data/.secret.key`（AES-GCM，cryptography 库）；无主密码、无解锁页（D15）。
- [ ] providers CRUD：API Key 写时加密、读时仅返回掩码/has_key/末 4 位；支持 clear_api_key；启用/停用。
- [ ] Provider Adapter：OpenAICompatibleProvider 通用实现 + DeepSeek/OpenAI 预设子类；test_connection/list_models/stream_chat/chat；模型同步 + 手动添加 + 默认模型。

**验收**：配置 DeepSeek→测试连接→同步/手动添加模型→选默认模型；数据库字段为密文；日志与响应无明文密钥；无主密码流程。

### A2-4 对话与上下文（简化）

- [ ] conversations CRUD（标题/重命名/固定/软删）+ messages 分页读取。
- [ ] 流式对话：用户消息先保存→SSE 流式→AI 消息落库（status 状态机 generating/completed/failed/stopped）；失败保留可重试；停止/重新生成。
- [ ] 对话关联人物/话题；简化上下文组装：人物已确认事实（过滤敏感/未确认）+ 话题摘要 + 最近消息；AI 内容标记 generated_by_ai。

**验收**：SSE 流式输出、刷新保留历史、停止/重新生成可用；人物 A 的信息不出现在人物 B 的对话。

### A2-5 前端：话题页、提供商设置页、对话页

- [ ] 话题列表/详情 + 笔记编辑器；提供商表单（密钥掩码、测试、模型管理）；对话页（流式渲染、复制、编辑重发、停止/重新生成、关联人物/话题）。

**验收**：手测“建话题写笔记→配置 DeepSeek→对话并关联人物/话题”全通。

### A2-6 R2 测试与验收

- [ ] 后端 pytest（笔记、加密往返、适配器请求转换、SSE 解析、上下文敏感过滤、状态机）+ 前端 vitest；lint/typecheck 全绿。

**验收**：全部检查通过；R2 验收主线可完整演示。

---

## 5. R3 备份与收尾

### A3-1 备份与导出（简化版，D17）

- [ ] JSON 全量导出/导入（校验后导入）；SQLite 快照备份/恢复（`sqlite3` backup API，恢复前二次确认并自动留安全快照）。
- [ ] 人物/话题/对话 Markdown 导出；前端设置-备份页（导出/导入/备份列表/恢复/下载）。

**验收**：备份→清库→恢复数据一致；JSON 导入非法文件被拒；不做恢复预览 UI。

### A3-2 README

- [ ] 完整安装（依赖版本）、启动、环境变量、使用、备份恢复、密钥文件说明（含“删除 .secret.key 即重置全部密钥”的提示）。

**验收**：新环境按 README 从零可复现。

### A3-3 端到端手测与安全自查

- [ ] R1/R2 手测路径完整执行；安全自查：密钥不出日志/异常/响应、路径防穿越、HTML 消毒、删除二次确认、敏感事实不发送模型。

**验收**：手测通过；安全用例全绿。

### A3-4 最终验收（对照 PRD 17.1）

- [ ] 1 人物管理 ｜ 2 标签管理 ｜ 3 互动记录 ｜ 4 话题知识库 ｜ 5 Tiptap 笔记 ｜ 6 AI 提供商管理 ｜ 7 三种提供商接口 ｜ 8 模型同步+手动添加 ｜ 9 AI 流式对话 ｜ 10 对话历史保存 ｜ 11 人物/话题/对话关联 ｜ 12 API Key 加密保存（本地密钥文件版）｜ 13 导入导出与备份 ｜ 14 原生一键启动（替代 Docker Compose）。

**验收**：13 项功能 + 原生一键启动逐项演示通过；对照 PRD 15 章 P0 适用项（1、2、3、4、7、8、9、10、11、13、14、15）全部满足。

---

## 6. 个人自用简化清单（相对原计划砍掉的部分）

- 主密码设置/解锁界面与 Argon2id 派生 → 本地密钥文件自动生成（D15）。
- 审计日志查看页、备份恢复预览、自动备份计划 → 不做（底层表保留基础写入，D17）。
- AI 上下文发送范围（context-scope）面板 → 只显示“已关联人物/话题”，不展示逐项类别清单。
- 人物/话题引用节点等 Tiptap 高级节点 → 个人版后置，保留基础富文本能力。
- 互动提取、聊天简报、复盘、练习等 → 属 P2，不提前实现。

---

## 7. P1/P2/P3 功能 backlog（随阶段细化，本轮不做）

### P1 知识库版本

- 文件上传与解析（PDF/DOCX/PPTX/XLSX/TXT/MD/HTML）、文本切分、嵌入配置、sqlite-vec/纯 Python 检索、文件问答与引用、FTS5 全局搜索、自定义字段、CSV/Markdown 导入、长对话压缩。

### P2 社交能力版本

- 聊天前简报、互动信息自动提取与用户确认、聊天复盘、AI 模拟聊天与多维度评分、社交目标、间隔复习、每周成长报告、长期记忆审批、待跟进提醒闭环。

### P3 增强版本

- 人物关系图、OCR、音频转文字、视频字幕、网页收藏/浏览器扩展、移动端适配、Tauri 桌面打包、本地模型（Ollama）、可选云同步。

---

## 8. 测试矩阵（合并版）

| 层级 | 覆盖点 | 对应任务 |
|---|---|---|
| 单元 | 人物/标签/事实/互动保存与软删、分页、审计 | A1-6 |
| 单元 | 笔记纯文本抽取与并发控制 | A2-6 |
| 单元 | API Key 加密往返、掩码、日志过滤 | A2-6 |
| 单元 | 适配器请求转换、SSE 解析、消息状态机 | A2-6 |
| 单元 | 上下文组装与敏感过滤 | A2-6 |
| 集成 | 人物→互动→时间线 | A1-6 |
| 集成 | 提供商→流式对话→历史保存与重试 | A2-6 |
| 集成 | SQLite 备份→恢复一致性、JSON 导入校验 | A3-1 |
| 安全 | 密钥不出日志、路径穿越、恶意 HTML、删除确认 | A3-3 |
