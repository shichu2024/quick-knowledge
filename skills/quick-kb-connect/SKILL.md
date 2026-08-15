---
name: quick-kb-connect
description: |
  建立双链、生成 MOC、绘制知识地图（canvas）。调 quick-kb-manager-agent 推荐关系与构建 MOC；写入类型化 relations（不再写扁平 related）；生成 06_wiki/mocs/<domain>-moc.md；接 json-canvas 生成 .canvas（Obsidian 缺失跳过）。
  触发词（中文）：连一下 / 建个 MOC / 给这领域建索引 / 画个知识地图 / 连接笔记
  Triggers (EN): connect these / build moc / map this domain / link notes
version: v1.8.2
phase: v0.2
applies_to: 06_wiki/ + 各笔记 frontmatter.relations
source_of_truth:
  - docs/DESIGN.md §6.7（关系类型化）· §9.2（obsidian-skills）
  - docs/SKILLS_SPEC.md §4
  - docs/AGENTS_SPEC.md §1.1（manager build_moc/recommend_relations）
  - docs/dev/v0.2-loops.md WP4
  - references/frontmatter-v0.2.md §3
  - references/json-canvas-schema.md（v1.6 · canvas 字段与着色规则）
  - references/wikilink-conventions.md（v1.6 · 双链命名约定）
---

# quick-kb-connect（v0.2）

> Connect 闭环：建立双链、生成 MOC、绘制知识地图。被 ingest 之后的「整理」步骤。

---

## 1. 何时调用

- 用户说「连一下这几条」「给 ai-engineering 建个 MOC」「画个知识地图」
- ingest 后用户想整理关系
- review 提示「孤立笔记 / 重复嫌疑」时

## 2. v0.2 范围

### 做

- 调 `quick-kb-manager-agent` intent=`recommend_relations`（返回结构见其 §0）推荐类型化关系（supports/contradicts/evolves/supersedes）
- 写入 `relations`（supports/contradicts/evolves/supersedes），不再写扁平 `related`
- 调 `quick-kb-manager-agent` intent=`build_moc`（返回结构见其 §0）生成 `06_wiki/mocs/<domain>-moc.md`
- 接 json-canvas 生成 `06_wiki/maps/<domain>.canvas`（Obsidian 缺失跳过）
- 更新 `06_wiki/_index.md` 全局导航

### 不做

- ❌ 不改正文（只改 frontmatter.relations + 新建 MOC/canvas）
- ❌ 不写 `related`（仅作 V1 兼容回退保留）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `scope` | ✓ | — | 领域名 / 某条笔记 / 某标签 |
| `action` | 否 | `all` | `moc` / `links` / `canvas` / `all` |
| `interactive` | 否 | `true` | 是否每条关系推荐都需要用户确认；`false` 时相似度 > 0.85 自动写入 |

---

## 4. 工作流

### 步骤 1 · 扫描范围

解析 `scope`：

- 领域名（如 `ai-engineering`）→ 扫描 `02_areas/<scope>/` 全部笔记
- **嵌套领域（v1.4+）**：`scope=programming` 扫描 `02_areas/programming/` 全子树（含 `python/`、`go/` 等所有子目录）；`scope=programming/python` 只扫该叶子目录
- 某条笔记路径 → 扫描该笔记 + 同 domain 的候选池
- 某标签 → 扫描全库含该标签的笔记

输出候选清单：

```
范围：02_areas/ai-engineering/（12 条笔记）
action：all
开始处理…
```

### 步骤 2 · 双链补全（action=links 或 all）

对每条笔记，调 `quick-kb-manager-agent` intent=`recommend_relations`：

- 入参/返回结构见 manager-agent SKILL.md §0 契约
- 返回候选列表（target / type / similarity / reason）

#### 2.0 写入前校验（v1.8 WP2）

落盘前按 [`write-validation-rules.md`](../../references/write-validation-rules.md) 校验，任一失败 → 按规则修正后才写入，不得静默落盘不合规内容；无文件索引可查时在输出中 ⚠ 标注：

- **relations 键必须 ∈ schema enum**（supports / contradicts / evolves / supersedes / evolved_by / superseded_by / derived_from / source_of / refines / refined_by，对照 [`frontmatter-v0.2.md` §3](../../references/frontmatter-v0.2.md)）——**禁止自创关系类型**（如 `complements`）
- **wikilink 目标存在性**：relations / MOC / 反向键中的 `[[X]]` 目标必须已存在于 vault 文件名索引，否则降级为普通文本或加粗
- **关系去重**：同一笔记对同 target + 同 type 的关系不重复写入

#### 2.1 写入策略（v1.7 含 WP3-A/B 循环与冲突检测）

