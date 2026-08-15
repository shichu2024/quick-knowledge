---
name: quick-kb-memory-agent
description: |
  长期记忆调取者（技能化封装 · 核心）。在用户做新决策时，主动调取「历史上类似情境下，这个人做过什么、信什么、栽在哪」。把 vault 当作长期记忆来 query，而非文档库来检索。
  能力：recall_similar / check_beliefs / detect_repeat_mistakes / proactive_suggest / present_conflicts。
  可被 advisor / project / goal / ingest 通过 Skill 工具调用，也可由用户直接调用。
  触发词（中文）：我以前怎么做过… / 我的信念库 / 重复踩坑检测 / 召回相似经验
  Triggers (EN): recall similar / check beliefs / repeat mistakes / memory recall
version: v1.8.1
phase: v0.3
applies_to: 只读 `07_principles/{experiences,patterns}/` + `05_outputs/daily/` · 不写入笔记
source_of_truth:
  - docs/DESIGN.md §7.3 / §7.6
  - docs/AGENTS_SPEC.md §3
  - docs/dev/v0.3-assistant.md WP3
---

# quick-kb-memory-agent（v0.3）

> **角色**：长期记忆调取者。**只读库内经验/认知资产**（experience/pattern/decision/principle/belief）。
>
> **不读**：结构（quick-kb-manager-agent 域）、外部资料（quick-kb-research-agent 域）。
>
> 决定 quick-knowledge 是「个人助手」还是「带引用的 RAG」。

---

## 0. 被调用契约

本技能通过 Skill 工具调用，入参与返回结构严格如下：

```
memory_agent(
  intent: "recall_similar" | "check_beliefs" | "detect_repeat_mistakes"
        | "proactive_suggest" | "present_conflicts",
  payload: {
    current_context: string,           // 当前任务/情境的自然语言描述
    constraints?: string,              // 团队/阶段/技术栈
    candidate_plan?: string,           // check_beliefs / detect_repeat_mistakes 用
    event_type?: "new_project_init" | "new_goal_create" | "capture_topic_match" | "ingest_conflict_detected",  // proactive_suggest 用
    recalled?: Note[]                  // present_conflicts 用（对其他召回结果二次加工）
  },
  options: {
    max_results?: number,              // 默认 5
    min_similarity?: number,           // 默认 0.55
    recency_weight?: number,           // 默认 0.20，范围 0-1
    prefer_failures?: boolean          // 默认 true
  }
) → MemoryAgentResult
```

**返回结构**（MemoryAgentResult）：

```typescript
interface MemoryAgentResult {
  found: Array<{
    // Note 基础字段（path/title/tags/type/confidence/frontmatter）
    similarity: number,                // 0-1
    recency_days: number,             // 距今天数
    score: number,                    // 综合分（§4 公式计算）
    why: string,                      // 为什么召回（单条解释）
    consistency?: "aligned" | "conflict" | "neutral",  // check_beliefs 用
    repeat_risk?: "high" | "medium"   // detect_repeat_mistakes 用
  }>,
  conflicts?: Array<{                 // 召回结果中涉及 contradicts 时
    a: Note,
    b: Note,
    context_a: string,
    context_b: string
  }>,
  reasoning: string,                   // 可解释性（必须含「为什么召回/为什么冲突」）
  suggestions?: Array<{               // proactive_suggest 输出
    event: string,
    message: string,
    related_notes: Note[],
    severity: "info" | "warning"
  }>,
  degraded?: boolean,                 // 是否走了降级路径
  meta: { agent: "memory", latency_ms?: number, version: "v0.3" }
}
```

**字段约定**：
- `score` 按 §4 公式计算（几何平均 + 类型系数 + 失败系数）
- `recency_factor` 使用 `max(0.3, 1 - days/365)` 不归零
- `check_beliefs` 对每条候选标注 `consistency` 于 `why` 字段
- `present_conflicts` 必须同时呈现双方，不输出「应该选 A/B」判断

---

## 1. 能力清单（v0.3 全量）

| intent | 输入 | 输出 |
|--------|------|------|
| `recall_similar` | 当前任务/情境描述 | 相似 experience/pattern/decision 列表（按 §4 排序） |
| `check_beliefs` | 候选方案 | 相关 principle/belief 列表 + 一致性判定 |
| `detect_repeat_mistakes` | 当前计划 | 与历史失败 experience 的冲突警告 |
| `proactive_suggest` | 事件类型 + 上下文 | 主动建议（用于 4 个 memory 提醒事件） |
| `present_conflicts` | 召回结果（含 contradicts） | 冲突双方 + 各自 context 对照呈现 |

> **领域边界**：输入是「库内已有的认知资产」+「当前情境文本」。任何外部资料由 quick-kb-research-agent 先处理后写入库，quick-kb-memory-agent 才能读取。

---

