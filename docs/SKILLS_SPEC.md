---
version: V2
updated: 2026-08-09
---

# quick-knowledge · 技能详细规格

> 本文件是对 [`DESIGN.md`](./DESIGN.md) 第 5 节「技能清单」的展开。每个技能给出：触发词、输入契约、工作流、输出契约、frontmatter 写法、边界与降级。
>
> 所有技能遵循通用规范：单文件 SKILL.md、零绝对路径、幂等、不破坏原始资料、可解释。

---

## 通用约定

### 触发词命名空间

所有技能名前缀 `quick-kb-`，避免与其他技能冲突。中英双触发词，写入 `description` frontmatter。

### 路径表达

文档中所有路径形如 `00_inbox/ideas/`、`02_areas/<domain>/`，均为相对 vault 根目录。技能运行时通过 runtime 提供的当前工作目录或显式 vault 路径解析。顶层目录加两位数字前缀实现流转可视化（见 ADR-015）。

### 嵌套 domain（v1.4+）

`domain` 字段可含 `/` 表达层级（如 `programming/python`），对应物理路径 `02_areas/programming/python/<slug>.md`。三个 skill 的统一处理：

| Skill | 嵌套行为 |
|-------|---------|
| `quick-kb-ingest` | 写 concept 时，若 `kb.config.yaml.domain_taxonomy` 命中顶层 key 且能从 tags/title 推断子域 → 嵌套落盘；未配置或未命中 → 单层（向后兼容） |
| `quick-kb-connect` | `scope` 接受嵌套路径段：`scope=programming` 扫全子树，`scope=programming/python` 只扫叶子；MOC 路径 `06_wiki/mocs/programming-python-moc.md`（`/` → `-`） |
| `quick-kb-normalize` | 新增 `action=regroup`：按 `domain_taxonomy` 把旧 flat-domain 笔记批量迁到嵌套结构（slug 保持不变 → slug-based wikilink 不断链） |

> `domain_taxonomy` 缺省时全部退为 v1.3 行为，零破坏。Obsidian 默认 wikilink 是 slug-based（`[[threading]]`），文件移动只要 slug 不变就不断链；path-qualified wikilink（`[[02_areas/programming/threading]]`）由 regroup 全库扫描重写。

### 日期类文件命名（v1.4+）

daily 日志 / review 报告 / goal·project progress 文件名采用 `<date-token>-<summary>.md` 形态，summary 由各 skill 的 LLM 从内容提炼 2-5 词 kebab-case（限 30 字符）。

| Skill | date-token | 示例 |
|-------|-----------|------|
| `quick-kb-daily` | `YYYY-MM-DD` | `2026-08-12-rag-eval-debug.md` |
| `quick-kb-review` (weekly) | `YYYY-Wxx` | `2026-W32-stability.md` |
| `quick-kb-review` (monthly) | `YYYY-MM` | `2026-08-stabilization.md` |
| `quick-kb-review` (adhoc) | `YYYY-MM-DD` | `2026-08-12-drift-check.md` |
| `quick-kb-goal` / `quick-kb-project` progress | `YYYY-MM-DD` | `progress/2026-08-12-chunk-baseline.md` |

**稳定性硬约束**：同日期/同周期若已存在任何形式的文件（纯日期 or 已带 summary）→ 加载既有文件编辑，**不重新提炼 summary，不改名**——避免 wikilink 断。内容空/不可提炼 → 退为纯日期。stats 报告（`stats-YYYY-MM-DD.md`）保留原形态不变。

### 输出反馈格式

每次写入后向用户报告：

```
✓ 写入：02_areas/ai-engineering/rag-architecture.md
  类型：concept | 文档状态：active | 成熟度：understood | 置信度：70
  来源：00_inbox/clips/20260808-1430-xxxx.md
  关联：[[Vector Database]]、[[Agent]]
```

---

## 1. quick-kb-init

**职责**：在当前空目录初始化 vault 骨架与系统文件。

### 触发词

