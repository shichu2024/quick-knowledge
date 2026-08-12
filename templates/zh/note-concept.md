<!--
模板：concept 笔记（中文 · v0.2）
用途：记录一个概念、原理或心智模型。Ingest 后写入 02_areas/<domain>/。
填充：由 quick-kb-ingest（接 research-agent）自动填充；用户可手动修订。
真相源：references/frontmatter-v0.2.md · docs/DESIGN.md §6/§8.3
-->
---
title: {{title}}                       # required
type: concept                          # required
created: {{date}}                      # required · YYYY-MM-DD
updated: {{date}}                      # required
tags:                                  # required · 受控标签 domain/topic
  - {{domain}}/{{topic}}
status: active                         # required · inbox/draft/active/done/cancelled/archived
domain: {{domain}}                     # optional · 可含 "/" 表达嵌套（如 programming/python），由 ingest 按 kb.config.yaml.domain_taxonomy 决定
confidence: 50                         # optional · 0-100 · 单源40/多源60+/一手80+
relations:                             # required 结构 · 类型化关系（DESIGN §6.7）
  supports:                            #   本笔记支持/被某笔记支撑（对称）
    - "[[{{相关概念}}]]"
  contradicts: []                      #   与之冲突（上下文相关，非对错）
  evolves: []                          #   由某笔记演化而来（有向）
  supersedes: []                       #   取代了某条过期笔记（有向）
context: {{适用上下文 · 自由文本 · 可选}}   # optional · DESIGN §6.8
value:                                 # required 结构 · v0.2 仅 reuse
  reuse: 0                             #   自动 · 入链+推荐+查询命中；ingest 时初值 0
source:                                # optional
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
