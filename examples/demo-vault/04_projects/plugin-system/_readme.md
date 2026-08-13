---
title: "插件系统 v2（quick-knowledge demo 项目）"
type: project
created: 2026-08-07
updated: 2026-08-08
tags:
  - project/plugin-system
status: active
maturity: applied
confidence: 70
deadline: 2026-10-15
domain: ai-engineering
relations:
  supports:
    - "[[03_goals/learn-plugin-design/_readme|learn-plugin-design]]"
  contradicts: []
  evolves: []
  supersedes:
    - "[[04_projects/bi-engine/_readme|bi-engine（已归档）]]"
context: 5 人小团队，公司内部工具要支持第三方扩展；参考 2024 BI 引擎教训
value:
  reuse: 0
  impact: 4
  uniqueness: 3
---

# 插件系统 v2

## 目标与背景

为公司内部工具设计第二代插件系统。前代（[[04_projects/bi-engine|BI 引擎]]）于 2024 因沙箱逃逸事故归档。本项目目标：

- 复用 [[experience/2024-plugin-sandbox-escape]] 的教训
- 直接采用进程级隔离方案
- 支持 5 个内部团队 + 后续 3 个外部第三方接入

## 范围

- 包含：扩展 SDK / 宿主侧运行时 / capability 授权系统 / 性能监控
- 不包含：插件市场（v2 之后）

## 经验复用建议（来自 quick-kb-memory-agent）

> 由 quick-kb-project init 调 quick-kb-memory-agent（new_project_init 事件）召回

### 高相关 experience
- [[experience/2024-plugin-sandbox-escape]] · 相关点：同为内部工具插件体系，且为本项目直接前置教训
- [[experience/2023-mid-team-microfrontend-overhead]] · 相关点：5 人小团队过度设计的反面参考

### 可应用 pattern
- [[pattern/process-level-isolation]] · 适用条件：不可信第三方扩展，完全满足
- [[pattern/in-process-sandbox]] · ⚠ contradicts：本项目明确不采用

### 相关 principle
- [[principle/boundary-over-reuse]] · 适用性：直接驱动本项目选型
- [[belief/micro-frontend-default]] · 弱相关（架构方向参考）

## 决策记录（Decision Ledger）

- decisions/2026-08-isolation-choice-v2（待开）：本项目隔离方案选型（进程级 + capability）

## 里程碑

- [x] M1：架构定稿 · 2026-08-15
- [ ] M2：扩展 SDK alpha · 2026-09-01
- [ ] M3：宿主侧运行时 v0.1 · 2026-09-30
- [ ] M4：1 个内部团队接入 · 2026-10-15

## 关联笔记

- [[02_areas/ai-engineering/agent-tool-use|agent-tool-use concept]]
- [[02_areas/ai-engineering/rag-architecture|rag-architecture concept]]

## 归档清单（archive 前）

- [ ] 所有 Decision Ledger 已填写 actual + lesson
- [ ] 关键经验已派生为 experience 笔记
- [ ] status → archived，maturity → teachable
