---
name: quick-kb-advisor
description: |
  Query+ 闭环 · 决策辅助。基于个人认知资产（principle/belief/pattern/experience）辅助用户决策。调 memory-agent 召回历史经验 + 检索认知资产 + 冲突检测，输出三段：你的历史 / 你的原则 / 建议路径。
  触发词（中文）：我要做…怎么搞 / 帮我决策 / 我该怎么选 / 设计个 X / advisor
  Triggers (EN): how should I / help me decide / design a / advise on
version: v0.3
phase: v0.3
applies_to: 读全库认知资产 + 调 memory-agent（recall_similar / check_beliefs）
source_of_truth:
  - docs/DESIGN.md §7.5
  - docs/SKILLS_SPEC.md §6
  - docs/AGENTS_SPEC.md §3 / §4.2
  - docs/dev/v0.3-assistant.md WP4
---

# quick-kb-advisor（v0.3）

> **决策辅助**：基于个人历史经验给"怎么做"的建议。
>
> 与 `quick-kb-query` 的区别：query 回答"是什么/有没有"（事实型，强制引用）；advisor 回答"怎么做"（思考型，基于个人经验综合建议）。两者并列，触发语义不同。

---

## 1. 何时调用

- 用户说「我要做一个 X，怎么搞」「帮我决策」「我该怎么选」「设计个插件系统」
- English: "how should I …", "help me decide", "design a …", "advise on …"
- **不调用**：用户只问"我笔记里有没有 X"（→ query）、"整理一下"（→ connect/review）

---

## 2. v0.3 范围

### 做

- 调 `memory-agent.recall_similar` 召回相关 experience/pattern/decision
- 调 `memory-agent.check_beliefs` 检索相关 principle/belief
- 检索相关 concept（domain 内的方法支撑）
- 候选方案与失败 experience 冲突时显式警告
- 输出三段：你的历史 / 你的原则 / 建议路径
- 缺口提示（建议 Capture 本次决策）

### 不做（v0.4+）

- 不写任何笔记（Capture 由用户决定）
- 不调 research-agent（外部资料由用户先 Capture/Ingest）
- 不调 manager-agent（结构问题归 review/connect）

---

## 3. 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 情境 `situation` | 是 | 当前任务/决策的自然语言描述 |
| 约束 `constraints` | 否 | 已知约束（时间、技术栈、团队、阶段） |
| 候选 `options` | 否 | 已有的备选方案；未给则由 advisor 推演 2-3 个 |

---

## 4. 工作流

```
1. 解析 situation + constraints → 提取关键概念和领域 domain
2. memory_agent.recall_similar({
     current_context: situation,
     constraints,
     options: { max_results: 5, prefer_failures: true }
   })
   → found: 相关 experience/pattern/decision
   → conflicts?: 召回结果内部的 contradicts

3. memory_agent.check_beliefs({
     current_context: situation,
     candidate_plan: options || 推演方案
   })
   → 相关 principle/belief，每条带 aligned/conflict/neutral 标注

4. 检索 concept（domain 内）：作为方法支撑
   → 用 Grep/ Glob 在 concepts/ 或顶层笔记中按 domain tag 搜

5. 冲突检测：
   - 若 options 与某条 failure experience 的 lesson 冲突 → 标 ⚠
   - 若 options 与某条 principle 的陈述方向相反 → 标 ⚠

6. 缺口判断：
   - 若关键决策缺乏经验支撑（召回 < 2 条 OR 召回 confidence 均低）
   - → 提示用户 Capture 本次决策

7. 综合输出（三段式，见 §5）
```

---

## 5. 输出格式（三段 + 缺口）

