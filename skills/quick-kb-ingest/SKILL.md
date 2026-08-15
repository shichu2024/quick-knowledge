---
name: quick-kb-ingest
description: |
  把 inbox 素材正式入库为 01_resources/<category>/（resource）或 02_areas/<domain>/（concept）笔记：调 quick-kb-research-agent 抽取原子观点、补全 v0.2 完整 frontmatter（含 relations/context/value.reuse）、链接原始素材、给置信度初值、调 quick-kb-manager-agent + quick-kb-memory-agent 做冲突检测。
  触发词（中文）：处理 inbox / 入库 / 把这条归档 / 消化这条 / 这条入库
  Triggers (EN): process inbox / ingest this / promote this note
version: v1.9.1
phase: v0.2
applies_to: 00_inbox/ → 02_areas/ / 01_resources/
source_of_truth:
  - docs/DESIGN.md §6（frontmatter）· §6.7（冲突处理）
  - docs/SKILLS_SPEC.md §3
  - docs/AGENTS_SPEC.md §1（关系推荐规则）· §2（原子化与 confidence 规则）· §4.2（冲突感知）
  - docs/dev/v0.2-loops.md WP9
  - references/frontmatter-v0.2.md
---

# quick-kb-ingest（v0.2）

> 把 inbox 一条素材变成 N 条原子笔记。**原始素材永不删除**；入库笔记通过 `source.note` 链回。
>
> **v0.2 升级**：调 `quick-kb-research-agent`（intent=`extract_atoms`）抽取原子观点；产出完整 frontmatter（含 relations/context/value.reuse）；加入冲突检测（调 `quick-kb-manager-agent.recommend_relations` 发现候选 + `quick-kb-memory-agent.present_conflicts` 呈现冲突）。

---

## 1. v0.2 范围

### 做

- 扫描 inbox 候选（单条 / 子目录 / 全 inbox；6 类源）
- 调 `quick-kb-research-agent` intent=`extract_atoms` 抽取原子观点（规则见其 SKILL.md §3.2）
- 分类去向：concept → `02_areas/<domain>/`、resource → `01_resources/<category>/`、idea（仍待消化）→ 留 inbox，标 `status: draft`
- 补全 **v0.2 完整 frontmatter**（含 relations/context/value.reuse）
- `source.note` 用 wikilink 指回 inbox 原始素材
- 置信度初值由 research-agent 给出（0-100 整数量纲；规则见其 SKILL.md §3.2）
- **冲突检测**：调 `quick-kb-manager-agent.recommend_relations` 扫描同 domain 已入库笔记，发现对立候选 → 调 `quick-kb-memory-agent.present_conflicts`（返回结构见其 §0）呈现 → 提示建立 contradicts 关系

### 不做

- ❌ 自动 maturity —— v0.3
- ❌ 自动 value.impact/uniqueness/KS —— v0.3

---

## 2. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `target` | 否 | `inbox` | 单条文件路径 / `inbox` 全量 / `00_inbox/ideas` 等子目录 |
| `domain` | 否 | 由抽取规则推断 | 指定领域 |
| `depth` | 否 | `standard` | `quick` / `standard` / `deep`（v0.2 deep 与 standard 一致；v0.3 启用语义判定后才有差异） |

---

## 3. 工作流

### 步骤 1 · 扫描候选

1. 解析 `target`，列出所有 inbox 候选
2. 按 `captured_at` 升序（FIFO）
3. 输出候选清单

### 步骤 2 · 逐条处理（standard 模式）

#### 2.1 读取与源类型识别

读取候选笔记全文。识别 `capture_type`：idea / web-clip / pdf / meeting / ai-dialog / reading。

**`capture_type → note_type` 默认映射（v1.5 WP7 · research-agent 可覆盖）**：

| capture_type | 默认 note_type | 说明 |
|--------------|---------------|------|
| `idea` | `concept` | 用户想法通常提炼为 concept |
| `web-clip` | `resource` | 网页素材归 resource |
| `pdf` | `resource` | 论文/报告归 resource；若内容是方法论 → concept |
| `meeting` | `concept` | 会议决议提炼为 concept |
| `ai-dialog` | `concept` | AI 对话中的观点提炼为 concept |
| `reading` | `resource` | 书籍/课程归 resource |

