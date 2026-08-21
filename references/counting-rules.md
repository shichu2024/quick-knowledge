---
version: v1.13.0
updated: 2026-08-21
phase: v1.13
applies_to: quick-kb-stats / quick-kb-review（以及任何需要统计「正式笔记数」的技能）
source_of_truth:
  - docs/DESIGN.md §4（目录结构）
  - docs/dev/v1.4-docs.md B-WP5
---

# 正式笔记计数规则 · Counting Rules

> 本文件定义「正式笔记」的精确边界。`quick-kb-stats` 和 `quick-kb-review` 在统计总笔记数、孤立率、置信度分布等指标时，**共同引用此规则**，确保两技能口径一致。

---

## 1. 「正式笔记」定义

正式笔记 = 以下 5 个目录下的所有 `.md` 文件（含嵌套子目录）：

| 目录 | 含义 | 典型 type |
|------|------|-----------|
| `02_areas/` | 领域知识（concept / resource / 嵌套 domain） | concept / resource |
| `07_principles/` | 认知资产（principle / belief / pattern / experience） | principle / belief / pattern / experience |
| `01_projects/` | 项目笔记 | project |
| `03_goals/` | 目标笔记 | goal |
| `04_daily/` | 每日日志 | daily |

> **注**：不同 vault 实际目录名可能以 `docs/DESIGN.md §4` 的最新目录结构为准。若 vault 使用 `04_projects/` / `05_outputs/daily/` 等变体路径，按实际 vault 结构扫描，但排除规则（§2）不变。

---

## 2. 排除清单

以下目录的 `.md` 文件**不计入**正式笔记：

| 目录 / 模式 | 排除原因 |
|-------------|---------|
| `98_archive/` | 已归档，不再活跃维护 |
| `99_system/` | 系统文件（配置、日志、工作流状态） |
| `00_inbox/` | 未入库的原始素材，尚未提炼为正式笔记 |
| `_templates/` | 模板文件，非实际知识内容 |
| `_logs/` | 运行日志 |

此外，以下文件**全局排除**（不论所在目录）：

| 模式 | 排除原因 |
|------|---------|
| `*-moc.md`（`<basename>-moc.md`，如 `general-moc.md`；v1.13.0 起领域 MOC 命名）/ `_index.md` | 索引文件，非独立知识笔记 |
| `.canvas` / `.json` / `.html` 等非 `.md` | 非笔记格式 |
| 含 `template: true` frontmatter 的文件 | 模板标记 |

---

## 3. 统计口径

### 3.1 总笔记数

```
正式笔记数 = count(02_areas/**/*.md)
           + count(07_principles/**/*.md)
           + count(01_projects/**/*.md)
           + count(03_goals/**/*.md)
           + count(04_daily/**/*.md)
           - 排除项（§2）
```

### 3.2 各 type 分布

仅统计正式笔记的 `frontmatter.type` 字段，按枚举值分组计数 + 百分比。

### 3.3 孤立笔记率

孤立笔记 = 正式笔记中既无入链又无出链的笔记（wikilink 图谱计算）。

```
孤立率 = 孤立笔记数 / 正式笔记数
```

### 3.4 inbox 周转时长

**不适用本规则** —— inbox 统计单独计算 `00_inbox/` 下的文件，不计入正式笔记数。

---

## 4. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.4 | 2026-08-13 | 初始版本，统一 stats 与 review 的计数口径 |
| v1.13.0 | 2026-08-21 | MOC 索引排除模式 `_moc.md` → `*-moc.md`（领域 MOC 命名统一，见 wikilink-conventions.md §2a） |
