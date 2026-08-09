---
version: V1
updated: 2026-08-09
---

# quick-knowledge · Agent 详细规格

> 本文件是对 [`DESIGN.md`](./DESIGN.md) 第 7 节「Agent 设计」的展开。三个 agent（manager / research / memory）的输入输出契约、排序公式、降级路径、调用示例在此规格化，便于任意技能按契约调用。
>
> 所有 agent 遵循通用规范：纯函数式（同样输入产同样输出）、不绑定 runtime、可被多技能并发调用、有降级路径。

---

## 目录

- [通用约定](#通用约定)
- [1. quick-kb-manager-agent](#1-quick-kb-manager-agent)
- [2. quick-kb-research-agent](#2-quick-kb-research-agent)
- [3. quick-kb-memory-agent](#3-quick-kb-memory-agent)
- [4. Agent 共享数据契约](#4-agent-共享数据契约)
- [附录 · 提醒优先级与限流](#附录--提醒优先级与限流)

---

## 通用约定

### 文件位置

```
99_system/agents/
├── quick-kb-manager-agent.md
├── quick-kb-research-agent.md
└── quick-kb-memory-agent.md
```

### 调用契约

agent 不直接被用户触发，而是由技能（quick-kb-*）在内部调用。调用形式：

```
<agent-name>(
  intent: <能力名>,
  payload: { ... },
  options: { max_results, min_confidence, ... }
) → AgentResult
```

### 统一返回结构

```typescript
interface AgentResult {
  found: Note[]              // 召回/产出的笔记列表
  reasoning: string          // 为什么返回这些（可解释性）
  conflicts?: Conflict[]     // 若涉及冲突，附上下文对照
  suggestions?: Suggestion[] // 主动建议（用于提醒机制）
  degraded?: boolean         // 是否走了降级路径
  meta: { agent, latency_ms, version }
}
```

### 输入域不重叠

| Agent | 输入域 | 不读 |
|-------|--------|------|
| research | 外部资料（URL/PDF/长文） | 库内已有笔记 |
| memory | 当前任务/情境（query） | 外部资料 |
| manager | 全库快照（结构） | 任务语义、外部资料 |

---

## 1. quick-kb-manager-agent

**角色**：知识库管家 + 知识架构师。维护索引、关系、价值、结构。

### 1.1 能力清单

| intent | 输入 | 输出 |
|--------|------|------|
| `tidy_inbox` | inbox 笔记列表 | 聚类 + 入库优先级排序 |
| `build_moc` | 领域名 / 标签 | MOC 笔记（写入 `06_wiki/mocs/`） |
| `recommend_relations` | 单条笔记 | 候选 `relations.{supports/evolves}` 列表 |
| `detect_orphans` | 全库快照 | 孤立笔记清单（无入链无出链） |
| `repair_deadlinks` | 全库快照 | 死链清单 + 修复建议 |
| `detect_structure_drift` | 全库快照 + 时间窗 | 子领域增速异常 → 升格建议 |
| `refresh_value` | 全库快照 + 查询日志 | 更新每条笔记的 `value.reuse` 与 KS |
| `proactive_remind` | 事件类型 + 上下文 | 主动建议列表（见附录） |

### 1.2 排序与阈值

- **MOC 聚类**：标签共现 + wikilink 图谱（Louvain 社区发现，纯规则实现，降级为标签共现）。
- **关系推荐**：标题/标签/embedding 相似度 > 0.6 进候选；> 0.85 提示合并或 `evolves`。
- **孤立笔记阈值**：入链 = 出链 = 0 → 标记孤立。
- **结构升格阈值**：某子领域近 6 个月新增 ≥ 30 条 或 占父领域 ≥ 40% → 建议升格。

### 1.3 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 无查询日志（早期 vault） | `refresh_value` 仅用入链数；`reuse` 数值偏低属正常 |
| 无 embedding 服务 | 关系推荐降为标签共现 + 标题关键词 |
| manager-agent 完全不可用 | 调用方技能自行做基于规则的最小检查 |

### 1.4 调用示例

```
manager_agent.detect_structure_drift(
  payload: { window_months: 6 },
  options: { min_count: 30 }
)
→ {
    found: [{ subarea: "02_areas/ai-engineering/mcp", count: 40, parent_ratio: 0.45 }],
    reasoning: "MCP 子领域近 6 个月新增 40 篇，占 AI 工程 45%，超阈值",
    suggestions: [{ action: "promote_to_domain", target: "02_areas/mcp/" }]
  }
```

---

## 2. quick-kb-research-agent

**角色**：研究员。面向外部资料，提取原子观点。

### 2.1 能力清单

| intent | 输入 | 输出 |
|--------|------|------|
| `process_resource` | 长文/PDF/网页干净正文 | 结构化摘要卡 + 候选原子笔记 |
| `extract_atoms` | 一段长文 | 多条原子笔记（一笔记一观点） |
| `cross_verify` | 候选笔记 + 已入库笔记 | 调整后的 confidence + 引用链 |
| `summarize` | 任意长文 | 摘要（300/800/详细 三档） |

### 2.2 抽取规则

- **原子化**：每条笔记只表达一个可独立成立的观点；含"且/并且/同时"的复合句优先拆分。
- **保留原始**：摘要的同时保留 source.raw 指向原始素材，永不删原始。
- **confidence 初值**：
  - 单一非一手来源 → 30-40
  - 多源佐证 → 60-75
  - 含一手实验/官方文档 → 80-95
  - 推测/无来源 → ≤ 30 并标 `maturity: captured`

### 2.3 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| research-agent 不可用 | ingest 回退为「模板套用 + 字段填充」，不抽原子观点；多观点素材仍作为单条入库，待人工拆分 |
| 抓取失败（404/付费墙） | 仅基于已有正文片段生成摘要，标 `partial: true` |

---

## 3. quick-kb-memory-agent

**角色**：长期记忆调取者。**核心 agent**，决定 quick-knowledge 是「个人助手」还是「带引用的 RAG」。

### 3.1 设计目标

让 AI 在用户做新决策时，主动调取「历史上类似情境下，这个人做过什么、信什么、栽在哪」。本质是把个人 vault 当作长期记忆来 query，而非文档库来检索。

### 3.2 能力清单

| intent | 输入 | 输出 |
|--------|------|------|
| `recall_similar` | 当前任务/情境描述 | 相似 experience/pattern/decision 列表 |
| `check_beliefs` | 候选方案 | 相关 principle/belief 列表 + 一致性判定 |
| `detect_repeat_mistakes` | 当前计划 | 与历史失败 experience 的冲突警告 |
| `proactive_suggest` | 事件类型 + 上下文 | 主动建议（用于提醒机制） |
| `present_conflicts` | 召回结果（含 contradicts） | 冲突双方 + 各自 context 对照呈现 |

### 3.3 输入契约

```typescript
interface MemoryQuery {
  current_context: string          // 当前任务/情境的自然语言描述
  constraints?: string             // 已知约束（团队/阶段/技术栈）
  intent: "recall_similar" | "check_beliefs" | ...
  options?: {
    max_results: number            // 默认 5
    min_similarity: number         // 默认 0.55
    recency_weight: number         // 默认 0.2，范围 0-1
    prefer_failures: boolean       // 默认 true，失败案例权重提升
  }
}
```

### 3.4 输出契约

```typescript
interface MemoryResult extends AgentResult {
  found: MemoryNote[]              // 排序后的相关记忆
  conflicts?: Array<{
    a: Note, b: Note,              // 冲突双方
    context_a: string, context_b: string  // 各自适用上下文
  }>
}

interface MemoryNote extends Note {
  similarity: number               // 0-1
  recency_days: number             // 距今天数
  score: number                    // 综合分（见 3.5）
  why: string                      // 为什么召回（可解释性）
}
```

### 3.5 召回排序公式（核心）

反馈明确建议：`similarity + recency + impact + confidence`。本规格采用**加权几何平均**（避免某因子为 0 时整体归零）：

```
score = similarity^w_s × recency_factor^w_r × impact_factor^w_i × confidence_factor^w_c
```

各因子归一到 [0,1]：

| 因子 | 计算 | 默认权重 |
|------|------|---------|
| `similarity` | embedding 余弦 或 标签 Jaccard（降级） | 0.45 |
| `recency_factor` | `max(0.3, 1 − days/365)`（1 年后衰减到底线 0.3，不归零） | 0.20 |
| `impact_factor` | `(value.impact ?? 3) / 5` | 0.15 |
| `confidence_factor` | `confidence / 100` | 0.20 |

**类型加权**（叠加在 score 上，乘以系数）：

| type | 加权系数 | 理由 |
|------|---------|------|
| `experience`（含失败） | **1.5** | 个人亲历教训最相关 |
| `pattern` | 1.3 | 已抽象的可复用模式 |
| `decision` | 1.2 | 历史选型参考 |
| `principle` | 1.1 | 长期价值观 |
| `belief` | 0.9 | 待验证，权重略低 |
| `concept` | 1.0 | 基准 |
| `resource` | 0.7 | 外部资料，弱个人关联 |

> `prefer_failures=true` 时，`experience` 中 status 含失败语义（标题/标签含"失败/教训/踩坑/fail"）再额外 ×1.2。

### 3.6 冲突呈现规则（关键 · 对应 ADR-011）

召回结果若涉及 `relations.contradicts`：

- **必须同时呈现双方**，不擅自选边。
- 标注各自的 `context`，让用户判断当前情境更接近哪一方。
- 在 `reasoning` 中显式说明：「检测到上下文冲突：A 适用于 X 情境，B 适用于 Y 情境，请基于当前情境选择」。

示例输出：

```json
{
  "found": [
    { "title": "微服务适合大型系统", "similarity": 0.78, "context": "团队 >100 人，多团队并行" },
    { "title": "模块化单体更适合创业团队", "similarity": 0.75, "context": "团队 <50 人，迭代周期 <2 周" }
  ],
  "conflicts": [{
    "a": "[[微服务适合大型系统]]",
    "b": "[[模块化单体更适合创业团队]]",
    "context_a": "团队 >100 人",
    "context_b": "团队 <50 人"
  }],
  "reasoning": "两条相互矛盾的经验都相关。请基于当前团队规模选择；若处于中间区间，建议 Capture 决策后跟踪 actual。"
}
```

### 3.7 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 库内笔记 < 50 条 | 返回「库内经验不足，以下基于通用建议」+ `degraded: true`；不强行编造经验 |
| 无 embedding 服务 | similarity 降为标签 Jaccard + 标题关键词重叠 |
| memory-agent 完全不可用 | advisor/project 退化为「只查 concept 不调经验」的 RAG，并明确告知用户 |

### 3.8 调用示例

```
memory_agent.recall_similar(
  payload: {
    current_context: "要为公司内部工具设计一个插件系统，团队 8 人，希望支持第三方扩展",
    constraints: "必须进程级隔离，性能次要"
  },
  options: { max_results: 5, prefer_failures: true }
)
→ {
    found: [
      { title: "BI 引擎插件隔离方案", type: "experience", similarity: 0.82, score: 0.79, why: "同为内部工具插件体系" },
      { title: "微前端 iframe 隔离", type: "pattern", similarity: 0.71, score: 0.61, why: "同涉及隔离边界" },
      { title: "2024 沙箱逃逸教训", type: "experience", similarity: 0.68, score: 0.72, why: "失败案例，prefer_failures 提升" }
    ],
    conflicts: [],
    reasoning: "召回到 3 条相关经验，其中 1 条失败教训按 prefer_failures 加权排第三"
  }
```

---

## 4. Agent 共享数据契约

### 4.1 Note 投影

agent 之间传递笔记时使用统一的 Note 投影（仅必要字段）：

```typescript
interface Note {
  path: string             // 相对 vault 根
  title: string
  type: NoteType
  frontmatter: {
    status, maturity?, confidence?, domain?,
    tags: string[],
    relations?: { supports?, contradicts?, evolves?, supersedes? },
    context?: string,
    value?: { reuse, impact?, uniqueness? },
    related?: string[]     // V1 兼容
  }
  excerpt: string          // 摘要片段
}
```

### 4.2 冲突感知协议

任何 agent 召回/推荐笔记时，若结果含 `relations.contradicts`，必须遵循：

1. **双方同时返回** —— 不可只返回一方。
2. **附 context** —— 各自的适用上下文必须呈现。
3. **不选边** —— AI 不替用户判断哪方正确，仅在 `reasoning` 中标注情境对照。
4. **缺口提示** —— 若当前情境与双方 context 都不完全匹配，提示「Capture 决策跟踪 actual」。

### 4.3 主动提醒协议

agent 输出的 `suggestions` 字段用于主动提醒机制（DESIGN §7.6）。每条 suggestion 含：

```typescript
interface Suggestion {
  event: string            // 触发事件
  priority: "high" | "medium" | "low"
  message: string          // 提醒文案
  refs: string[]           // 关联笔记 [[wikilink]]
  action?: string          // 建议的下一步技能调用
}
```

限流规则见附录。

---

## 附录 · 提醒优先级与限流

### 优先级

| 事件 | 默认优先级 |
|------|----------|
| 与失败 experience 冲突 | high |
| 与 belief/principle 冲突 | high |
| 新笔记与既有 contradicts 苗头 | medium |
| 相似项目/目标召回 | medium |
| 结构演化升格建议 | low |
| 孤立笔记提示 | low |
| 长期未触碰笔记衰减提示 | low |

### 限流

- 同一事件最多触发 1 次提醒（去重）。
- 单次技能调用最多向用户呈现 **3 条**提醒，按优先级截断。
- 同一会话内同类型提醒最多出现 2 次。
- 库内笔记 < 50 条时，**关闭**主动提醒（避免噪音）。
- 用户可在 `kb.config.yaml` 关闭某类提醒：

```yaml
proactive_reminders:
  enabled: true
  suppress: [structure_drift]   # 关闭结构演化提醒
  quiet_below_notes: 50
```
