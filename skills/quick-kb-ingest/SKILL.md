---
name: quick-kb-ingest
description: |
  把 inbox 素材正式入库为 areas/resources 笔记：抽取原子观点、补全 frontmatter、链接原始素材、给置信度初值。v0.1 简化版：内置 LLM 抽取（不调 research-agent），不做关系类型化与冲突检测。
  触发词（中文）：处理 inbox / 入库 / 把这条归档 / 消化这条 / 这条入库
  Triggers (EN): process inbox / ingest this / promote this note
version: v0.1
phase: v0.1
applies_to: inbox/ → areas/ / resources/
source_of_truth:
  - docs/DESIGN.md §6（frontmatter）
  - docs/SKILLS_SPEC.md §3
  - docs/dev/v0.1-mvp.md WP4
  - references/frontmatter-v0.1.md
---

# quick-kb-ingest（v0.1 · 简化版）

> 把 inbox 一条素材变成 N 条原子笔记。**原始素材永不删除**；入库笔记通过 `source.note` 链回。

---

## 1. 何时调用

- 用户说「处理 inbox」「把这条入库」「消化 [[inbox/clips/...]]」
- daily 技能识别到候选想法后建议调用
- capture 写入后用户主动要求整理

## 2. v0.1 范围

### 做

- 扫描 inbox 候选（单条 / 子目录 / 全 inbox）
- 抽取原子观点（一笔记一观点；多观点拆成多条）
- 分类去向：`concept` → `areas/<domain>/`、`resource` → `resources/<category>/`、`idea`（仍待消化）留在 `inbox/ideas/` 并标 `status: draft`
- 补全 v0.1 frontmatter（见 `references/frontmatter-v0.1.md`）
- `source.note` 用 wikilink 指回 inbox 原始素材
- 置信度初值规则（单源 40 / 多源 60+ / 一手 80+）

### 不做

- ❌ 调用 research-agent（v0.2 才上）—— 用内置 LLM 直接抽取
- ❌ 关系类型化（`relations`）—— v0.2
- ❌ 冲突检测（contradicts）—— v0.2
- ❌ 自动 maturity —— v0.3
- ❌ 自动 value.reuse —— v0.2（依赖 manager-agent）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `target` | 否 | `inbox` | 单条文件路径 / `inbox` 全量 / `inbox/ideas` 等子目录 |
| `domain` | 否 | AI 推荐 | 指定领域，未指定则 AI 基于内容+`kb.config.yaml` 推荐 |
| `depth` | 否 | `standard` | `quick`（不拆原子观点，单条直转）/ `standard`（默认，拆分）/ `deep`（v0.2 接 research-agent） |

---

## 4. 工作流

### 步骤 1 · 扫描候选

1. 解析 `target`：
   - 文件路径 → 单条
   - 目录路径 → 该目录下所有 `.md`
   - `inbox` → `ideas/clips/meetings/ai-dialogs/reading` 全扫（v0.1 通常只有前两者有内容）
2. 按 `captured_at` 升序排列（FIFO）。
3. 输出候选清单：

   ```
   发现 N 条候选（按时间排序）：
     1. inbox/clips/20260809-1000-<slug>.md  · 2026-08-09 10:00
     2. inbox/ideas/20260809-1100-<slug>.md  · 2026-08-09 11:00
   开始处理…
   ```

### 步骤 2 · 逐条处理（standard 模式）

对每条 inbox 候选：

#### 2.1 读取与理解

读取候选笔记全文 + frontmatter。识别：
- **源类型**：idea / web-clip / （未来：pdf/meeting/ai-dialog）
- **核心观点数量**：用内置 LLM 抽取，输出 `[{观点, 类型, domain, tags}, ...]`

#### 2.2 原子化拆分

- 一条素材含 N 个独立观点 → 拆成 N 条笔记
- 单观点 → 1 条
- `depth=quick` → 不拆，整篇转一条 resource

#### 2.3 分类去向

