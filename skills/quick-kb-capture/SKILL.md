---
name: quick-kb-capture
description: |
  低摩擦采集：把用户的想法、网页 URL、PDF、会议转写、AI 对话、阅读笔记快速写入 inbox。v0.2 接入 defuddle 抓取干净正文；新增 PDF/会议/AI 对话/阅读四类源；主动提醒（memory 事件）推迟 v0.3。
  触发词（中文）：记一下 / 快记 / 收藏这个 / 抓这个网页 / 保存这段 / 记个想法 / 抓 PDF / 保存对话
  Triggers (EN): capture this / save this / clip this page / quick note / capture pdf
version: v0.2
phase: v0.2
applies_to: inbox/
source_of_truth:
  - docs/DESIGN.md §6.9（inbox 最小 frontmatter）· §9.2（obsidian-skills 依赖）
  - docs/SKILLS_SPEC.md §2
  - docs/dev/v0.2-loops.md WP9
  - references/frontmatter-v0.2.md §7
---

# quick-kb-capture（v0.2）

> 把现在脑子里的东西 / 看到的页面 / 拿到的素材快速落进 inbox。**采集即廉价**：只写最小 frontmatter，分类与提炼留给 ingest。
>
> **v0.2 升级**：接 defuddle 抓干净正文；新增 PDF/会议/AI 对话/阅读四类源；capture 路径不再用基础 HTML→MD（缺失时降级）。

---

## 1. 何时调用

- 用户说"记一下 …"、"快记 …"、「抓这个网页 …」、「保存这段对话」、「抓这个 PDF」
- daily 日志识别到「值得入库」时，由 daily 技能建议调用
- review 提示「capture 候选」时

## 2. v0.2 支持的源类型

| 源类型 | v0.1 | v0.2 | 流向 |
|--------|------|------|------|
| 纯文本想法 | ✓ | ✓ | `inbox/ideas/` |
| URL（网页） | ✓ 基础 | ✓ defuddle | `inbox/clips/` + `_raw/` |
| PDF / 文件 | ✗ | ✓ | `inbox/reading/` |
| 会议转写 | ✗ | ✓ | `inbox/meetings/` |
| AI 对话 | ✗ | ✓ | `inbox/ai-dialogs/` |
| 阅读笔记 | ✗ | ✓ | `inbox/reading/` |

**v0.2 仍不做**：主动提醒（memory 事件，DESIGN §7.6）→ v0.3

---

## 3. 输入

| 参数 | 必填 | 形态 | 说明 |
|------|------|------|------|
| `content` | 二选一 | string | 纯文本/转写文本 |
| `url` | 二选一 | string | 网页链接 |
| `file_path` | 二选一 | string | PDF/文件路径 |
| `source_type` | 否 | enum | 强制指定 `idea`/`web-clip`/`pdf`/`meeting`/`ai-dialog`/`reading`；未给则自动判定 |
| `source_hint` | 否 | string | 用户标注来源（「同事 X 说的」「某书第 3 章」） |
| `suggested_tags` | 否 | string[] | 用户主动给的候选标签；未给则 AI 推断 |

> `content` / `url` / `file_path` 至少一个。组合给出时按主导源处理，其他作为附注。

---

## 4. 工作流（通用）

### 步骤 1 · 识别源类型

| 判定 | 流向 |
|------|------|
| URL 正则匹配 | → web-clip |
| `.pdf` / `.epub` 后缀 | → pdf |
| 含「会议」「参会」「主持人」等会议关键词 | → meeting（若 source_type=meeting 强制） |
| 含「AI 说」「Claude 答」「GPT」等对话关键词 | → ai-dialog（若 source_type=ai-dialog 强制） |
| 其他（文本） | → idea 或 reading（用户选） |

### 步骤 2 · 抓取与清洗（按源类型）

#### 2a · idea（纯文本）

- 标题：从 content 抽取前 20-30 字符或核心名词
- 不做改写

#### 2b · web-clip（URL）

1. **优先调 defuddle**（obsidian-skills/defuddle）抓干净正文
2. **保留原始**：HTML 写入 `inbox/clips/_raw/YYYYMMDD-HHMM-<slug>.html`
3. **降级**：defuddle 不可用 → 基础 HTML→MD（去 `<script>/<style>/<nav>/<footer>/<aside>`，保留 `<article>/<main>/<section>`）
4. **失败**：抓取失败（404/付费墙/超时）→ 仍写笔记，`partial: true`

#### 2c · pdf

1. 调 runtime 的 PDF 文本提取（如 pdfplumber / pdftotext）
2. 失败 → 标 `partial: true`，提示用户提供纯文本
3. 原始 PDF 路径写入 `source.raw`

#### 2d · meeting

