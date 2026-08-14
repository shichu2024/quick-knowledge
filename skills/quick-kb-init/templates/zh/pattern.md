<!--
模板：pattern 可复用解决模式（中文 · v0.3）
用途：从多次实践中抽象出的可复用方案。无 domain，写入 07_principles/patterns/。
真相源：references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§6.4
-->
---
title: {{模式名称}}
type: pattern
created: {{date}}
updated: {{date}}
tags:
  - pattern/{{topic}}
status: active
maturity: applied              # pattern 通常 ≥ applied（已被多次应用）
confidence: 75
relations:
  supports: []                 # 支撑该模式的 experience
  contradicts: []              # 对立模式（anti-pattern 或不同 context）
  evolves: []                  # 由早期模式演化
  supersedes: []               # 取代旧模式
context: {{适用情境：问题类型、约束条件}}
value:
  reuse: 0                     # pattern 通常 reuse 较高
  impact: 4
  uniqueness: 3
---

# {{模式名称}}

## 解决什么问题

{{这一模式针对哪类问题 · 触发条件}}

## 模式描述

{{结构化描述：参与角色、流程、关键决策点}}

## 关键步骤

1. {{步骤 1}}
2. {{步骤 2}}
3. {{步骤 3}}

## 适用条件

- {{条件 1 · 必须满足}}
- {{条件 2 · 加分项}}

## 反模式（不要这样用）

- {{反例 1 · 会导致 ...}}

## 已应用案例

- [[project-1]] · {{应用细节 · 结果如何}}
- [[project-2]] · {{应用细节}}

## 相关模式

- [[相关 pattern]]（可组合 / 互斥）
- [[anti-pattern]]（如有 → contradicts）

## 待抽象

- [ ] {{是否还有更通用的抽象层？}}
