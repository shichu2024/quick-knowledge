---
version: v1.8
updated: 2026-08-14
phase: v1.8
applies_to: quick-kb-stats（KS Top 10）/ quick-kb-review（价值刷新）/ quick-kb-memory-agent（召回排序）/ quick-kb-manager-agent · quick-kb-query · quick-kb-advisor（无 embedding 降级相似度）
source_of_truth:
  - docs/DESIGN.md §6.5（Knowledge Score）/ §6.6（value 维度）
  - docs/AGENTS_SPEC.md §3（排序公式）
  - docs/dev/v1.4-docs.md B-WP5
  - docs/dev/v1.8-e2e-calibration.md WP3-3
---

# 评分公式 · Scoring Formulas

> 本文件公开 quick-knowledge 使用的三个核心评分公式。`quick-kb-stats`、`quick-kb-review` 和 `quick-kb-memory-agent` 在计算 Knowledge Score、复用度、时效性时**共同引用此文件**，确保评分口径透明、可复现。

---

## 1. Knowledge Score（KS）

Knowledge Score 是笔记的综合价值评分，取值范围 **0-100**。

```
KS = 0.4 × confidence + 0.3 × recency_norm + 0.3 × reuse_norm
```

| 因子 | 权重 | 来源 | 取值范围 | 说明 |
|------|------|------|---------|------|
| `confidence` | 0.4 | `frontmatter.confidence` | 0-100 | 置信度：单源 30-40 / 多源 60-75 / 一手 80-95 |
| `recency_norm` | 0.3 | 实时计算（见 §3） | 0-100 | 时效性归一化值 |
| `reuse_norm` | 0.3 | 实时计算（见 §2） | 0-100 | 复用度归一化值 |

> **设计理由**：confidence 权重最大（0.4），因为知识库的核心价值在于「可信」；recency 和 reuse 等权（各 0.3），兼顾「鲜活」与「被引用」。

---

## 2. 复用度（reuse）

复用度衡量一条笔记被库内其他笔记、MOC、查询「消费」的程度。

```
reuse = 0.5 × wikilink_count + 0.3 × moc_indexed_count + 0.2 × query_hit_count
```

| 因子 | 权重 | 说明 | 数据来源 |
|------|------|------|---------|
| `wikilink_count` | 0.5 | 被其他笔记通过 `[[]]` 引用的次数 | wikilink 图谱扫描 |
| `moc_indexed_count` | 0.3 | 被 MOC 文件收录的次数 | `06_wiki/mocs/` 扫描 |
| `query_hit_count` | 0.2 | 被 quick-kb-query 召回的次数 | `99_system/workflows/.query-log.jsonl` |

> **归一化**：`reuse_norm` 将 `reuse` 原始值映射到 0-100。常用方法为全库最大值归一化：`reuse_norm = (reuse / max_reuse_in_vault) × 100`。库内 max_reuse = 0 时（首次运行），reuse_norm = 0。

---

## 3. 时效性归一化（recency_norm）

时效性衡量笔记「最近一次更新距今」的新鲜程度，使用调和衰减函数。

```
recency_norm = 1 / (1 + days_since_updated / 30)
```

| 变量 | 说明 | 数据来源 |
|------|------|---------|
| `days_since_updated` | 最近一次更新（`frontmatter.updated`）距今的天数 | frontmatter.updated |
| `30` | 半衰期常数（约 1 个月） | 固定值 |

### 3.1 行为特性

| days_since_updated | recency_norm | 含义 |
|-------------------|-------------|------|
| 0（今天） | 1.0 | 最新 |
| 30（约 1 月） | 0.5 | 半衰 |
| 90（约 3 月） | 0.25 | 较旧 |
| 180（约半年） | 0.143 | 陈旧 |
| 365（约 1 年） | 0.076 | 过时 |

### 3.2 recency_factor 分段（v1.7 review refresh_value 用）

为便于 review 在 KS 排序时快速估算时效性贡献，使用以下分段简化计算（与调和衰减函数近似）：

