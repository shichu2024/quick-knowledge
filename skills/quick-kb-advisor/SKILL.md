---
name: quick-kb-advisor
description: |
  Query+ 闭环 · 决策辅助。基于个人认知资产（principle/belief/pattern/experience）辅助用户决策。扫描 07_principles/ + 05_outputs/daily/ 召回历史经验 + 核对信念 + 冲突检测，输出三段：你的历史 / 你的原则 / 建议路径。
  触发词（中文）：我要做…怎么搞 / 帮我决策 / 我该怎么选 / 设计个 X / advisor
  Triggers (EN): how should I / help me decide / design a / advise on
version: v0.3
phase: v0.3
applies_to: 读全库认知资产（07_principles/ + 05_outputs/daily/）；调 quick-kb-memory-agent 召回与排序
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

- 调 `quick-kb-memory-agent` skill（intent=`recall_similar`）召回相关 experience/pattern/decision；score 排序由 memory-agent 按 `docs/AGENTS_SPEC.md` §3.5 公式计算（experience 失败案例权重提升）
- 扫描 `07_principles/{principles,beliefs}/`，对每条判定与候选方案的 aligned/conflict/neutral 关系
- 检索相关 concept（domain 内的方法支撑，走简单 Grep/标签匹配）
- 候选方案与失败 experience 冲突时显式警告
- 输出三段：你的历史 / 你的原则 / 建议路径
- 缺口提示（建议 Capture 本次决策）

### 不做（v0.4+）

- 不写任何笔记（Capture 由用户决定）
- 不检索外部资料（外部资料由用户先 Capture/Ingest）
- 不做结构分析（结构问题归 review/connect）

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
2. 经验召回：
   - 调 `quick-kb-memory-agent`（intent=`recall_similar`，候选限 type∈{experience,pattern,decision}）
   - memory-agent 内部按 §3.5 计算 score（几何平均 + 类型系数 + 失败系数，prefer_failures=true）
   - 取 score 最高的 max_results=5 条

3. 信念核对：
   - 调 `quick-kb-memory-agent`（intent=`check_beliefs`）对 principle/belief 逐条判定 aligned/conflict/neutral
   - 若 candidate_plan 缺省 → 先推演 2-3 个再核对

4. 检索 concept（domain 内）：作为方法支撑
   → 用 Grep/Glob 在 02_areas/<domain>/ 按 domain tag 搜

5. 冲突检测（调 `quick-kb-memory-agent` intent=`detect_repeat_mistakes` + `present_conflicts`）：
   - 若 options 与某条 failure experience 的 lesson 冲突 → 标 ⚠（memory-agent 输出 repeat_risk）
   - 若 options 与某条 principle 的陈述方向相反 → 标 ⚠
   - 召回结果含 contradicts → memory-agent.present_conflicts 输出双方对照

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
> 由 `quick-kb-memory-agent.recall_similar` 召回，按 §3.5 score 公式排序（experience 失败案例权重提升）。
> 候选集：`07_principles/{experiences,patterns,principles,beliefs}/` + `05_outputs/daily/`。

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
| 无 embedding 服务 | similarity 降为「标签 Jaccard + 标题关键词重叠」（权重各 0.5），输出标注「⚠ 未启用语义相似度」 |
| 召回 0 条 | "你的历史"段输出「未找到相关经验」+ 强化缺口提示 |

---

## 8. 边界

- **承认主观性** —— advisor 明确这是「基于你个人经验的建议」，不是客观最优解
- **不替代决策** —— 给建议，最终决定权在人
- **不写笔记** —— 输出仅展示给用户；Capture 决策由用户显式触发
- **不调外部资料** —— 外部 research 由 capture/ingest 阶段完成；advisor 只读库内

---

## 9. 幂等保证

- 同一 `situation` 多次调用，输出顺序一致（memory-agent 按 §3.5 score 公式排序）
- 召回结果只读，不修改任何笔记
- 缺口提示文本一致（基于召回数量阈值，非随机）

---

## 10. 自检清单

- [ ] 调用了 `quick-kb-memory-agent` 而非全库盲搜（候选集限定 07_principles/ + 05_outputs/daily/）
- [ ] memory-agent 按 §3.5 score 公式排序（experience 失败案例排前）
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
| concept 不进入经验召回候选集 | 经验召回候选集严格限定为 experience/pattern/decision/principle/belief；concept 检索单独走 Grep/标签 | docs/AGENTS_SPEC.md §3 类型加权表 |
| options 缺省时推演 2-3 个 | SKILLS_SPEC §6 输入表标注 options 非必填，但工作流第 5 步要"综合建议" | docs/SKILLS_SPEC.md §6 |
| 不检索外部资料 | advisor 阶段不做扩展研究（避免发散）；外部资料由 capture/ingest 先入库 | docs/DESIGN.md §7 边界 |
