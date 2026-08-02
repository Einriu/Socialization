# Socialization 软件产品需求与开发方案

## 一、项目概述

### 1.1 项目名称

**Socialization**

中文名称可暂定为：**社会化助手 / 社交成长助手**

### 1.2 项目定位

Socialization 是一款面向个人使用的社会化能力提升软件，核心目标不是单纯记录联系人，而是建立一套完整的：

**人物信息管理 + 话题知识管理 + 社交准备 + 对话复盘 + AI 陪练 + 长期成长追踪系统。**

软件帮助用户解决以下问题：

1. 对认识的人的信息、喜好、经历和关系缺少系统整理。
2. 对聊天话题缺少持续积累，遇到具体对象时不知道聊什么。
3. 学到的知识分散在网页、PDF、Word、视频笔记和聊天记录中。
4. 每次聊天缺少提前准备和事后复盘。
5. 使用不同 AI 模型时，对话上下文无法统一保存。
6. 不清楚自己的社交弱点是否正在改善。

### 1.3 产品原则

1. **本地优先**：人物资料、聊天记录、文件和 API 密钥默认保存在用户本地。
2. **知识驱动**：不仅记录“对方喜欢什么”，还要帮助用户真正理解相关话题。
3. **辅助而非操控**：AI 用于提升倾听、共情、表达和理解能力，不用于欺骗或操纵他人。
4. **用户控制记忆**：AI 不得擅自把推测写入人物档案，重要记忆必须由用户确认。
5. **模型可替换**：DeepSeek、OpenAI及其他兼容模型可以自由添加、测试和切换。
6. **可解释引用**：AI 使用知识库内容回答时，应显示引用了哪些文件和笔记。

---

# 二、目标用户与主要场景

## 2.1 目标用户

首版只服务一个用户，即软件所有者本人，不需要团队协作和复杂权限体系。

## 2.2 主要使用场景

### 场景一：认识了一个新朋友

用户创建人物档案，记录：

- 姓名、昵称、头像和认识时间
- 认识途径
- 工作、专业、家乡和生活城市
- 兴趣、喜好、厌恶和近期目标
- 沟通风格
- 重要日期
- 已聊过的话题
- 下次可以继续追问的内容
- 用户与其相处时的感受

### 场景二：聊天前进行准备

用户选择某个人，软件自动生成：

- 最近一次互动摘要
- 对方最近提到的重要事情
- 不应重复询问的问题
- 可以自然延续的话题
- 相关话题知识卡片
- 可使用的开场方式
- 需要避免的敏感话题
- 本次聊天目标，例如“多听少说”“了解其最近工作变化”

### 场景三：学习某一类聊天话题

例如用户想学习“咖啡”“电影”“汽车”“健身”“旅行”“人工智能”。

用户可以：

- 创建话题知识库
- 上传文件和网页摘录
- 创建笔记
- 让 AI 总结核心知识
- 生成初级、中级和深入问题
- 生成适合自然聊天的表达
- 将话题关联到具体人物
- 设置复习任务

### 场景四：聊天结束后复盘

用户记录：

- 聊天对象、时间、地点和方式
- 聊了什么
- 对方透露的新信息
- 哪些话题反应较好
- 哪些地方让人不舒服或冷场
- 自己说得过多、过少或表达不清的地方
- 下一次需要继续了解的事情

AI 根据用户记录进行复盘，但不得把 AI 的推测直接当作事实保存。

### 场景五：AI 模拟聊天

用户指定一个人物或场景，例如：

- 与不太熟的同事吃饭
- 第一次参加聚会
- 与朋友久别重逢
- 与上级进行非正式交流
- 对方比较内向
- 聊天出现冷场

AI 扮演对方与用户进行模拟对话，结束后从倾听、追问、表达、共情、节奏和边界感等维度评分。

---

# 三、信息架构

软件左侧主导航建议设置为：

1. **首页**
2. **人物**
3. **互动记录**
4. **话题知识库**
5. **文件资料库**
6. **AI 助手**
7. **社交练习**
8. **复习计划**
9. **全局搜索**
10. **设置**

---

# 四、详细功能需求

## 4.1 首页仪表盘

首页展示当前最需要关注的信息。

### 首页组件

- 最近联系的人
- 长时间未联系的人
- 即将到来的生日或重要日期
- 待跟进事项
- 最近新增人物信息
- 最近学习的话题
- 今日复习卡片
- 本周社交互动次数
- 本周复盘完成率
- AI 建议的下一步行动
- 快速记录入口

### 快速操作

- 新建人物
- 记录一次互动
- 创建话题
- 上传文件
- 开始聊天准备
- 开始 AI 模拟对话
- 添加临时想法

---

## 4.2 人物管理

### 4.2.1 人物基础资料

每个人物支持以下字段：


