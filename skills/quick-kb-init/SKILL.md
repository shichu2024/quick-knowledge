---
name: quick-kb-init
description: |
  初始化一个 quick-knowledge 知识库 vault。在当前目录（或指定 vault 根）按 PARA + 系统层模型创建完整目录骨架，铺设系统文件、配置与默认模板。
  触发词（中文）：初始化知识库 / 初始化 KB / quick-kb-init / 建知识库
  Triggers (EN): init knowledge base / setup kb / initialize kb
version: v1.8.0
phase: v0.1
applies_to: vault 根目录
source_of_truth:
  - docs/DESIGN.md §4（目录结构）
  - docs/DESIGN.md §4.2（kb.config.yaml）
  - docs/SKILLS_SPEC.md §1
  - docs/dev/v0.1-mvp.md WP2
---

# quick-kb-init

> 在空目录初始化一个 quick-knowledge vault。**只铺骨架，不创建任何笔记内容。**

---

## 1. 何时调用

- 用户在新目录中开始使用 quick-knowledge
- 用户克隆 demo-vault 后想建立自己的工作 vault
- 显式触发：「初始化知识库」「setup kb」等

## 2. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `language` | 否 | `zh` | 模板语言：`zh` / `en`（v0.1 仅铺设 `zh`） |
| `domains` | 否 | `["general"]` | 初始领域列表，用于创建 `02_areas/<domain>/` 子目录；条目可含 `/` 表达嵌套（如 `programming/python`），init 会建多层目录 |
| `obsidian` | 否 | 自动探测 | 是否生成 `.obsidian/` 基础配置（v0.1 不处理，留给 v0.2） |
| `vault_root` | 否 | 当前工作目录 | vault 根路径；不传则在 CWD 创建 |

> v0.1 范围：`obsidian` 参数接受但**不实际生成** `.obsidian/` 配置（Obsidian 集成在 v0.2 完成）。如检测到 Obsidian 已安装，写入 `_readme.md` 提示「Obsidian 集成将在 v0.2 启用」。

---

## 3. 工作流

### 步骤 1 · 前置检查（幂等守门）

1. 检查 `vault_root` 下是否已存在 `.kb-initialized` 标记文件或 `99_system/` 目录。
2. **若已初始化**：
   - 不覆盖任何文件。
   - 输出提示：

   ```
   ⚠ 已检测到 quick-knowledge vault（初始化于 2026-08-13，schema v1 / skill v1.8.0）。
     - 如需重新初始化，请手动删除 .kb-initialized 与 99_system/ 后重试。
     - 如需升级配置，编辑 99_system/config/kb.config.yaml。
   ```

   - 结束流程。

### 步骤 2 · 创建目录骨架（含 `.gitkeep`）