1. 接受转写文本（v0.2 不接录音；录音转写由用户事先完成）
2. 不做结构化（留给 ingest）；capture 仅保留全文 + 元信息（时间/与会者，若用户提供）

#### 2e · ai-dialog

1. 接受对话文本（用户粘贴或 runtime 提供）
2. 保留角色标识（user/assistant），不做摘要
3. 可选：识别「值得记」的关键发言段，标 `highlight: [段落索引]`（hint 给 ingest）

#### 2f · reading

1. 用户阅读时的笔记片段
2. 与 idea 区分：reading 通常带书本/课程出处，idea 是原创灵感

### 步骤 3 · 去重检测

- web-clip：URL 完全相同 → 直接拒绝（提示已存在）；标题相似度 > 0.85 → 同 idea 流程提示
- 其他源：标题相似度 > 0.85（与近 7 天同子目录文件比对）→ 提示

```
⚠ 疑似重复：inbox/clips/20260809-1000-<existing>.md（相似度 0.92）
  - [合并] / [新建] / [取消]
```

### 步骤 4 · 生成文件名

`inbox/<source-dir>/YYYYMMDD-HHMM-<slug>.md`

| source_type | 子目录 |
|-------------|--------|
| idea | `inbox/ideas/` |
| web-clip | `inbox/clips/` |
| pdf / reading | `inbox/reading/` |
| meeting | `inbox/meetings/` |
| ai-dialog | `inbox/ai-dialogs/` |

`<slug>` kebab-case，限 40 字符。重名追加 `-2`/`-3`。

### 步骤 5 · 写入文件（frontmatter）

所有源统一走 inbox 最小集（[`frontmatter-v0.2.md` §7](../../references/frontmatter-v0.2.md)）：

```yaml
---
title: {{自动生成的简短标题}}
captured_at: {{YYYY-MM-DDTHH:MM}}
capture_type: {{idea | web-clip | pdf | meeting | ai-dialog | reading}}
source:
  - url: {{原始 URL，若有}}
  - raw: {{原始资料路径，若有}}
  - person: {{来源人，若有}}
  - fetched_at: {{抓取时间，若有}}
suggested_tags:            # AI 预标注候选；ingest 时转正为 tags
  - {{domain}}/{{topic}}
partial: false             # 抓取/解析不全时改 true
---
```

**严禁**在 inbox 阶段写入：`type` / `status` / `maturity` / `relations` / `context` / `value` / `confidence`。这些由 ingest 阶段补全。

### 步骤 6 · 反馈输出

```
✓ 已采集（{{source_type}} · inbox/{{dir}}/20260809-1430-<slug>.md）
  标题：{{生成的标题}}
  候选标签：{{suggested_tags}}
  partial: {{true|false}}
  下一步：
    → quick-kb-ingest inbox/{{dir}}/20260809-1430-<slug>.md
```

---

## 5. 边界

- **不改正文** —— 用户原文 / 抓取正文逐字保留
- **不做分类决策** —— `suggested_tags` 是 hint
- **不删除原始** —— `_raw/` 与 `source.raw` 永久保留
- **不主动提醒** —— v0.2 不调 memory-agent
- **不抓付费墙内容** —— 标 `partial: true`

## 6. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 无 defuddle | 退为基础 HTML→MD（去 script/style/nav） |
| 无 web fetch 工具 | 仅存 URL 不抓正文，正文写「> runtime 未提供 web fetch」 |
| PDF 解析失败 | `partial: true` + 提示用户给纯文本 |
| 无网络 | `partial: true` + 写入失败原因 |
| 标题推断失败 | 时间戳作标题 |
| suggested_tags 推断失败 | 留空数组 |
| 文件名冲突 | `-2`/`-3` 后缀 |

## 7. 幂等保证

- URL 完全相同 → 拒绝重复
- 标题相似度 > 0.85 → 提示去重
- 永远不覆盖既有文件

---

## 8. 自检清单

- [ ] 文件路径正确（按 source_type 进入对应子目录）
- [ ] frontmatter 含 `title` + `captured_at`
- [ ] web-clip/pdf 写入 `_raw/` 或 `source.raw`
- [ ] 用户原文/抓取正文未被改写
- [ ] 反馈输出含「下一步 → ingest」提示
- [ ] 无 v0.2 正式字段被提前写入（maturity/relations/context/value 等）

---

## 9. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 不调 memory-agent 主动提醒 | memory-agent 在 v0.3 | dev/v0.2-loops.md WP10 |
| meeting 不接录音 | v0.2 仅文本转写；录音转写由用户事先完成 | 实现简化，不偏离设计 |
| ai-dialog 可选 highlight hint | ingest 时帮助识别关键段，不强制 | 不冲突 SKILLS_SPEC §2 |
