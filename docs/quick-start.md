# 快速开始 · Quick Start

> 5 分钟跑通 quick-knowledge 基本流程。
>
> 5-minute quickstart for quick-knowledge.

[中文](#中文) · [English](#english)

---

## 中文

### 前置条件

- 已安装任一兼容 runtime（Claude Code / Codex / Cursor / OpenCode）
- 已安装 quick-knowledge 技能（见 [README](../README.md#安装)）

### Step 1 · 初始化 vault

在任意空目录唤起你的 runtime，说：

```
初始化我的知识库
```

技能会生成如下结构：

```
.
├── inbox/                # 待采集的素材
├── concepts/             # 概念笔记
├── resources/            # 资源笔记
├── principles/           # 认知资产（principle/belief/pattern/experience）
├── projects/             # 项目
├── goals/                # 目标
├── daily/                # 每日笔记
├── reviews/              # 复盘
├── outputs/reviews/      # 复盘报告
├── wiki/mocs/            # MOC 索引
├── archive/              # 归档
├── templates/            # 模板（从技能复制）
├── system/               # 系统文件
└── kb.config.yaml        # 配置
```

### Step 2 · 第一条 Capture

抓取一篇网页：

```
抓 https://example.com/article
```

技能会把网页正文转 Markdown，写入 `inbox/<时间戳>-<标题>.md`。frontmatter 已填好 `title` / `captured_at` / `source.url` / `status: inbox`。

其他抓取方式：

```
抓 https://example.com/article.pdf    → PDF
读 /path/to/meeting-notes.md          → 本地文件
抓和 Cursor 的这次对话                → AI 对话（v0.2+）
```

### Step 3 · 第一次 Ingest

把 inbox 中的素材入库为正式笔记：

```
入库 inbox 最新那条
```

技能会：
1. 调 research-agent 抽取原子观点
2. 推断 type（concept / resource / ...）与 domain
3. 生成 frontmatter（confidence 初始值）
4. 检测与既有笔记的关系（manager-agent v0.2 / memory-agent v0.3）
5. 移到对应目录（如 `concepts/`）

### Step 4 · 第一次 Query（v0.2+）

事实型检索，每句结论挂引用：

```
我笔记里关于 RAG 怎么说？
```

strict 模式（默认）输出：

```
## 答
RAG 的核心是检索后生成 [[RAG 架构设计]]。
分块推荐按语义切分 [[Vector Database]]。

> 召回笔记：N 条 · 平均置信度：70
```

若召回涉及 `contradicts` 关系，双方会同时呈现（ADR-011）。

### Step 5 · 第一次 Advisor（v0.3+）

决策辅助，调取个人经验：

```
我要设计一个插件系统，怎么做？
```

输出三段：
- **你的历史**：召回到的相关 experience/pattern
- **你的原则**：相关 principle/belief + 是否冲突
- **建议路径**：基于历史/原则的可执行建议

### Step 6 · 第一次 Review（v0.2+）

每周复盘：

```
复盘本周
```

技能输出：孤立笔记清单、低复用高占用笔记、高价值低置信待验证项、结构演化建议。

### 下一步

- 设置目标：`新建目标：学 Rust`
- 开项目：`开个项目：插件系统`
- 看健康度：`KB 统计一下`（v0.4+）
- 多语言切换：编辑 `kb.config.yaml` 的 `language` 字段

完整文档：[DESIGN.md](./DESIGN.md) · [SKILLS_SPEC.md](./SKILLS_SPEC.md) · [AGENTS_SPEC.md](./AGENTS_SPEC.md)

---

## English

### Prerequisites

- Any compatible runtime installed (Claude Code / Codex / Cursor / OpenCode)
- quick-knowledge skill installed (see [README](../README.md#installation))

### Step 1 · Initialize Vault

In any empty directory, invoke your runtime and say:

```
Initialize my knowledge base
```

The skill generates the directory skeleton (inbox / concepts / resources / principles / projects / goals / daily / reviews / outputs / wiki / archive / templates / system) plus `kb.config.yaml`.

### Step 2 · First Capture

Grab a webpage:

```
Grab https://example.com/article
```

The skill converts HTML to Markdown and writes `inbox/<timestamp>-<title>.md` with `title` / `captured_at` / `source.url` / `status: inbox` filled.

Other forms:

```
Grab https://example.com/article.pdf    → PDF
Read /path/to/meeting-notes.md          → local file
Grab this Cursor conversation           → AI dialog (v0.2+)
```

### Step 3 · First Ingest

Promote an inbox item to a formal note:

```
Ingest the latest inbox note
```

The skill:
1. Calls research-agent to extract atomic viewpoints
2. Infers type (concept / resource / ...) and domain
3. Generates frontmatter (initial confidence)
4. Detects relations with existing notes (manager-agent v0.2 / memory-agent v0.3)
5. Moves to the appropriate directory (e.g. `concepts/`)

### Step 4 · First Query (v0.2+)

Factual retrieval with mandatory citations:

```
What do my notes say about RAG?
```

Strict mode (default) output:

```
## Answer
The core of RAG is retrieval-augmented generation [[RAG Architecture]].
Chunking should be semantic rather than fixed-length [[Vector Database]].

> Recalled notes: N · Average confidence: 70
```

If recall involves `contradicts` relations, both sides are shown simultaneously (ADR-011).

### Step 5 · First Advisor (v0.3+)

Decision support with personal experience recall:

```
I'm designing a plugin system, how should I do it?
```

Three-section output:
- **Your history**: recalled experience/pattern
- **Your principles**: relevant principle/belief + conflict check
- **Suggested path**: actionable advice grounded in history/principles

### Step 6 · First Review (v0.2+)

Weekly review:

```
Weekly review
```

The skill reports orphan notes, low-reuse high-occupancy notes, high-value low-confidence items, and structural drift suggestions.

### Next Steps

- Set a goal: `New goal: learn Rust`
- Start a project: `New project: plugin system`
- Health check: `KB stats` (v0.4+)
- Switch language: edit `language` in `kb.config.yaml`

Full docs: [DESIGN.md](./DESIGN.md) · [SKILLS_SPEC.md](./SKILLS_SPEC.md) · [AGENTS_SPEC.md](./AGENTS_SPEC.md)
