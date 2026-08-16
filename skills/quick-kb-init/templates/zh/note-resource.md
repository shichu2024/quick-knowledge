<!--
模板：resource 笔记（中文 · v0.2）
用途：外部资源摘要（文章、书、课程、开源项目等）。Ingest 后写入 01_resources/<category>/。
区别：concept 是"我的理解"，resource 是"别人写的东西的摘要"。
真相源：references/frontmatter-v0.2.md · docs/DESIGN.md §6/§8
-->
---
title: {{资源标题}}                     # required
type: resource                         # required
created: {{date}}                      # required
updated: {{date}}                      # required
tags:                                  # required
  - {{category}}/{{topic}}             #   category ∈ articles/books/courses/repos
status: active                         # required
domain: {{domain}}                     # optional
confidence: 40                         # optional · 单源默认 40；交叉验证后提升
relations:                             # required 结构
  supports: []                         #   本 resource 支撑了哪些 concept
  contradicts: []                      #   与哪些 resource 冲突（如同主题不同结论）
  evolves: []                          #   由早期版本演化而来
  supersedes: []                       #   取代了过期的 resource
context: {{适用情境 · 可选}}
value:
  reuse: 0
source:                                # optional · 但 resource 强烈建议填 · object 格式（v1.9.3 对齐 schema）
  url: {{原始链接}}
  author: "{{作者/出处}}"
  published: {{发表日期}}
  note: "[[{{inbox原始素材wikilink}}]]"
---

# {{资源标题}}

## 一句话概括

{{这篇文章/这本书/这个项目讲了什么}}

## 关键观点

1. {{观点 1 · 用自己的话复述，不是摘抄}}
2. {{观点 2}}
3. {{观点 3}}

## 我为什么收藏

{{对我当前的项目/目标/认知有什么用}}

## 关键摘录

> {{值得反复回看的一句话/一段}}

## 相关笔记

- [[相关 concept]]
- [[相关 project/goal]]

## 待行动

- [ ] {{若资源触发具体行动，记在这里}}