> research-agent `extract_atoms` 返回的 `note_type` 优先于本默认映射（按内容实质判定）。映射冲突时以 research-agent 输出为准 + 在 ingest 报告标 ⚠。

**保留 `capture_type` 作溯源（v1.5 WP7）**：入库笔记 frontmatter 加 `source.capture_type: <原值>`，便于后续按来源筛选（如「找出所有来自会议的 concept」）。

#### 2.2 抽取原子观点（调 `quick-kb-research-agent` intent=`extract_atoms`）

操作：

1. 阅读 inbox 笔记正文
2. 调 research-agent 按其 SKILL.md §3.2 原子化规则拆分（每条只表达一个可独立成立的观点；含"且/并且/同时"的复合句优先拆分）
3. 对每条原子观点（返回结构见 research-agent §0 契约）：
   - `note_type`：`concept` 或 `resource`
   - `title` / `body` / `tags` / `source_excerpt`
   - `confidence`（0-100 量纲）
   - `domain`（单层或嵌套，如 `programming/python`）

> **嵌套 domain 决策（v1.4+）**：当 `kb.config.yaml.domain_taxonomy` 命中顶层 key 且能从 tags/title 推断子域 → 推断嵌套 domain（`key/sub`）；未配置 taxonomy 或未命中 → 单层（向后兼容）。

#### 2.3 原子化拆分

- 抽取得到 N 条原子笔记 → 拆为 N 条
- `depth=quick` → 不拆，整篇转一条 resource（调 research-agent intent=`summarize`；返回结构见其 §0）

#### 2.4 分类去向

| 观点类型 | 目标目录 | 模板 |
|---------|---------|------|
| concept | `02_areas/<domain>/<slug>.md`（`<domain>` 可含 `/` 嵌套，如 `programming/python`） | [`templates/zh/note-concept.md`](../../templates/zh/note-concept.md) |
| resource | `01_resources/<category>/<slug>.md` | [`templates/zh/note-resource.md`](../../templates/zh/note-resource.md) |
| idea（仍不够结构化） | 留 `00_inbox/ideas/`，更新 `status: draft` | 不创建新文件 |

> **嵌套路径示例**：`domain: programming/python` → `02_areas/programming/python/threading.md`。建中间目录（`mkdir -p` 语义）。slug 保持不变 → slug-based wikilink 不断。

> v0.2 不产出 decision/goal/project/principle/belief/pattern/experience/moc/review/daily 类型。

#### 2.5 补全 v0.2 完整 frontmatter（v1.7 WP2-D）

严格按 [`references/frontmatter-v0.2.md`](../../references/frontmatter-v0.2.md)：

```yaml
---
title: {{精炼后的标题}}
type: concept                       # 或 resource
created: {{today}}
updated: {{today}}
tags:                               # 由 suggested_tags 转正，对照 kb.config.yaml 词表
  - {{domain}}/{{topic}}            # v1.7 强制：必须为 inline array 格式 [tag1, tag2]
status: active                      # 默认 active；字段不全 → draft
domain: {{domain}}
confidence: {{初值}}                # 0-100 整数 · 单源 30-40 / 多源 60-75 / 一手 80-95（AGENTS_SPEC §2.2）
relations:                          # v0.2 启用 · 见 §2.7
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
context: {{从正文提取，可选}}         # v0.2 启用
value:                              # v0.2 启用 · 仅 reuse
  reuse: 0
source:
  - note: "[[{{inbox原始素材wikilink}}]]"   # 必须 · 链回 inbox
  - url: {{若 web-clip，沿用原始 URL}}
---
```

**v1.7 强制规则（WP2-D）**：
- `tags` 必须为 inline array 格式 `[tag1, tag2]`，禁止 YAML block list 格式
- 写入前检测：若为 block list → 自动转换为 inline array

**严禁**写入：`maturity` / `value.impact` / `value.uniqueness`（v0.3 字段）。

#### 2.6 正文生成

