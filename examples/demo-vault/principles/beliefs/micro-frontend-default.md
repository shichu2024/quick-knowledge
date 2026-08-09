---
title: 我倾向认为微前端在多数中型团队是过度设计
type: belief
created: 2026-08-08
updated: 2026-08-08
tags:
  - belief/frontend
  - belief/architecture
status: active
maturity: captured
confidence: 40
relations:
  supports: []
  contradicts:
    - "[[experience/2023-large-team-microfrontend-success]]"
  evolves: []
  supersedes: []
context: 团队 5-30 人的中型团队，前端项目复杂度中等
value:
  reuse: 0
  impact: 3
  uniqueness: 3
---

# 我倾向认为微前端在多数中型团队是过度设计

## 假设陈述

我认为，对 5-30 人的前端团队，微前端（模块联邦 / single-spa 等）引入的运维复杂度通常超过其带来的独立性收益。模块化单体（Module Federation 的反模式 / monorepo + 内部包）是更务实的选择。

## 为什么这么认为

- 在 [[experience/2023-mid-team-microfrontend-overhead]] 中观察到：3 个项目落地 micro-frontend，独立部署收益 < 公共依赖升级成本
- 微前端的核心理由（独立团队并行）在 < 30 人团队几乎不成立

## 验证方式

- [ ] 收集 ≥ 5 个中型团队微前端落地的 actual 数据（团队规模、迭代速度、运维成本）
- [ ] 反例搜索：是否有中型团队通过微前端显著受益的案例？

## 当前证据

### 支持
- [[experience/2023-mid-team-microfrontend-overhead]]

### 反对
- [[experience/2023-large-team-microfrontend-success]] · 大团队场景，不直接反驳中型假设但提示边界条件

## 待解决

- [ ] 「中型团队」的精确阈值（5-30 还是 5-50？）

## 升格路径

- 验证通过 + 可量化阈值 → 升格为 [[principle/微前端适用边界]]
- 被反证推翻 → 降为 `maturity: deprecated` + 强化 contradicts