- 中文：初始化知识库、初始化 KB、quick-kb-init
- English: init knowledge base, setup kb

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 语言偏好 `language` | 否 | `zh` / `en`，默认 `zh` |
| 领域列表 `domains` | 否 | 如 `["ai-engineering", "front-end"]` |
| 是否接入 Obsidian `obsidian` | 否 | `true` / `false`，默认探测 |

### 工作流

1. **前置检查**：当前目录是否已含 `99_system/` 或 `.kb-initialized` 标记。是 → 提示已初始化，询问是否覆盖配置。
2. **创建骨架**：按 DESIGN 第 4 节生成全部目录（带 NN_ 前缀），含 `.gitkeep`。
3. **生成系统文件**：
   - `99_system/config/kb.config.yaml`（根据用户输入）
   - `99_system/templates/{zh,en}/` 下铺设全部模板
   - `06_wiki/_index.md` 全局导航页
   - `00_inbox/_readme.md` 说明 inbox 用法
4. **写入 Obsidian 配置**（若启用）：`.obsidian/` 基础配置、推荐 Bases 视图。
5. **生成 README**：vault 根目录 `_readme.md`，说明这是 quick-knowledge vault。
6. **提交标记**：写入 `.kb-initialized`（记录版本号、初始化日期）。

### 输出

- 完整目录树
- `kb.config.yaml`
- `系统统计`：创建目录数、模板数

### 边界

- **不创建任何笔记内容** —— 只铺骨架。
- **不破坏既有文件** —— 遇到同名文件跳过，报告跳过项。
- **降级**：用户未装 obsidian-skills 时，跳过 .base/.canvas 生成。

---

## 2. quick-kb-capture（Capture 闭环）

**职责**：多源低摩擦采集到 inbox。

### 触发词

- 中文：记一下、快记、收藏这个、抓这个网页、保存这段对话
- English: capture this, save this, clip this page, quick note

### 输入（任选一种或组合）

| 源类型 | 形态 | 处理 |
|--------|------|------|
| 纯文本想法 | 字符串 | 直接存 00_inbox/ideas/ |
| URL | 网页链接 | 调用 defuddle/抓取 → 00_inbox/clips/ |
| PDF/文件 | 文件路径 | 提取文本摘要 → 00_inbox/reading/ |
| 会议转写 | 长文本 | 结构化为 00_inbox/meetings/ |
| AI 对话 | 对话文本 | 提取关键观点 → 00_inbox/ai-dialogs/ |
| 阅读笔记 | 文本 | 存 00_inbox/reading/ |

### 工作流

1. **识别源类型**：自动判断 URL/文件/文本。
2. **抓取与清洗**（URL/PDF）：调用 defuddle 或内置抓取，保留原始 HTML/正文到 `_raw/` 子目录，干净文本进 inbox。
3. **AI 润色提议**（v1.2+ · 仅限用户手敲输入）：对 idea / meeting / ai-dialog / reading 类型，若 input 字符数 < 50 或无标点或用户显式说「润色」，AI 主动生成扩写版，连同原文呈现三选一（[1] 用润色 / [2] 保留原文 / [3] 再改一版）。用户选 [1] 时正文写润色版、原文存 `source.original_text`、frontmatter 加 `ai_polished: true`。web-clip / pdf 不进润色流程。详见 DESIGN §6.10 + ADR-016。
4. **最小 frontmatter**：只填 `title` + `captured_at`（见 DESIGN 6.3）。
5. **AI 预标注**（可选）：根据内容猜测 1-3 个候选 tag，但**不**写入正式 tag 字段，而是写 `suggested_tags`，留给 Ingest 决定。
6. **文件命名**：`00_inbox/<type>/YYYYMMDD-HHMM-<slug>.md`。
7. **去重检测**：与 inbox 近 7 天内容比对相似度，>0.85 时提示「疑似重复：[文件名]，是否合并？」
8. **主动提醒**（V2 新增 · 见 DESIGN §7.6）：若素材主题命中已有 `belief`/`pattern`/`experience`，调用 quick-kb-memory-agent 提示「这与你的 [[某原则]] 相关」；若与既有笔记存在 `contradicts` 苗头，提示「注意：与 [[某笔记]] 似乎冲突，Ingest 时建议声明各自 context」。提醒非阻塞，库内 < 50 条笔记时关闭。