| 观点类型 | 目标目录 | 模板 |
|---------|---------|------|
| 概念/原理/心智模型（concept） | `areas/<domain>/<slug>.md` | `templates/zh/note-concept.md` |
| 外部资源摘要（resource） | `resources/<category>/<slug>.md` | `templates/zh/note-resource.md` |
| 个人想法/灵感（仍不够结构化） | 留 `inbox/ideas/`，更新 `status: draft` | 不创建新文件，原笔记加 callout |

> v0.1 不产出 decision/goal/project/principle/belief/pattern/experience/moc/daily/review 类型，这些由对应阶段技能产出。

#### 2.4 补全 frontmatter（严格按 v0.1 子集）

参考 [`references/frontmatter-v0.1.md`](../../references/frontmatter-v0.1.md)：

```yaml
---
title: {{抽取/精炼后的标题}}
type: concept                      # 或 resource
created: {{today}}
updated: {{today}}
tags:                              # 由 suggested_tags 转正；对照 kb.config.yaml 词表（v0.1 词表可空）
  - {{domain}}/{{topic}}
status: active                     # 默认 active；若抽取信息不全 → draft
domain: {{domain}}
confidence: {{初值}}               # 单源 40 / 多源 60+ / 一手 80+；见 §2.6
source:
  - note: "[[{{inbox原始素材wikilink}}]]"   # 必须有；链回 inbox
  - url: {{若 web-clip，沿用原始 URL}}
---
```

**严禁**写入：`maturity` / `relations` / `context` / `value` / 其他 v0.2+ 字段。

#### 2.5 正文生成

- concept：按 `note-concept.md` 模板的章节（核心定义/为什么有用/关键组成/应用场景/示例/关联知识/待验证）填充
- resource：按 `note-resource.md` 模板章节（一句话概括/关键观点/我为什么收藏/关键摘录/相关笔记/待行动）填充
- **抽取失败降级**：若 LLM 无法稳定填充某章节，留 `{{}}`，整体标 `status: draft`，不强行编造

#### 2.6 置信度初值规则

| 来源 | confidence 初值 |
|------|----------------|
| 单源（一篇博客/一次会议/一段想法） | **40** |
| 多源（待 ingest 时已有 2+ 来源佐证） | **60** |
| 一手实验/官方文档/本人亲历的失败 | **80+** |

- v0.1 由 LLM 基于来源类型自动判断；用户可在事后手动调整。
- 不强制写入；若不确定则留空（v0.1 子集 `confidence` 可选）。

#### 2.7 文件命名

`<vault-root>/<target-dir>/<slug>.md`

- `<slug>` kebab-case，限 40 字符，从标题归一化
- 重名：追加 `-2`/`-3` 后缀

### 步骤 3 · 写入并反馈

对每条产出：

```
✓ 写入：areas/ai-engineering/rag-architecture.md
  类型：concept | 状态：active | 置信度：60
  来源：inbox/clips/20260809-1000-<slug>.md
  标签：ai/rag · eng/architecture
  → 抽取自 1/N 条候选
```

### 步骤 4 · 处理报告（一批结束后）

```
📊 Ingest 处理报告（共 N 条候选）
  ✓ 成功：X 条（concept × A / resource × B）
  ⚠ 草稿：Y 条（字段不全，已标 status: draft）
  ⏭ 跳过：Z 条（重复或类型不支持）

  下一步建议：
    → quick-kb-connect scope={{domain}}         # v0.2 启用
    → 手动复核 draft 笔记：[[list-of-drafts]]
```

### 步骤 5 · 更新 inbox 原始素材（非破坏性）

- **不删除**原始 inbox 文件
- 在原始素材顶部追加一行 callout（不改正文）：

  ```markdown
  > [!info] 已入库
  > - [[areas/ai-engineering/rag-architecture]]（concept · 2026-08-09）
  > - [[resources/articles/...]]（resource · 2026-08-09）
  ```

---

## 5. 输出契约

### 5.1 正式笔记路径

- concept：`areas/<domain>/<slug>.md`
- resource：`resources/<category>/<slug>.md`，`category ∈ {articles, books, courses, repos}`

### 5.2 frontmatter

严格遵循 [`references/frontmatter-v0.1.md`](../../references/frontmatter-v0.1.md) §2 正式笔记子集。

### 5.3 反馈格式

对齐 SKILLS_SPEC §"输出反馈格式"。

