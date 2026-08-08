---
name: quick-kb-capture
description: |
  低摩擦采集：把用户的想法、网页 URL、对话片段快速写入 inbox。v0.1 仅支持纯文本和 URL（PDF/会议/AI 对话推迟到 v0.2）。
  触发词（中文）：记一下 / 快记 / 收藏这个 / 抓这个网页 / 保存这段 / 记个想法
  Triggers (EN): capture this / save this / clip this page / quick note
version: v0.1
phase: v0.1
applies_to: inbox/
source_of_truth:
  - docs/DESIGN.md §6.9（inbox 最小 frontmatter）
  - docs/SKILLS_SPEC.md §2
  - docs/dev/v0.1-mvp.md WP3
  - references/frontmatter-v0.1.md §3
---

# quick-kb-capture（v0.1 · 简化版）

> 把现在脑子里的东西快速落进 inbox。**采集即廉价**：只写最小 frontmatter，分类与提炼留给 ingest。

---

## 1. 何时调用

- 用户说"记一下 …"、"快记 …"、「抓这个网页 …」
- 用户提供一个 URL，希望保存内容
- daily 日志中识别到「值得入库」时，由 daily 技能建议调用本技能

## 2. v0.1 范围

| 源类型 | v0.1 支持 | 说明 |
|--------|----------|------|
| 纯文本想法 | ✓ | → `inbox/ideas/` |
| URL（网页） | ✓ 基础 | → `inbox/clips/`，原始 HTML 存 `inbox/clips/_raw/` |
| PDF / 文件 | ✗ | v0.2（接 defuddle） |
| 会议转写 | ✗ | v0.2 |
| AI 对话 | ✗ | v0.2 |

**v0.1 不做**：

- 主动提醒（DESIGN §7.6 memory 事件）→ v0.2+
- defuddle 集成 → v0.2（v0.1 用基础 HTML→Markdown）
- embedding 去重 → v0.1 用标题相似度

---

## 3. 输入

| 参数 | 必填 | 形态 | 说明 |
|------|------|------|------|
| `content` | 二选一 | string | 纯文本想法 |
| `url` | 二选一 | string | 网页链接 |
| `source_hint` | 否 | string | 用户标注来源（如「同事 X 说的」「某本书第 3 章」） |
| `suggested_tags` | 否 | string[] | 用户主动给的候选标签；未给则 AI 推断 |

> 至少要有 `content` 或 `url` 之一。两者都给则按 URL 主线处理，`content` 作为用户的附注并入。

---

## 4. 工作流

### 步骤 1 · 识别源类型

| 判定 | 流向 |
|------|------|
| 输入匹配 URL 正则 | → `web-clip` 流程 |
| 其他（文本） | → `idea` 流程 |

### 步骤 2a · `idea` 流程（纯文本）

1. **生成标题**：从 `content` 抽取前 20-30 字符或核心名词作为 `title`。
2. **生成文件名**：`inbox/ideas/YYYYMMDD-HHMM-<slug>.md`（`<slug>` kebab-case，从标题归一化，限 40 字符）。
3. **去重检测**：扫描 `inbox/ideas/` 近 7 天文件，标题字符相似度 > 0.85（基于 token Jaccard 或 Levenshtein 归一化）时，提示：

   ```
   ⚠ 疑似重复：inbox/ideas/20260809-1015-<existing>.md（相似度 0.92）
     - [合并] 追加本次内容到已有笔记
     - [新建] 仍创建新笔记
     - [取消] 丢弃本次输入
   ```

4. **写入文件**：使用 [`templates/zh/note-idea.md`](../../templates/zh/note-idea.md) 模板，填充：
   - `title`、`captured_at`（当前 ISO 8601 含时间）
   - `capture_type: idea`
   - `suggested_tags`（用户给的优先；否则 AI 从内容推 1-3 个，**不写正式 tags**）
   - `source`（如有 `source_hint`）
5. **正文**：用户原文逐字保留，不做改写。

### 步骤 2b · `web-clip` 流程（URL）

1. **抓取页面**：
   - 调用 runtime 的 web fetch 工具
   - **保留原始**：将原始 HTML 写入 `inbox/clips/_raw/YYYYMMDD-HHMM-<slug>.html`
   - **正文清洗**（v0.1 基础版）：
     - 移除 `<script>`/`<style>`/`<nav>`/`<footer>`/`<aside>`
     - 保留 `<article>`/`<main>`/`<section>` 主体
     - HTML→Markdown：标题、段落、列表、代码块、图片 alt
     - **失败降级**：若抓取失败（404/付费墙/超时），仍写入笔记，标 `partial: true`，正文写「抓取失败原因 + 用户附注」

2. **生成标题**：优先用 `<title>` 或 `<h1>`，否则取 URL slug。

3. **生成文件名**：`inbox/clips/YYYYMMDD-HHMM-<slug>.md`。

4. **去重检测**：URL 完全相同 → 直接提示「此 URL 已采集过：[文件名]」，默认拒绝；URL 不同但标题相似度 > 0.85 → 同 `idea` 流程的去重提示。