| 关系 | 相似度 | interactive=true | interactive=false |
|------|--------|-----------------|------------------|
| supports | > 0.6 | 提示用户确认 | 自动写入 |
| evolves | > 0.85 | **必须确认**（演化关系强） | 自动写入 + 报告 |
| supersedes | 候选 status=deprecated | 提示用户确认 | 自动写入 |
| contradicts | 对立语义 + 高相似度 | **必须确认** + 提示声明 context | 自动写入 + 警告 |

**v1.7 WP3-A 循环检测（双向 evolves）**：
```markdown
写入 A→B 前检测 B 是否已含 A→B 或反向 evolves：
若检测到循环：
- 不写入
- 报告：「⚠ 关系循环：A evolves B 与 B evolves A 冲突，请改用 supersedes 或拆分」
- 建议用户手动消歧
```

**v1.7 WP3-B 冲突消歧（supports + contradicts）**：
```markdown
写入 supports 或 contradicts 前，检测同一对笔记是否已有反向关系：
若 A.supports=[B] 已存在，新写 A.contradicts=[B]：
- 暂不写入 contradicts
- 报告：「⚠ 语义冲突：A 对 B 已 supports，是否覆盖？需补充 context」
```

#### 2.2 V1 兼容

- 既有笔记的扁平 `related` 不删除
- 若 `related` 中的笔记同时被推荐为 `supports` → 写入 `relations.supports`，保留 `related`
- 批量迁移由 v0.4 normalize 完成

#### 2.3 双向关系

- supports/contradicts（对称）→ 在双方 frontmatter 都写入
- evolves/supersedes（有向）→ 仅在源笔记写入（B→A 时只在 A 写 `evolves: [B]`）

#### 2.4 写入后自检（v1.8 WP2）

写 A→B 关系后，**必须**检查 B 的 frontmatter 已含对应反向键，缺失则补写（幂等，已存在不重复追加）：

- 对称关系（supports/contradicts）→ B 的对应键必须已含 A
- 有向关系按 §5.2.1 反向补全表：`evolves`→`evolved_by`、`supersedes`→`superseded_by`、`derived_from`→`source_of`、`refines`→`refined_by`

### 步骤 3 · MOC 生成（action=moc 或 all）

调 `quick-kb-manager-agent` intent=`build_moc`：

- 入参/返回结构见 manager-agent SKILL.md §0 契约
- 返回 MOC 路径与聚类说明

#### 3.1 模板

基于 [`templates/zh/moc.md`](../../templates/zh/moc.md)。

#### 3.2 已存在 MOC 的处理（diff merge）

- 保留人工修订章节（如含 `<!-- manual -->` 标记的段落）
- 仅刷新自动生成区（聚类清单）
- 写入 frontmatter `updated` 为今天

### 步骤 4 · 知识地图（action=canvas 或 all）

1. 探测 json-canvas 技能是否可用
2. 可用 → 调用生成 `06_wiki/maps/<domain>.canvas`，节点 = 笔记、边 = relations（按 [`json-canvas-schema.md`](../../references/json-canvas-schema.md) §4 着色）
3. 不可用 → 跳过，报告「Obsidian-skills 缺失，仅产出 MOC；安装后运行 connect action=canvas 补全」

> 节点 `id` / `file` / `label` 与边 `color` / 方向严格按 [`references/json-canvas-schema.md`](../../references/json-canvas-schema.md)。对称关系只生成一条无向边；反向键（evolved_by 等）不重复生成边。

### 步骤 5 · 更新全局导航

更新 `06_wiki/_index.md`：

- 主题 MOC 段加入新 MOC wikilink
- 最近段可选更新

### 步骤 6 · 反馈输出

```
✓ Connect 完成（scope: ai-engineering）

  双链：
    ✓ 写入 relations × N 条
      - supports × A（自动 × X / 确认 × Y）
      - contradicts × B（已建立双向，请补充 context）
      - evolves × C
      - supersedes × D
    ⏭ 跳过（相似度 < 阈值）× M

  MOC：
    ✓ 06_wiki/mocs/ai-engineering-moc.md（新建 / 更新）
    聚类：RAG (4) · Agent (3) · 工具调用 (2) · 待补充 (1)

  Canvas：
    ✓ 06_wiki/maps/ai-engineering.canvas
    （或：⏭ Obsidian 缺失，跳过）

  下一步：
    → quick-kb-review focus=knowledge  # 检查本次 connect 是否引入冲突
    → 手动补充 contradicts 笔记的 context
```

> 💡 **下一步**：运行 `quick-kb-query` 验证检索效果，或 `quick-kb-stats` 查看知识库健康度。

---

## 5. 输出契约

### 5.1 frontmatter.relations

严格按 [`frontmatter-v0.2.md` §3](../../references/frontmatter-v0.2.md)。

