---
version: V1
updated: 2026-08-09
phase: v0.2
applies_to: v0.2 技能产出的所有正式笔记
source_of_truth: docs/DESIGN.md §6
supersedes: references/frontmatter-v0.1.md（v0.1 子集仍兼容，v0.2 起技能产出走本文档）
---

# v0.2 · Frontmatter 完整规范

> 本文件锁定 v0.2 阶段所有技能产出的 frontmatter 字段范围。在 v0.1 子集基础上新增 `relations`（类型化）、`context`、`value.reuse`，对应 DESIGN V2 §6.1/6.6/6.7/6.8。
>
> **真相源**：`docs/DESIGN.md` §6。本文件仅是 v0.2 阶段的字段声明。

---

## 1. 与 v0.1 的差异

| 字段 | v0.1 | v0.2 | 备注 |
|------|------|------|------|
| `relations` | ❌ 不写 | ✓ 写入（connect / ingest 时填充） | 类型化关系，DESIGN §6.7 |
| `context` | ❌ 不写 | ✓ 可选写入（ingest 时从正文提取） | 自由文本，DESIGN §6.8 |
| `value.reuse` | ❌ 不写 | ✓ 自动写入初值 0；review 时刷新 | DESIGN §6.6 |
| `maturity` | ❌ 不写 | ❌ 仍推迟到 v0.3 | 依赖认知资产与 KS |
| `value.impact`/`uniqueness` | ❌ 不写 | ❌ 仍推迟（手动可选） | 与 KS 一起在 v0.3 启用 |

> v0.1 旧笔记**不强制回填**这些字段；用户可通过 v0.4 的 `quick-kb-normalize` 批量补齐。

---

## 2. 字段清单（正式笔记）

| 字段 | 必填 | 类型 | v0.2 取值 / 说明 | 对应 DESIGN |
|------|------|------|----------------|-------------|
| `title` | ✓ | string | 笔记标题 | §6.1 |
| `type` | ✓ | enum | v0.2 仍仅 concept/resource/idea/daily/moc/review（principle/belief/pattern/experience 推迟 v0.3） | §6.2 |
| `created` | ✓ | ISO date | YYYY-MM-DD | §6.1 |
| `updated` | ✓ | ISO date | YYYY-MM-DD | §6.1 |
| `tags` | ✓ | string[] | 受控标签 | §6.1 |
| `status` | ✓ | enum | inbox/draft/active/done/cancelled/archived（v0.2 完整 6 态，因引入归档概念） | §6.3 |
| `source` | 可选 | list of `{url?, note?}` | 原始来源 | §6.1 |
| `domain` | 可选 | string | 所属领域；可含 `/` 表达嵌套（如 `programming/python`、`ai-engineering/rag`）。嵌套规则由 `kb.config.yaml.domain_taxonomy` 约束，缺省时退为单层 kebab-case。路径段全部小写 kebab-case，深度建议 ≤ 3。 | §6.1 |
| `confidence` | 可选 | integer 0-100 | ingest 时初值；用户可改。**全局统一 0-100 整数量纲**（v1.5 WP2 定档）。历史 0-1 小数写法由 normalize 自动迁移。 | §6.5 |
| **`relations`** | ✓（结构存在，子键可空） | object | 类型化关系（见 §3） | §6.7 |
| **`context`** | 可选 | string | 自由文本适用上下文 | §6.8 |
| **`value`** | ✓（结构存在，子键可空） | object | 价值维度（见 §4） | §6.6 |

### 2.1 显式排除（v0.3+ 才允许）

| 字段 | 引入阶段 | 原因 |
|------|---------|------|
| `maturity` | v0.3 | 依赖认知资产目录与 KS 排序逻辑 |
| `value.impact`（手填） | v0.3 | KS 计算需要 |
| `value.uniqueness` | v0.3 | 同上 |

> v0.2 写入 `value` 时**仅含 `reuse`**（自动），不写 `impact`/`uniqueness`。

---

## 3. relations 字段（DESIGN §6.7）

