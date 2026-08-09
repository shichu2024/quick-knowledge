---
title: 2024 BI 引擎插件沙箱逃逸（项目归档派生）
type: experience
created: 2024-12-20
updated: 2026-08-08
tags:
  - experience/lesson-security
  - project/bi-engine
status: active
maturity: teachable
confidence: 95
relations:
  supports:
    - "[[principle/boundary-over-reuse]]"
    - "[[pattern/process-level-isolation]]"
  contradicts: []
  evolves: []
  supersedes: []
context: 8 人 BI 团队，内部工具，支持第三方插件；选了进程内 V8 隔离以省 IPC 开销
value:
  reuse: 0
  impact: 5
  uniqueness: 5
source:
  - note: "[[04_projects/bi-engine/decisions/2024-02-isolation-choice]]"
derived_from: "[[04_projects/bi-engine/decisions/2024-02-isolation-choice]]"
event_date: 2024-07-15
outcome: failure
---

# 2024 BI 引擎插件沙箱逃逸（项目归档派生）

## 背景

8 人 BI 团队的内部 BI 引擎，需支持业务方上传自定义指标计算插件。当时（2024-02）为节省 IPC 开销选了进程内 V8 isolate 沙箱。

## 事件经过

- 2024-02：Decision Ledger 记录选型，预期"V8 isolate 足够安全"
- 2024-07：业务方某插件利用 V8 内已知 CVE 完成 OOB 读，泄露宿主 token
- 2024-07：紧急回滚插件机制，3 周后改用进程级隔离（[[04_projects/bi-engine]] archive）
- 2024-12：项目归档时本 experience 由 lesson 字段派生

## 结果

- **failure**：选型决策（V8 沙箱）失败
- 直接损失：1 个客户数据泄露事件，2 周紧急重构成本
- 长期收益：提炼出 [[principle/boundary-over-reuse]] + [[pattern/process-level-isolation]]

## 教训（lesson）

> 派生自 [[04_projects/bi-engine/decisions/2024-02-isolation-choice]] 的 lesson 字段

**对不可信代码，进程级隔离的代价（30% 性能）远低于沙箱逃逸的代价（数据泄露）。** 边界契约缺失时，运行时沙箱只是延迟不可避免的失败。

## 可抽象的 principle/pattern

- ✅ 已升格 → [[principle/boundary-over-reuse]]
- ✅ 已抽象 → [[pattern/process-level-isolation]]

## 适用范围

- 适用于：所有需支持第三方/不可信扩展的系统
- 不适用于：完全可信的内部团队脚本

## 相关经验

- [[experience/2023-mid-team-microfrontend-overhead]] · 类似「过度优化非核心维度」的失败模式

## 待追踪

- [x] 下次插件系统选型时是否复用此教训？（[[04_projects/plugin-system]] 已复用）
