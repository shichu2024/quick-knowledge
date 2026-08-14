<!--
模板：project 项目（中文 · v0.3）
用途：项目主笔记（04_projects/<slug>/_readme.md），含经验复用建议和 Decision Ledger 索引。
真相源：references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§8.4 · docs/AGENTS_SPEC.md §4
-->
---
title: {{项目名称}}
type: project
created: {{date}}
updated: {{date}}
tags:
  - project/{{slug}}
status: active                 # active → done（完成）/ cancelled（取消）/ archived（归档）
maturity: applied              # 项目运行中即 applied，归档时为 teachable
confidence: 60
deadline: {{YYYY-MM-DD}}       # 可选 · 项目交付日期
domain: {{domain}}             # 可选
relations:
  supports: []                 # 支撑的目标 goal
  contradicts: []
  evolves: []
  supersedes: []
context: {{项目情境：背景、约束、目标用户}}
value:
  reuse: 0                     # 归档后由 normalize/derive 贡献
  impact: 4
  uniqueness: 3
# project 不写 outcome；归档时驱动 Decision Ledger 派生 experience
---

# {{项目名称}}

## 目标与背景

{{项目要解决什么问题 · 与哪个 [[goal]] 关联}}

## 范围

- 包含：{{in-scope}}
- 不包含：{{out-of-scope}}

## 经验复用建议

> 由 quick-kb-project create 调 quick-kb-memory-agent 生成；按 AGENTS_SPEC §3.5 排序

### 高相关 experience
- [[experience/xxx]] · 相关点：{{}}
- [[experience/yyy]] · 相关点：{{}}

### 可应用 pattern
- [[pattern/xxx]] · 适用条件：{{}}

### 相关 principle
- [[principle/xxx]] · 适用性：{{}}

## 决策记录（Decision Ledger）

> 重要决策写入 decisions/ 子目录；归档时 lesson 字段派生为 experience

- [[decisions/2026-XX-XX-xxx|决策标题]]
- [[decisions/2026-XX-XX-yyy|决策标题]]

## 里程碑

- [ ] M1：{{}} · {{YYYY-MM-DD}}
- [ ] M2：{{}} · {{YYYY-MM-DD}}

## 关联笔记

- [[concept 1]]
- [[concept 2]]

## 归档清单（archive 前）

- [ ] 所有 Decision Ledger 已填写 actual + lesson
- [ ] 关键经验已派生为 experience 笔记
- [ ] status → archived，maturity → teachable

