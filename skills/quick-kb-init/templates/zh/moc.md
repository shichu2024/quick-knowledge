---
title: {{domain}} · MOC
type: moc                              # required
created: {{date}}                      # required
updated: {{date}}                      # required
tags:                                  # required
  - moc/{{domain}}
status: active                         # required
domain: {{domain}}                     # required · 此 MOC 所属领域
relations:                             # required 结构 · MOC 与领域笔记的关系
  supports: []                         #   通常留空（MOC 是聚合，不"支撑"）
  contradicts: []
  evolves: []                          #   由旧 MOC 演化（如重新聚类后）
  supersedes: []                       #   取代了旧 MOC
value:
  reuse: 0                             #   MOC 通常 reuse 较高（被多次引用）
---

<!--
模板：MOC 主题索引（中文 · v0.2）
用途：领域/专题索引页，由 quick-kb-connect 写入 06_wiki/mocs/<domain>-moc.md。
特性：quick-kb-manager-agent.build_moc 按标签共现 + wikilink 图谱聚类生成；用户可手动调整。
真相源：references/frontmatter-v0.2.md · docs/DESIGN.md §6 · docs/SKILLS_SPEC.md §4
-->

# {{domain}} · 主题索引

> 由 quick-kb-connect 调用 quick-kb-manager-agent.build_moc 生成。手动调整后下次 connect 保留人工修订（diff merge）。

## 主题聚类 1 · {{topic-1}}

- [[{{note-1}}]]
- [[{{note-2}}]]

## 主题聚类 2 · {{topic-2}}

- [[{{note-3}}]]

## 待补充

- [ ] {{quick-kb-manager-agent 检测到的缺口，但暂无对应笔记}}
- [ ]

## 相关 MOC

- [[{{related-moc}}]]