| 分类     | 字段                                           |
| -------- | ---------------------------------------------- |
| 基础资料 | 姓名、昵称、头像、性别称谓、认识日期、认识地点 |
| 联系方式 | 电话、邮箱、微信、社交平台、备注               |
| 身份信息 | 公司、职业、职位、专业、学校、家乡、常住地     |
| 关系信息 | 关系类型、熟悉程度、关系状态、认识途径         |
| 个性信息 | 沟通风格、性格印象、情绪表达方式               |
| 喜好信息 | 兴趣、食物、音乐、电影、运动、品牌、旅行偏好   |
| 禁忌信息 | 不喜欢的话题、过敏事项、边界和敏感内容         |
| 重要事项 | 生日、纪念日、近期目标、正在处理的问题         |
| 用户记录 | 对方给我的感受、相处注意事项、未来跟进方向     |

其中“性格印象”等主观字段必须标注为：

- 用户明确观察
- 对方亲口表达
- AI 推测
- 尚未确认

### 4.2.2 自定义字段

用户可以创建自定义字段，例如：

- 喜欢的咖啡
- 宠物名字
- 游戏账号
- 最近看的电视剧
- 饮食禁忌
- 是否喜欢提前做计划

字段类型支持：

- 单行文本
- 多行文本
- 数字
- 日期
- 单选
- 多选
- 布尔值
- 链接
- 文件
- 人物关联

### 4.2.3 标签系统

支持系统标签和自定义标签，例如：

- 同事
- 同学
- 跑友
- 客户
- 朋友
- 家人
- 内向
- 喜欢旅行
- 对科技感兴趣
- 需要近期跟进

标签支持颜色、分组、筛选和批量编辑。

### 4.2.4 人物详情页

人物详情页包含：

1. 人物概览
2. 标签与喜好
3. 时间线
4. 互动记录
5. 已聊话题
6. 关联知识
7. 文件附件
8. 待跟进事项
9. AI 人物摘要
10. 聊天准备按钮

### 4.2.5 人物关系图

支持建立人物之间的关系：

- 同事
- 朋友
- 家人
- 上下级
- 伴侣
- 同学
- 共同兴趣
- 由某人介绍

后续可使用关系网络图展示人物连接，但不列入首版必须功能。

---

## 4.3 互动记录

一次互动可以是：

- 面对面聊天
- 电话
- 微信聊天
- 聚会
- 工作交流
- 一起运动
- 一起吃饭
- 其他活动

### 互动字段

- 标题
- 关联人物，可多选
- 时间
- 地点
- 互动方式
- 持续时间
- 互动摘要
- 讨论过的话题
- 对方新增信息
- 对方情绪或状态
- 自己的表现
- 正面反馈
- 冷场或问题
- 后续事项
- 相关文件或截图
- 隐私等级

### AI 提取功能

用户输入自然语言记录后，AI 可以生成建议：

- 可能的新人物信息
- 可能的新喜好
- 可创建的待办事项
- 可关联的话题
- 下次可继续追问的内容

所有提取结果必须先进入“待确认”区域，由用户勾选后写入档案。

---

## 4.4 话题知识库

话题知识库是本软件的核心模块。

### 4.4.1 话题分类

系统预设分类：

- 日常生活
- 工作与职业
- 学习与教育
- 科技与数码
- 电影与电视剧
- 音乐
- 游戏
- 运动
- 健身与健康常识
- 美食
- 咖啡与茶
- 旅行
- 城市与地域文化
- 汽车
- 时尚与消费
- 宠物
- 情感与关系
- 社会新闻
- 历史与文化
- 个人成长

用户可以创建自己的分类和多级目录。

### 4.4.2 话题内容结构

每个话题页面包含：

- 话题名称
- 简介
- 核心概念
- 入门知识
- 常见观点
- 最新笔记
- 常见误区
- 常用词汇
- 可用于聊天的事实
- 轻度问题
- 深入问题
- 个人观点
- 争议点
- 敏感点
- 关联人物
- 关联文件
- 信息来源
- 最后复习时间
- 掌握程度

### 4.4.3 话题掌握等级

每个话题可以标记为：

1. 未了解
2. 知道基本概念
3. 能进行简单交流
4. 能提出有质量的问题
5. 能表达自己的观点
6. 能进行深入讨论

### 4.4.4 富文本编辑

话题笔记应支持：

- 标题
- 加粗、斜体和高亮
- 引用
- 表格
- 图片
- 文件附件
- 待办清单
- 代码块
- 折叠内容
- 内部页面链接
- 人物引用
- 话题引用
- `/` 快捷命令

推荐使用 Tiptap 构建类似 Notion 的编辑器。Tiptap 是基于 ProseMirror 的无头富文本编辑框架，内容可保存为结构化 JSON，适合后续插入人物、话题、文件引用等自定义节点。

---

## 4.5 文件资料库