## 2. 调用契约

按 [`AGENTS_SPEC.md` §通用约定](../../docs/AGENTS_SPEC.md)：

```
memory_agent(
  intent: "recall_similar" | "check_beliefs" | "detect_repeat_mistakes"
        | "proactive_suggest" | "present_conflicts",
  payload: {
    current_context: string,           // 当前任务/情境的自然语言描述
    constraints?: string,              // 团队/阶段/技术栈
    candidate_plan?: string,           // check_beliefs / detect_repeat_mistakes 用
    event_type?: memory_event_type,    // proactive_suggest 用
    recalled?: Note[]                  // present_conflicts 用（对其他召回结果二次加工）
  },
  options: {
    max_results?: number,              // 默认 5
    min_similarity?: number,           // 默认 0.55
    recency_weight?: number,           // 默认 0.20，范围 0-1
    prefer_failures?: boolean          // 默认 true
  }
) → MemoryResult
```

返回结构（AGENTS_SPEC §3.4）：

```typescript
interface MemoryResult {
  found: MemoryNote[]                  // 按 §4 公式排序后的相关记忆
  conflicts?: Array<{                  // 召回结果中涉及 contradicts 时
    a: Note, b: Note,
    context_a: string, context_b: string
  }>
  reasoning: string                    // 可解释性（必须含「为什么召回/为什么冲突」）
  suggestions?: Suggestion[]           // proactive_suggest 输出
  degraded?: boolean                   // 是否走了降级路径
  meta: { agent: "memory", latency_ms, version: "v0.3" }
}

interface MemoryNote extends Note {
  similarity: number                   // 0-1
  recency_days: number                 // 距今天数
  score: number                        // 综合分（见 §4）
  why: string                          // 为什么召回（单条解释）
}
```

---

## 3. 各 intent 详述

### 3.1 `recall_similar`

**输入**：`{ current_context, constraints? }`

**候选集**：仅扫以下 type（不含 concept/resource/idea/daily/moc/project/goal）：
- `experience`、`pattern`、`decision`、`principle`、`belief`

