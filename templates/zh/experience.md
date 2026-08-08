<!--
模板：experience 经历教训（中文 · v0.3）
用途：具体历史事件/教训。无 domain，写入 principles/experiences/。
关键：通常由 quick-kb-project 在 archive 时从 Decision Ledger 的 lesson 字段自动派生。
真相源：references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§6.4/§8.4
-->
---
title: {{事件一句话 · 含时间/项目}}
type: experience
created: {{date}}              # 通常为事件发生日期或项目归档日期
updated: {{date}}
tags:
  - experience/{{topic}}
  - {{secondary-tag}}          # 如 lesson/security、lesson/performance
status: active
maturity: applied              # 经验已应用（或 applied→teachable）
confidence: 80                 # 亲历通常高置信
relations:
  supports: []                 # 该经验支撑的 principle/pattern
  contradicts: []              # 与其他 experience 冲突（不同 context）
  evolves: []
  supersedes: []
context: {{事件背景：团队规模、阶段、技术栈、约束}}
value:
  reuse: 0                     # experience reuse 通常较高（被 advisor 反复召回）
  impact: 4                    # 失败教训 impact 通常更高
  uniqueness: 4
source:
  - note: "[[{{源 Decision Ledger}}]]"   # 派生自哪条决策
derived_from: "[[{{源 Decision Ledger}}]]"  # v0.3 派生关系字段
# 不写 domain（认知资产横切）
event_date: {{事件发生日期}}    # 可选 · 与 created 区分
outcome: success | failure | mixed   # 结果类型 · failure 在 memory-agent 召回时加权 ×1.2
---

# {{事件一句话}}

## 背景

{{事件发生的上下文 · 团队、阶段、约束}}

## 事件经过

{{时间线 · 关键决策点 · 转折点}}

## 结果

{{结果描述 · 失败/成功/混合}}

## 教训（lesson）

> 派生自 [[{{源 Decision Ledger}}]] 的 lesson 字段

{{一句话可复用的教训 · 这是本笔记的核心}}

## 可抽象的 principle/pattern

- 候选 principle：{{是否可升格}}
- 候选 pattern：{{是否可抽象}}
- → 升格时建立 wikilink 并标 relations.evolves

## 适用范围

{{context 详述 · 何时不适用}}

## 相关经验

- [[相关 experience]]（可对比）

## 待追踪

- [ ] 下次类似场景是否复用此教训？
