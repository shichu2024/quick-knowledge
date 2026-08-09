---
name: quick-kb-ingest
description: |
  把 inbox 素材正式入库为 02_areas/resources 笔记：调用 research-agent 抽取原子观点、补全 v0.2 完整 frontmatter（含 relations/context/value.reuse）、链接原始素材、给置信度初值、做冲突检测。v0.3 将接入 memory-agent 做更准确的冲突判定。
  触发词（中文）：处理 inbox / 入库 / 把这条归档 / 消化这条 / 这条入库
  Triggers (EN): process inbox / ingest this / promote this note
version: v0.2
phase: v0.2
applies_to: 00_inbox/ → 02_areas/ / 01_resources/
source_of_truth:
  - docs/DESIGN.md §6（frontmatter）· §6.7（冲突处理）
  - docs/SKILLS_SPEC.md §3
  - docs/AGENTS_SPEC.md §2（research-agent）
  - docs/dev/v0.2-loops.md WP9
  - references/frontmatter-v0.2.md
---

# quick-kb-ingest（v0.2）

> 把 inbox 一条素材变成 N 条原子笔记。**原始素材永不删除**；入库笔记通过 `source.note` 链回。
>
> **v0.2 升级**：调用 research-agent（替换 v0.1 内置 LLM）；产出完整 frontmatter（含 relations/context/value.reuse）；加入冲突检测（用 manager-agent.recommend_relations 降级，v0.3 接 memory-agent）。

---

## 1. v0.2 范围

### 做

- 扫描 inbox 候选（单条 / 子目录 / 全 inbox；6 类源）
- 调用 **research-agent** 抽取原子观点（替换 v0.1 内置 LLM）
- 分类去向：concept → `02_areas/<domain>/`、resource → `01_resources/<category>/`、idea（仍待消化）→ 留 inbox，标 `status: draft`
- 补全 **v0.2 完整 frontmatter**（含 relations/context/value.reuse）
- `source.note` 用 wikilink 指回 inbox 原始素材
- 置信度初值规则（research-agent 决定）
- **冲突检测**：调 manager-agent.recommend_relations，发现对立候选 → 提示建立 contradicts 关系

### 不做

- ❌ 调 memory-agent（v0.3 才上）—— 冲突检测用 manager-agent 降级
- ❌ 自动 maturity —— v0.3
- ❌ 自动 value.impact/uniqueness/KS —— v0.3

---

## 2. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `target` | 否 | `inbox` | 单条文件路径 / `inbox` 全量 / `00_inbox/ideas` 等子目录 |
| `domain` | 否 | research-agent 推荐 | 指定领域 |
| `depth` | 否 | `standard` | `quick` / `standard` / `deep`（v0.2 deep 与 standard 一致；v0.3 接 memory-agent 才有差异） |

---

## 3. 工作流

### 步骤 1 · 扫描候选

1. 解析 `target`，列出所有 inbox 候选
2. 按 `captured_at` 升序（FIFO）
3. 输出候选清单

### 步骤 2 · 逐条处理（standard 模式）

#### 2.1 读取与源类型识别

读取候选笔记全文。识别 `capture_type`：idea / web-clip / pdf / meeting / ai-dialog / reading。

#### 2.2 调 research-agent 抽原子观点

```
research_agent.extract_atoms(
  payload: {
    text: {{inbox 笔记正文}},
    hint: { domain: {{用户指定或推荐}}, known_tags: {{kb.config.yaml tags_vocabulary}} }
  },
  options: { max_atoms: 5 }
) → {
  found: [
    {
      note_type: "concept" | "resource",
      title, body, tags, confidence, source_excerpt
    }, ...
  ]
}
```

#### 2.3 原子化拆分

- research-agent 返回 N 条原子笔记 → 拆为 N 条
- `depth=quick` → 不拆，整篇转一条 resource（用 `summarize` intent）

#### 2.4 分类去向

| 观点类型 | 目标目录 | 模板 |
|---------|---------|------|
| concept | `02_areas/<domain>/<slug>.md` | [`templates/zh/note-concept.md`](../../templates/zh/note-concept.md) |
| resource | `01_resources/<category>/<slug>.md` | [`templates/zh/note-resource.md`](../../templates/zh/note-resource.md) |
| idea（仍不够结构化） | 留 `00_inbox/ideas/`，更新 `status: draft` | 不创建新文件 |

