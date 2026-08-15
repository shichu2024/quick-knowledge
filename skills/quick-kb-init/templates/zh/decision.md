<!--
模板：Decision Ledger（中文 · v0.3）
用途：方案决策记录（ADR 风格强化版）。由 quick-kb-project 在 init/archive 时引导生成；归档时 lesson 自动派生为 experience 笔记。
真相源：references/frontmatter-v0.3.md · docs/DESIGN.md §8.4 · docs/SKILLS_SPEC.md §10
-->
---
title: 决策 {{编号}}：{{决策标题}}
type: decision
created: {{date}}
updated: {{date}}
tags:
  - decision/{{project-slug}}
  - {{topic}}
status: active                # active → done（决策落地）/ superseded（被新决策取代，配 relations.supersedes）
maturity: understood          # decision 仍属知识型，但 v0.3 起可选；通常 understood 起步
confidence: 60                # 决策依据的置信度
relations:
  supports: []
  contradicts: []             # 与其他决策冲突时双向声明
  evolves: []                 # 由早期决策演化
  supersedes: []              # 取代了旧决策
context: {{决策时的上下文：团队/阶段/约束}}
value:
  reuse: 0
  impact: 4                   # 决策影响通常较高
source: []
project: "[[{{project README}}]]"   # 所属项目 wikilink
---

# 决策 {{编号}}：{{决策标题}}

## Problem · 问题

{{要解决的决策问题 · 1-2 段}}

## Options · 候选方案

1. **{{方案 A}}** · {{一句话描述}}
   - 优点：...
   - 缺点：...
2. **{{方案 B}}** · {{一句话描述}}
   - 优点：...
   - 缺点：...
3. **{{方案 C}}** · {{一句话描述}}
   - 优点：...
   - 缺点：...

## Chosen · 选定

**{{方案 X}}**

## Reason · 理由

{{为什么选这个 · 引用相关 principle 或 experience}}
- 基于 [[{{某 principle}}]]
- 历史经验 [[{{某 experience}}]]

## Rejected · 否决原因

- {{方案 A}}：{{为什么否决}}
- {{方案 C}}：{{为什么否决}}

## Expected · 预期结果

{{决策落地后期望的结果 · 可量化指标更好 · init 时填，archive 时与 actual 对照}}

- 指标 1：{{预期值}}
- 指标 2：{{预期值}}

## Actual · 实际结果

> 项目归档（archive）时补全

- 指标 1：{{实际值}}
- 指标 2：{{实际值}}
- 偏差：{{对照 Expected 的差距}}

## Lesson · 教训

> 项目归档时由 quick-kb-project 提取，自动派生为独立 experience 笔记到 `07_principles/experiences/`

{{一句话提炼可复用的教训 · 例：「插件体系必须进程级隔离，性能次要」}}

派生：[[{{experience 笔记 wikilink}}]]
