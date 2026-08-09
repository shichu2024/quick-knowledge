---
title: 边界管理优先于组件复用
type: principle
created: 2026-08-08
updated: 2026-08-08
tags:
  - principle/engineering
status: active
maturity: validated
confidence: 85
relations:
  supports:
    - "[[experience/2024-plugin-sandbox-escape]]"
    - "[[pattern/process-level-isolation]]"
  contradicts: []
  evolves: []
  supersedes: []
context: 设计内部工具的扩展点时；当第三方/不可信代码要进入主进程时尤其适用
value:
  reuse: 0
  impact: 5
  uniqueness: 4
---

# 边界管理优先于组件复用

## 原则陈述

当一个系统需要支持扩展/插件时，先定义清晰的边界契约（接口/进程/数据流），再考虑复用既有组件。

## 为什么持有

从 [[experience/2024-plugin-sandbox-escape]] 提炼：早期 BI 引擎插件直接复用宿主对象模型，导致沙箱逃逸；事后回看，边界契约的缺失是根因，组件复用只是表象优化。

## 适用范围

- 内部工具要做插件体系 → 强适用
- 团队 < 5 人的小项目 → 弱适用（复用优先）
- 第三方不可信代码 → 必须适用

## 关键推论

- 进程级隔离优于进程内沙箱（对不可信代码）
- 接口 schema 版本化是必须的
- 性能损失换隔离边界是值得的

## 相关经验

- [[experience/2024-plugin-sandbox-escape]] · 直接教训
- [[pattern/process-level-isolation]] · 由此原则抽象出的模式

## 待验证

- [ ] 是否对内部可信团队的插件也可降低门槛？

## 已应用

- [[projects/plugin-system/_readme|插件系统项目]] · 进程级隔离方案选型