### 支持文件类型

首版支持：

- PDF
- DOCX
- PPTX
- XLSX
- TXT
- Markdown
- HTML
- 图片
- 网页文字粘贴

后续支持：

- 图片 OCR
- 音频转文字
- 视频字幕提取
- 网页自动抓取

### 文件处理流程

1. 用户上传文件。
2. 系统保存原始文件。
3. 提取文件文本。
4. 按标题、段落和长度切分内容。
5. 生成内容摘要。
6. 生成向量表示。
7. 写入知识库索引。
8. 用户将文件关联到人物或话题。
9. AI 回答时检索相关片段。
10. 回答底部显示引用文件和页码。

### 文件状态

- 等待处理
- 正在解析
- 已完成
- 部分失败
- 解析失败
- 等待重新处理

### 去重

使用文件哈希判断重复文件，同时允许同一文件更新版本。

---

## 4.6 AI 助手

### 4.6.1 AI 对话类型

AI 助手支持以下模式：

1. 通用对话
2. 人物分析
3. 聊天前准备
4. 聊天复盘
5. 话题学习
6. 文件问答
7. 社交模拟
8. 表达润色
9. 消息回复建议
10. 每周成长总结

### 4.6.2 对话保存

每次 AI 对话保存：

- 会话标题
- 创建时间
- 更新时间
- 使用的提供商
- 使用的模型
- 系统提示词
- 用户消息
- AI 消息
- 消耗量
- 响应时间
- 关联人物
- 关联话题
- 关联文件
- 检索到的知识片段
- 上下文快照
- 是否加入长期记忆

### 4.6.3 上下文组成

每次请求模型时，后端按以下顺序组装上下文：

1. 软件全局行为规则
2. 当前 AI 模式提示词
3. 用户个人资料和表达偏好
4. 当前关联人物的已确认信息
5. 当前关联话题摘要
6. 从文件知识库检索的相关片段
7. 当前会话摘要
8. 最近若干轮原始消息
9. 用户本次输入

不得把人物全部信息无条件发送给模型，只发送与当前问题相关的内容。

### 4.6.4 长对话压缩

当对话过长时：

- 保留最近消息
- 对较早消息生成阶段摘要
- 提取明确事实、用户偏好和未完成事项
- 保存摘要版本
- 支持查看摘要历史
- 用户可以重新生成或手动修改摘要

### 4.6.5 AI 记忆

记忆分为：

- 用户长期偏好
- 用户社交目标
- 用户常见问题
- 人物已确认事实
- 话题学习进度
- 当前会话临时记忆

AI 提议写入长期记忆时，展示：

> 建议记忆：你希望在聊天中减少连续讲述，多向对方提问。

用户可以选择：

- 保存
- 修改后保存
- 仅本次使用
- 忽略

---

## 4.7 API 提供商与模型管理

### 支持类型

首版支持：

1. DeepSeek
2. OpenAI
3. 通用 OpenAI 兼容接口
4. 自定义接口

后续增加：

- Anthropic
- Google Gemini
- 阿里云百炼
- 火山引擎
- 硅基流动
- 本地 Ollama

### API 提供商字段

- 提供商名称
- 提供商类型
- Base URL
- API Key
- 自定义请求头
- 是否启用
- 连接超时
- 最大重试次数
- 代理设置
- 默认聊天模型
- 默认推理模型
- 默认嵌入模型
- 创建时间
- 最后测试时间

### 模型字段

- 模型 ID
- 显示名称
- 模型类型
- 上下文长度
- 是否支持流式输出
- 是否支持工具调用
- 是否支持 JSON 输出
- 是否支持图片
- 是否支持推理内容
- 输入价格备注
- 输出价格备注
- 是否启用

### 模型同步

不要把任何提供商的模型名称永久写死在代码中。系统应优先动态获取模型列表，同时保留手动添加模型的能力。

### 提供商适配器接口

```typescript
interface AIProviderAdapter {
  testConnection(): Promise<TestResult>;
  listModels(): Promise<ModelInfo[]>;
  chat(request: ChatRequest): Promise<ChatResponse>;
  chatStream(request: ChatRequest): AsyncIterable<ChatEvent>;
  createEmbeddings?(request: EmbeddingRequest): Promise<EmbeddingResponse>;
}
```

不得在业务代码中直接调用某一家模型接口。所有模型调用必须经过适配器层。

---

## 4.8 聊天准备中心

用户选择人物后，系统生成一份“聊天简报”。

### 简报内容

- 人物关系和熟悉程度
- 最近三次互动摘要
- 对方近期重要事件
- 尚未跟进的事项
- 对方感兴趣的话题
- 已经重复聊过的话题
- 推荐延续的问题
- 与人物相关的知识卡片
- 本次聊天目标
- 需要注意的边界
- 三种开场方式
- 冷场时可切换的话题
- 结束聊天时的自然表达

