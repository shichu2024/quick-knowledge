---
version: V1
updated: 2026-08-09
phase: v0.1
applies_to: v0.1 技能产出的所有正式笔记
source_of_truth: docs/DESIGN.md §6
---

# v0.1 · Frontmatter 子集规范

> 本文件锁定 v0.1 阶段所有技能产出的 frontmatter 字段范围，避免提前使用 v0.2+ 字段（maturity / value / relations / context）造成后续迁移成本。
>
> **真相源**：`docs/DESIGN.md` §6（元数据规范）。本文件仅是 v0.1 阶段的子集声明，字段含义以设计文档为准。

---

## 1. 设计原则

1. **子集不偏离** —— v0.1 出现的每个字段必须在 DESIGN §6.1 标准字段中存在，含义一致。
2. **采集零摩擦** —— inbox 原始素材走 DESIGN §6.9 最小集；正式笔记才走本文件子集。
3. **预留平滑升级** —— 不引入 v0.2+ 字段，但写入时不应阻止后续手工或 normalize 补齐这些字段。

---

## 2. 字段清单（正式笔记）

正式笔记 = 已经 ingest 入库到 `02_areas/` / `01_resources/` / `04_projects/` / `03_goals/` 等目录的笔记。

| 字段 | 必填 | 类型 | v0.1 取值 / 说明 | 对应 DESIGN |
|------|------|------|----------------|-------------|
| `title` | ✓ | string | 笔记标题 | §6.1 |
| `type` | ✓ | enum | v0.1 仅：`concept` / `resource` / `idea` / `daily` | §6.2 |
| `created` | ✓ | ISO date | `YYYY-MM-DD` | §6.1 |
| `updated` | ✓ | ISO date | `YYYY-MM-DD` | §6.1 |
| `tags` | ✓ | string[] | 受控标签（`domain/topic` 形式建议） | §6.1 |
| `status` | ✓ | enum | v0.1 仅：`inbox` / `draft` / `active` / `done`（`cancelled` / `archived` 推迟到 v0.2+ 项目/目标场景） | §6.3 |
| `source` | 可选 | list of `{url?, note?}` | 原始来源；URL 与 wikilink 至少一项 | §6.1 |
| `domain` | 可选 | string | 所属领域（对应 `02_areas/`）；横切认知资产（v0.3 引入）不留此字段 | §6.1 |
| `confidence` | 可选 | number 0-100 | ingest 时按规则给初值（单源 40 / 多源 60+ / 一手 80+），用户可改 | §6.5 |

### 2.1 关于 `confidence` 的说明

WP1 dev doc 显式列出 8 个字段未包含 `confidence`，但 WP4（ingest）又要求"置信度初值规则"。**以设计文档为真相源**：DESIGN §6.1 将 `confidence` 列为标准字段，§6.5 给出评分参考。本文件据此将 `confidence` 纳入 v0.1 子集（可选，但 ingest 强烈建议生成），保证升级到 v0.2+ 时无需回填。

### 2.2 显式排除（v0.2+ 才允许）

以下字段在 v0.1 **不得**由技能自动写入，避免后续 schema 变更造成迁移负担：

| 字段 | 引入阶段 | 原因 |
|------|---------|------|
| `maturity` | v0.3 | 依赖认知资产目录与 KS 排序逻辑 |
| `value.reuse` 等 | v0.2 | 依赖 quick-kb-manager-agent 的 reuse 计算 |
| `relations.{supports,contradicts,evolves,supersedes}` | v0.2 | 依赖 connect 技能与 manager 推荐能力 |
| `context` | v0.2 | 依赖 ingest 冲突检测 + 用户确认流程 |

> **向后兼容例外**：DESIGN §6.7 允许 V1 扁平 `related: [...]` 作为弱关联回退。v0.1 技能不主动写 `related`，但若用户手填，ingest 不应删除。

---

## 3. Inbox 最小集（原始素材）

完全遵循 DESIGN §6.9：

```yaml
---
title:                    # 必填
captured_at:              # 必填 · ISO 8601（含时间）· 如 2026-08-08T14:30
---
```

Inbox 笔记**不**写 type/tags/status 等字段；这些由 ingest 阶段补全。Capture 技能可附加 `suggested_tags` 作为 hint，但它是建议字段，不属于正式 frontmatter schema。

---

## 4. 示例

### 4.1 正式笔记（concept，ingest 产出）

```yaml
---
title: RAG 检索增强生成基础
type: concept
created: 2026-08-09
updated: 2026-08-09
tags:
  - ai/rag
status: active
domain: ai-engineering
confidence: 60
source:
  - url: https://example.com/article
  - note: "[[原始摘录-RAG-基础]]"
---
```

### 4.2 Inbox 原始素材（capture 产出）

```yaml
---
title: RAG 基础摘录
captured_at: 2026-08-09T10:15
---
```

### 4.3 Daily 日志

```yaml
---
title: 2026-08-09 日志
type: daily
created: 2026-08-09
updated: 2026-08-09
tags:
  - daily
status: active
---
```

---

## 5. 校验规则（供技能内部使用）

技能产出 frontmatter 时，按以下顺序自检：

1. 必填字段是否齐全（缺则标 `status: draft`，提示用户补全）
2. `type` 是否在 v0.1 子集 4 个值内
3. `status` 是否在 v0.1 子集 4 个值内
4. `tags` 是否非空数组
5. `created` / `updated` 格式是否为 `YYYY-MM-DD`
6. 若出现 v0.2+ 字段（maturity / value / relations / context）→ 警告但不删除，由用户决定

校验失败时降级路径：保留字段、写入文件、在 frontmatter 或正文顶部加 callout 提示，不在写入阶段阻断流程。

---

## 6. 升级路径

- **v0.1 → v0.2**：v0.2 技能开始写入 `relations` / `context` / `value.reuse`；v0.1 旧笔记通过 `quick-kb-normalize`（v0.4）批量补齐。
- **v0.2 → v0.3**：引入 `maturity` 字段；认知资产 4 类 type 启用。
- 任何阶段都不强制回填历史笔记；用户可手动或通过 normalize 批量处理。
