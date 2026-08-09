---
title: 2023 大团队（120 人）微前端落地成功
type: experience
created: 2023-12-15
updated: 2026-08-08
tags:
  - experience/lesson-architecture
  - experience/frontend
status: active
maturity: applied
confidence: 80
relations:
  supports: []
  contradicts:
    - "[[experience/2023-mid-team-microfrontend-overhead]]"
    - "[[belief/micro-frontend-default]]"
  evolves: []
  supersedes: []
context: 120 人前端组织，6 个子产品线，跨时区协作
value:
  reuse: 0
  impact: 4
  uniqueness: 4
event_date: 2023-12-01
outcome: success
---

# 2023 大团队（120 人）微前端落地成功

> ⚠ 与 [[belief/micro-frontend-default]] 部分冲突，但 context 不同（团队规模）。

## 背景

120 人的前端组织，6 个子产品线分布在 3 个时区。2023-Q2 落地 micro-frontend（自研 shell + module federation）。

## 事件经过

- 各产品线独立部署 → 释放跨时区协调压力
- 公共依赖通过设计 token + 主题包解耦
- 引入版本兼容矩阵工具

## 结果

**success**：
- 跨产品线发布协调次数下降 70%
- 各团队迭代速度 +25%
- 公共依赖升级成本可控（自动化工具支撑）

## 教训（lesson）

在多团队（> 100 人）、跨时区、子产品差异大的场景，微前端的协调收益显著超过其引入的复杂度。但前提是配套工具（版本兼容、主题解耦、监控）到位。

## 可抽象的 principle/pattern

- 候选 principle：「团队规模是架构选型的边界条件」→ 待进一步验证

## 适用范围

- 适用于：> 100 人组织，多产品线，跨时区
- 不适用于：< 30 人团队（参考 [[experience/2023-mid-team-microfrontend-overhead]]）

## 相关经验

- [[experience/2023-mid-team-microfrontend-overhead]] · 与本条 contradicts，但 context 不同
- [[belief/micro-frontend-default]] · 待验证假设的边界条件由本案例提供
