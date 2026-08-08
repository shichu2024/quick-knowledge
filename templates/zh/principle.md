<!--
模板：principle 个人原则（中文 · v0.3）
用途：跨项目方法论、价值观底线。无 domain（横切），写入 principles/principles/。
真相源：references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§6.4
-->
---
title: {{原则一句话}}
type: principle
created: {{date}}
updated: {{date}}
tags:
  - principle/{{topic}}
status: active
maturity: validated            # 原则通常 ≥ validated
confidence: 80
relations:
  supports: []                 # 支撑该原则的 experience/pattern
  contradicts: []              # 对立原则（如有 context 区分）
  evolves: []                  # 由早期 belief 演化
  supersedes: []               # 取代了旧原则
context: {{适用范围 · 自由文本}}
value:
  reuse: 0
  impact: 5                    # 原则影响通常最高
  uniqueness: 4
# 不写 domain（认知资产横切）
---

# {{原则一句话}}

## 原则陈述

{{清晰陈述这条原则 · 一句话}}

## 为什么持有

{{起源：从哪些经验中提炼 / 哪些 values 衍生}}

## 适用范围

{{context 详述：什么场景下适用、什么场景下不适用}}

## 关键推论

- {{推论 1}}
- {{推论 2}}

## 相关经验

- [[支撑 experience 1]]
- [[支撑 experience 2]]

## 待验证

- [ ] {{是否有反例？}}

## 已应用

- [[project-1]] · {{如何应用}}
- [[project-2]] · {{如何应用}}
