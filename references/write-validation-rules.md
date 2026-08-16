---
version: v1.10.0
updated: 2026-08-16
phase: v1.8 写入校验层 + v1.10.0 语言一致性
applies_to: 所有写入型技能（ingest / capture / connect / daily / goal / project / import）落盘前的 frontmatter 与 wikilink 校验；§6 语言一致性适用于全部技能的生成内容与报告输出
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
| `status` | ∈ schema enum（inbox / draft / active / done / cancelled / archived / in-progress / blocked / superseded / ingested；progress 用 in-progress / blocked / done，decision 用 active / done / superseded，ingested 仅 inbox 素材被 ingest 后标记） | `status: published` |
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

## 6. 语言一致性（v1.10.0）

> 全库语言由 init 写入 `kb.config.yaml.language`（新库默认 `en`），全部技能读写内容时遵循本节。

### 6.1 语言判定优先级

```
kb.config.yaml.language（显式库语言，最高）
  → 用户当前输入语言（仅无 config 场景——capture/daily 的素材/口述阶段跟随用户语言）
  → en（兜底默认）
```

### 6.2 适用于（AI 生成的结构化内容）

| 对象 | 规则 |
|------|------|
| 笔记标题提炼 / 摘要 / 正文写作 | 用库语言写（zh 库中文，en 库英文） |
| 文件名 slug | en → kebab-case 英文；zh → 按 [`slug-rules.md`](./slug-rules.md) 保留中文 |
| 模板选择 | 从 `99_system/templates/<language>/` 取（两套均由 init 铺设，未铺设时按 §3 ⚠ 标注降级） |
| 报告输出 | query / review / stats / 三 agent / advisor 的分析报告正文用库语言 |
| MOC / 归档索引等系统生成文档 | 用库语言 |

### 6.3 不适用于（保持原样）

| 对象 | 理由 |
|------|------|
| 用户原始输入（capture 素材正文 / daily 口述） | **素材化原则**：逐字保留，永不翻译改写 |
| frontmatter 字段名与枚举值（type/status/maturity/relations 键/source 键/domain） | 机器解析层，恒英文——语言约定只管值不管键 |
| tags 条目 | 跟随 `tags_vocabulary` 实际内容（词表本身由用户/config 定义） |
| 目录名 / 配置键 / 文件路径 | 技术标识，恒英文 |

### 6.4 自检

- [ ] 写入前已读取 `kb.config.yaml.language`；无 config 时按用户输入语言回退
- [ ] AI 生成的标题/摘要/正文/报告与库语言一致
- [ ] slug 语言形态与库语言匹配（en kebab-case / zh 保留中文）
- [ ] 用户原文未被翻译改写（无论库语言为何）

---

## 7. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.8.0 | 2026-08-14 | 初始版本：frontmatter 最小校验集 / wikilink 目标存在性 / 失败处理三段式 |
| v1.10.0 | 2026-08-16 | 新增 §6 语言一致性：库语言判定优先级 / 适用与豁免对象 / slug 语言形态 |