### 输出

```yaml
---
title: {{自动生成的简短标题}}
captured_at: 2026-08-08T14:30
source:                              # 嵌套字典（object），禁 list 格式（v1.9.3）
  url: {{原始 URL，若有}}
  raw: {{原始资料路径，若有}}
suggested_tags:    # 候选标签，Ingest 时确认
  - ai/agent
  - eng/architecture
capture_type: web-clip   # idea | web-clip | pdf | meeting | ai-dialog | reading
---
{{干净正文 / 用户原文}}
```

### 边界

- **不追求完整分类** —— 只进 inbox 子目录，不决定领域。
- **保留原始** —— 抓取的网页同时存 `_raw/`，永不丢失。
- **降级**：无 defuddle 时用基础 HTML→Markdown。

---

## 3. quick-kb-ingest（Ingest + Normalize 闭环）

**职责**：把 inbox 素材正式入库为 02_areas/01_resources/04_projects 笔记。

### 触发词

- 中文：处理 inbox、入库、把这条归档、消化这条
- English: process inbox, ingest this, promote this note

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 目标 `target` | 否 | 单条文件路径 / `inbox` 全量 / `00_inbox/ideas` 子目录 |
| 领域 `domain` | 否 | 指定领域，未指定则 AI 推荐 |
| 档位 `depth` | 否 | `quick` / `standard`（默认）/ `deep` |

### 工作流

1. **扫描候选**：列出 target 内的 inbox 笔记，按 captured_at 排序。
2. **逐条处理**（可并行，由 quick-kb-research-agent 承担）：
   1. **抽取原子观点**：一笔记一观点；多条观点拆成多条笔记。
   2. **分类去向**：concept → 02_areas/、resource → 01_resources/、decision → 05_outputs/decisions/（用 Decision Ledger 模板，见 DESIGN §8.4）。
   3. **补全 frontmatter**：依据 DESIGN 第 6 节填全部字段（含 `relations`、`context`）。
   4. **标签规范化**：`suggested_tags` → 正式 `tags`，对照 `kb.config.yaml` 受控词表。
   5. **来源链接**：`source.note` 用 wikilink 指回 inbox 原始素材（永不删除原始）。
   6. **置信度初值**：单源 40，多源 60+，含一手实验 80+。
   7. **关系类型化**：扫描已存在笔记，按 DESIGN §6.7 分类写入 `relations.{supports/contradicts/evolves/supersedes}`，并尝试从正文提取 `context`。
3. **冲突检测与主动提醒**（V2 关键）：
   - 与已入库笔记相似度 >0.85：提示合并或建立 `evolves`/`supersedes`。
   - 与已入库笔记语义对立（如"X 适合" vs "X 不适合"）：调用 quick-kb-memory-agent 判定冲突，**主动**建议建立 `contradicts` 关系并各自声明 `context`（见 DESIGN §7.6 触发表）。
4. **写入并反馈**：每条笔记的写入位置、类型、置信度、关系、context。

### 输出（单条 concept 笔记示例）

路径：`02_areas/ai-engineering/rag-architecture.md`

```yaml
---
title: RAG 架构设计
type: concept
created: 2026-08-08
updated: 2026-08-09
tags:
  - ai/rag
  - eng/architecture
status: active
maturity: understood
confidence: 60
relations:
  supports: ["[[Vector Database]]"]
  contradicts: []
  evolves: ["[[RAG 基础概念]]"]
  supersedes: []
context: "通用 RAG 架构；创业团队请参考 [[轻量 RAG 方案]]"
source:                             # object 格式（v1.9.3 对齐 schema）
  note: "[[20260808-1430-rag-article]]"
  url: https://example.com/rag
domain: ai-engineering
---

# RAG 架构设计

## 核心定义
{{从原始素材抽取}}

...
```

### 边界

- **原始素材永不删除** —— inbox 文件原地保留，Review 闭环统一清理。
- **不提升 maturity** —— Ingest 后 `maturity` 默认 `understood`、`status` 为 `active`，需 Review/实践才能升到 `validated` 及以上。
- **降级**：quick-kb-research-agent 不可用时，回退为「字段填充 + 模板套用」，不抽原子观点。

