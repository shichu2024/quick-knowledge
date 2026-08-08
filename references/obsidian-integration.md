---
version: V1
updated: 2026-08-09
phase: v0.2
applies_to: 全部技能（运行时探测）
source_of_truth:
  - docs/DESIGN.md §9
  - docs/dev/v0.2-loops.md WP7
---

# Obsidian-skills 集成与降级

> quick-knowledge **依赖** [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) 提供的底层能力，而非重新实现。本文件说明 5 项依赖的集成点与缺失时的降级路径。
>
> 非 Obsidian 用户（VSCode / Cursor / 纯文件）同样可用 —— 所有 .md 文件可独立读写，仅 .base/.canvas 是 Obsidian 专属。

---

## 1. 依赖清单

| obsidian-skill | quick-knowledge 如何使用 | 缺失时降级 | 引入阶段 |
|----------------|------------------------|-----------|---------|
| `obsidian-markdown` | 写入笔记时遵守 wikilink、callout、properties 规范 | 纯 GFM（GitHub-flavored Markdown） | v0.2 |
| `obsidian-bases` | 生成 inbox/areas/goals 的 .base 视图做仪表盘 | 跳过 .base 生成 | v0.2（按需） |
| `json-canvas` | connect 闭环生成知识地图 .canvas | 跳过 .canvas，仅产出 MOC | v0.2 |
| `obsidian-cli` | 与 Obsidian 应用交互（打开笔记、触发命令） | 跳过自动打开 | v0.2（按需） |
| `defuddle` | capture 闭环抓取网页时提取干净正文 | 基础 HTML→MD（去 script/style/nav） | v0.2 |

---

## 2. 各集成点详述

### 2.1 obsidian-markdown

**用途**：规范 frontmatter / wikilink / callout 写法，保证 Obsidian 正确解析。

**集成点**：
- 所有技能写入笔记时遵守：
  - frontmatter 用 YAML（`---` 围栏）
  - wikilink 用 `[[Note Title]]` 或 `[[path/to/note|alias]]`
  - callout 用 `> [!info]` / `> [!warning]` 等 Obsidian 类型
- 不写非标准扩展（如 Logseq 的 `[[page]]` 块引用）

**缺失降级**：
- 输出纯 GFM 兼容的 Markdown
- callout 改为普通 `>` 引用块（视觉一致，无 Obsidian 折叠/着色）
- frontmatter 仍用 YAML（GFM 兼容）

### 2.2 obsidian-bases

**用途**：生成 `.base` 文件做仪表盘（inbox 待办、areas 笔记数、goals 进度等）。

**集成点**：
- `quick-kb-init`（v0.2+）：可选生成 `inbox.base` / `areas.base` / `goals.base`
- `quick-kb-review`：可触发 .base 刷新

**缺失降级**：
- 跳过 .base 生成
- 用户通过 markdown 表格 / dataview 替代（非 Obsidian 用户不需要）

### 2.3 json-canvas

**用途**：connect 闭环生成知识地图。

**集成点**：
- `quick-kb-connect action=canvas`：生成 `wiki/maps/<domain>.canvas`
- 节点 = 笔记，边 = relations（按类型着色：supports=绿 / contradicts=红 / evolves=蓝 / supersedes=灰）

**缺失降级**：
- 跳过 .canvas 生成
- 仅产出 MOC（markdown 列表）
- 用户安装 json-canvas 后可重新运行 `connect action=canvas` 补全

### 2.4 obsidian-cli

**用途**：与 Obsidian 应用交互（自动打开笔记、触发命令、刷新 Bases）。

**集成点**：
- `quick-kb-capture`：写入后自动在 Obsidian 中打开（可选）
- `quick-kb-connect`：生成 canvas 后在 Obsidian 中可视化
- `quick-kb-review`：完成后打开报告

**缺失降级**：
- 跳过自动打开
- 输出文件路径，由用户手动打开

### 2.5 defuddle

**用途**：capture 闭环抓取网页时提取干净正文（去除导航/广告/侧边栏）。

**集成点**：
- `quick-kb-capture source_type=web-clip`：调 defuddle 处理 URL
- 原始 HTML 保留到 `inbox/clips/_raw/`

**缺失降级**：
- 基础 HTML→MD：
  1. 移除 `<script>` / `<style>` / `<nav>` / `<footer>` / `<aside>` / `<iframe>`
  2. 保留 `<article>` / `<main>` / `<section>` / `<div role="main">` 主体
  3. 标题、段落、列表、代码块、图片 alt 转换为 Markdown
  4. 失败 → `partial: true` + 错误原因

---

## 3. 能力探测

每个技能运行时检测 obsidian-skills 是否存在：

```
def has_skill(name: str) -> bool:
    """检测某 obsidian-skill 是否在 runtime 注册"""
    # runtime 提供的 skill registry / capabilities API
    ...
```

技能内部根据探测结果选择主路径或降级路径，对用户透明（仅在反馈中标注「降级运行」）。

---

## 4. 安装建议（用户文档）

### 4.1 Obsidian 用户（推荐）

```
# 1. 先安装 obsidian-skills
npx skills add kepano/obsidian-skills

# 2. 再安装 quick-knowledge
npx skills add shichu2024/quick-knowledge
```

享受全功能（含 .canvas / .base / defuddle / 自动打开）。

### 4.2 非 Obsidian 用户

```
npx skills add shichu2024/quick-knowledge
```

可直接使用，技能内部自动降级。仅 .canvas / .base 不可用（如需可视化，建议改用 Obsidian 或 VSCode + Markdown 预览）。

---

## 5. 测试矩阵

| 环境 | init | capture(URL) | ingest | connect | query | review |
|------|------|-------------|--------|---------|-------|--------|
| Obsidian + obsidian-skills 全装 | 完整 | defuddle | research-agent | MOC + canvas | 完整 | 完整 + .base |
| Obsidian 但仅装部分 | 完整 | 视缺失 | 完整 | 视缺失 | 完整 | 完整 |
| VSCode / Cursor / 纯文件 | 完整 | 基础 HTML→MD | 完整 | 仅 MOC（无 canvas） | 完整 | 完整（无 .base） |

---

## 6. 版本演进

- **v0.2**：5 项依赖全部接入（含降级）
- **v0.3+**：无新 obsidian-skill 依赖；新功能（memory-agent/advisor/goal/project）均为纯文件操作
- **v1.0**：CI 测试矩阵覆盖上表三种环境

---

## 7. 与设计文档的偏差说明

无偏差。本文件是 DESIGN §9 的展开。
