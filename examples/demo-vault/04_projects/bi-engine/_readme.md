---
title: "BI 引擎（已归档 · quick-knowledge demo）"
type: project
created: 2024-01-10
updated: 2024-12-20
tags:
  - project/bi-engine
status: archived
maturity: teachable
confidence: 90
domain: ai-engineering
relations:
  supports: []
  contradicts: []
  evolves:
    - "[[04_projects/plugin-system/_readme|插件系统 v2]]"
  supersedes: []
context: 8 人 BI 团队的内部 BI 引擎；2024-Q1 落地 V8 沙箱插件，Q3 沙箱逃逸事故后重写为进程级，Q4 归档
value:
  reuse: 0
  impact: 5
  uniqueness: 4
---

# BI 引擎（已归档）

> 本项目已于 2024-12 归档。下一代理项目 [[04_projects/plugin-system/_readme|插件系统 v2]] 继承了本项目教训。

## 归档原因

2024-07 沙箱逃逸事故后，团队决定整体重写为进程级架构（而非在原代码上打补丁）。重写期间项目以「v2」命名单独立项 → [[04_projects/plugin-system/_readme|插件系统 v2]]。

## 关键 Decision Ledger

- [[decisions/2024-02-isolation-choice|Decision 001：BI 引擎插件隔离方案选型]]
  · 已完成 expected/actual/lesson 闭环
  · lesson 派生为 → [[07_principles/experiences/2024-plugin-sandbox-escape]]

## 经验沉淀

- [[07_principles/experiences/2024-plugin-sandbox-escape]] · failure
- [[07_principles/principles/boundary-over-reuse]] · principle
- [[07_principles/patterns/process-level-isolation]] · pattern