---

## 4. quick-kb-connect（Connect 闭环）

**职责**：建立双链、生成 MOC、绘制知识地图。

### 触发词

- 中文：连一下、建个 MOC、给这领域建索引、画个知识地图
- English: connect these, build moc, map this domain

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 范围 `scope` | 是 | 领域名 / 某条笔记 / 某标签 |
| 操作 `action` | 否 | `moc` / `links` / `canvas` / `all`（默认） |

### 工作流

1. **扫描范围**：列出 scope 下全部笔记及其 frontmatter。
2. **双链补全**（`action=links`）：
   - 找出每条笔记的 `related` 字段，自动创建反向 wikilink（Obsidian 双链语义）。
   - 检测标题共现、标签共现，推荐 3-5 个候选连接，由用户确认。
3. **MOC 生成**（`action=moc`）：调用 quick-kb-manager-agent，按主题聚类，生成 `06_wiki/mocs/<domain>-moc.md`。
4. **知识地图**（`action=canvas`）：调用 json-canvas 技能，生成 `06_wiki/maps/<domain>.canvas`。
5. **更新 _index.md**：将新 MOC 加入全局导航页。

### 输出（MOC 示例）

路径：`06_wiki/mocs/ai-engineering-moc.md`

```markdown
---
title: AI 工程 MOC
type: moc
created: 2026-08-08
updated: 2026-08-08
tags:
  - moc/ai-engineering
domain: ai-engineering
---

# AI 工程 · 主题索引

## RAG
- [[RAG 架构设计]]
- [[Vector Database 选型]]

## Agent
- [[Agent 框架对比]]
- [[Tool Use 模式]]

## 待补充
- [ ] Multi-Agent 编排
```

### 边界

- **不修改笔记正文** —— 只改 frontmatter.related 和新建 MOC/canvas。
- **降级**：无 obsidian-skills 时跳过 canvas 生成，仅产出 MOC。

---

## 5. quick-kb-query（Query 闭环）

**职责**：基于库内笔记回答问题，强制引用。

### 触发词

- 中文：我笔记里…、找一下…、关于 X 怎么说、KB 查
- English: search my notes, what do I have on, kb query

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 问题 `question` | 是 | 自然语言 |
| 范围 `scope` | 否 | 领域 / 标签 / 全库（默认） |
| 模式 `mode` | 否 | `strict`（默认，必须引用）/ `hybrid`（库内+推测分离） |

### 工作流

1. **检索**：基于关键词 + 标签 + wikilink 图谱召回候选笔记（quick-kb-manager-agent 协助）。
2. **排序**：按 confidence × recency × 入链数加权。
3. **回答生成**：
   - `strict`：每句结论必须挂 `[[]]` 或 `source` 引用；无法引用则不写。
   - `hybrid`：库内结论 + 推测结论分段呈现，推测段明确标注「以下不在库内」。
4. **未命中提示**：召回 < 阈值时返回「库内未找到，以下为推测」，并提示「是否要 Capture 相关资料补全？」

### 输出

```markdown
## 答

RAG 的核心是检索后生成，关键决策在于分块策略和向量库选型 [[RAG 架构设计]]。

分块推荐按语义切分而非固定长度 [[Vector Database 选型]]。

> 引用笔记：2 条 | 平均置信度：70 | 最近更新：2026-08-08

### 库内未覆盖
（仅 hybrid 模式显示）
- 多模态 RAG 的具体实现细节 —— 以上为推测，建议 Capture 相关资料。
```

### 边界

- **绝不编造引用** —— 找不到引用就说找不到。
- **不修改笔记** —— 只读。
- **触发 Capture** —— 检测到缺口时，主动建议调用 quick-kb-capture。

---

## 6. quick-kb-advisor（Query+ 闭环 · 决策辅助）

**职责**：基于个人认知资产（principle/belief/pattern/experience）辅助决策。

