---
version: V2
updated: 2026-08-09
phase: v0.3
applies_to: capture / ingest / review / project / goal / advisor 技能 + quick-kb-manager-agent + quick-kb-memory-agent
source_of_truth:
  - docs/DESIGN.md §7.6（主动提醒机制全量）
  - docs/AGENTS_SPEC.md §4.3 + 附录（限流）
  - docs/dev/v0.3-assistant.md WP9
supersedes:
  - references/proactive-reminders-v0.2.md（v0.2 仅 manager 子集）
---

# v0.3 主动提醒机制 · 全量 7 类事件实现说明

> v0.3 在 v0.2 manager 事件子集（3 类）基础上补齐 memory 事件（4 类），实现 DESIGN §7.6 全量 7 类。由 quick-kb-memory-agent（4 类）+ quick-kb-manager-agent（3 类）协作执行。

---

## 1. 全量 7 类事件总览

| # | 事件 | 触发 agent | 触发技能 | v0.2 | v0.3 |
|---|------|----------|---------|------|------|
| 1 | Ingest 新笔记 | manager | ingest | ✓ | ✓ |
| 2 | Review 完成 | manager | review | ✓ | ✓ |
| 3 | 长期未触碰 applied | manager | review | ✓（updated 时间） | ✓（改为基于 maturity/applied） |
| 4 | 新建项目 | memory | project init | ✗ | ✓ |
| 5 | 新建目标 | memory | goal create | ✗ | ✓ |
| 6 | Capture 某主题素材 | memory | capture | ✗ | ✓ |
| 7 | Ingest 检测冲突 | memory | ingest | ✗ | ✓ |

---

## 2. v0.3 新增 memory 事件详解

### 2.1 new_project_init（项目 init）

**触发点**：`quick-kb-project init` 完成 vault 结构后（WP5）

```
memory_agent.proactive_suggest({
  event_type: "new_project_init",
  current_context: <项目 description>,
  constraints: <team/tech stack if known>
})
```

**内部调用**：`recall_similar`（候选限 type∈{project, experience}）

**输出示例**：
```
[info] 你过去有 3 个类似项目：
  - [[BI 插件体系]]（相关点：同为内部工具插件体系）
  - [[工作流引擎]]（相关点：同为扩展性设计）
  - [[MCP 工具设计]]（相关点：同为第三方扩展场景）
是否复用？建议在 _readme.md 的「经验复用建议」区块引用。
```

**写入位置**：`04_projects/<slug>/_readme.md` 的「经验复用建议」段

---

### 2.2 new_goal_create（目标 create）

**触发点**：`quick-kb-goal create` 写入 goal.md 后（WP6）

```
memory_agent.proactive_suggest({
  event_type: "new_goal_create",
  current_context: <目标 description>,
  constraints: <domain>
})
```

**内部调用**：`recall_similar`（候选限 domain 内的 principle/belief/experience）

**输出示例**：
```
[info] 该目标关联领域 [[前端工程]] 有：
  - 原则 2 条：[[principle/boundary-over-reuse]] [[principle/small-fast-steps]]
  - 待验证假设 1 条：[[belief/micro-frontend-default]]
  - ⚠ 失败教训 1 条：[[experience/2024-spa-seo-fail]]
建议先看。
```

**写入位置**：`03_goals/<slug>/goal.md` 的「相关笔记」段

---

### 2.3 capture_topic_match（Capture 完成）

**触发点**：`quick-kb-capture` 写入素材后（web-clip / pdf / meeting / ai-dialog / reading）

```
memory_agent.proactive_suggest({
  event_type: "capture_topic_match",
  current_context: <素材 topic + 摘要>
})
```

**内部调用**：`recall_similar` + `check_beliefs`

**输出示例**：
```
[info] 这条素材与你 [[experience/2025-rag-practice]] 相关
[warning] 注意：[[experience/2025-rag-failure]] 与之冲突（context: <...>）
```

**呈现方式**：capture 输出末尾的「相关召回」段（不写文件，仅显示）

---

### 2.4 ingest_conflict_detected（Ingest 冲突）

**触发点**：`quick-kb-ingest` 写入新笔记时，新笔记 frontmatter 含 `relations.contradicts` 或检测到潜在冲突

```
memory_agent.proactive_suggest({
  event_type: "ingest_conflict_detected",
  current_context: <新笔记 + 既有冲突笔记>
})
```

**内部调用**：`present_conflicts`