### 生成原则

AI 生成的问题应避免：

- 审问式连续提问
- 过度私人化
- 利用对方脆弱信息
- 假装了解自己并不了解的内容
- 强行迎合对方
- 重复询问对方已回答的问题

---

## 4.9 社交练习

### 练习模式

- 陌生人初次交流
- 同事闲聊
- 饭局交流
- 聚会加入话题
- 朋友近况交流
- 与内向者聊天
- 与健谈者聊天
- 与上级交流
- 冷场恢复
- 观点不同情况下交流
- 拒绝他人
- 表达边界
- 表达感谢或关心

### AI 角色参数

- 年龄范围
- 身份
- 与用户关系
- 熟悉程度
- 性格
- 当前情绪
- 对用户态度
- 回复长度
- 主动程度
- 对隐私问题的敏感程度
- 场景目标

### 练习评分

每次练习结束后评价：

- 开场自然度
- 倾听能力
- 有效追问
- 共情表达
- 自我表达
- 话题衔接
- 边界意识
- 对话节奏
- 结束方式
- 总体舒适度

评分必须附带具体对话证据，不能只输出分数。

---

## 4.10 复习与成长系统

### 话题复习

使用简化间隔复习机制：

- 今日学习
- 明日复习
- 三天后
- 七天后
- 十四天后
- 三十天后

用户可根据掌握情况选择：

- 忘记
- 模糊
- 掌握
- 非常熟练

### 社交能力目标

用户可以设置：

- 每周主动联系两个人
- 每周完成一次聊天复盘
- 每周学习一个话题
- 聊天中至少提出三个开放式问题
- 减少打断
- 避免连续讲述过久
- 练习表达不同意见

### 周报

AI 每周生成：

- 本周互动概况
- 新认识的人
- 关系变化
- 主要聊天话题
- 表现较好的部分
- 重复出现的问题
- 下周建议
- 需要复习的话题
- 需要跟进的人

---

## 4.11 全局搜索

支持搜索：

- 人物
- 标签
- 人物字段
- 互动记录
- 话题
- 笔记
- 文件名
- 文件正文
- AI 对话
- 待办事项

支持筛选：

- 时间范围
- 人物
- 话题
- 文件类型
- 标签
- 内容来源
- 是否由 AI 生成
- 是否已确认

---

## 4.12 导入、导出与备份

### 导入

- CSV 人物数据
- JSON 完整数据
- Markdown 笔记
- 文件夹批量上传
- 浏览器收藏内容，后续实现

### 导出

- 单个人物 Markdown
- 单个话题 Markdown
- AI 会话 Markdown
- 全部数据 JSON
- 数据库备份
- 原始文件打包

### 自动备份

- 手动备份
- 每日备份
- 每周备份
- 保留最近若干版本
- 自定义备份路径
- 恢复前预览

---

# 五、数据库设计

## 5.1 核心数据表

### 用户与设置

- `users`
- `user_profiles`
- `app_settings`
- `custom_fields`
- `custom_field_values`

### 人物模块

- `persons`
- `person_contacts`
- `person_preferences`
- `person_facts`
- `person_relationships`
- `tags`
- `person_tags`
- `important_dates`
- `follow_up_tasks`

### 互动模块

- `interactions`
- `interaction_participants`
- `interaction_topics`
- `interaction_files`
- `interaction_extracted_facts`

### 话题模块

- `topic_categories`
- `topics`
- `topic_notes`
- `topic_person_links`
- `topic_relations`
- `topic_learning_records`
- `review_tasks`

### 文件模块

- `documents`
- `document_versions`
- `document_chunks`
- `document_links`
- `processing_jobs`

### AI 模块

- `ai_providers`
- `ai_models`
- `conversations`
- `conversation_messages`
- `conversation_links`
- `conversation_summaries`
- `context_snapshots`
- `memory_items`
- `prompt_templates`
- `ai_usage_logs`

### 练习模块

- `practice_scenarios`
- `practice_sessions`
- `practice_messages`
- `practice_evaluations`

## 5.2 关键表字段示例

### persons