> 与 `quick-kb-query` 的区别：query 回答"是什么/有没有"（事实型，强制引用）；advisor 回答"怎么做"（思考型，基于个人经验综合建议）。两者并列，触发语义不同。

### 触发词

- 中文：我要做…怎么搞、帮我决策、我该怎么选、设计个 X、advisor
- English: how should I, help me decide, design a, advise on

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 情境 `situation` | 是 | 当前任务/决策情境 |
| 约束 `constraints` | 否 | 已知约束（时间、技术栈、团队等） |
| 候选 `options` | 否 | 已有的备选方案（未给则由 advisor 推演） |

### 工作流

1. **调用 quick-kb-memory-agent**：基于情境做经验召回（输入/输出/排序公式见 [`AGENTS_SPEC.md`](./AGENTS_SPEC.md) §3），找出历史上类似任务相关的 experience/pattern/decision。
2. **检索认知资产**：列出相关的 principle（这个人相信什么）、belief（待验证假设）、pattern（可复用模式）。
3. **检索领域知识**：调出相关 concept 笔记作为方法支撑。
4. **冲突检测**：若候选方案与某条 experience 教训冲突，显式警告。
5. **综合建议**：分三段产出 ——
   - **你的历史**：列出召回的相关经验，每条带 `[[]]` 引用。
   - **你的原则**：列出适用原则，标注是否与候选冲突。
   - **建议路径**：综合给出 1-3 条可执行建议，每条说明基于哪条经验/原则。
6. **缺口提示**：若关键决策缺乏经验支撑，提示「→ 调用 quick-kb-capture 记录这次决策，下次可复用」。

### 输出

```markdown
## 你要做的：设计一个插件系统

### 你的历史
- [[BI Engine 插件隔离方案]]（2024，曾遇到沙箱逃逸）
- [[微前端 iframe 隔离]]（2023，可行但通信成本高）

### 你的原则
- [[工程原则]]："边界管理优先于组件复用"
- ⚠ 候选方案 B 与 [[2024 插件沙箱教训]] 冲突

### 建议路径
1. 先定插件 ↔ 宿主的边界契约（基于上述原则）
2. 隔离方案选进程级（基于 BI Engine 教训）
3. ...

### 缺口
- 缺少"插件版本治理"相关经验 → 建议 Capture 本次决策
```

### 边界

- **承认主观性** —— advisor 明确这是"基于你个人经验的建议"，不是客观最优解。
- **降级**：库内笔记 < 50 条或无认知资产时，回退为通用建议并标注「以下非基于个人经验」。
- **不替代决策** —— 给建议，最终决定权在人。

---

## 7. quick-kb-review（Review 闭环）

**职责**：周期复盘 + 健康检查。

### 触发词

- 中文：复盘本周、复盘这个月、年度复盘、扫一下孤立笔记、KB 体检
- English: weekly review, monthly review, kb health check

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 周期 `period` | 是 | `daily` / `weekly` / `monthly` / `quarterly` / `yearly` / `adhoc` |
| 维度 `focus` | 否 | `knowledge`（知识库）/ `project` / `goal` / `daily` / `all`（默认） |
| 日期范围 `range` | 否 | 自定义，如 `2026-W32` |

### 工作流

1. **快照采集**：扫描对应周期的 daily/项目/目标笔记。
2. **价值刷新**（调用 quick-kb-manager-agent）：重算所有知识型笔记的 `value.reuse`，更新 Knowledge Score 排序。
3. **维度分析**：
   - **knowledge**：孤立笔记率、重复嫌疑、死链、maturity 衰减（长期未触碰 → `deprecated`）。
   - **value**：列出"高价值低置信"（KS 高但 confidence<60，该验证了）与"低复用高占用"（confidence 高但 reuse=0，该连 MOC 或归档）两类待办。
   - **structure**：识别子领域增速异常，建议拆分/升格为新领域（quick-kb-manager-agent 能力）。
   - **project**：进度偏离、阻塞项。
   - **goal**：目标进展、学习路径完成度。
   - **daily**：时间分布、重复模式。
