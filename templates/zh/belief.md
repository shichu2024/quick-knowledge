<!--
模板：belief 待验证假设（中文 · v0.3）
用途：个人假设/判断，尚未充分验证。无 domain，写入 principles/beliefs/。
真相源：references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§6.4
-->
---
title: {{假设一句话}}
type: belief
created: {{date}}
updated: {{date}}
tags:
  - belief/{{topic}}
status: active
maturity: captured             # belief 通常 captured / understood，验证后转 principle 或 pattern
confidence: 40                 # 待验证，置信度偏低
relations:
  supports: []                 # 支撑该假设的证据
  contradicts: []              # 反证
  evolves: []                  # 若验证后升格为 principle/pattern
  supersedes: []
context: {{假设的适用情境}}
value:
  reuse: 0
  impact: 3                    # 假设影响中等
  uniqueness: 3
---

# {{假设一句话}}

## 假设陈述

{{清晰陈述你的假设 · 通常含「我认为 / 我倾向于」}}

## 为什么这么认为

{{直觉来源 · 经验碎片 · 观察到的现象}}

## 验证方式

- [ ] {{如何能验证这个假设 · 可量化}}
- [ ] {{反例搜索：什么情况下假设不成立}}

## 当前证据

### 支持
- [[experience/pattern/resource]]

### 反对
- [[experience/pattern/resource]]（若有 → 应建立 contradicts）

## 待解决

- [ ] ...

## 升格路径

- 验证通过且可抽象 → 升格为 [[相关 principle]] 或 [[相关 pattern]]（maturity → validated/applied）
- 被反证推翻 → 降为 `maturity: deprecated` + 建立 contradicts