按对应模板章节填充（concept/resource）。**抽取失败**：留 `{{}}`，标 `status: draft`，不强行编造。

#### 2.7 关系推荐（调 `quick-kb-manager-agent` intent=`recommend_relations`）

操作：

1. 取本笔记 `domain` 下所有已入库笔记作为候选池
2. 调用及返回结构见 manager-agent SKILL.md §0 契约（相似度 > 0.6 进候选；> 0.85 建议 evolves/contradicts）
3. 输出候选列表（target / type / similarity）

- supports/evolves/supersedes 候选 → 自动写入 relations（相似度 > 0.85 的 evolves 提示用户确认）
- **contradicts 候选** → 进入步骤 3 冲突检测流程

#### 2.8 写入前校验（v1.8 WP2）

落盘前按 [`references/write-validation-rules.md`](../../references/write-validation-rules.md) 校验，**不得静默落盘不合规内容**：

1. frontmatter 全集：必填字段（title/type/created/updated/status）、`confidence` 0-100 整数、无 v0.3 越权字段
2. relations 类型化：dict 格式、键 ∈ schema enum（禁止自创关系类型）、值为 wikilink 字符串数组
3. wikilink 目标存在性：`source.note` / relations / 正文中的 `[[X]]` 目标必须在 vault 文件名索引内；不存在 → 降级为普通文本或加粗
4. 校验失败的修正项记入步骤 6 处理报告；无文件索引可查时 ⚠ 标注「未执行写入前校验」

### 步骤 3 · 冲突检测与主动提醒（V2 关键）

> manager-agent.recommend_relations 发现对立候选 → 调 memory-agent.present_conflicts（返回结构见其 §0）按冲突感知协议处理（同时呈现双方 + 各自 context）。

#### 3.1 检测规则

- 抽取候选中若存在标题/标签对立语义 → 标记为 `contradicts`
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

#### 3.3 confidence 协商（v1.8.2 · research 初值 → memory 冲突调整回写）

> 消除 research-agent 初值与 memory-agent 冲突检测结果之间的数据断裂：调整结果必须回写笔记 frontmatter，不依赖人工传递。

1. research-agent `extract_atoms` 给出 confidence 初值（§2.5 规则）→ 写入新笔记 frontmatter
2. 步骤 3 冲突检测完成后，按结果调整并**回写** confidence：
   - 检出 `contradicts` 冲突且对方 confidence 更高 → 新笔记 confidence 下调（建议 −10，下限 20），在 ingest 报告记 why「冲突方 [[对方]] confidence {x} 更高」
   - 检出 `evolves`（新笔记为演化版）→ confidence 保持或 +5（上限 95），记 why「evolves 自 [[来源]]」
   - 无冲突命中 → 保持初值不动
3. 回写动作与步骤 4 写入合并执行（避免二次改文件）；调整记录进 ingest 报告的「confidence 协商」段

### 步骤 4 · 关系反向补全与写入（v1.7）

#### 4.1 关系反向补全（v1.7 WP2-A）

对每条新增笔记的 `relations.supports` / `evolves` / `supersedes`：
- 复用 `quick-kb-connect SKILL.md` §5.2.1 的反向补全表（见下表）
- 在目标笔记 frontmatter 写入对应反向键
- 反向补全幂等——已存在不重复追加
- 写入失败（目标笔记不可写）→ 仅在报告列「⚠ 反向补全失败清单」，不阻断入库

**反向补全表（引用 connect §5.2.1）**：

| 正向（A→B） | 自动补的反向（B→A） |
|-------------|---------------------|
| `evolves` | `evolved_by` |
| `supersedes` | `superseded_by` |
| `derived_from` | `source_of` |
| `refines` | `refined_by` |
| `supports` / `contradicts` | 对称，已在双方写入（保持现状） |

#### 4.2 冲突消歧检测（v1.7 WP3-B）

写入 `supports` 或 `contradicts` 前，检测同一对笔记是否已有反向关系：

```markdown
若 A.supports=[B] 已存在，新写 A.contradicts=[B]：
- 暂不写入 contradicts
- 报告：「⚠ 语义冲突：A 对 B 已 supports，是否覆盖？需补充 context」
- 若 A.contradicts=[B] 已存在，新写 A.supports=[B]：同样提示
```

