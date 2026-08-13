---
version: V2
updated: 2026-08-09
phase: v0.3
applies_to: quick-kb-query / quick-kb-advisor / quick-kb-memory-agent / quick-kb-ingest
source_of_truth:
  - docs/DESIGN.md §6.7（冲突处理原则）
  - docs/AGENTS_SPEC.md §3.6 / §4.2（冲突感知协议）
  - ADR-011
  - docs/dev/v0.3-assistant.md WP8
---

# ADR-011 冲突呈现规则 · v0.3 全量落地说明

> **核心规则**：任何召回/推荐场景，若涉及 `relations.contradicts`，必须**同时呈现双方 + 各自 context**，**不擅自选边**，让用户基于当前情境判断。

---

## 1. 规则四要素（AGENTS_SPEC §3.6）

1. **双方同时呈现**：A 和 B 都出现在结果中，不论哪一方原始相似度更高
2. **context 显式标注**：每条笔记的 `context` 字段必须显示（缺失则用 type+tags 退化标注）
3. **reasoning 中说明情境对照**：在 `reasoning` 字段中显式指出冲突
4. **缺口提示**：若当前情境与双方都不完全匹配，建议 Capture 决策跟踪 actual

---

## 2. v0.3 落地点

| 组件 | 落地位置 | 实现要点 |
|------|---------|---------|
| `quick-kb-query` SKILL §步骤 5 | v0.2 已有；v0.3 验证不变 | 召回含 conflicts → 双方并列 + context + 缺口建议 |
| `quick-kb-advisor` SKILL §6 | v0.3 WP4 新增 | 候选方案与失败 experience 冲突时显式 ⚠，contradicts 双方同时呈现 |
| `quick-kb-memory-agent` §3.5 + §3.6 | v0.3 WP3 新增 | `present_conflicts` intent 专门处理；recall_similar 结果含 conflicts 字段 |
| `quick-kb-ingest` SKILL | v0.2 已有 contradicts 检测；v0.3 强化 | 新笔记写入时检测与既有笔记 contradicts 关系，触发 memory 事件 ingest_conflict_detected |

---

## 3. 输出格式规范（统一）

### 3.1 query / advisor 输出（Markdown）

```markdown
## ⚠ 经验冲突（关于：{{主题}}）

- [[笔记 A]] · context: <context_a>
  · 摘要：<一句话观点>
- [[笔记 B]] · context: <context_b>
  · 摘要：<一句话对立观点>

> 这两条笔记声明了不同的适用上下文。请基于你当前的 <关键约束> 判断；
> 若处于中间区间，建议 Capture 本次决策跟踪 actual。
```

### 3.2 quick-kb-memory-agent 返回（JSON）

```typescript
{
  found: [/* 双方都在 found 中，按 score 排序 */],
  conflicts: [{
    a: Note, b: Note,
    context_a: string,
    context_b: string
  }],
  reasoning: "检测到上下文冲突：A 适用于 <context_a>，B 适用于 <context_b>。请基于当前情境选择；若处于中间区间，建议 Capture 决策后跟踪 actual。"
}
```

---

## 4. 严禁行为（AGENTS_SPEC §4.2）

- ❌ 擅自选边（"我认为 A 更对" / "推荐 A"）
- ❌ 隐藏其中一方（即便原始相似度低于阈值）
- ❌ 不呈现 context（"两条笔记互相矛盾" 而不说各自适用场景）
- ❌ 在 reasoning 中给出「应该选 A/B」的判断
- ❌ 把冲突降级为「仅供参考」

---

## 5. 冲突的来源与传播

### 5.1 显式声明（用户/quick-kb-manager-agent 建立）

- 用户在 ingest/connect 阶段显式建立 `relations.contradicts`
- quick-kb-manager-agent.recommend_relations 在相似度 > 0.85 但 type/title 暗示对立时建议

### 5.2 隐式发现（quick-kb-memory-agent 检测）

- recall_similar 召回双方且双方 context 不同 → 提示用户「疑似冲突，是否建立 contradicts」
- check_beliefs 发现候选方案与某 principle 方向相反 → 标 ⚠

### 5.3 传播

- 任何组件发现冲突 → 调用 quick-kb-memory-agent.present_conflicts 统一加工为输出
- 不允许各组件自己实现冲突呈现逻辑（避免不一致）

---

## 6. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 不新增单独的「冲突技能」 | DESIGN §6.7 明确冲突呈现是规则不是技能，由各召回技能统一执行 | docs/DESIGN.md §6.7 |
| ingest 阶段也执行规则 | v0.2 ingest 已有 contradicts 检测；v0.3 通过 memory 事件 ingest_conflict_detected 闭环 | docs/dev/v0.3-assistant.md WP8 + WP9 |