```yaml
relations:
  supports: ["[[Vector Database]]"]        # A 支撑/佐证 B（对称）
  contradicts: []                          # A 与 B 冲突（上下文相关，非对错，对称）
  evolves: ["[[RAG 基础概念]]"]            # A 由 B 演化而来（有向 B→A）
  supersedes: []                           # A 取代了过期的 B（有向 A→B）
```

### 3.0.1 反向键（自动补全，connect 写入）

有向关系写入 A 的正向键时，自动在目标笔记 B 补对应反向键。反向键与正向键同 schema（`string[]`，元素为 wikilink），仅语义反向：

```yaml
relations:
  evolved_by: ["[[RAG 架构设计]]"]         # B 被 A 演化自（A.evolves → B 的反向）
  superseded_by: ["[[RAG v2]]"]            # B 被 A 取代（A.supersedes → B 的反向）
  source_of: ["[[衍生笔记]]"]              # B 是 A 的衍生来源（A.derived_from → B 的反向）
  refined_by: ["[[精炼版]]"]               # B 被 A 精炼（A.refines → B 的反向）
```

| 反向键 | 对应正向键 | 语义 |
|--------|-----------|------|
| `evolved_by` | `evolves` | B 被 A 演化自（A 在 evolves 中列出 B） |
| `superseded_by` | `supersedes` | B 被 A 取代（A 在 supersedes 中列出 B） |
| `source_of` | `derived_from` | B 是 A 的衍生来源（A 在 derived_from 中列出 B） |
| `refined_by` | `refines` | B 被 A 精炼（A 在 refines 中列出 B） |

**写入规则**：
- 反向键由 connect 技能在写入正向键时自动补全（详见 `skills/quick-kb-connect/SKILL.md` §5.2.1）。
- 补全幂等——已存在不重复追加。
- 反向键为可选字段，结构不存在时视为空（不强制要求 4 键齐全）。

### 3.0.2 derived_from / derived_to（v1.5 WP4 · 支持多对一派生）

Decision Ledger 派生 experience 时使用。**强制 YAML list of wikilink**（不支持单字符串），以支持「多个 decision → 一条 experience」的多对一场景。

```yaml
# experience 笔记
relations:
  derived_from:
    - "[[04_projects/<slug>/decisions/2026-08-13-auth]]"
    - "[[04_projects/<slug>/decisions/2026-08-14-token]]"   # 多对一：两条 decision 合并派生
  source_of: []                                             # 反向键（被派生时填）

# 对应 decision 笔记
relations:
  derived_to:
    - "[[07_principles/experiences/2026-08-15-auth-token-lesson]]"
```

**规则**：
- 派生判定（project SKILL §6 step 3.1）：同 domain + 同 lesson 主题词 → 合并既有 experience，`derived_from` 追加
- 反向键 `source_of` 由 connect/project 自动补全，幂等
- 格式违规（单字符串）由 normalize `schema_check` 拦截

### 3.1 v0.2 写入时机

| 时机 | 写入字段 | 来源 |
|------|---------|------|
| ingest 新笔记 | `supports`/`evolves`（如能从已有笔记推断） | quick-kb-manager-agent.recommend_relations |
| connect 显式调 | 全部 4 类 | quick-kb-manager-agent.recommend_relations + 用户确认 |
| 冲突检测命中 | `contradicts` 双向 | ingest 时由 manager 候选 + 用户确认 |
| 笔记取代（手填或 review） | `supersedes` | 用户确认 |

### 3.2 V1 兼容（扁平 `related`）

- 仍有效，视作未类型化的弱关联（默认归入 `supports`）
- v0.2 技能**不主动写** `related`，但保留既有 `related` 字段不删除
- 批量迁移由 v0.4 `quick-kb-normalize` 完成

### 3.3 冲突处理原则（DESIGN §6.7 核心）

- `contradicts` 不代表某一方错误 —— 而是标注**适用上下文不同**，由 `context` 字段区分
- query/advisor 召回冲突笔记时必须**同时呈现**并标注各自 context，AI 不擅自选边（ADR-011）
- v0.2 起 query 技能开始执行此规则

---

## 4. value 字段（DESIGN §6.6）

```yaml
value:
  reuse: 12         # 自动 · 入链数 + Connect 推荐频次（v0.2）+ 查询命中（v0.2 简易日志）
  # impact: 4       # v0.3 启用（手填，1-5）
  # uniqueness: 3   # v0.3 启用（自动估算，1-5）
```