4. **生成报告**：写入 `05_outputs/reviews/<period>/YYYY-Wxx.md`，按对应模板填充。
5. **产出待办**（按优先级）：
   - 「这 3 条高价值低置信笔记该去验证了」
   - 「这 2 条结论被新笔记部分推翻，建议降为 `deprecated`」
   - 「这 3 条孤立笔记建议归档或连接」
   - 「inbox 有 5 条 >7 天未处理」
   - 「MCP 子领域半年新增 40 篇，建议升格为独立领域」
6. **建议动作**：每条待办挂一个可执行技能调用（「→ 调用 quick-kb-ingest 处理 inbox」）。

### 输出（健康检查表格）

```markdown
## 健康指标

| 指标 | 当前 | 阈值 | 状态 |
|------|------|------|------|
| inbox 周转 | 4.2 天 | <7 天 | ✓ |
| 孤立笔记率 | 22% | <15% | ⚠ 超标 |
| frontmatter 缺失 | 3% | <5% | ✓ |
| maturity 衰减笔记 | 8 条 | — | → 验证或降级 |
| 高价值低置信 | 3 条 | — | → 优先验证 |
| 结构演化建议 | 1 项 | — | → 评估升格 |
```

### 边界

- **只标记不删除** —— `deprecated` 是状态，不直接归档。
- **不自动降级 maturity** —— 由人确认；agent 仅建议。
- **降级**：无 quick-kb-manager-agent 时仅做基于规则的检查，跳过价值刷新与结构演化。

---

## 8. quick-kb-daily（Capture 闭环 · 日志专属）

**职责**：每日日志，描述不足时反问补充。

### 触发词

- 中文：今天的日志、记日志、daily
- English: daily log, today's notes

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 内容 `content` | 否 | 用户口述，可为空 |
| 日期 `date` | 否 | 默认今天 |

### 工作流

1. **加载/创建当天日志**：路径 `05_outputs/daily/YYYY/MM/YYYY-MM-DD.md`。
2. **解析输入**：把用户口述拆成「做了什么 / 学到什么 / 想法 / 卡点」四块。
3. **反问补充**（关键特性）：当某块描述不足（如「开会」太笼统），AI **必须**反问：
   - 「这个会议主题是什么？有没有决策需要记录？」
   - 「你说『学了很多』，能具体列出 1-2 个要点吗？」
   - 反问最多 2 轮，避免变成问卷。
4. **AI 润色提议**（v1.2+ · 关键特性）：反问结束后，扫描 4 段中所有 < 30 字符的短句，一次性向用户呈现编号润色菜单（[1] 全部润色 / [2] 选编号润色 / [3] 全部保留 / [4] 单条再改）。选定的条目用润色版替换，原句以 `<!-- original: ... -->` 行内 HTML 注释保留。frontmatter 加 `ai_polished_entries: [条目编号]`。与反问互补：反问让用户自补，润色由 AI 主动扩写。详见 DESIGN §6.10 + ADR-016。
5. **抽取关联**：识别文本中的概念/项目/目标，自动生成 wikilinks。
6. **抽取待入库项**：发现「这个想法值得记」→ 提示「→ 调用 quick-kb-capture 单独入库？」
7. **更新 weekly review 锚点**：在 `05_outputs/reviews/weekly/` 当周文件里追加该日摘要。

### 输出

```markdown
---
title: 2026-08-08 日志
type: daily
created: 2026-08-08
updated: 2026-08-08
tags:
  - daily
---

# 2026-08-08

## 做了什么
- [[项目 X]] 需求评审
- ...

## 学到什么
- {{}}

## 想法
- {{}}

## 卡点
- {{}}
```

### 边界

- **反问有上限** —— 最多 2 轮，避免疲劳。
- **不强制结构** —— 用户只说一句话也能记录，反问是增强不是阻塞。

---

## 9. quick-kb-goal

**职责**：目标管理 + 学习路径推荐 + 进展记录。

### 触发词

- 中文：新建目标、学 X 这个目标、更新目标进度、完成目标
- English: new goal, learning path for, update goal progress

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 操作 `action` | 是 | `create` / `progress` / `complete` / `cancel` / `path` |
| 目标 `goal` | 是 | 名称 |
| 截止 `deadline` | 否 | 日期 |
| 路径来源 `path_source` | 否 | `recommend`（AI 推荐）/ `manual` |