> v0.2 不产出 decision/goal/project/principle/belief/pattern/experience/moc/review/daily 类型。

#### 2.5 补全 v0.2 完整 frontmatter

严格按 [`references/frontmatter-v0.2.md`](../../references/frontmatter-v0.2.md)：

```yaml
---
title: {{research-agent 精炼后的标题}}
type: concept                       # 或 resource
created: {{today}}
updated: {{today}}
tags:                               # 由 suggested_tags 转正，对照 kb.config.yaml 词表
  - {{domain}}/{{topic}}
status: active                      # 默认 active；字段不全 → draft
domain: {{domain}}
confidence: {{research-agent 初值}}  # 单源 30-40 / 多源 60-75 / 一手 80-95
relations:                          # v0.2 启用 · 见 §2.7
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
context: {{research-agent 从正文提取，可选}}  # v0.2 启用
value:                              # v0.2 启用 · 仅 reuse
  reuse: 0
source:
  - note: "[[{{inbox原始素材wikilink}}]]"   # 必须 · 链回 inbox
  - url: {{若 web-clip，沿用原始 URL}}
---
```

**严禁**写入：`maturity` / `value.impact` / `value.uniqueness`（v0.3 字段）。

#### 2.6 正文生成

按对应模板章节填充（concept/resource）。**抽取失败**：留 `{{}}`，标 `status: draft`，不强行编造。

#### 2.7 关系推荐（调用 manager-agent）

```
manager_agent.recommend_relations(
  payload: { note: {{新笔记}}, candidate_pool: {{同 domain 已入库笔记}} }
) → {
  found: [
    { target: "[[Vector Database]]", type: "supports", similarity: 0.72 },
    { target: "[[模块化单体]]", type: "contradicts", similarity: 0.78 }
  ]
}
```

- supports/evolves/supersedes 候选 → 自动写入 relations（相似度 > 0.85 的 evolves 提示用户确认）
- **contradicts 候选** → 进入步骤 3 冲突检测流程

### 步骤 3 · 冲突检测与主动提醒（V2 关键）

> v0.2 用 manager-agent 降级；v0.3 接 memory-agent 后会有更准确的语义判定。

#### 3.1 检测规则

- research-agent 返回的候选中若存在标题/标签对立语义 → manager_agent.recommend_relations 标记为 `contradicts`
- 相似度 > 0.85 的笔记：
  - 标题近义 → `evolves`（自动）
  - 内容对立 → `contradicts`（提示用户）

#### 3.2 处理 contradicts

1. **不擅自选边**（ADR-011）
2. 在新笔记与既有笔记各自建立 `contradicts` 双向链接
3. **要求声明 context**：若两方都未填 `context`，提示用户：「⚠ 检测到冲突，请为双方各自声明适用上下文，否则 review 时无法呈现对照」
4. 反馈输出：

```
⚠ 冲突检测命中：
  新笔记：[[02_areas/ai-engineering/microservices]]
  既有笔记：[[02_areas/ai-engineering/modular-monolith]]
  类型：contradicts（上下文相关，非对错）
  → 已自动建立双向 contradicts 关系
  → 请补充各自的 context（推荐：[[02_areas/ai-engineering/microservices]] 的 context = "大团队、多团队并行"）
```

### 步骤 4 · 写入并反馈

对每条产出：

```
✓ 写入：02_areas/ai-engineering/rag-architecture.md
  类型：concept | 状态：active | 置信度：60
  来源：00_inbox/clips/20260809-1000-<slug>.md
  标签：ai/rag · eng/architecture
  relations：
    supports: [[Vector Database]]
    evolves: [[RAG 基础概念]]
  context: "通用 RAG 架构；创业团队请参考 [[轻量 RAG 方案]]"
  value.reuse: 0
```

### 步骤 5 · 主动提醒（manager 事件子集）

调用 `manager_agent.proactive_remind(event: "ingest_new", context: { new_note })`：

- 提示建立 `supports`/`evolves` 关系（已在 §2.7 完成）
- 库 < 50 条时关闭

### 步骤 6 · 处理报告