---

## 6. 边界

- **原始素材永不删除** —— inbox 文件原地保留，Review 闭环统一清理。
- **不提升 maturity** —— v0.1 不写此字段。
- **不写关系** —— `relations`/`context`/`value` 留给 v0.2。
- **不调 agent** —— v0.1 用内置 LLM；`depth: deep` 在 v0.1 退化为 `standard`。
- **不强填空章节** —— 抽取失败的章节留 `{{}}` 并标 `status: draft`。

## 7. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 内置 LLM 抽取不稳定 | 提供 prompt 模板（见 §8）；多次抽取结果不一致 → 标 draft |
| 候选素材为空/格式损坏 | 跳过，报告「跳过：格式不支持」 |
| 无候选（target 无文件） | 输出「inbox 已清空」 |
| 目标 domain 不存在于 `areas/` | 自动创建 `areas/<domain>/_moc.md`（与 init 一致） |
| 文件名冲突 | 追加 `-2`/`-3` |
| 抽取观点数量为 0 | 标记为 `idea`（保留 inbox），输出「暂不足以入库」 |

---

## 8. 内置抽取 Prompt（参考）

```
你是 quick-knowledge 知识库的 ingest 助手。给定一条 inbox 素材：

1. 抽取其中的独立观点（一笔记一观点）。
2. 每个观点判断类型：
   - concept：概念/原理/心智模型（用户自己的理解）
   - resource：外部内容摘要（保留作者原意）
   - idea：仍是灵感，不足以结构化（保留 inbox）
3. 对 concept/resource 观点，按模板章节填充：
   - concept: 核心定义 / 为什么有用 / 关键组成 / 应用场景 / 示例 / 关联知识 / 待验证
   - resource: 一句话概括 / 关键观点 / 我为什么收藏 / 关键摘录 / 相关笔记 / 待行动
4. 推断 domain 与 tags（domain/topic 形式）。
5. 判断 confidence 初值：单源 40 / 多源 60+ / 一手 80+。
6. 抽取失败的字段留 {{}}，不要编造。
7. 严禁写入 maturity / relations / context / value 字段（这些在 v0.2+ 才有）。

输出 JSON：
[
  {
    "type": "concept" | "resource" | "idea",
    "title": "...",
    "domain": "...",
    "tags": ["domain/topic", ...],
    "confidence": 40|60|80,
    "frontmatter": {...},
    "body": "完整 Markdown 正文，按模板章节组织"
  }, ...
]
```

---

## 9. 幂等保证

- **同一条 inbox 候选二次 ingest**：
  - 检测 inbox 原始素材顶部是否已有 `> [!info] 已入库` callout
  - 已有 → 输出「此素材已入库：[[已产出的笔记列表]]」，不重复处理
- **目标文件已存在** → 不覆盖，追加 `-2` 后缀并提示

---

## 10. 自检清单（执行后）

- [ ] 每条产出笔记的 `source.note` 指回 inbox 原始素材
- [ ] inbox 原始素材未被删除，顶部追加 `已入库` callout
- [ ] frontmatter 仅含 v0.1 子集字段（无 maturity/relations/context/value）
- [ ] 抽取失败的笔记标 `status: draft`
- [ ] 多观点素材被正确拆分
- [ ] 文件名 kebab-case，无中文/空格
- [ ] 处理报告含「成功/草稿/跳过」统计

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源依据 |
|--------|------|-----------|
| 不调 research-agent | v0.2 才上，v0.1 用内置 LLM | dev/v0.1-mvp.md WP4 「不做」清单 |
| 不做 relations/context/value | v0.2 引入（依赖 connect/manager） | dev/v0.1-mvp.md WP4 「不做」清单 + frontmatter-v0.1.md §2.2 |
| 不做冲突检测 | v0.2 引入（依赖 memory-agent） | 同上 |
| `confidence` 仍写入 | DESIGN §6.1 标准字段；WP4 明确要求「置信度初值规则」 | 见 frontmatter-v0.1.md §2.1 |
| `status: draft` 标记抽取失败 | 兜底降级，避免阻塞 | dev/v0.1-mvp.md §7 风险与降级 |