```sql
CREATE TABLE persons (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    nickname VARCHAR(100),
    avatar_path TEXT,
    relationship_type VARCHAR(50),
    familiarity_level INTEGER DEFAULT 1,
    met_at TIMESTAMP,
    met_location TEXT,
    met_via TEXT,
    organization TEXT,
    occupation TEXT,
    location TEXT,
    summary TEXT,
    privacy_level VARCHAR(20) DEFAULT 'private',
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### person_facts

```sql
CREATE TABLE person_facts (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL REFERENCES persons(id),
    fact_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(30) NOT NULL,
    source_id UUID,
    confidence VARCHAR(20) DEFAULT 'confirmed',
    is_sensitive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

`confidence` 可选值：

- confirmed
- user_observation
- unconfirmed
- ai_inference
- outdated

### conversations

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    mode VARCHAR(50) NOT NULL,
    provider_id UUID,
    model_id UUID,
    summary TEXT,
    pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### conversation_messages

```sql
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,
    content TEXT,
    reasoning_content TEXT,
    status VARCHAR(20) DEFAULT 'completed',
    token_input INTEGER,
    token_output INTEGER,
    latency_ms INTEGER,
    provider_message_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL
);
```

### document_chunks

```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id),
    chunk_index INTEGER NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    heading_path TEXT,
    content TEXT NOT NULL,
    token_count INTEGER,
    embedding VECTOR,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL
);
```

PostgreSQL 可以通过 pgvector 保存向量并执行相似度检索，适合把人物、话题、文件、消息和向量索引放在同一个数据库中管理。

---

# 六、AI 与知识库技术设计

## 6.1 RAG 检索流程

用户提问后：

1. 判断当前对话模式。
2. 获取关联人物、话题和文件范围。
3. 对用户问题生成检索向量。
4. 在 `document_chunks` 中执行向量检索。
5. 执行关键词和标签过滤。
6. 对结果进行重排。
7. 选择最相关的若干片段。
8. 将片段加入模型上下文。
9. 保存实际使用的片段 ID。
10. AI 回答时返回引用信息。

## 6.2 检索范围优先级

1. 用户手动选中的文件
2. 当前人物关联文件
3. 当前话题关联文件
4. 当前会话曾使用的资料
5. 全局知识库

## 6.3 文件切分建议

- 普通文本：每段约 500—800 个中文字符
- 重叠：80—150 个字符
- 保留标题层级
- 保留页码
- 表格独立处理
- 不把不同章节强行拼接
- 同一文件保存解析版本

## 6.4 混合检索评分

```text
最终分数 =
向量相似度 × 0.65
+ 关键词匹配 × 0.20
+ 人物或话题关联度 × 0.10
+ 内容时效性 × 0.05
```

权重放入配置文件，不应写死在业务逻辑中。

## 6.5 Prompt 模板

系统内置模板：

- 通用社交助手
- 人物档案整理
- 互动信息提取
- 聊天准备
- 聊天复盘
- 话题导师
- 文件问答
- 模拟聊天
- 消息回复建议
- 周报生成

每个模板支持：

- 查看
- 编辑
- 复制
- 恢复默认
- 绑定模型
- 设置温度
- 设置最大输出长度

---

# 七、隐私与安全需求

## 7.1 API Key 安全

- API Key 不得发送到前端日志。
- API Key 不得以明文写入数据库。
- 后端使用 AES-256-GCM 加密。
- 首次启动时由用户设置主密码。
- 使用 Argon2id 从主密码派生密钥。
- 不保存主密码原文。
- 界面只能显示掩码。
- 支持立即删除密钥。
- 日志中自动过滤 Authorization 请求头。

## 7.2 数据安全

- 软件默认仅监听 `127.0.0.1`。
- 不默认开放局域网访问。
- 文件路径需要防止目录穿越。
- 上传文件需要限制大小和类型。
- HTML 内容需要消毒，防止脚本注入。
- 数据删除支持软删除和彻底删除。
- AI 调用前显示当前会发送哪些类别的信息。
- 敏感人物信息可标记为“禁止发送给外部模型”。

## 7.3 AI 行为限制

AI 不得：

- 将推测写成事实
- 根据有限信息诊断他人心理疾病
- 鼓励监控、欺骗或操纵他人
- 自动发送消息给联系人
- 擅自修改人物资料
- 擅自创建敏感标签
- 将一个人物的信息泄露到另一个人物的对话中

---

# 八、非功能需求

## 8.1 性能

- 普通页面首次打开不超过 2 秒
- 搜索结果不超过 1 秒
- AI 输出支持流式显示
- 文件解析在后台任务中完成
- 上传大文件时显示进度
- 数据库操作支持分页
- 单次对话失败不影响已保存消息

## 8.2 可用性

- 支持浅色和深色模式
- 支持键盘快捷键
- 支持自动保存
- 删除操作需要二次确认
- 表单离开时提示未保存内容
- 所有 AI 生成内容必须明确标记
- 失败状态提供重新执行按钮

## 8.3 可维护性

- 前后端类型清晰
- 数据库使用迁移工具
- API 使用统一响应格式
- 模型提供商使用适配器模式
- 文件解析器使用插件式接口
- Prompt 与代码分离
- 所有核心功能具有自动化测试

---

# 九、推荐技术架构

## 9.1 首版推荐方案

### 前端

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Tiptap
- TanStack Query
- Zustand
- React Hook Form
- Zod

### 后端

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Celery 或轻量后台任务队列

### 数据层

- PostgreSQL
- pgvector
- 本地文件系统
- Redis，可在需要后台任务时引入

### 部署

- Docker Compose
- 默认访问地址：`http://127.0.0.1:3000`
- 后续使用 Tauri 或 Electron 打包为桌面程序

## 9.2 架构图

```text
┌───────────────────────────────────────────┐
│             React Web Frontend            │
│ 人物 / 话题 / 文件 / AI / 练习 / 设置     │
└─────────────────────┬─────────────────────┘
                      │ REST + SSE
┌─────────────────────▼─────────────────────┐
│                FastAPI Backend            │
│                                           │
│ Person Service     Topic Service          │
│ Interaction Service Document Service      │
│ Conversation Service Memory Service       │
│ Retrieval Service  Practice Service       │
│ Provider Adapter   Security Service       │
└───────────────┬───────────────┬───────────┘
                │               │
┌───────────────▼──────┐  ┌─────▼───────────┐
│ PostgreSQL + pgvector│  │ Local File Store │
│ Metadata + Embedding │  │ Original Files   │
└──────────────────────┘  └─────────────────┘
                │
┌───────────────▼───────────────────────────┐
│ DeepSeek / OpenAI / Compatible Providers  │
└───────────────────────────────────────────┘
```

---

# 十、后端目录结构

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── encryption.py
│   │   └── logging.py
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   │   ├── person_service.py
│   │   ├── interaction_service.py
│   │   ├── topic_service.py
│   │   ├── document_service.py
│   │   ├── retrieval_service.py
│   │   ├── conversation_service.py
│   │   ├── memory_service.py
│   │   └── practice_service.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── openai_compatible.py
│   │   ├── openai_provider.py
│   │   └── deepseek_provider.py
│   ├── parsers/
│   │   ├── base.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── pptx_parser.py
│   │   ├── xlsx_parser.py
│   │   └── text_parser.py
│   ├── api/
│   │   ├── persons.py
│   │   ├── interactions.py
│   │   ├── topics.py
│   │   ├── documents.py
│   │   ├── conversations.py
│   │   ├── providers.py
│   │   ├── search.py
│   │   └── backup.py
│   └── prompts/
├── migrations/
├── tests/
├── requirements.txt
└── Dockerfile
```

# 十一、前端目录结构

```text
frontend/
├── src/
│   ├── app/
│   ├── pages/
│   │   ├── Dashboard/
│   │   ├── Persons/
│   │   ├── Interactions/
│   │   ├── Topics/
│   │   ├── Documents/
│   │   ├── Assistant/
│   │   ├── Practice/
│   │   ├── Reviews/
│   │   └── Settings/
│   ├── components/
│   │   ├── editor/
│   │   ├── person/
│   │   ├── topic/
│   │   ├── chat/
│   │   ├── document/
│   │   └── common/
│   ├── api/
│   ├── hooks/
│   ├── stores/
│   ├── schemas/
│   ├── types/
│   ├── utils/
│   └── styles/
├── tests/
├── package.json
└── Dockerfile
```

---

# 十二、核心 API 设计

## 人物

```text
GET    /api/persons
POST   /api/persons
GET    /api/persons/{id}
PATCH  /api/persons/{id}
DELETE /api/persons/{id}

POST   /api/persons/{id}/facts
PATCH  /api/person-facts/{fact_id}
DELETE /api/person-facts/{fact_id}

GET    /api/persons/{id}/timeline
GET    /api/persons/{id}/briefing
```

## 互动

```text
GET    /api/interactions
POST   /api/interactions
GET    /api/interactions/{id}
PATCH  /api/interactions/{id}
DELETE /api/interactions/{id}

POST   /api/interactions/{id}/extract
POST   /api/interactions/{id}/confirm-extractions
POST   /api/interactions/{id}/review
```

## 话题

```text
GET    /api/topics
POST   /api/topics
GET    /api/topics/{id}
PATCH  /api/topics/{id}
DELETE /api/topics/{id}

POST   /api/topics/{id}/summarize
POST   /api/topics/{id}/generate-questions
POST   /api/topics/{id}/generate-cards
```

## 文件

```text
POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/{id}
DELETE /api/documents/{id}

POST   /api/documents/{id}/process
POST   /api/documents/{id}/reprocess
GET    /api/documents/{id}/chunks
```

## AI 提供商

```text
GET    /api/providers
POST   /api/providers
PATCH  /api/providers/{id}
DELETE /api/providers/{id}

POST   /api/providers/{id}/test
POST   /api/providers/{id}/sync-models
GET    /api/providers/{id}/models
```

## 对话

```text
GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{id}
PATCH  /api/conversations/{id}
DELETE /api/conversations/{id}

GET    /api/conversations/{id}/messages
POST   /api/conversations/{id}/messages
GET    /api/conversations/{id}/stream
POST   /api/conversations/{id}/summarize
```

---

# 十三、开发阶段

## P0：可运行基础版本

必须完成：

- Docker Compose
- 数据库迁移
- 人物增删改查
- 标签管理
- 互动记录
- 话题管理
- 基础富文本笔记
- AI 提供商配置
- DeepSeek/OpenAI兼容接口
- 模型选择
- 流式聊天
- 对话保存
- API Key 加密
- 数据导出和备份

完成标准：用户可以创建人物、记录互动、建立话题、配置 DeepSeek，并进行能够保存历史的 AI 对话。

## P1：知识库版本

增加：

- 文件上传
- PDF、DOCX、PPTX、XLSX解析
- 文本切分
- 嵌入模型配置
- pgvector 检索
- 文件问答
- 人物和话题关联
- 回答引用来源
- 全局搜索

完成标准：用户可以上传资料，并让 AI 只基于指定人物、话题和文件回答问题。

## P2：社交能力版本

增加：

- 聊天前简报
- 互动信息自动提取
- 用户确认后写入档案
- 聊天复盘
- AI 模拟聊天
- 多维度评价
- 社交目标
- 话题复习
- 每周成长报告

## P3：增强版本

增加：

- 人物关系图
- OCR
- 音频转文字
- 网页收藏
- 浏览器扩展
- 移动端适配
- 桌面程序打包
- 本地模型
- 可选云同步

---

# 十四、测试要求

## 单元测试

覆盖：

- 人物信息保存
- 人物事实确认
- API Key 加解密
- 文件切分
- 检索过滤
- 上下文组装
- 提供商请求转换
- 对话摘要
- 记忆写入审批

## 集成测试

覆盖：

- 创建人物到生成聊天简报
- 上传文件到完成问答
- 创建提供商到流式对话
- 记录互动到确认人物新信息
- 删除人物后的关联数据处理
- 数据备份与恢复

## 安全测试

覆盖：

- API Key 不出现在日志
- 非法文件路径
- 恶意 HTML
- 超大文件
- 错误模型接口
- 请求中断
- 数据库恢复
- 不同人物上下文隔离

---

# 十五、验收标准

首个正式版本需要满足：

1. 软件可以通过一条 Docker Compose 命令运行。
2. 用户可以完整管理人物档案和自定义标签。
3. 用户可以记录互动并建立时间线。
4. 用户可以建立类似 Notion 的话题笔记。
5. 用户可以上传常见办公文件。
6. AI 可以引用上传文件回答问题。
7. 用户可以添加多个模型提供商。
8. 用户可以测试连接并同步模型。
9. 对话支持流式输出和历史保存。
10. 对话可以关联人物、话题和文件。
11. API Key 在数据库中不是明文。
12. AI 提取的信息必须经过用户确认。
13. 可以导出所有数据并完成恢复。
14. 删除和修改操作具有审计信息。
15. README 包含完整安装和使用步骤。

---

# 十六、首版应避免的功能

为了防止项目失控，P0 阶段不要开发：

- 多用户协作
- 复杂社交平台自动同步
- 自动读取微信聊天记录
- 自动发送消息
- 实时语音通话
- 复杂的人脸识别
- 原生手机应用
- 云端账户系统
- 付费订阅系统
- 过度复杂的关系评分算法

首版的核心判断标准是：

> 能否让用户在一次聊天前快速了解对方、准备话题，并在聊天后完成有效复盘。

---

# 十七、AI 开发主提示词

你是一名资深产品架构师、全栈工程师和测试工程师。请根据以下要求开发一套名为 **Socialization** 的个人本地社会化能力提升软件。

## 17.1 开发目标

Socialization 用于管理人物资料、人物喜好、互动记录、话题知识、上传文件、AI 对话、聊天准备和聊天复盘。

首轮只开发 P0，不要一次实现全部高级功能。

P0 必须包含：

1. 人物管理
2. 标签管理
3. 互动记录
4. 话题知识库
5. Tiptap 富文本笔记
6. AI 提供商管理
7. DeepSeek、OpenAI和通用 OpenAI 兼容接口
8. 模型同步和手动添加
9. AI 流式对话
10. 对话历史保存
11. 人物、话题与对话关联
12. API Key 加密保存
13. 数据导入、导出和备份
14. Docker Compose 本地部署

## 17.2 技术栈

前端：

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Tiptap
- TanStack Query
- Zustand
- React Hook Form
- Zod

后端：

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic

数据：

- PostgreSQL
- pgvector
- 本地文件目录

部署：

- Docker Compose

## 17.3 强制架构要求

1. 前后端分离。
2. 所有数据库修改必须通过 Alembic 迁移。
3. 所有 AI 模型调用必须经过 Provider Adapter。
4. 不得在业务服务中直接调用 DeepSeek 或 OpenAI SDK。
5. DeepSeek 模型名称不得写死。
6. 提供商必须支持手动输入 Base URL。
7. 提供商必须支持同步模型和手动添加模型。
8. API Key 必须在后端加密后保存。
9. API Key 不得返回前端。
10. API Key 不得出现在日志和异常信息中。
11. 对话采用 SSE 或等效方式流式输出。
12. 用户消息必须先保存，再调用模型。
13. 模型请求失败时保留用户消息，并允许重新生成。
14. 所有 AI 内容标记 `generated_by_ai=true`。
15. AI 提取的人物信息不得自动写入正式档案。
16. 软件默认只监听本地地址。
17. 所有删除操作必须有明确确认。
18. 所有列表接口必须支持分页。
19. 所有时间使用 UTC 保存，前端按本地时区显示。
20. 所有核心数据使用 UUID。

## 17.4 实施方法

按照以下顺序实施，不要跳过基础设施：

### 阶段一：初始化

1. 创建前后端目录。
2. 创建 Docker Compose。
3. 启动 PostgreSQL 和 pgvector。
4. 配置环境变量。
5. 创建 FastAPI 健康检查。
6. 创建 React 基础布局。
7. 创建统一错误响应格式。
8. 创建日志和异常处理。

### 阶段二：数据库

创建以下表：

- persons
- tags
- person_tags
- person_facts
- interactions
- interaction_participants
- topic_categories
- topics
- topic_notes
- ai_providers
- ai_models
- conversations
- conversation_messages
- conversation_links
- app_settings
- backup_records

为所有表创建 SQLAlchemy 模型、Pydantic Schema、Repository、Service 和 Router。

### 阶段三：人物与互动

完成：

- 人物列表
- 创建人物
- 编辑人物
- 人物详情
- 人物标签
- 人物事实
- 人物时间线
- 互动记录
- 互动关联多个人物

### 阶段四：话题知识库

完成：

- 话题分类
- 话题列表
- 话题详情
- Tiptap 编辑器
- 自动保存
- 话题与人物关联
- 笔记内容保存为 JSON
- 可选生成纯文本用于搜索

### 阶段五：AI 提供商

创建统一适配器：

```python
class BaseAIProvider:
    async def test_connection(self):
        raise NotImplementedError

    async def list_models(self):
        raise NotImplementedError

    async def stream_chat(self, request):
        raise NotImplementedError

    async def chat(self, request):
        raise NotImplementedError
```

实现：

- OpenAICompatibleProvider
- DeepSeekProvider
- OpenAIProvider

配置字段包括：

- name
- provider_type
- base_url
- encrypted_api_key
- custom_headers
- enabled
- default_model_id
- timeout_seconds
- max_retries

### 阶段六：AI 对话

完成：

- 新建对话
- 对话列表
- 对话重命名
- 删除对话
- 选择提供商
- 选择模型
- 关联人物
- 关联话题
- 保存消息
- 流式输出
- 停止生成
- 重新生成
- 复制回答
- 编辑用户消息后重新发送
- 保存 token 和延迟信息

### 阶段七：备份

完成：

- JSON 导出
- 数据库备份
- 备份列表
- 恢复确认
- 导出人物 Markdown
- 导出话题 Markdown
- 导出 AI 对话 Markdown

## 17.5 界面要求

整体风格：

- 简洁
- 安静
- 信息密度适中
- 类似 Notion，但不能直接复制其界面
- 支持浅色和深色模式
- 左侧固定导航
- 中间主内容区
- AI 页面可以有右侧上下文面板

人物详情页使用：

- 顶部人物信息
- 左侧主要资料
- 中间时间线
- 右侧待办和相关话题

AI 对话页面右侧显示：

- 当前人物
- 当前话题
- 当前文件
- 当前模型
- 将发送给模型的上下文范围

## 17.6 代码质量

1. 使用严格 TypeScript。
2. 禁止大量使用 `any`。
3. Python 添加类型注解。
4. Service 不直接依赖 HTTP Request。
5. Router 不直接访问数据库。
6. Repository 只负责数据访问。
7. Provider 不负责业务数据保存。
8. 关键函数必须有测试。
9. 不允许只创建空页面或假接口。
10. 不允许以 TODO 代替 P0 核心功能。
11. 提交前运行 lint、类型检查和测试。
12. README 必须包含完整启动方式。

## 17.7 每一阶段的输出格式

每完成一个阶段，输出：

1. 本阶段完成内容
2. 新增文件树
3. 数据库变化
4. API 列表
5. 启动命令
6. 测试命令
7. 手动验收步骤
8. 已知限制
9. 下一阶段计划

不得一次生成大量无法验证的代码。每一阶段必须保持项目可运行。

现在从“阶段一：初始化”开始，先输出项目目录、Docker Compose、环境变量模板、数据库配置、FastAPI 健康检查和 React 基础页面。完成后给出精确的运行与验收步骤。
