---
name: quick-kb-query
description: |
  基于库内笔记回答事实型问题，强制引用。strict 模式默认（每句结论挂 [[]]）；召回含 contradicts 时同时呈现双方 + context（ADR-011）；召回为 0 明确说「未找到」，不编造。
  触发词（中文）：我笔记里… / 找一下… / 关于 X 怎么说 / KB 查
  Triggers (EN): search my notes / what do I have on / kb query
version: v1.9.2
phase: v0.2
applies_to: 读全库 · 落简易查询日志
source_of_truth:
  - docs/DESIGN.md §6.7（冲突处理）· §7（agent 协作）
  - docs/SKILLS_SPEC.md §5
  - docs/AGENTS_SPEC.md §4.2（冲突感知协议）
  - docs/dev/v0.2-loops.md WP5
---

# quick-kb-query（v0.2）

> 事实型检索：基于库内笔记回答「是什么/有没有」。每句结论挂引用；冲突同时呈现。

---

## 1. 何时调用

- 用户说「我笔记里关于 X 怎么说」「KB 查一下 …」
- 与 advisor 区别：query = 事实型（强制引用）；advisor = 思考型（基于经验综合建议，v0.3）

## 2. v0.2 范围

### 做

- 检索：基于关键词 + 标签 + wikilink 图谱召回候选
- 排序：按 `confidence × recency × 入链数（value.reuse）` 加权
- strict 模式默认：每句结论挂 `[[]]` 或 source 引用
- hybrid 模式可选：库内 + 推测分段
- **冲突呈现**（ADR-011）：召回含 contradicts → 双方同时呈现 + 各自 context
- 召回 < 阈值 → 明确说「未找到」+ 提示 capture
- 落简易查询日志（供 review/refresh_value 用）

### 不做

- ❌ 不调经验召回（v0.3 才有完整排序公式）
- ❌ 不修改笔记（只读）
- ❌ 不做决策建议（advisor 域）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `question` | ✓ | — | 自然语言问题 |
| `scope` | 否 | 全库 | 领域 / 标签 / 全库；领域可含 `/` 嵌套（v1.4+，如 `programming/python`，扫叶子目录；单层 `programming` 扫全子树） |
| `mode` | 否 | `strict` | `strict`（必须引用）/ `hybrid`（库内 + 推测分段） |
| `include_archived` | 否 | `true` | `true`：归档笔记（`98_archive/`）正常参与召回（默认，向后兼容）；`false`：过滤掉 `98_archive/` 下的命中 |

---

## 4. 工作流

### 步骤 1 · 检索

1. **关键词提取**：从 question 抽取核心名词、动词
2. **多路召回**：
   - 标签匹配（受控词表）
   - 标题关键词匹配（模糊）
   - wikilink 图谱扩展（命中笔记的 relations 邻居加分）