### 工作流（create）

1. **目标澄清**：确认目标定义、成功标准、deadline、关联领域。
2. **生成 goal.md**：写入 `03_goals/<slug>/goal.md`，含成功标准、关键里程碑。
3. **学习路径推荐**（`path_source=recommend`）：
   - 调用 quick-kb-research-agent，基于已入库笔记 + 公开资料生成路径。
   - 路径分层：基础概念 → 进阶 → 实战项目。
   - 每个节点关联库内已有笔记或建议 Capture 的资料。
4. **建立 _moc.md**：路径 `03_goals/<slug>/_moc.md`，索引该目标的所有相关笔记。

### 工作流（progress）

1. **追加进展**：写入 `03_goals/<slug>/progress/YYYY-MM-DD.md`。
2. **更新里程碑**：勾选 goal.md 里完成的里程碑。
3. **路径动态调整**：基于进展推荐新节点或跳过冗余节点。

### 工作流（complete/cancel）

1. **归档**：移动 `03_goals/<slug>/` 到 `98_archive/goals/<slug>/`。
2. **复盘联动**：生成一份对应目标的复盘草稿到 `05_outputs/reviews/`。
3. **状态传播**：相关笔记的 `status` 转 `archived`，`maturity` 视情况保留或提升。

### 输出（goal.md 示例）

```markdown
---
title: 学 Rust
type: goal
created: 2026-08-08
updated: 2026-08-08
status: active
deadline: 2026-12-31
domain: systems-programming
tags:
  - goal/rust
related:
  - "[[所有权与借用]]"
---

# 学 Rust

## 成功标准
- [ ] 能独立写出 CLI 工具
- [ ] 读得懂 tokio 源码

## 学习路径
1. 基础语法（2 周） → [[Rust 语法入门]]
2. 所有权与借用（1 周） → [[所有权与借用]]
3. 异步编程（3 周）
4. 实战项目：实现一个文件同步工具（4 周）

## 里程碑
- [ ] M1：跑通 hello world（2026-08）
- [ ] M2：完成所有权练习
- [ ] M3：CLI 工具 v0.1
```

### 边界

- **学习路径基于库内优先** —— 库内已有笔记优先关联；缺口才建议 Capture。
- **不自动标完成** —— 必须用户确认。

---

## 10. quick-kb-project

**职责**：项目全生命周期。

### 触发词

- 中文：开个项目、项目 X、归档项目
- English: new project, archive project

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 操作 `action` | 是 | `init` / `update` / `archive` |
| 项目 `project` | 是 | 名称（slug） |
| 模板 `template` | 否 | 项目模板，默认 `_template` |

### 工作流（init）

1. **创建目录**：`04_projects/<slug>/`。
2. **生成 README**：项目说明、目标、关键决策、进度索引。
3. **拉起子目录**：`notes/`（项目笔记）、`decisions/`（Decision Ledger，见 DESIGN §8.4）、`refs/`（参考资料 wikilink）。
4. **建立 _moc.md**：项目内索引页。
5. **关联目标**：询问是否关联 goal，建立 wikilink。
6. **主动相似项目召回**（V2 关键 · 见 DESIGN §7.6）：调用 quick-kb-memory-agent，基于项目主题召回历史相似项目/相关 experience/pattern/失败教训，在 README 顶部生成「经验复用建议」段：
   ```
   ## 经验复用建议（来自 quick-kb-memory-agent）
   - 相似项目：[[BI 插件体系]]、[[工作流引擎]]
   - 适用 pattern：[[插件隔离模式]]
   - ⚠ 失败教训：[[2024 沙箱逃逸教训]] —— 注意隔离边界
   - 是否复用？→ 用户确认后写入 refs/ 与 relations.supports
   ```
7. **决策骨架**：若项目有明确的初始方案选型，引导生成首条 Decision Ledger（含 expected，留 actual/lesson 待归档时补）。

### 工作流（archive）

