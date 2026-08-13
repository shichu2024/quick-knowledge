---
version: V1
updated: 2026-08-09
phase: v0.2
applies_to: capture / ingest / review 技能
source_of_truth:
  - docs/DESIGN.md §7.6（主动提醒机制全量）
  - docs/AGENTS_SPEC.md §4.3 + 附录（限流）
  - docs/dev/v0.2-loops.md WP10
---

# v0.2 主动提醒机制 · manager 事件子集实现说明

> 本文件汇总 v0.2 阶段在 capture / ingest / review 三技能中插入的 manager 事件主动提醒。memory 事件（4 类）推迟到 v0.3，由 quick-kb-memory-agent 接入后补齐。

---

## 1. 全量 7 类事件 vs v0.2 范围

DESIGN §7.6 定义 7 类事件：

| 事件 | 触发 agent | v0.2 | v0.3 |
|------|----------|------|------|
| Ingest 新笔记 | manager | ✓ | — |
| Review 完成 | manager | ✓ | — |
| 长期未触碰 applied 笔记 | manager | ✓（基于 updated 时间，不基于 maturity） | v0.3 改为基于 maturity |
| 新建项目 | memory | ✗ | ✓ |
| 新建目标 | memory | ✗ | ✓ |
| Capture 某主题素材 | memory | ✗ | ✓ |
| Ingest 检测冲突 | memory | ✗ | ✓ |

> v0.2 处理 3 类（manager 部分），v0.3 补 4 类（memory 部分）。

---

## 2. 各技能的提醒实现点

### 2.1 capture（v0.2 不调 memory）

- **不产主动提醒** —— v0.2 capture 不调 quick-kb-memory-agent
- 仅在反馈输出中提示「下一步 → ingest」（非提醒，是工作流引导）

### 2.2 ingest（v0.2 manager 事件 · ingest_new）

调用：

```
manager_agent.proactive_remind(
  event: "ingest_new",
  context: { new_note, recommended_relations }
)
```

产出：

- **关系建立提示**：「新笔记 [[X]] 与 [[Y]] 相似度 0.78，已建立 supports；与 [[Z]] 似有对立，已建立 contradicts，请补充各自 context」
- **冲突提示**（contradicts 候选）：强制用户确认 + 声明 context（见 ingest SKILL §3.2）

### 2.3 review（v0.2 manager 事件 · review_done + 长期未触碰）

调用：

```
manager_agent.proactive_remind(
  event: "review_done",
  context: { snapshot, high_value_low_confidence, low_reuse_high_occupancy }
)

manager_agent.proactive_remind(
  event: "stale_applied_notes",
  context: { snapshot }  # updated > 6 个月（v0.2 代理指标）
)
```

产出：

- 「这 3 条高价值低置信笔记该去验证了：[[X]] [[Y]] [[Z]]」
- 「这 5 条低复用高占用笔记该连 MOC 或归档」
- 「这 2 条笔记已 6 个月未更新，建议重审：[[A]] [[B]]」

---

## 3. 限流（AGENTS_SPEC 附录）

| 规则 | 值 |
|------|-----|
| 单次技能调用呈现上限 | **≤ 3 条**（按优先级截断） |
| 同事件去重 | 同一对象同事件最多 1 次 |
| 同会话同类型上限 | 最多 2 次 |
| 库内笔记 < N 时关闭 | **N = 50** |

### 3.1 优先级（AGENTS_SPEC 附录）

| 事件 | 默认优先级 |
|------|----------|
| 与失败 experience 冲突 | high（v0.3 memory 事件） |
| 与 belief/principle 冲突 | high（v0.3 memory 事件） |
| 新笔记与既有 contradicts 苗头 | **medium（v0.2 ingest）** |
| 相似项目/目标召回 | medium（v0.3 memory 事件） |
| 结构演化升格建议 | low（v0.3 manager 扩展） |
| 孤立笔记提示 | low（v0.2 review） |
| 长期未触碰笔记衰减提示 | **low（v0.2 review）** |
| 高价值低置信验证提示 | **medium（v0.2 review）** |

---

## 4. 配置覆盖

用户可在 `kb.config.yaml` 关闭某类提醒（v0.3 起完整支持，v0.2 部分支持）：

```yaml
# v0.2 支持的字段
proactive_reminders:
  enabled: true                # 总开关
  quiet_below_notes: 50        # 低于此数关闭
  # suppress: []               # v0.3 启用（关闭某类）
  # max_per_session: 3         # v0.3 启用（自定义上限）
```

---

## 5. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 仅 manager 事件（3 类），不做 memory 事件（4 类） | quick-kb-memory-agent 在 v0.3 | dev/v0.2-loops.md WP10 |
| 长期未触碰基于 updated 时间而非 maturity/applied | maturity 字段未启用（v0.3） | DESIGN §6.4 |
| suppress / max_per_session 配置项推迟 v0.3 | v0.2 仅做最基础的开关 | 实现简化，不偏离设计 |
| review 高价值低置信提示基于 reuse + confidence（非 KS） | KS 依赖 maturity（v0.3） | frontmatter-v0.2.md §4.2 |
