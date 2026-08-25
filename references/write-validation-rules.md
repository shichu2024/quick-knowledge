---
version: v1.14.0
updated: 2026-08-25
phase: v1.8 写入校验层 + v1.10.0 语言一致性 + v1.11.0 写入后复验 + v1.14.0 domain 判定链
applies_to: 所有写入型技能（ingest / capture / connect / daily / goal / project / import）落盘前的 frontmatter 与 wikilink 校验；§5 写入后复验（ingest）；§6 语言一致性适用于全部技能的生成内容与报告输出；§7 domain/category 判定链适用于推断落位目录的入库技能（ingest / capture ai-article 快速入库）
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

## 5. 写入后复验（core 检查集）（v1.11.0）

> §1 / §2 是**写入前**防线；本节是**写入后**第二层——写入方（ingest §4.4）在落盘后重读文件，按下表 core 检查集核对，兜住写入前校验未拦住的 schema/格式类执行漂移（v1.9.3 source list 漂移的根因即写入后无人核对）。修正须当场执行并记入处理报告；无修正也显式记「复验通过 0 修正」。

| # | 检查项 | 违规形态 → 修正 |
|---|--------|------|
| 1 | frontmatter 无行内注释 | `confidence: 80 # verified` → 剥离注释 |
| 2 | `source` 为 object 格式 | list 格式 → 合并为 object（v1.9.3 口径） |
| 3 | `tags` inline array + 对照 tags_vocabulary | block list / 词表外变体 → 转换/修正 |
| 4 | v0.2 必填字段齐全 | 缺失 → 按规则补；不可推断 → `status: draft` |
| 5 | domain 兜底落位（v1.14.0） | 落 default_domain（如 `02_areas/general/`）的笔记 `status ≠ draft` → 改 `draft` + 报告记「⚠ 待分流」（见 §7） |

> **单一真相源声明**：本 core 集与 normalize `run` 检查项（步骤 2.1 行内注释剥离 / source list→object 迁移）及 `schema_check` 检查项 #1/#6/#7/#10/#12 同源——定义以本文件为准，ingest §4.4 与 normalize 均复用，不另行维护副本。死链不在本集（§2 写入前已拦截）。

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

## 7. domain/category 判定链（v1.14.0）

> 入库技能（ingest / capture ai-article 快速入库）推断笔记落位目录时遵循本节。`domain`（02_areas concept 路径）与 `category`（01_resources resource 路径）共用同一条链——两者是同构的「目录推断」问题。背景：此前 spec 未规定低置信 domain 的处理，执行方静默读 `default_domain: general` 落兜底域，致 `02_areas/general/` 成为垃圾桶目录。

### 7.1 判定优先级

```
① kb.config.yaml.domain_taxonomy 命中（tags/title 显式命中 key 或 key/sub）
  → ② 02_areas/（或 01_resources/）已有目录名命中（含嵌套父目录）
  → ③ tags/title 强推导（允许新建 domain：自动建目录 + <basename>-moc.md，先例见 ingest §6 降级表；
     嵌套规则同 v1.4+——仅对用户显式输入的 domain 建中间层）
  → ④ 低置信兜底：kb.config.yaml.default_domain（默认 general）
     —— 落兜底域的笔记【强制 status: draft】，且处理报告必须含：
        「⚠ 待分流：<slug> 落 default_domain（<domain>），建议后续 quick-kb-normalize action=triage_general」
```

### 7.2 边界

- 「低置信」= tags 为空/全不在词表 且 title 无可推导领域词——**必须穷尽 ①②③ 后才允许进 ④**，严禁跳过推导直接读 default_domain（静默落 general 是本节要消灭的形态）
- 兜底域不是垃圾桶：draft 标记 + ⚠ 报告 + normalize schema_check #12 巡检 + normalize `action=triage_general` 迁移，四层防线保证兜底笔记可追溯、可分流
- 用户显式指定 domain 时本链不介入（用户输入优先于一切推断）

### 7.3 自检

- [ ] 目录推断已按 §7.1 顺序穷尽 ①②③，才使用 default_domain
- [ ] 落兜底域的笔记 status 为 draft
- [ ] 处理报告含「⚠ 待分流」条目

---

## 8. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.8.0 | 2026-08-14 | 初始版本：frontmatter 最小校验集 / wikilink 目标存在性 / 失败处理三段式 |
| v1.10.0 | 2026-08-16 | 新增 §6 语言一致性：库语言判定优先级 / 适用与豁免对象 / slug 语言形态 |
| v1.11.0 | 2026-08-19 | 新增 §5 写入后复验（core 检查集）：行内注释 / source list→object / tags 词表与格式 / 必填字段；与 normalize 检查项及 schema_check 同源 |
| v1.14.0 | 2026-08-25 | 新增 §7 domain/category 判定链：四级优先级 + 兜底域强制 draft + ⚠ 待分流报告；§5 core 集扩第 5 项（domain 兜底落位），同源声明补 schema_check #12 |
