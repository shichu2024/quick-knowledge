---
title: 2023 中型团队微前端落地过重（3 个项目观察）
type: experience
created: 2023-11-10
updated: 2026-08-08
tags:
  - experience/lesson-architecture
  - experience/frontend
status: active
maturity: applied
confidence: 80
relations:
  supports:
    - "[[belief/micro-frontend-default]]"
  contradicts: []
  evolves: []
  supersedes: []
context: 3 个 8-25 人团队的项目，2022-2023 期间落地 micro-frontend（模块联邦/single-spa）
value:
  reuse: 0
  impact: 4
  uniqueness: 3
event_date: 2023-11-01
outcome: mixed
---

# 2023 中型团队微前端落地过重（3 个项目观察）

## 背景

观察 3 个中型团队（8 人 / 15 人 / 25 人）在 2022-2023 期间落地的微前端项目：A 电商后台（module federation）、B 内容平台（single-spa）、C 内部 CRM（自研 iframe）。

## 事件经过

- A 团队：3 个子应用独立部署，6 个月内公共依赖（设计系统）升级需要 4 次协调
- B 团队：1 个团队负责壳 + 2 个子应用，每次路由变更需三方同步
- C 团队：iframe 方案通信成本高，子应用加载体验差

## 结果

**mixed**：
- 期望的"独立部署"收益达成 60%（发布耦合降低）
- 但公共依赖升级成本 +3 倍
- A 团队 2024-Q1 拆回 monorepo + 内部包

## 教训（lesson）

对中型团队，微前端引入的协调成本通常大于并行收益。在团队 < 30 人时，模块化单体 + 内部包通常更务实。

## 可抽象的 principle/pattern

- 候选 belief：→ 已升格为 [[belief/micro-frontend-default]]（待验证）

## 适用范围

- 适用于：5-30 人中型团队的前端架构决策
- 不适用于：> 100 人的多团队组织（参考 [[experience/2023-large-team-microfrontend-success]]）

## 相关经验

- [[experience/2024-plugin-sandbox-escape]] · 类似「过度优化非核心维度」的失败
- [[experience/2023-large-team-microfrontend-success]] · 反例，大团队场景