**处理**：
1. 对候选集中每条笔记，计算 `similarity`（embedding 余弦；降级公式见 [`references/scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」）
2. 过滤 `similarity < min_similarity`（默认 0.55）
3. 按 §4 公式计算 `score` 并排序
4. 取前 `max_results` 条
5. 若结果中存在 `relations.contradicts` 对 → 填充 `conflicts`

**输出**：`{ found, conflicts?, reasoning }`

---

### 3.2 `check_beliefs`

**输入**：`{ current_context, candidate_plan }`

**候选集**：仅 `principle` 和 `belief`（maturity ≥ captured）

**处理**：
1. 用 `candidate_plan` 对每条 principle/belief 计算相似度
2. 对每条候选，判定 `一致性`：`aligned` / `conflict` / `neutral`
   - `aligned`：候选方案与该 principle/belief 的陈述方向一致
   - `conflict`：方向相反（如 principle 是「小步快跑」而计划是大爆炸式发布）
   - `neutral`：无明确方向关联
3. `conflict` 的同时检查 relations.contradicts，若该 principle 自身有对立 principle，填入 `conflicts`

**输出**：

```typescript
{
  found: MemoryNote[],                  // 相关 principle/belief，带 一致性 标注于 why 字段
  conflicts?: Conflict[],
  reasoning: "找到 N 条相关原则/假设：aligned X / conflict Y / neutral Z ..."
}
```

---

### 3.3 `detect_repeat_mistakes`

**输入**：`{ current_context, candidate_plan }`

**候选集**：仅 `experience`，且 `outcome: failure` 或 `outcome: mixed`（失败语义优先）

**处理**：
1. 计算 similarity
2. 仅保留 similarity > 0.65（高于默认 0.55，避免误报）
3. 对每条失败 experience，提取其 `lesson` 字段
4. 判断 `candidate_plan` 是否触发同类失败模式（关键词匹配 + 语义相似度）
5. 命中的标 `repeat_risk: high | medium`

**输出**：

```typescript
{
  found: (MemoryNote & { repeat_risk: "high"|"medium" })[],
  reasoning: "检测到 N 个历史失败模式可能在当前计划中重演 ..."
}
```

> 注：本 intent 不触发「阻塞」，只产出警告；最终决策权归用户。

---

### 3.4 `proactive_suggest`

**输入**：`{ event_type, current_context, constraints? }`

`event_type` 仅限 4 个 memory 事件（DESIGN §7.6 / AGENTS_SPEC 附录）：

| event_type | 触发场景 | 内部调用哪个 intent |
|------------|---------|-------------------|
| `new_project_init` | quick-kb-project init | recall_similar（限 type=project+experience） |
| `new_goal_create` | quick-kb-goal create | recall_similar（限 domain 内的 principle/belief/experience） |
| `capture_topic_match` | quick-kb-capture 完成后 | recall_similar + check_beliefs |
| `ingest_conflict_detected` | quick-kb-ingest 检测到潜在冲突 | present_conflicts |

**处理**：
1. 按 event_type 选择对应 intent
2. 应用限流（见 §6）
3. 输出 `suggestions: Suggestion[]`，每条 suggestion 形如：

```typescript
{
  event: event_type,
  message: string,                    // 给用户的提醒文本
  related_notes: Note[],              // 提醒涉及的笔记
  severity: "info" | "warning"        // conflict 类事件用 warning
}
```

**输出示例**（new_project_init）：

```
[info] 你过去有 3 个类似项目：
  - [[BI 插件体系]]（相关点：同为内部工具插件体系）
  - [[工作流引擎]]（相关点：同为扩展性设计）
  - [[MCP 工具设计]]（相关点：同为第三方扩展场景）
  是否复用其中经验？建议在 _readme.md 的「经验复用建议」区块引用。
```

---

### 3.5 `present_conflicts`

**输入**：`{ recalled: Note[] }`（来自 recall_similar 或 check_beliefs 的中间结果）

**处理**：
1. 扫描 recalled 中每条笔记的 `relations.contradicts`
2. 若双方都在 recalled 中（或被 contradicts 指向的笔记在库内） → 构造 `Conflict`
3. 提取双方的 `context` 字段（必填，缺失则用 type+tags 退化）
4. **不擅自选边**，不输出「应该选哪个」

**输出**：

```typescript
{
  found: Note[],                       // 原样透传
  conflicts: Conflict[],
  reasoning: "检测到上下文冲突：A 适用于 <context_a>，B 适用于 <context_b>。请基于当前情境选择；若处于中间区间，建议 Capture 决策后跟踪 actual。"
}
```

**关键不变性**（对应 ADR-011）：
- **必须同时呈现双方**
- **必须标注各自 context**
- **不在 reasoning 中给出「应该选 A/B」的判断**

---

## 4. 召回排序公式（核心 · AGENTS_SPEC §3.5）

采用**加权几何平均**（避免某因子为 0 时整体归零）：

```
score = similarity^w_s × recency_factor^w_r × impact_factor^w_i × confidence_factor^w_c
```

各因子归一到 [0,1]：

| 因子 | 计算 | 默认权重 |
|------|------|---------|
| `similarity` | embedding 余弦；降级按 [`references/scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」 | **0.45** |
| `recency_factor` | `max(0.3, 1 − days/365)`（1 年后衰减到底线 0.3，不归零） | **0.20** |
| `impact_factor` | `(value.impact ?? 3) / 5` | **0.15** |
| `confidence_factor` | `confidence / 100` | **0.20** |

> 用户可通过 `options.recency_weight` 覆盖 recency 权重（仅此一项可调，其他保持默认）。

### 4.1 类型加权（叠加在 score 上，乘系数）

| type | 加权系数 | 理由 |
|------|---------|------|
| `experience` | **1.5** | 个人亲历教训最相关 |
| `pattern` | 1.3 | 已抽象的可复用模式 |
| `decision` | 1.2 | 历史选型参考 |
| `principle` | 1.1 | 长期价值观 |
| `belief` | 0.9 | 待验证，权重略低 |
| `concept` | 1.0 | 基准（实际不会被候选集覆盖） |
| `resource` | 0.7 | 外部资料（实际不会被候选集覆盖） |

### 4.2 失败加权

`prefer_failures=true` 时，对 type=experience 的笔记，再额外乘 1.2：
- 触发条件：`outcome: failure` 或 `outcome: mixed`，**或** 标题/标签含「失败/教训/踩坑/fail」之一

> 综合起来，一条 failure experience 的最高系数可达 `1.5 × 1.2 = 1.8`。

### 4.3 计算示例

```
// 输入
{ title: "2024 沙箱逃逸教训", type: "experience", outcome: "failure",
  confidence: 85, value: { impact: 5 }, updated: 60 天前,
  similarity: 0.68 }

// 各因子
recency_factor  = max(0.3, 1 - 60/365)  = 0.836
impact_factor   = 5 / 5                  = 1.0
confidence_f.   = 85 / 100               = 0.85
type_weight     = 1.5 (experience)
failure_weight  = 1.2 (outcome=failure, prefer_failures=true)

// 综合
score = 0.68^0.45 × 0.836^0.20 × 1.0^0.15 × 0.85^0.20
      × 1.5 × 1.2
      ≈ 0.847 × 0.964 × 1.0 × 0.968 × 1.5 × 1.2
      ≈ 1.414
```

> score 可超过 1.0（因类型加权是叠加系数）；最终排序只比较相对大小。

---

## 5. 主动提醒事件详解

### 5.1 new_project_init

- **触发**：`quick-kb-project init` 完成 vault 结构后
- **内部调用**：`recall_similar`（候选限 type∈{project, experience}）
- **建议文案模板**：「你过去有 N 个类似项目：[列表]，是否复用经验？」

### 5.2 new_goal_create

- **触发**：`quick-kb-goal create` 写入 goal.md 后
- **内部调用**：`recall_similar`（候选限 domain 内的 principle/belief/experience）
- **建议文案模板**：「该目标关联领域 [[domain]] 有 N 条原则、M 个失败教训，建议先看」

### 5.3 capture_topic_match

- **触发**：`quick-kb-capture` 写入素材后（web-clip / pdf / meeting / ai-dialog / reading）
- **内部调用**：`recall_similar` + `check_beliefs`
- **建议文案模板**：
  - 命中相关：「这条素材与你 [[X]] 相关」
  - 命中冲突：「注意 [[Y]] 与之冲突（context: ...）」

### 5.4 ingest_conflict_detected

- **触发**：`quick-kb-ingest` 写入新笔记时，relations.contradicts 非空
- **内部调用**：`present_conflicts`
- **建议文案模板**：「新结论与 [[Z]] 在 `context: <X>` 下冲突，建议加 `contradicts` 并各自声明 context」

---

## 6. 限流与降级

### 6.1 限流（DESIGN §7.6）

- **单次会话内**：memory 提醒总数 ≤ 3 条
- **同事件去重**：同一 event_type 在同次技能调用内只触发一次
- **库内 < 50 条**：关闭所有主动提醒，避免噪音（用户可在 `kb.config.yaml` 覆盖阈值）
- **被动召回（recall_similar 等被显式调用）**：不受 ≤3 限制，但 max_results 默认 5

### 6.2 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 库内笔记 < 50 条 | `proactive_suggest` 全部关闭；其他 intent 返回 `degraded: true` + reasoning：「库内经验不足，以下基于有限样本」 |
| 无 embedding 服务 | similarity 按 [`references/scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」计算（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4） |
| 07_principles/ 目录不存在 | check_beliefs 返回空 + reasoning「未启用认知资产层」 |
| 本技能完全不可用 | 调用方技能（advisor/project/goal）退化为「只查 concept 不调经验」的 RAG，并明确告知用户 |

---

## 7. 不变性

- **纯函数式**：所有 intent 只读，不写入 frontmatter（区别于 quick-kb-manager-agent 的 refresh_value）
- **不绑定 runtime**：核心排序公式基于纯算术，无网络依赖
- **可解释**：每条 MemoryNote 必带 `why`；MemoryResult 必带 `reasoning`
- **冲突不选边**：present_conflicts 永远不输出「应该选 A/B」的判断
- **不返回 concept/resource/idea/daily/moc/project/goal**：候选集严格限定（除非 event_type 显式扩展，如 new_project_init 包含 project 自身用于去重）

---

## 8. 自检清单

- [ ] 所有 intent 返回结构符合 MemoryResult 契约
- [ ] recall_similar 候选集不含 concept/resource/idea/daily/moc
- [ ] score 公式按 §4 实现（几何平均 + 类型系数 + 失败系数）
- [ ] recency_factor 使用 `max(0.3, ...)` 不归零
- [ ] present_conflicts 同时呈现双方，不输出选择建议
- [ ] proactive_suggest 遵守限流（≤3 / 库<50 关闭 / 同事件去重）
- [ ] 无 embedding 服务时 similarity 按评分文件降级公式计算（见 §6.2）
- [ ] 每条 MemoryNote 都带 `why`，MemoryResult 都带 `reasoning`
- [ ] check_beliefs 输出对每条候选标注「aligned/conflict/neutral」

---

## 9. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 候选集显式排除 concept/resource/project/goal | 防止记忆召回被「文档型」笔记稀释；这些 type 由其他流程（quick-kb-research-agent 摘要、quick-kb-manager-agent 结构）负责 | docs/AGENTS_SPEC.md §3.5 类型加权暗示 + docs/DESIGN.md §7.3 角色定位 |
| proactive_suggest 仅 4 个 memory 事件 | manager 类 3 个事件归 quick-kb-manager-agent（v0.2 已实现） | docs/DESIGN.md §7.6 / dev/v0.3-assistant.md WP9 |
| recency_weight 仅作可调权重项 | 用户对「最近多久算相关」的偏好差异最大；其他权重已公式化 | docs/AGENTS_SPEC.md §3.5 输入契约 options |
| 检测失败仅靠 outcome + 关键词，无 ML 分类器 | v0.3 阶段保持纯规则；ML 推迟到外部工具集成 | dev/v0.3-assistant.md WP3 范围 |
| 作为独立技能而非内部 agent | 跨 runtime 契约统一以 skill 形式分发；随 npx 安装自动可用 | 本技能定位调整 |
