---
title: 隔离模式 MOC（quick-knowledge demo）
type: moc
created: 2026-08-08
updated: 2026-08-08
tags:
  - moc/isolation
  - moc/plugin
status: active
maturity: applied
confidence: 80
relations:
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
context: 库内关于「扩展/插件隔离」的所有笔记索引
value:
  reuse: 0
  impact: 3
  uniqueness: 2
---

# 隔离模式 MOC

> 本 MOC 汇集所有关于扩展系统隔离设计的笔记。本主题是 [[04_projects/plugin-system|插件系统 v2 项目]] 的核心知识支撑。

## 原则

- [[principle/boundary-over-reuse]] · **核心原则**

## 模式

- [[pattern/process-level-isolation]] · 不可信扩展首选
- [[pattern/in-process-sandbox]] · 仅可信扩展；与 process-level 互斥

## 经验

### 失败教训
- [[experience/2024-plugin-sandbox-escape]] · ⚠ failure · 沙箱逃逸事故

### 对照
- [[experience/2023-mid-team-microfrontend-overhead]] · 类似过度优化失败（前端架构）

## 决策

- [[04_projects/bi-engine/decisions/2024-02-isolation-choice|BI 引擎 Decision 001]] · archived · 派生 experience

## 项目

- [[04_projects/bi-engine/_readme|BI 引擎]]（已归档，2024）
- [[04_projects/plugin-system/_readme|插件系统 v2]]（active）

## 目标

- [[03_goals/learn-plugin-design/_readme|学习插件系统设计]]

## 冲突对照

> 以下笔记对在 context 不同的情况下互为 contradicts：

- [[experience/2023-mid-team-microfrontend-overhead]] vs [[experience/2023-large-team-microfrontend-success]]
  · 前者适用于 5-30 人；后者适用于 100+ 人
- [[pattern/process-level-isolation]] vs [[pattern/in-process-sandbox]]
  · 前者用于不可信；后者仅用于可信