3. **embedding 路径**（如可用）：question embedding → 余弦相似度
4. **降级**：无 embedding → 相似度按 [`references/scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」计算，召回仍叠加上述规则

### 步骤 2 · 排序

```
score = confidence_factor × recency_factor × reuse_factor

confidence_factor = confidence / 100
recency_factor    = max(0.3, 1 − days_since_updated / 365)
reuse_factor      = log2(1 + value.reuse) / log2(1 + max_reuse_in_pool)
                    # 除零保护（v1.9.2）：max_reuse_in_pool = 0（冷启动全库 reuse=0）时
                    # reuse_factor 取 1（中性），排序退化为 confidence × recency；
                    # 若 confidence 亦全部相同 → 降级为 created 倒序并在输出 ⚠ 标注「冷启动排序」
```

> v0.2 简化排序；v0.3 启用完整公式（含类型加权、prefer_failures，见 `docs/AGENTS_SPEC.md` §3.5）。

### 步骤 3 · 冲突检测

对召回结果，调 `quick-kb-memory-agent` intent=`present_conflicts`：

- 入参/返回结构见 memory-agent SKILL.md §0 契约
- 返回 conflicts 列表（同时呈现双方 + 各自 context）

### 步骤 4 · 回答生成

#### 4.1 strict 模式（默认）

- **每句结论必须挂引用**（`[[]]` 或 `source`）
- 无法引用 → 不写（避免幻觉）
- 召回为 0 → 明确说「库内未找到关于 X 的笔记」，建议 capture
- **归档笔记标注**：命中 `98_archive/` 下的笔记时，引用后追加 `(📄 已归档 YYYY-MM-DD)`，日期取该笔记 frontmatter 的 `archived_at` 字段；若无 `archived_at` 字段则写 `(📄 已归档)`

输出：

```markdown
## 答

RAG 的核心是检索后生成，关键决策在于分块策略和向量库选型 [[RAG 架构设计]]。

分块推荐按语义切分而非固定长度 [[Vector Database]]。

> 召回笔记：N 条 · 平均置信度：70 · 最近更新：2026-08-09
```

#### 4.2 hybrid 模式

库内结论（强制引用）+ 推测结论分段呈现：

```markdown
## 答（库内）

RAG 的核心是检索后生成 [[RAG 架构设计]]。

## 库内未覆盖（以下为推测）

- 多模态 RAG 的具体实现细节 —— 建议捕获相关资料。
```

### 步骤 5 · 冲突呈现（ADR-011）

若召回含 conflicts：

```markdown
## 答

关于「微服务架构是否适合创业团队」，库内有两条相互冲突的经验：

- [[微服务适合大型系统]] · context: 团队 >100 人，多团队并行
  - "微服务允许独立部署，适合多团队大型组织"
- [[模块化单体更适合创业团队]] · context: 团队 <50 人，迭代周期 <2 周
  - "创业团队应优先选择模块化单体以降低运维成本"

> ⚠ 这两条笔记声明了不同的适用上下文（relations.contradicts）。请基于你当前的团队规模判断；若处于中间区间，建议捕获本次决策跟踪 actual。
```

**严禁**：
- 擅自选边（"我认为 A 更对"）
- 隐藏其中一方
- 不呈现 context

### 步骤 6 · 未命中提示

召回 < 阈值（默认相似度 < 0.4 全部候选；**降级态 0.30**，见 [`scoring.md`](../../references/scoring.md) §5.1）：

```
库内未找到关于「X」的笔记。
  → 是否调用 quick-kb-capture 抓相关资料？
    预填充：quick-kb-capture "X · 待研究"（capture_type=idea · suggested_tags 取本次查询关键词）
  → 或调用 quick-kb-advisor（v0.3）做基于经验的建议？
```

> v1.8.2：零召回建议 capture 时附预填充内容（待研究问题原句 + 查询关键词作 suggested_tags），用户确认后直接执行。

### 步骤 7 · 落查询日志

每次 query 写入 `99_system/workflows/.query-log.jsonl`（追加）：

```json
{
  "ts": "2026-08-09T14:30",
  "question": "...",
  "scope": "...",
  "hits": ["[[note-1]]", "[[note-2]]"],
  "mode": "strict",
  "had_conflicts": false
}
```

供 review/refresh_value 计算查询命中次数。

---

## 5. 输出契约

按 SKILLS_SPEC §5 输出格式。strict 模式每句结论挂引用；冲突同时呈现。

---

## 6. 边界

- **绝不编造引用** —— 找不到引用就说找不到
- **不修改笔记** —— 只读
- **不擅自选边** —— conflicts 双方同时呈现
- **触发捕获** —— 检测到缺口时，建议调用 capture

## 7. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 无 embedding | 相似度按 [`references/scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」计算（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4），叠加关键词 + 标题模糊匹配 |
| 无 wikilink 图谱可扩展 | 仅关键词召回 |
| 召回为 0 | 直接说「未找到」+ capture 建议 |
| 库 < 5 条笔记 | 提示「库内经验不足」，仍尝试回答但标注 low-confidence |

## 8. 幂等保证

- query 是只读，本身幂等
- 查询日志追加模式，不覆盖

---

## 9. 自检清单

- [ ] strict 模式下每句结论挂引用
- [ ] 召回含 contradicts → 双方都呈现 + 各自 context
- [ ] 召回为 0 → 明确「未找到」+ capture 建议
- [ ] hybrid 模式库内/推测分段清晰
- [ ] 查询日志已落 jsonl
- [ ] 落查询日志：确认 99_system/workflows/.query-log.jsonl 存在且已追加本次查询
- [ ] 不修改任何笔记
- [ ] 归档命中是否标注 (📄 已归档)

---

## 10. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| v0.2 用简化排序公式 | 完整公式（含类型加权、prefer_failures）在 v0.3 启用 | dev/v0.2-loops.md WP5 + docs/AGENTS_SPEC.md §3.5 |
| 排序公式简化（confidence × recency × reuse） | v0.2 无 maturity/impact，简化合理 | AGENTS_SPEC §3.5 完整公式在 v0.3 启用 |
| 落 .query-log.jsonl | 供 review refresh_value 用 | dev/v0.2-loops.md WP6 review 需 reuse 刷新 |
| conflicts 检测基于 relations.contradicts 字段 | ADR-011 + AGENTS_SPEC §4.2 | DESIGN §6.7 |