1. **状态检查**：未关闭的决策/笔记提醒。
2. **决策闭环**：扫描本项目 `decisions/`，对每条 Decision Ledger 补全 `actual` 与 `lesson`；将每条 lesson **自动派生为独立 `experience` 笔记**到 `07_principles/experiences/`，并在原 decision 中建立 wikilink。
3. **迁移**：`04_projects/<slug>/` → `98_archive/projects/<slug>/`。
4. **归档复盘**：生成项目复盘草稿（含 expected vs actual 偏差分析）。
5. **清理引用**：更新指向该项目的 wikilinks；`status` 转 `archived`，`maturity` 视情况保留或提升。

### 输出（项目 README 示例）

```markdown
---
title: 项目 X
type: project
created: 2026-08-08
updated: 2026-08-08
status: active
deadline: 2026-10-01
related_goals:
  - "[[学 Rust]]"
---

# 项目 X

## 目标
{{}}

## 关键决策
- [[决策 001：选型 Y]]

## 进度笔记
- [[周报 2026-W32]]

## 参考资料
- [[某外部资源]]
```

### 边界

- **不删除项目笔记** —— 归档即迁移，保留可检索性。
- **状态传播** —— 关联目标的进展随归档同步。

---

## 11. 扩展技能（简表）

| 技能 | 触发词 | 输入 | 输出 | 边界 |
|------|--------|------|------|------|
| `quick-kb-normalize` | 规整笔记、normalize | 范围（领域/全库） | 补全 frontmatter、归一标签 | 不改正文，仅元数据 |
| `quick-kb-archive` | 归档、archive | 目标对象 | 迁移到 98_archive/，更新引用 | 不删除，可恢复 |
| `quick-kb-stats` | KB 统计、健康度 | 范围 | 仪表盘（孤立率、置信度分布等） | 只读 |
| `quick-kb-import` | 导入、import | 来源（Obsidian/Notion） | 转换后的笔记 + inbox 候选 | 不删原库 |

---

## 附录 A · 技能与闭环映射速查

```
Capture    : quick-kb-capture, quick-kb-daily
Ingest     : quick-kb-ingest
Normalize  : quick-kb-ingest, quick-kb-normalize
Connect    : quick-kb-connect (+ quick-kb-manager-agent)
Query      : quick-kb-query（事实型）
Query+     : quick-kb-advisor（决策型，+ quick-kb-memory-agent）
Review     : quick-kb-review (+ quick-kb-manager-agent)

横切       : quick-kb-init, quick-kb-goal, quick-kb-project
研究支撑   : quick-kb-research-agent（读外部，被 capture/ingest/goal 调用）
记忆支撑   : quick-kb-memory-agent（调旧经验，被 advisor/project/goal 调用）
主动提醒   : 事件触发（project-init/goal-create/capture/ingest/review）→ quick-kb-memory-agent/quick-kb-manager-agent
派生       : Decision Ledger 的 lesson → experience 笔记（项目归档时）
扩展       : quick-kb-archive, quick-kb-stats, quick-kb-import
```

> Agent 详细规格（输入/输出/排序公式/降级）见 [`AGENTS_SPEC.md`](./AGENTS_SPEC.md)。

## 附录 B · 技能间调用关系

```
quick-kb-init
    └─ 初始化 vault

quick-kb-capture ─────┐
quick-kb-daily ───────┤
                      ├─▶ quick-kb-ingest ─▶ quick-kb-connect
                      │         ▲                  │
                      │    quick-kb-research-agent          │
                      │         │                  ▼
                      │         │           quick-kb-query（事实）
                      │         │           quick-kb-advisor（决策）
                      │         │                  ▲
                      │         │           quick-kb-memory-agent
                      │         │                  │
                      └─────────┴──────────────────┘
                                                     │
quick-kb-review ◀──── quick-kb-manager-agent ◀───────────────┘
    │
    ├─▶ 价值刷新（重算 value.reuse、KS 排序）
    ├─▶ 结构演化建议（升格新领域）
    └─▶ 触发任意闭环修复

quick-kb-goal / quick-kb-project 横跨 Capture/Ingest/Connect/Review/Query+
```