**输出示例**：
```
[warning] 新笔记 [[新结论]] 与 [[2024 微服务最优论]] 在 `context: 创业团队` 下冲突
建议：
  - 在新笔记的 relations.contradicts 引用 [[2024 微服务最优论]]
  - 双方各自声明 context
  - Capture 本次决策后跟踪 actual
```

**呈现方式**：ingest 输出的「冲突提示」段（强制用户确认）

---

## 3. v0.2 继承的 manager 事件（保持不变）

### 3.1 ingest_new

调用：
```
manager_agent.proactive_remind(
  event: "ingest_new",
  context: { new_note, recommended_relations }
)
```

### 3.2 review_done + stale_applied_notes

调用：
```
manager_agent.proactive_remind(
  event: "review_done",
  context: { snapshot, high_value_low_confidence, low_reuse_high_occupancy }
)

manager_agent.proactive_remind(
  event: "stale_applied_notes",
  context: { snapshot }  # v0.3 改为基于 maturity: applied 且 updated > 6 月
)
```

**v0.3 改进**：长期未触碰的检测从「updated 时间」改为「maturity: applied 且 updated > 6 月」（更精准）

---

## 4. 限流（AGENTS_SPEC 附录）

| 规则 | 值 |
|------|-----|
| 单次技能调用呈现上限 | **≤ 3 条**（按优先级截断） |
| 同事件去重 | 同一对象同事件最多 1 次 |
| 同会话同类型上限 | 最多 2 次 |
| 库内笔记 < N 时关闭 | **N = 50** |
| memory 事件与会话内总数 | memory 提醒 ≤ 3 条/会话（与 manager 合并计数） |

### 4.1 优先级（v0.3 全量）

| 事件 | 默认优先级 | 触发 agent |
|------|----------|-----------|
| 与失败 experience 冲突 | **high** | memory |
| 与 belief/principle 冲突 | **high** | memory |
| ingest 检测 contradicts 苗头 | **high** | memory |
| 新笔记与既有 contradicts 苗头 | medium | manager |
| 高价值低置信验证提示 | medium | manager |
| 相似项目/目标召回 | medium | memory |
| Capture 命中相关 belief/pattern | medium | memory |
| 结构演化升格建议（v0.3 启用） | low | manager |
| 孤立笔记提示 | low | manager |
| 长期未触碰笔记衰减提示 | low | manager |

---

## 5. 配置覆盖（kb.config.yaml）

v0.3 完整支持以下字段：

```yaml
proactive_reminders:
  enabled: true                    # 总开关
  quiet_below_notes: 50            # 低于此数关闭
  suppress: []                     # 关闭某类（按事件名）
    # 可选值：new_project_init / new_goal_create / capture_topic_match
    #         / ingest_conflict_detected / ingest_new / review_done
    #         / stale_applied_notes
  max_per_session: 3               # 单会话呈现上限（默认 3）
  max_per_skill_call: 2            # 单次技能调用上限（默认 2，避免噪音）
```

---

## 6. 实现要点

### 6.1 触发顺序

memory 事件优先于 manager 事件检测（memory 优先级更高）。例如 ingest 同时触发 ingest_conflict_detected（memory）和 ingest_new（manager）→ 先呈现 conflict，再呈现 relation 建议。

### 6.2 提醒去重

- 同会话内同一笔记不重复提醒
- 用户已 dismiss 的提醒不重复弹出（v0.4 可记录到 99_system/workflows/.reminder-state.json）

### 6.3 与降级配合

- 库 < 50 → 所有 memory 事件关闭（manager 事件保留，因其为结构提醒不依赖经验）
- quick-kb-memory-agent 完全不可用 → memory 事件全部跳过，不报错

---

## 7. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| memory 事件「≤3/会话」与 manager 合并计数 | 避免用户被多事件淹没 | docs/DESIGN.md §7.6「单次会话内提醒总数 ≤ 3」 |
| stale_applied_notes v0.3 改为基于 maturity | maturity 字段 v0.3 启用，比 updated 时间更精准 | docs/DESIGN.md §7.6 + §6.4 |
| capture_topic_match 仅显示不写文件 | capture 阶段笔记尚未 ingest，召回结果不稳定；待 ingest 后由 manager 事件 ingest_new 落地 | 实现简化 |
| 同事件去重扩展到全 7 类 | v0.2 仅 3 类去重；v0.3 memory 事件可能高频触发需更严格 | docs/AGENTS_SPEC.md 附录 |