### 4.1 reuse 计算（v0.2 版本）

```
reuse = 入链数（wikilink 入链）
      + Connect 推荐频次（quick-kb-manager-agent.recommend_relations 候选中出现次数）
      + 查询命中次数（query 技能命中的次数，由 v0.2 落简易日志）
```

- **初值**：ingest 时 = 0
- **刷新**：review 时由 quick-kb-manager-agent.refresh_value 重算
- **降级**：无 query 日志时仅算入链数

### 4.2 Knowledge Score 推迟到 v0.3

```
KS = confidence × log2(1 + reuse) × impact
```

v0.2 不计算 KS（因 impact 未启用）；review 仅基于 reuse 与 confidence 简单排序。

---

## 5. context 字段（DESIGN §6.8）

```yaml
context: "通用场景；创业团队请同时参考 [[模块化单体]]"
```

- **自由文本**，不强制结构化
- 描述本笔记**适用的情境**（团队规模、阶段、技术栈、领域）
- ingest 时由 AI 从正文提取候选 context，由用户确认
- 含 wikilink 时可关联到对比情境笔记
- 与 `contradicts` 配合使用：冲突的两条笔记各自声明 context

### 5.1 v0.2 写入策略

- ingest 时尝试从正文提取（关键词：场景/团队/阶段/约束/适用于...）
- 提取失败 → 不写此字段（可选）
- 用户在 connect / review 时可补全

---

## 6. 完整示例（concept）

```yaml
---
title: RAG 架构设计
type: concept
created: 2026-08-09
updated: 2026-08-09
tags:
  - ai/rag
  - eng/architecture
status: active
domain: ai-engineering
confidence: 60
relations:
  supports:
    - "[[Vector Database]]"
  contradicts: []
  evolves:
    - "[[RAG 基础概念]]"
  supersedes: []
context: "通用 RAG 架构；创业团队请参考 [[轻量 RAG 方案]]"
value:
  reuse: 0
source:
  - note: "[[00_inbox/clips/20260809-1000-rag-article]]"
  - url: https://example.com/rag
---
```

---

## 7. Inbox 最小集（不变）

仍遵循 DESIGN §6.9：

```yaml
---
title:
captured_at:
---
```

v0.2 capture 可附加 `suggested_tags` / `capture_type` / `source` 等扩展字段，**不**写正式字段。

### 7.1 v1.2+ AI 润色扩展字段（可选）

v1.2 起，capture 经过润色提议且用户选「用润色版」时，附加可选字段（仍属 inbox 扩展，不进 §2 正式字段清单）：

```yaml
ai_polished: true                 # 默认 false / 不写；仅当用户采纳润色版时为 true
source:
  original_text: <用户原始输入>    # 仅 ai_polished=true 时存在；与 source.url/raw 并列
```

daily 文件不同——用 frontmatter `ai_polished_entries: [条目编号]` + 正文行内 `<!-- original: ... -->` 注释保留原句（详见 `skills/quick-kb-daily/SKILL.md` 步骤 3.5）。

---

## 8. 校验规则

技能产出时按以下顺序自检：

1. 必填字段是否齐全
2. `type` 在 v0.2 子集内（concept/resource/idea/daily/moc/review）
3. `status` 在完整 6 态内
4. `relations` 结构存在（4 个子键齐全，可全为 `[]`）
5. `value.reuse` 存在（数字）
6. 出现 `maturity`/`value.impact`/`value.uniqueness` → 警告但不删除
7. `contradicts` 非空 → 检查是否同时声明了 `context`（提醒，不阻塞）

校验失败降级：保留字段、写入文件、frontmatter 顶部 callout 提示。

---

## 9. 升级路径

- **v0.1 → v0.2**：v0.2 技能开始写完整字段；v0.1 旧笔记通过 v0.4 normalize 批量补齐。
- **v0.2 → v0.3**：启用 `maturity`；启用认知资产 4 类 type；启用 `value.impact`/`uniqueness` 与 KS 排序。
- 任何阶段都不强制回填；用户可手动或通过 normalize 处理。