| `updated` 距今 | recency_factor |
|----------------|----------------|
| ≤ 30 天 | 1.0 |
| 30-90 天 | 0.8 |
| 90-180 天 | 0.65 |
| > 180 天 | 0.5 |

> 该分段在 `quick-kb-review` refresh_value 步骤中使用（见 `skills/quick-kb-review/SKILL.md` §步骤 2）。

> **映射到 0-100**：`recency_norm`（0-1）乘以 100 即得 0-100 分制下的值。

> **半衰期 = 30 天** 的设计理由：知识库中大部分技术类笔记的「保鲜期」约 1 个月；超过 30 天未更新的笔记，其时效性贡献快速下降但不归零（调和衰减保证旧笔记仍有微弱分数）。

---

## 4. 综合示例

假设一条笔记：

| 因子 | 原始值 | 归一化（0-100） |
|------|--------|----------------|
| confidence | 75 | 75 |
| updated | 10 天前 | recency_norm = 1/(1+10/30) = 0.75 → 75 |
| reuse | wikilink=3, moc=1, query=2 → 0.5×3+0.3×1+0.2×2=2.2 | 假设全库 max=5 → 2.2/5×100 = 44 |

```
KS = 0.4 × 75 + 0.3 × 75 + 0.3 × 44 = 30 + 22.5 + 13.2 = 65.7
```

---

## 5. 无 embedding 降级相似度公式

embedding 服务不可用时，所有依赖相似度的技能（quick-kb-manager-agent / quick-kb-memory-agent / quick-kb-query / quick-kb-advisor，以及 ingest 关系推荐中的 manager-agent 调用）**统一引用本条目**，不再各自定义权重：

```
similarity = 标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4
```

| 因子 | 权重 | 说明 |
|------|------|------|
| 标签 Jaccard | 0.6 | `|tags_A ∩ tags_B| / |tags_A ∪ tags_B|` |
| 标题关键词重叠 | 0.4 | 标题分词后重叠词数 / 较长标题词数 |

> **统一理由**：同一对笔记在不同技能中的 similarity 必须相等（跨技能一致性）；此前 manager-agent 用 0.6/0.4、memory-agent/query 各自定义，导致同一 vault 内排序不可复现（dev doc v1.8 §0.2 N3）。降级精度下降仅影响推荐质量，不影响公式本身。

### 5.1 降级态推荐阈值（v1.9.1）

**实测分布（测试10）**：中英文混合 vault（标签英文、上下文中文）下，降级公式输出集中在 **0.1-0.25**——若沿用正常态阈值（0.45-0.65），召回率趋近于零（61 项输出全部 degraded 且无命中）。降级态必须**同步下调阈值**，各技能统一执行：

| 技能 | 正常态阈值 | 降级态阈值 | 说明 |
|------|-----------|-----------|------|
| memory-agent `recall_similar` / `check_beliefs`（min_similarity） | 0.55 | **0.35** | 主召回 |
| memory-agent `detect_repeat_mistakes` | 0.65 | **0.45** | 重复错误检测（需更高精度） |
| memory-agent 隐式冲突检测（present_conflicts） | 0.65 | **0.75**（提高，v1.8.2） | 防误报，方向相反 |
| manager-agent `recommend_relations`（threshold） | 0.6 | **0.40** | 关系推荐候选 |
| query 召回阈值 | 0.4 | **0.30** | 查询召回 |
| advisor | 继承 memory-agent | 继承 memory-agent | — |

> 阈值下调的代价是误报率上升——降级态输出必须携带 ⚠「降级模式：阈值已下调至 X，结果精度低于正常态」标注，由用户自行判断。embedding 可用后自动恢复正常态阈值。

---

## 6. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.4 | 2026-08-13 | 初始版本，公开三个公式及参数 |
| v1.8 | 2026-08-14 | 新增 §5 无 embedding 降级相似度公式（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4，全局统一定档） |