```
📊 Ingest 处理报告（共 N 条候选）
  ✓ 成功：X 条（concept × A / resource × B）
  ⚠ 草稿：Y 条（字段不全，已标 status: draft）
  ⚠ 冲突候选：Z 条（已建立 contradicts，请补充 context）
  ⏭ 跳过：W 条（重复或类型不支持）

  下一步建议：
    → quick-kb-connect scope={{domain}}（生成 MOC + 双链）
    → 手动复核 draft 笔记：[[list-of-drafts]]
    → 补充冲突笔记的 context：[[list-of-conflicts]]
```

### 步骤 7 · 更新 inbox 原始素材（非破坏性）

在原始素材顶部追加 callout（不改正文）：

```markdown
> [!info] 已入库
> - [[02_areas/ai-engineering/rag-architecture]]（concept · 2026-08-09）
>   - relations: supports [[Vector Database]] / evolves [[RAG 基础概念]]
> - [[01_resources/articles/...]]（resource · 2026-08-09）
```

---

## 4. 输出契约

- concept：`02_areas/<domain>/<slug>.md`
- resource：`01_resources/<category>/<slug>.md`
- frontmatter 严格遵循 [`frontmatter-v0.2.md`](../../references/frontmatter-v0.2.md)
- 反馈格式对齐 SKILLS_SPEC §通用约定

---

## 路径约束（硬性）

- **禁止绝对路径** —— 抽取产出的 concept/resource 笔记中，所有内联引用、`source.url`、`source.raw` 不得使用 `file://`、`C:\`、`/Users/...` 等绝对路径
- **外部依赖复制入库** —— 若 ingest 依赖本地外部素材，先复制到 `01_resources/` 下相应子目录，再以 vault 相对路径引用
- **source.url 仅两种合法形态** —— `https://原始来源 URL` 或 `01_resources/...` 相对路径

## 5. 边界

- **原始素材永不删除** —— inbox 文件原地保留
- **不提升 maturity** —— v0.2 不写此字段
- **不写 value.impact/uniqueness/KS** —— v0.3
- **不擅自选边** —— contradicts 双方同时建立，提示用户声明 context
- **不强填空章节** —— 抽取失败留 `{{}}`，标 `status: draft`

## 6. 降级路径

| 场景 | 降级行为 |
|------|---------|
| research-agent 不可用 | 回退为「模板套用 + 字段填充」，不抽原子观点；多观点素材作单条入库 |
| manager-agent 不可用 | 不做关系推荐与冲突检测，relations 全空，标 `needs_review: true` |
| 候选素材为空/格式损坏 | 跳过，报告 |
| 无候选（target 无文件） | 输出「inbox 已清空」 |
| 目标 domain 不存在 | 自动创建 `02_areas/<domain>/_moc.md` |
| 文件名冲突 | `-2`/`-3` |

---

## 7. 幂等保证

- **同一 inbox 候选二次 ingest**：
  - 检测 inbox 原始素材顶部 `> [!info] 已入库` callout
  - 已有 → 输出「此素材已入库：[[列表]]」，不重复处理
- **目标文件已存在** → 不覆盖，追加 `-2`

---

## 8. 自检清单

- [ ] 每条产出笔记的 `source.note` 指回 inbox 原始素材
- [ ] inbox 原始素材未被删除，顶部追加 callout
- [ ] frontmatter 含完整 v0.2 字段（含 relations/context/value.reuse）
- [ ] 无 v0.3 字段（maturity/value.impact/value.uniqueness）
- [ ] 抽取失败的笔记标 `status: draft`
- [ ] 多观点素材被正确拆分（research-agent）
- [ ] contradicts 候选已建立双向关系 + 提示补充 context
- [ ] 文件名 kebab-case
- [ ] 处理报告含统计 + 下一步建议

---

## 9. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 冲突检测用 manager-agent 而非 memory-agent | memory-agent 在 v0.3 | dev/v0.2-loops.md WP9 + 偏差检查报告 §3.3 |
| 产出完整 v0.2 frontmatter | DESIGN §6.1 V2 标准 | frontmatter-v0.2.md |
| deep 档位与 standard 一致 | v0.3 接 memory-agent 后才有差异 | dev doc 不冲突 |
| contradicts 自动建立双向 | ADR-011 + AGENTS_SPEC §4.2 不选边 | DESIGN §6.7 |
