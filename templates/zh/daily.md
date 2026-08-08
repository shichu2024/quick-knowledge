<!--
模板：daily 日志（中文 · v0.2）
用途：每日日志，由 quick-kb-daily 写入 outputs/daily/YYYY/MM/YYYY-MM-DD.md。
特性：描述不足时 AI 反问补充（最多 2 轮）；自动识别已有笔记标题生成 wikilinks。
真相源：references/frontmatter-v0.2.md · docs/DESIGN.md §6/§8 · docs/SKILLS_SPEC.md §8
注意：daily 属文档型笔记，无 maturity；但仍有 relations/value 结构。
-->
---
title: {{YYYY-MM-DD}} 日志             # required
type: daily                            # required
created: {{date}}                      # required
updated: {{date}}                      # required
tags:                                  # required
  - daily
status: active                         # required
domain:                                # optional · 日志通常无领域
relations:                             # required 结构 · 日志关联其他笔记
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
value:
  reuse: 0
---

# {{YYYY-MM-DD}}

## 做了什么

- {{开会/编码/沟通/... · 一句话一行 · 笼统时 AI 会反问}}

## 学到什么

- {{今天的新认知 · 可关联到 concept 笔记 [[...]]}}

## 想法

- {{灵感/观察 · 值得 capture 的会被提示}}

## 卡点

- {{阻塞/困惑/待解决 · 关联到 project 或 goal}}

## 待入库

> AI 检测到以下内容值得单独入库，是否调用 quick-kb-capture？

- [ ] {{候选想法 1}}
- [ ] {{候选想法 2}}

---

<!-- 反问记录（最多 2 轮）：
     Q1: {{AI 第 1 轮反问}}
     A1: {{用户回答}}
     Q2: {{AI 第 2 轮反问（如有）}}
     A2: {{用户回答}}
-->