按 [`DESIGN.md` §4](../../docs/DESIGN.md#4-目录结构) 创建全部目录。**v0.1 创建完整骨架**，但 v0.1 技能本身只操作其中一部分（详见 §5 阶段范围说明）。

每个空目录放置 `.gitkeep` 占位文件（仅一行注释：`# 占位 · 由 quick-kb-init 创建`），保证 git 跟踪。

**v1.7 补充**：`99_system/workflows/` 目录必须创建 `.gitkeep`，因为 `quick-kb-query` 会向该目录写入 `.query-log.jsonl`（见 query SKILL §步骤 7）。

骨架清单（按创建顺序）：

```
00_inbox/
├── ideas/
├── clips/
│   └── _raw/              # 原始抓取保留区
├── meetings/
├── ai-dialogs/
└── reading/

04_projects/
└── _template/             # 项目模板占位

01_resources/
├── articles/
├── books/
├── courses/
└── repos/

02_areas/
└── <domain>/              # 对每个用户输入 domain 创建；至少 general
                          # v1.4+ · domain 可含 "/"（如 programming/python）→ 建多层目录
    └── _moc.md            # 领域 MOC 占位（含模板头；仅建在最深层）

07_principles/
├── principles/
├── beliefs/
├── patterns/
└── experiences/

06_wiki/
├── mocs/
└── maps/

05_outputs/
├── daily/                 # YYYY/MM/ 由 daily 技能动态创建
├── reviews/
│   ├── weekly/
│   ├── monthly/
│   ├── quarterly/
│   └── yearly/
├── decisions/
└── works/

03_goals/

99_system/
├── skills/                # 软链或复制本框架技能（v0.1 仅创建空目录）；v0.3+ 含 manager/memory/research 三类 agent skill
├── templates/
│   ├── zh/                # v1.4 铺设全部 14 个模板
│   └── en/                # v1.4 铺设全部 14 个模板
├── attachments/
├── workflows/             # v1.7 创建 .gitkeep（供 query-log.jsonl 用）
├── prompts/
└── config/

98_archive/
├── projects/
├── goals/
├── reviews/
└── materials/
```

### 步骤 3 · 生成系统文件

#### 3.1 `99_system/config/kb.config.yaml`（最小版）

```yaml
# quick-knowledge vault 配置 · 由 quick-kb-init 生成
# 完整 schema 见 docs/DESIGN.md §4.2；v0.1 仅启用基础字段。

language: zh                       # zh | en（模板语言）
default_domain: general            # 默认领域
domains:                           # 已注册领域（与 02_areas/ 子目录对应）
  - general
# tags_vocabulary:                 # v0.4 启用（受控标签词表）
# review:                          # v0.2 启用
#   inbox_max_age_days: 7
#   orphan_threshold: 0.15
#   confidence_decay_months: 6
# proactive_reminders:             # v0.3 启用
#   enabled: true
# domain_taxonomy:                 # v1.4 启用（嵌套领域分类树，选填）
#   programming: [python, go, rust]
#   ai-engineering: [rag, agent, eval]
```

#### 3.2 `99_system/templates/{zh,en}/` 下铺设全部 14 个模板

将仓库 `templates/zh/` 与 `templates/en/` 下的全部 14 个模板文件复制到 vault 的 `99_system/templates/{zh,en}/`：

**基础 4 类（v0.1 起即有）**：

- `note-concept.md`
- `note-idea.md`
- `note-resource.md`
- `daily.md`

**认知资产 8 类（v1.4 起，与 `07_principles/` 子目录一一对应）**：

- `experience.md`
- `principle.md`
- `belief.md`
- `decision.md`
- `goal.md`
- `project.md`
- `pattern.md`
- `moc.md`

两种语言各 14 个文件，共 28 个。**已存在同名文件则跳过，不覆盖。**

#### 3.2.1 `99_system/config/frontmatter-schema.json`（v1.5 WP3 起）

schema 源按优先级探测（v1.8 WP1 起，与 §3.3 模板三级回退同构）：

| 优先级 | 源 | 探测路径 |
|--------|-----|---------|
| ① 最高 | 技能自带 | `skills/quick-kb-init/references/frontmatter-schema-v1.json`（v1.8 起随技能包分发，与仓库根源字节级一致） |
| ② 中 | 仓库根 | `$QUICK_KB_REPO_ROOT/references/frontmatter-schema-v1.json` |

命中即复制到 vault 的 `99_system/config/frontmatter-schema.json`。

- 作用：所有技能产出的笔记由 normalize `schema_check` 子动作按此 schema 校验
- **已存在同名文件则跳过，不覆盖**（upgrade 场景由 §3.7 比对版本）
- 复制成功后在 `.kb-initialized` 记录 schema 指纹（SHA-256 前 8 位，见步骤 5 字段表）
- ①② 均不可达时，**禁止自行编写 schema 内容**，只能落盘占位声明文件并 ⚠（见 §3.3「禁止即兴生成条款」）

#### 3.3 模板路径三级回退

模板文件按以下顺序探测，命中即复制（每语言独立探测，混合命中合法）：

| 优先级 | 源 | 探测路径 | 适用场景 |
|--------|-----|---------|---------|
| ① 最高 | 技能自带 | `skills/quick-kb-init/templates/{zh,en}/<filename>` | v1.8 WP1 起技能包自带全部模板文件，此级常规命中（推荐，随技能包分发） |
| ② 中 | 仓库根 | `$QUICK_KB_REPO_ROOT/templates/{zh,en}/<filename>` | 环境变量 `QUICK_KB_REPO_ROOT` 指向 quick-knowledge 仓库根 |
| ③ 兜底 | 占位模板 | （无源文件，由 init 生成占位） | ①② 均未命中时，写入占位模板（仅 frontmatter + 标题）并在报告 ⚠ 高亮（见下方兜底范围澄清） |

**探测逻辑**：

1. 对每个模板文件（如 `note-concept.md`），依次检查优先级 ① → ② → ③。
2. 命中第一级可用源即从该源复制，**不为同一文件降级到更低优先级**。
3. 若某文件在所有级别均不可用，写入占位模板（仅 frontmatter + 标题），并在报告中标 ⚠。
4. **幂等**：目标已存在同名文件则跳过，不覆盖。

> **兜底范围澄清（v1.8 WP1）**：本 SKILL.md 仅内嵌 **4 个系统文件**的文本（§3.4 `06_wiki/_index.md`、§3.5 `00_inbox/_readme.md`、§3.6 `02_areas/<domain>/_moc.md`、步骤 5 `.kb-initialized`），**14 个笔记模板不内嵌**。①② 均未命中时：4 个系统文件仍以内嵌文本写入，笔记模板按探测逻辑第 3 条写占位模板并 ⚠ 高亮。

**禁止即兴生成条款（v1.8 WP1）**：若模板 / schema 的 ①② 级源均不可达，**禁止自行编写 schema 或模板内容**——即兴生成的第三套 schema / 模板会污染下游所有技能。此时只能落盘占位声明文件（仅 frontmatter + 标题 + 一行「模板/schema 源不可达」说明），并在报告中 ⚠ 高亮提示用户：设置 `QUICK_KB_REPO_ROOT` 环境变量，或重装自带 `templates/` 与 `references/` 的技能包。

#### 3.4 `06_wiki/_index.md`（全局导航页占位）

```markdown
---
title: 全局导航
type: moc
created: {{date}}
updated: {{date}}
tags:
  - moc/index
---

# 全局导航

> quick-knowledge vault 索引页。MOC 生成（v0.2）后将自动填充。

## 领域
- [[02_areas/general/_moc|General]]

## 主题 MOC
- _（待 quick-kb-connect 生成）_

## 最近
- _（待 quick-kb-review 列出）_
```

#### 3.5 `00_inbox/_readme.md`（inbox 用法说明）

```markdown
# Inbox · 采集入口

> 所有未经整理的素材先进这里。用 quick-kb-capture 写入，用 quick-kb-ingest 入库。

## 子目录

| 目录 | 用途 |
|------|------|
| `ideas/` | 临时灵感、想法 |
| `clips/` | 网页摘录（原始抓取在 `clips/_raw/`） |
| `meetings/` | 会议记录（v0.2 启用） |
| `ai-dialogs/` | AI 对话精华（v0.2 启用） |
| `reading/` | 阅读笔记（v0.2 启用） |

## 工作流

1. `quick-kb-capture "想记的东西"` → 写入 inbox 子目录
2. `quick-kb-ingest 00_inbox/clips/某条.md` → 入库到 02_areas/resources
3. inbox 原始素材**永不删除**，由 review 闭环统一清理
```

#### 3.6 `02_areas/<domain>/_moc.md`（每个领域一份）

```markdown
---
title: {{domain}} · MOC
type: moc
created: {{date}}
updated: {{date}}
tags:
  - moc/{{domain}}
domain: {{domain}}
---

# {{domain}} · 主题索引

> 此 MOC 由 quick-kb-init 创建为占位。运行 `quick-kb-connect scope={{domain}}`（v0.2）后将自动刷新。

## 主题
- _（待填充）_

## 待补充
- [ ]
```

#### 3.7 upgrade 子流程（v1.4 起）

当步骤 1 检测到 `.kb-initialized` 已存在时，**不立即结束**，而是先读取其 `schema_version` 与 `skill_version`，与当前技能版本比较：

```
.kb-initialized.schema_version  <  当前技能 schema_version？
```

- **版本一致** → 走步骤 1 原有逻辑（提示已初始化，结束流程）。
- **版本不一致（需升级）** → 执行以下补缺操作，**全部幂等**：

> **版本判定口径（v1.8 WP1）**：`skill_version` 以 **17 个技能的统一版本号**为准（v1.8.0 起统一），不逐技能比较——逐技能比较时新旧版本交错（如部分 v0.1、部分 v1.7）会导致 upgrade 误判。

| 动作 | 细则 | 幂等保证 |
|------|------|---------|
| 补缺失模板 | 按 §3.3 三级回退探测，将 vault `99_system/templates/{zh,en}/` 中缺失的模板文件补齐 | 已存在同名文件则跳过，不覆盖 |
| **模板完整性校验（v1.5 WP1）** | 对 vault 内已存在的每个模板文件计算 SHA-256，与仓库源 `templates/{zh,en}/<name>.md` 比对。**不一致**（用户手改或旧版残留）→ 在 upgrade 报告标 ⚠，**询问**用户是否覆盖（默认不覆盖，保留用户改动） | SHA-256 一致则跳过；不一致未确认则不动 |
| 补缺失 schema | 按 §3.2.1 源优先级（① 技能自带 / ② 仓库根）将 `frontmatter-schema-v1.json` 复制到 vault `99_system/config/frontmatter-schema.json`（若缺失） | 已存在则跳过 |
| **schema 指纹校验（v1.8 WP1）** | 计算 vault 内 `frontmatter-schema.json` 的 SHA-256 前 8 位，与当前权威源（§3.2.1 命中的 ① 或 ②）指纹比对，并核对 `.kb-initialized.schema_sha256`。**不一致**（用户手改或曾即兴生成）→ upgrade 报告标 ⚠，**询问**用户是否以权威版覆盖（默认不覆盖） | 指纹一致则跳过；不一致未确认则不动 |
| 补缺失目录 | 按 §2 骨架清单检查 `00_inbox/` ~ `99_system/` 下的目录，缺失则创建并放 `.gitkeep` | 已存在目录则跳过 |
| 合并 config 新字段 | 读取 `99_system/config/kb.config.yaml`，将当前技能版本新增的字段（如 `domain_taxonomy`）以注释默认值形式追加 | 已存在同名字段则跳过，不覆盖已有值 |

**升级完成后**：

1. 更新 `.kb-initialized` 的 `schema_version` 与 `skill_version` 为当前值，并刷新 `schema_sha256` 指纹（v1.8 WP1）。
2. 输出升级报告，列出补缺的文件 / 目录 / config 字段。
3. 结束流程（不进入后续步骤 4 ~ 6）。

> upgrade 子流程是 init 的「增量补缺」模式：只补不删、只补不改，确保用户自定义内容永不被破坏。

### 步骤 4 · 写入 vault 根 `_index.md`（v1.7 WP5-D）

```markdown
# {{vault-name}}

本 vault 使用 quick-knowledge 体系。

## 入口

- 采集新素材 → quick-kb-capture
- 查询笔记 → quick-kb-query
- 周期复盘 → quick-kb-review
- 仪表盘 → quick-kb-stats

完整技能列表见 99_system/_index.md。
```

### 步骤 5 · 写入 `.kb-initialized` 标记

采用 YAML frontmatter 格式，便于 upgrade 子流程解析 `schema_version`：

```yaml
---
schema_version: 1
skill_version: v1.8.0
initialized_at: 2026-08-13
language: zh
domains: general,programming/python
runtime_hint: claude-code
schema_sha256: 5e3ffca2
---
```

| 字段 | 说明 |
|------|------|
| `schema_version` | vault 结构 schema 版本号（整数递增），用于 upgrade 子流程判断是否需补缺 |
| `skill_version` | 初始化时使用的技能版本号（如 `v1.8.0`；v1.8.0 起为 17 技能统一版本号，见 §3.7 版本判定口径） |
| `initialized_at` | 初始化日期（`YYYY-MM-DD`） |
| `language` | 模板语言（`zh` / `en`） |
| `domains` | 初始化时注册的领域列表（逗号分隔） |
| `runtime_hint` | init 时检测到的 runtime（`claude-code` / `codex` / `cursor` / `opencode` / `unknown`），供后续诊断 |
| `schema_sha256` | 所复制 `99_system/config/frontmatter-schema.json` 的 SHA-256 前 8 位指纹（v1.8 WP1），供 upgrade 子流程校验 schema 权威性 |

### 步骤 6 · 输出报告

```
✓ quick-knowledge vault 已初始化
  路径：{{vault_root}}
  阶段：v0.1
  语言：{{language}}
  领域：{{domains}}

  创建目录：N 个（含 .gitkeep）
  系统文件：
    - 99_system/config/kb.config.yaml
    - 99_system/config/frontmatter-schema.json（v1.5 WP3）
    - 99_system/templates/{zh,en}/ × 14 each（共 28 个）
    - 06_wiki/_index.md
    - 00_inbox/_readme.md
    - 02_areas/{{domain}}/_moc.md × N
    - _readme.md（vault 根）
    - .kb-initialized

  下一步：
    → quick-kb-capture "你的第一条想法"
    → quick-kb-capture <URL>
```

---

## 4. 阶段范围（v0.1 vs 后续）

**v0.1 init 创建完整骨架，但本阶段技能只操作其中一部分**：

| 目录 | v0.1 是否使用 | 使用者 |
|------|--------------|--------|
| `00_inbox/ideas/`, `00_inbox/clips/` | ✓ | capture / ingest |
| `00_inbox/meetings/`, `ai-dialogs/`, `reading/` | 创建但不写 | v0.2 capture |
| `02_areas/<domain>/` | ✓ | ingest |
| `01_resources/` | ✓ | ingest |
| `05_outputs/daily/` | ✓ | daily |
| `05_outputs/reviews/`, `decisions/`, `works/` | 创建但不写 | v0.2+ review/project |
| `07_principles/` | 创建但不写 | v0.3 认知资产 |
| `04_projects/`, `03_goals/`, `06_wiki/mocs/`, `06_wiki/maps/` | 创建但不写 | v0.2+ connect / v0.3 goal/project |
| `98_archive/` | 创建但不写 | v0.3+ project / v0.4 archive |
| `99_system/templates/en/` | ✓ 铺设 14 个模板 | init（v1.4 起，与 zh 同步） |

> **理由**：完整骨架让用户从 day 1 看到最终形态，避免后续升级时频繁迁移目录结构。v0.1 不使用的目录靠 `_moc.md` 占位或 `.gitkeep` 标注用途。

---

## 5. 边界

- **不创建任何笔记内容** —— 只铺骨架 + 占位文件。
- **不破坏既有文件** —— 同名文件跳过，输出跳过列表。
- **不接入 Obsidian** —— `.obsidian/` 配置在 v0.2 引入 obsidian-skills 后启用。
- **不生成 agent 文件** —— agent（manager/memory/research）以独立 skill 形式存在于 `skills/quick-kb-*-agent/`，随技能包分发，init 不需单独创建 `99_system/agents/` 目录。

## 6. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 用户无写权限 | 报错并列出需要权限的目录，不写入任何文件 |
| 目录名冲突（已有同名非空目录） | 保留原内容，仅补缺的子目录与 `.gitkeep` |
| 磁盘空间不足 | 报错并清理已写入的临时文件（保持幂等） |
| 模板源缺失（仓库未带 `templates/zh/`） | 写入占位模板（仅 frontmatter + 标题），并在报告中标 ⚠ |
| 模板源全缺失（①② 两级均未命中） | 4 个系统文件用 SKILL 内嵌文本写入；笔记模板落盘占位声明文件并 ⚠ 提示设置 `QUICK_KB_REPO_ROOT` 或重装技能包（**禁止即兴生成**，见 §3.3 条款） |

---

## 7. 自检清单（执行后）

- [ ] vault 根含 `.kb-initialized` 与 `_readme.md`
- [ ] `99_system/config/kb.config.yaml` 存在且 `language` 字段有效
- [ ] `99_system/templates/zh/` 与 `99_system/templates/en/` 各含 14 个模板文件（共 28 个）
- [ ] `99_system/config/frontmatter-schema.json` 存在（v1.5 WP3，normalize schema_check 依赖）
- [ ] **upgrade 场景**：28 个模板 SHA-256 已与仓库源比对，不一致项已 ⚠ 标注（v1.5 WP1）
- [ ] `.kb-initialized` 记录 `schema_sha256` 指纹（SHA-256 前 8 位）；upgrade 场景已与权威源比对，不一致项已 ⚠ 询问（v1.8 WP1）
- [ ] `00_inbox/`、`02_areas/`、`01_resources/`、`07_principles/`、`06_wiki/`、`05_outputs/`、`03_goals/`、`04_projects/`、`98_archive/`、`99_system/` 顶层目录齐全
- [ ] 每个空叶子目录含 `.gitkeep`
- [ ] 每个领域至少一个 `_moc.md`
- [ ] 二次执行：提示已初始化，不覆盖
- [ ] upgrade 场景：版本不一致时补缺模板/目录/config 字段，不覆盖已有文件

---

## 8. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源依据 |
|--------|------|-----------|
| v0.1 创建完整骨架（而非 v0.1 子集） | 让用户从 day 1 看到最终形态，避免后续迁移 | DESIGN §4 是真相源；dev/v0.1-mvp.md WP2 亦明确「创建 DESIGN §4 目录骨架」 |
| `confidence` 纳入 frontmatter 子集 | DESIGN §6.1 列为标准字段；WP4 ingest 需置信度初值规则 | 见 `references/frontmatter-v0.1.md` §2.1 |
| `.kb-initialized` 用简单键值而非 YAML | 避免引入 YAML 解析依赖，便于跨平台 | 不冲突，SKILLS_SPEC §1 仅要求"记录版本号 + 日期" |
| v1.4 起 `.kb-initialized` 改为 YAML frontmatter 格式 | upgrade 子流程（§3.7）需解析 `schema_version` / `skill_version` 做版本比较，YAML frontmatter 支持结构化字段读写 | 与 SKILLS_SPEC §1 兼容（仍含版本号 + 日期），仅格式升级 |
