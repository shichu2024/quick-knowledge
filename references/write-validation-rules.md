---
version: v1.8.0
updated: 2026-08-14
phase: v1.8 写入校验层
applies_to: 所有写入型技能（ingest / capture / connect / daily / goal / project / import）落盘前的 frontmatter 与 wikilink 校验
source_of_truth:
  - references/frontmatter-schema-v1.json
  - references/wikilink-conventions.md
  - docs/dev/v1.8-e2e-calibration.md WP2
---

# 写入前校验规则 · Write Validation Rules

> 本文件定义所有写入型技能在**落盘前**必须执行的最小校验集。校验发生在写文件步骤之前；校验只存在于 normalize（事后治理）不够，写入时无拦截是死链与 schema 漂移的共同根因（dev doc v1.8 §0.2 N1/N2）。

---

## 1. frontmatter 最小校验集

| 校验项 | 规则 | 违规示例 |
|--------|------|---------|
| 必填字段 | `title` / `type` / `created` / `updated` / `status` 全部存在且非空 | 缺 `status` |
| `confidence` | **0-100 整数**；禁止 0-1 小数（0.85 → 应写 85） | `confidence: 0.85` |
| 行内注释 | **落盘 frontmatter 禁止携带 `# 说明` 行内注释**——模板/SKILL 示例中的注释是填写指引，不得照抄进实际笔记（污染源见 normalize 步骤 2.1 剥离规则） | `confidence: 80 # verified` |
| `type` | ∈ schema enum（concept / resource / idea / daily / moc / review / principle / belief / pattern / experience / decision / goal / project / progress / retrospective） | `type: note` |
| `status` | ∈ schema enum（inbox / draft / active / done / cancelled / archived / in-progress / blocked / superseded；progress 用 in-progress / blocked / done，decision 用 active / done / superseded） | `status: published` |
| `relations` | **类型化 dict**：键 ∈ `supports` / `contradicts` / `evolves` / `supersedes` / `evolved_by` / `superseded_by` / `derived_from` / `derived_to` / `source_of` / `refines` / `refined_by`，值为 wikilink 字符串数组；**禁止 array 格式**（如 `relations: ["[[X]]"]`）与自创关系类型（如 `complements`） | `relations: { complements: [] }` |
| `maturity` | 写入时必须 ∈ 6 态词表：`captured` / `understood` / `validated` / `applied` / `teachable` / `deprecated` | `maturity: mature` |
| 自创字段 | **禁止** schema（[`frontmatter-schema-v1.json`](./frontmatter-schema-v1.json)）之外自创字段；不确定的字段不写，缺字段值 → 标 `status: draft` | `author_tier: expert` |

> 各技能的适用子集：ingest 用全集（v0.2 完整 frontmatter）；capture 用 inbox 简化集（`title` / `captured_at` / `capture_type` 等按 [`frontmatter-v0.2.md`](./frontmatter-v0.2.md) §7，严禁提前写入正式字段）；import 用转换后字段集 + 禁止自创字段。

---

## 2. wikilink 校验

**目标存在性**：写入的 `[[X]]`（正文或 `relations` 内）目标必须已存在于 vault 文件名索引：

- basename 形式 → 全库存在唯一匹配的 `.md`（解析口径同 [`wikilink-conventions.md`](./wikilink-conventions.md) §8）
- 目标**不存在** → 降级为普通文本或加粗（如 `[[vector-database]]` → `**vector-database**`），**不得写入死链**
- 目标存在但 basename 歧义 → 改用 path-qualified 形式（wikilink-conventions §2）

**形式禁止**：

| 禁止形式 | 原因 |
|---------|------|
| 路径式 `[[dir/sub/file]]`（非消歧场景） | 默认场景 basename 已唯一（wikilink-conventions §1/§7）；仅 §2 重名消歧与 §5 深路径对象允许 path-qualified |
| 双前缀 `[[dec-dec-001]]` | wikilink 必须匹配实际文件名（`dec-001.md` → `[[dec-001]]`）；禁止把编号前缀重复一遍 |
| 含扩展名 / 空格大写 / 全角括号后缀 | 见 wikilink-conventions §7 |

> 例外：import 保留源库原有 wikilink（目标可能尚未存在于本库），待 connect / repair_deadlinks 后续处理——import 技能不对原文 wikilink 做存在性拦截。

---

## 3. 校验失败处理

1. **按规则修正后写入**：confidence 量纲转换（0.85 → 85）、自创关系类型映射到最近似合法键或删除、死链降级为普通文本——修正项记入当次处理报告。
2. **不得静默落盘不合规内容**：无法自动修正的字段（如 type 推断失败）→ 该笔记标 `status: draft`，不编造值。
3. **无法校验时 ⚠ 标注**：运行环境无文件索引 / 无 schema 可查（如技能包资源不可达）→ 照常写入但在输出中 ⚠ 标注「未执行写入前校验」，不得默默跳过。

---

## 4. 自检

- [ ] 落盘前已执行 §1 frontmatter 校验（按本技能适用子集）
- [ ] 落盘前已执行 §2 wikilink 校验（import 除外——原文 wikilink 保留）
- [ ] 校验失败的修正项已记入处理报告
- [ ] 无法校验时输出含 ⚠ 标注

---

## 5. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.8.0 | 2026-08-14 | 初始版本：frontmatter 最小校验集 / wikilink 目标存在性 / 失败处理三段式 |