#### 4.3 写入并反馈

对每条产出：

```
✓ 写入：02_areas/ai-engineering/rag-architecture.md
  类型：concept | 状态：active | 置信度：60
  来源：00_inbox/clips/20260809-1000-<slug>.md
  标签：ai/rag · eng/architecture
  relations：                          # wikilink 一律用目标文件 basename（kebab-case slug），禁止标题格式
    supports: [[vector-database-selection]]
    evolves: [[rag-basic-concepts]]
  context: "通用 RAG 架构；创业团队请参考 [[lightweight-rag-solution]]"
  value.reuse: 0
```

### 步骤 4.5 · inbox 素材归档（v1.7 WP2-B）

入库成功后，对源 inbox 笔记：
- 在 frontmatter 追加 `status: ingested` + `ingested_to: "[[02_areas/...]]"`
- 移动到 `00_inbox/_processed/<原子目录>/`（保留 mtime）
- 不删除（保留追溯链，需归档时调 archive）

### 步骤 5 · 主动提醒（manager 事件子集）

调 `quick-kb-manager-agent` intent=`proactive_remind`（event=`ingest_new`；返回结构见其 §0）触发主动提醒：

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

> 💡 **下一步**：运行 `quick-kb-connect` 建立 relations 与 MOC，把刚入库的笔记接入知识图谱。

### 步骤 7 · 更新 inbox 原始素材（v1.7 已移至步骤 4.5）

本步骤已合并到步骤 4.5「inbox 素材归档」：

- 在原始素材 frontmatter 追加 `status: ingested` + `ingested_to: "[[02_areas/...]]"`
- 移动到 `00_inbox/_processed/<原子目录>/`
- 不删除（保留追溯链）

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
| 无 embedding 服务 | similarity 降为「标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4」（统一公式见 [`references/scoring.md`](../../references/scoring.md) §5）；关系推荐仍可工作但精度下降 |
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
- [ ] inbox 原始素材已移至 `00_inbox/_processed/` 且 frontmatter 含 `status: ingested`
- [ ] frontmatter 含完整 v0.2 字段（含 relations/context/value.reuse）
- [ ] 无 v0.3 字段（maturity/value.impact/value.uniqueness）
- [ ] 抽取失败的笔记标 `status: draft`
- [ ] 原子观点拆分（二选一 · v1.5 WP8）：
      · 正常态：调 quick-kb-research-agent intent=extract_atoms（规则见其 SKILL.md §3.2）
      · 降级态：手动按「含且/并且/同时的复合句优先拆」+ ⚠ 标注；confidence 给保守值 30-40
- [ ] 冲突检测（二选一 · v1.5 WP8）：
      · 正常态：调 manager-agent.recommend_relations + memory-agent.present_conflicts
      · 降级态：手动 Grep 同 domain 笔记找对立语义候选 + ⚠ 标注「未启用语义冲突检测」
- [ ] contradicts 候选已建立双向关系 + 提示补充 context
- [ ] （v1.8.2）confidence 协商：冲突检测结果已按 §3.3 规则调整并回写，调整记录含 why
- [ ] 文件名 kebab-case
- [ ] 处理报告含统计 + 下一步建议
- [ ] **v1.7 新增**（WP2）：
      · [ ] 关系反向补全已执行（目标笔记含反向键）
      · [ ] inbox 素材已归档至 `_processed/`
      · [ ] tags 格式为 inline array
- [ ] **v1.7 新增**（WP3-B）：
      · [ ] supports/contradicts 冲突消歧检测已执行
- [ ] **v1.8 新增**（WP2）：写入前校验已执行（§2.8），修正项记入报告

---

## 9. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 产出完整 v0.2 frontmatter | DESIGN §6.1 V2 标准 | frontmatter-v0.2.md |
| deep 档位与 standard 一致 | v0.3 启用语义判定后才有差异 | dev doc 不冲突 |
| contradicts 自动建立双向 | ADR-011 + AGENTS_SPEC §4.2 不选边 | DESIGN §6.7 |