```markdown
## 你要做的：<situation 一句话>

### 你的历史
> 召回的相关经验，按 memory-agent score 排序。
> **无论是否降级都优先列 experience**：降级时来自 `07_principles/{experiences,patterns,principles,beliefs}/` + `05_outputs/daily/` 的规则扫描（见 §7 降级路径），非降级时来自 `memory-agent.recall_similar`。

- [[experience/BI-engine-plugin-isolation]] · 相关点：<...>
  · 教训：<lesson 摘要>
- [[pattern/micro-frontend-iframe-isolation]] · 相关点：<...>
- [[experience/2024-sandbox-escape]] · ⚠ failure · 教训：<...>

### 你的原则
> 适用原则/信念，标注是否与候选冲突

- [[principle/boundary-over-reuse]] · aligned：「边界管理优先于组件复用」
- [[principle/small-fast-steps]] · aligned
- ⚠ 候选方案 B 与 [[experience/2024-sandbox-escape]] 的 lesson 冲突
  · 该教训：进程内沙箱在 <context> 下不可靠
  · 候选方案 B 采用进程内沙箱 → 不建议

### 建议路径
> 综合建议，每条说明基于哪条经验/原则

1. 先定插件 ↔ 宿主的边界契约
   · 基于 [[principle/boundary-over-reuse]]
2. 隔离方案选进程级
   · 基于 [[experience/2024-sandbox-escape]] 的教训
3. ...

### 缺口
> 缺乏经验支撑的部分

- 缺少"插件版本治理"相关经验
- → 建议 quick-kb-capture 记录本次决策；归档时 lesson 派生为新的 experience
```

---

## 6. 冲突呈现规则（对应 ADR-011 / AGENTS_SPEC §3.6）

当召回或检测涉及 `relations.contradicts` 时：

- **同时呈现双方**，不擅自选边
- **标注各自 `context`**，让用户判断当前情境更接近哪一方
- 在 `reasoning` 中显式说明：
  > 检测到上下文冲突：[[A]] 适用于 <context_a>，[[B]] 适用于 <context_b>。请基于当前情境选择；若处于中间区间，建议 Capture 决策后跟踪 actual。

格式示例：

```markdown
### ⚠ 经验冲突
- [[microservice-large-team]] · 适用：团队 >100 人，多团队并行
- [[modular-monolith-startup]] · 适用：团队 <50 人，迭代周期 <2 周
> 当前情境（团队 8 人）更接近后者；但若预期 6 个月内扩张，前者更优。
> 建议：Capture 本次选择，6 个月后跟踪 actual。
```

---

## 7. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 库内笔记 < 50 条 | advisor 仍可工作，但所有建议都标注「⚠ 库内经验不足，以下非基于充分个人经验」 |
| `07_principles/` 目录不存在 | "你的原则"段输出「未启用认知资产层」+ 提示 v0.3 启用 |
| memory-agent 完全不可用 | 扫描 `07_principles/{experiences,patterns,principles,beliefs}/` + `05_outputs/daily/` 中匹配 decision keywords 的笔记，按 `score = 0.5 × tag_overlap + 0.3 × recency_norm + 0.2 × title_keyword_hit` 排序（recency_norm = 1/(1+days_since_updated/30)），输出明确标注「⚠ 未启用 memory-agent，以下为规则召回，质量可能下降」 |
| 召回 0 条 | "你的历史"段输出「未找到相关经验」+ 强化缺口提示 |

---

## 8. 边界

- **承认主观性** —— advisor 明确这是「基于你个人经验的建议」，不是客观最优解
- **不替代决策** —— 给建议，最终决定权在人
- **不写笔记** —— 输出仅展示给用户；Capture 决策由用户显式触发
- **不调外部资料** —— 外部 research 由 capture/ingest 阶段完成；advisor 只读库内

---

## 9. 幂等保证

- 同一 `situation` 多次调用，输出顺序一致（按 memory-agent score 排序）
- 召回结果只读，不修改任何笔记
- 缺口提示文本一致（基于召回数量阈值，非随机）

---

## 10. 自检清单

- [ ] 调用了 memory-agent（不是直接 Grep 库）
- [ ] 召回结果按 memory-agent score 排序（experience 失败案例排前）
- [ ] 输出含三段：你的历史 / 你的原则 / 建议路径
- [ ] 候选与失败 experience 冲突时显式 ⚠ 警告
- [ ] contradicts 双方同时呈现（ADR-011）
- [ ] 缺口段在召回不足时给出 Capture 建议
- [ ] 降级时显式标注「非基于充分个人经验」
- [ ] 不写任何笔记文件

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| concept 检索不调 memory-agent | memory-agent 候选集排除 concept（见 memory-agent §1）；concept 检索走简单 Grep/标签 | docs/AGENTS_SPEC.md §3 类型加权表暗示 |
| options 缺省时推演 2-3 个 | SKILLS_SPEC §6 输入表标注 options 非必填，但工作流第 5 步要"综合建议" | docs/SKILLS_SPEC.md §6 |
| 不调 research-agent 检索外部 | 外部资料域归 research-agent，但 advisor 阶段不做扩展研究（避免发散） | docs/DESIGN.md §7 边界 |