> **❌ 硬约束**：生成 MOC 条目时，`confidence` / `maturity` / `tags` / `status` / `domain` **必须逐字段从对应笔记 frontmatter 原样复制**，禁止从正文关键词推断。任何字段缺失 → 条目该字段留空 + 在 MOC 末尾「⚠ 字段缺失清单」列出，**禁止默认填充**。

### 5.2 MOC 路径

`06_wiki/mocs/<domain>-moc.md`

> **嵌套 domain（v1.4+）**：`scope` 含 `/` 时，MOC 文件名用 `-` 连接：`scope=programming/python` → `06_wiki/mocs/programming-python-moc.md`。

#### 5.2.1 非对称关系反向补全

写入有向关系时，自动在目标笔记补反向键：

| 正向（A→B） | 自动补的反向（B→A） |
|-------------|---------------------|
| `evolves` | `evolved_by` |
| `supersedes` | `superseded_by` |
| `derived_from` | `source_of` |
| `refines` | `refined_by` |
| `supports` / `contradicts` | 对称，已在双方写入（保持现状） |

**规则**：
- 反向补全**幂等**——已存在不重复追加。
- 删除 A 中正向关系后，B 的反向键**不自动删除**（保留人工痕迹，仅在报告列「孤儿反向键」）。

#### 5.2.2 v1.7 WP3-C evolves/supersedes 候选推荐

build_moc 时，对同 domain + 同 type 的笔记对，若满足以下条件标记为 evolves/supersedes 候选（不自动写入，仅提示）：
- tag Jaccard ≥ 0.7
- created 时间差 > 30 天
- 标题语义相似（关键词重叠）

**提示格式**：
```markdown
⚠ evolves/supersedes 候荐：
  - [[新笔记]] 可能是 [[旧笔记]] 的演进（相似度 X，时间差 Y 天）
  - 建议用户确认后手动添加 evolves 关系
```

### 5.3 Canvas 路径

`06_wiki/maps/<domain>.canvas`（Obsidian 缺失时不创建）

---

## 6. 边界

- **不改正文** —— 只改 frontmatter.relations + 新建 MOC/canvas
- **不擅自选边** —— contradicts 双方同时建立 + 提示声明 context
- **不删除 related** —— V1 兼容字段保留

## 7. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 无 embedding 服务 | similarity 按 [`scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」计算（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4） |
| 范围内笔记相似度均 < 0.6 | connect 退为「只扫标题共现」，标 `needs_review: true` |
| 无 json-canvas | 跳过 .canvas 生成 |
| MOC 聚类失败 | 按 tag.topic 简单分组 |
| 范围内笔记 < 3 条 | 不生成 MOC，提示「笔记太少，建议先 ingest」 |

## 8. 幂等保证

- 同一对笔记的同一类型关系 → 不重复写入
- MOC 二次运行 → diff merge，保留人工修订
- Canvas 二次运行 → 覆盖（canvas 是衍生品，可重建）

---

## 9. 自检清单

- [ ] 所有写入的关系都是 `relations`（不再写扁平 `related`）
- [ ] 对称关系（supports/contradicts）在双方都写入
- [ ] contradicts 候选已提示用户声明 context
- [ ] MOC 模板对齐 `templates/zh/moc.md`
- [ ] 既有 MOC 的人工修订段被保留
- [ ] Canvas 在 Obsidian 缺失时正确跳过
- [ ] 全局导航 `06_wiki/_index.md` 已更新
- [ ] **MOC 字段 vs frontmatter 一致性自检**——生成 MOC 后立即 diff，不一致直接 fail（不再仅警告）
- [ ] **v1.7 WP3-A 新增**：
      · [ ] 循环关系检测已执行（双向 evolves 100% 被拒绝）
- [ ] **v1.7 WP3-B 新增**：
      · [ ] supports/contradicts 冲突消歧检测已执行
- [ ] **v1.7 WP3-C 新增**：
      · [ ] evolves/supersedes 候选推荐已生成（若适用）
- [ ] **写入前校验（v1.8 WP2）**：relations 键 ∈ schema enum（无自创类型）/ wikilink 目标存在 / 同 target+type 去重
- [ ] **写入后自检（v1.8 WP2）**：每条 A→B 写入后，B 的反向键已确认存在或已补写

---

## 10. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| SKILLS_SPEC §4 step 2 表述「找 related 字段」，v0.2 实现改为优先读 relations | V2 升级 relations，related 仅作 V1 兼容回退 | DESIGN §6.7 + 偏差检查报告 §3.1 |
| interactive 模式默认 true | 避免自动写入错误的 evolves/contradicts | 风险控制，不偏离设计 |
| Canvas 边按 relations 类型着色 | 区分 supports/contradicts/evolves/supersedes | 增强 ADR-011 冲突可视化 |
