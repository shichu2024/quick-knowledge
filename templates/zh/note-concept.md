<!--
模板：concept 笔记（中文 · v0.1）
用途：记录一个概念、原理或心智模型。Ingest 后写入 areas/<domain>/。
填充：由 quick-kb-ingest 自动填充占位符；用户可手动修订。
真相源：references/frontmatter-v0.1.md · docs/DESIGN.md §6/§8.3
-->
---
title: {{title}}                       # required · 笔记标题
type: concept                          # required · 固定 concept
created: {{date}}                      # required · YYYY-MM-DD
updated: {{date}}                      # required · YYYY-MM-DD
tags:                                  # required · 受控标签，domain/topic 形式
  - {{domain}}/{{topic}}
status: active                         # required · inbox/draft/active/done
domain: {{domain}}                     # optional · 对应 areas/<domain>/
confidence: 50                         # optional · 0-100 · 单源40/多源60+/一手80+
source:                                # optional · 原始来源
  - note: "[[{{inbox原始素材wikilink}}]]"
  # - url: https://...
---

# {{title}}

## 核心定义

{{一句话说清这个概念是什么}}

## 为什么有用

{{解决了什么问题}}

## 关键组成

-

## 应用场景

-

## 示例

{{内联一个具体例子，便于回忆}}

## 关联知识

- [[相关概念]]

## 待验证

- [ ] {{若存在尚未确认的结论，记在这里，由 review 跟踪}}