5. **写入文件**：基于 `templates/zh/note-idea.md` 变体（`capture_type: web-clip`）：

   ```yaml
   ---
   title: {{页面标题}}
   captured_at: 2026-08-09T14:30
   capture_type: web-clip
   source:
     - url: {{原始 URL}}
     - raw: inbox/clips/_raw/20260809-1430-<slug>.html
     - fetched_at: {{抓取时间}}
   suggested_tags:
     - {{domain}}/{{topic}}
   partial: false                  # 抓取不全时改 true
   ---
   ```

6. **正文**：干净 Markdown 正文，顶部加一行 `> 来源：[{{域名}}]({{url}}) · 抓取于 {{date}}`。

### 步骤 3 · 反馈输出

```
✓ 已采集（idea · inbox/ideas/20260809-1430-<slug>.md）
  标题：{{生成的标题}}
  候选标签：{{suggested_tags}}
  下一步：
    → quick-kb-ingest inbox/ideas/20260809-1430-<slug>.md
```

或：

```
✓ 已采集（web-clip · inbox/clips/20260809-1430-<slug>.md）
  来源：https://example.com/article
  原始：inbox/clips/_raw/20260809-1430-<slug>.html
  标题：{{页面标题}}
  下一步：
    → quick-kb-ingest inbox/clips/20260809-1430-<slug>.md
```

### 步骤 4 · 提示下一步（非阻塞）

写入后追加一行（不打断用户当前思路）：

> 💡 有空时运行 `quick-kb-ingest inbox/` 把它正式入库。本提示不强制。

---

## 5. 输出契约

### 5.1 文件路径

- idea：`inbox/ideas/YYYYMMDD-HHMM-<slug>.md`
- web-clip：`inbox/clips/YYYYMMDD-HHMM-<slug>.md` + `inbox/clips/_raw/...html`

### 5.2 frontmatter 严格遵循 DESIGN §6.9 + `references/frontmatter-v0.1.md §3`

inbox 最小集：

```yaml
---
title:
captured_at:
---
```

扩展字段（capture 用）：`capture_type` / `source.{url,raw,fetched_at,person}` / `suggested_tags` / `partial`。

**严禁**在 inbox 阶段写入：`type`/`status`/`maturity`/`relations`/`context`/`value`/`confidence`。这些由 ingest 阶段补全。

### 5.3 反馈格式

对齐 SKILLS_SPEC §通用约定 §"输出反馈格式"，但 v0.1 简化版省略 `类型/成熟度/关联`（这些字段在 inbox 不存在）。

---

## 6. 边界

- **不改正文** —— 用户原文 / 抓取正文逐字保留。
- **不做分类决策** —— `suggested_tags` 是 hint，不强制为 `tags`。
- **不删除原始** —— `_raw/` 永久保留。
- **不主动提醒** —— v0.1 不调 memory-agent。
- **不抓付费墙内容** —— 检测到登录墙时标 `partial: true`，写入「需要登录才能访问」。

## 7. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 无网络（URL 抓取失败） | 写入笔记，`partial: true`，正文写「抓取失败：{{原因}}」+ 用户附注 |
| 无 web fetch 工具可用 | 退化为「只存 URL 不抓正文」，正文写「> runtime 未提供 web fetch；正文待手动补」 |
| HTML 解析异常 | 保留纯文本提取版，标 `partial: true` |
| 标题无法推断 | 用时间戳作标题（`无标题-20260809-1430`） |
| 文件名冲突 | 追加 `-2`/`-3` 后缀 |
| suggested_tags 推断失败 | 留空数组，不强制 |

## 8. 幂等保证

- **URL 完全相同** → 不重复写入，提示已存在路径
- **内容相同（标题相似度 > 0.85）** → 提示去重，由用户决定
- **重新运行**：永远不覆盖既有文件；如需更新，先 rename 旧文件

---

## 9. 自检清单（执行后）

- [ ] 文件已写入正确路径（`inbox/ideas/` 或 `inbox/clips/`）
- [ ] frontmatter 含 `title` + `captured_at`
- [ ] web-clip 同时写入 `_raw/` 原始
- [ ] 用户原文/抓取正文未被改写
- [ ] 反馈输出含「下一步 → ingest」提示
- [ ] 无 v0.2+ 字段被提前写入

---

## 10. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源依据 |
|--------|------|-----------|
| 仅支持 idea / web-clip 两类源 | v0.1 范围（dev WP3 明确） | dev/v0.1-mvp.md WP3 |
| 不调 defuddle，用基础 HTML→MD | v0.2 才集成 obsidian-skills | dev/v0.1-mvp.md WP3 关键点 |
| 标题相似度去重而非 embedding | 无 embedding，v0.1 简化 | dev/v0.1-mvp.md WP3 关键点 |
| inbox frontmatter 加入扩展字段（capture_type/suggested_tags） | DESIGN §6.9 允许 inbox 自由扩展；SKILLS_SPEC §2 输出格式如此 | docs/SKILLS_SPEC.md §2 输出示例 |
