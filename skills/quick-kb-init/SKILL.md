---
name: quick-kb-init
description: |
  初始化一个 quick-knowledge 知识库 vault。在当前目录（或指定 vault 根）按 PARA + 系统层模型创建完整目录骨架，铺设系统文件、配置与默认模板。
  触发词（中文）：初始化知识库 / 初始化 KB / quick-kb-init / 建知识库
  Triggers (EN): init knowledge base / setup kb / initialize kb
version: v0.1
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
| `domains` | 否 | `["general"]` | 初始领域列表，用于创建 `02_areas/<domain>/` 子目录 |
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
   ⚠ 已检测到 quick-knowledge vault（初始化于 2026-08-08，版本 v0.1）。
     - 如需重新初始化，请手动删除 .kb-initialized 与 99_system/ 后重试。
     - 如需升级配置，编辑 99_system/config/kb.config.yaml。
   ```

   - 结束流程。

### 步骤 2 · 创建目录骨架（含 `.gitkeep`）

按 [`DESIGN.md` §4](../../docs/DESIGN.md#4-目录结构) 创建全部目录。**v0.1 创建完整骨架**，但 v0.1 技能本身只操作其中一部分（详见 §5 阶段范围说明）。

每个空目录放置 `.gitkeep` 占位文件（仅一行注释：`# 占位 · 由 quick-kb-init 创建`），保证 git 跟踪。

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
    └── _moc.md            # 领域 MOC 占位（含模板头）

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
├── skills/                # 软链或复制本框架技能（v0.1 仅创建空目录）
├── agents/                # v0.2+ 才有 agent 文件
├── templates/
│   ├── zh/                # v0.1 铺设 4 个模板
│   └── en/                # v0.1 创建空目录，v0.2 填充
├── attachments/
├── workflows/
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
```

#### 3.2 `99_system/templates/zh/` 下铺设 4 个 v0.1 模板

复制仓库 `templates/zh/` 下的：

- `note-concept.md`
- `note-idea.md`
- `daily.md`
- `note-resource.md`

若仓库本身被克隆安装，则从仓库根 `templates/zh/` 复制；若 runtime 提供 inline 内嵌，按 SKILL 提示词内嵌版本写入。**已存在同名文件则跳过，不覆盖。**

#### 3.3 `06_wiki/_index.md`（全局导航页占位）

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

#### 3.4 `00_inbox/_readme.md`（inbox 用法说明）

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

#### 3.5 `02_areas/<domain>/_moc.md`（每个领域一份）

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

### 步骤 4 · 写入 vault 根 `_readme.md`

```markdown
# {{vault-name}} · quick-knowledge vault

> 此 vault 由 [quick-knowledge](https://github.com/shichu2024/quick-knowledge) 初始化。
> 初始化日期：{{date}} ｜ 阶段：v0.1 ｜ 语言：{{language}}

## 快速开始

1. **采集**：`quick-kb-capture "想法"` 或 `quick-kb-capture <URL>`
2. **入库**：`quick-kb-ingest 00_inbox/`
3. **日志**：`quick-kb-daily`

完整指南见 [docs/quick-start.md](docs/quick-start.md)（v0.4 提供）。

## 目录结构

见 [docs/DESIGN.md §4](docs/DESIGN.md#4-目录结构)。

## 配置

编辑 [99_system/config/kb.config.yaml](99_system/config/kb.config.yaml)。
```

### 步骤 5 · 写入 `.kb-initialized` 标记

```
quick-knowledge vault
version: v0.1
initialized_at: {{ISO datetime}}
language: {{language}}
domains: {{comma-separated}}
runtime_hint: {{auto-detected}}
```

> 标记文件**仅一行一个字段**，避免 YAML 解析依赖。`runtime_hint` 记录 init 时检测到的 runtime（claude-code / codex / cursor / opencode / unknown），供后续诊断。

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
    - 99_system/templates/zh/ × 4
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
| `99_system/templates/en/` | 创建空目录 | v0.2 英文模板 |

> **理由**：完整骨架让用户从 day 1 看到最终形态，避免后续升级时频繁迁移目录结构。v0.1 不使用的目录靠 `_moc.md` 占位或 `.gitkeep` 标注用途。

---

## 5. 边界

- **不创建任何笔记内容** —— 只铺骨架 + 占位文件。
- **不破坏既有文件** —— 同名文件跳过，输出跳过列表。
- **不接入 Obsidian** —— `.obsidian/` 配置在 v0.2 引入 obsidian-skills 后启用。
- **不生成 agent 文件** —— `99_system/agents/` 在 v0.2 起由对应阶段填充。

## 6. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 用户无写权限 | 报错并列出需要权限的目录，不写入任何文件 |
| 目录名冲突（已有同名非空目录） | 保留原内容，仅补缺的子目录与 `.gitkeep` |
| 磁盘空间不足 | 报错并清理已写入的临时文件（保持幂等） |
| 模板源缺失（仓库未带 `templates/zh/`） | 写入占位模板（仅 frontmatter + 标题），并在报告中标 ⚠ |

---

## 7. 自检清单（执行后）

- [ ] vault 根含 `.kb-initialized` 与 `_readme.md`
- [ ] `99_system/config/kb.config.yaml` 存在且 `language` 字段有效
- [ ] `99_system/templates/zh/` 含 4 个模板文件
- [ ] `00_inbox/`、`02_areas/`、`01_resources/`、`07_principles/`、`06_wiki/`、`05_outputs/`、`03_goals/`、`04_projects/`、`98_archive/`、`99_system/` 顶层目录齐全
- [ ] 每个空叶子目录含 `.gitkeep`
- [ ] 每个领域至少一个 `_moc.md`
- [ ] 二次执行：提示已初始化，不覆盖

---

## 8. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源依据 |
|--------|------|-----------|
| v0.1 创建完整骨架（而非 v0.1 子集） | 让用户从 day 1 看到最终形态，避免后续迁移 | DESIGN §4 是真相源；dev/v0.1-mvp.md WP2 亦明确「创建 DESIGN §4 目录骨架」 |
| `confidence` 纳入 frontmatter 子集 | DESIGN §6.1 列为标准字段；WP4 ingest 需置信度初值规则 | 见 `references/frontmatter-v0.1.md` §2.1 |
| `.kb-initialized` 用简单键值而非 YAML | 避免引入 YAML 解析依赖，便于跨平台 | 不冲突，SKILLS_SPEC §1 仅要求"记录版本号 + 日期" |
