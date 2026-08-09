---
title: 原子笔记原则
type: concept
created: 2026-08-07
updated: 2026-08-08
tags:
  - kb/method
  - eng/note-taking
status: active
domain: general
confidence: 80
source:
  - note: "[[05_outputs/daily/2026/08/2026-08-07]]"
---

# 原子笔记原则

## 核心定义

一条笔记只表达一个独立观点。多观点素材在 ingest 阶段拆分为多条原子笔记，每条聚焦单一概念。

## 为什么有用

- **可复用**：原子笔记可被多个上层结构（MOC、项目、目标）引用
- **可追溯**：单一观点便于审查来源与置信度
- **可演化**：观点变化时只更新一条，不污染其他笔记
- **可召回**：检索时精准命中，而非命中一个"什么都谈一点"的长笔记

## 关键组成

- 一笔记一观点（concept / principle / belief / pattern / experience）
- 自包含：脱离上下文也能理解
- 命名清晰：标题直接表达观点
- 双向连接：通过 wikilink 与相关笔记建立关系

## 应用场景

- 任何 ingest 流程的默认行为
- 写作前先把素材原子化
- 知识 review 时检查「这条笔记是否塞了多个观点」

## 示例

反面：

```markdown
# RAG 与 Agent 心得
RAG 是检索增强生成。Agent 用工具调用。今天用了 LangChain。
```

正面：拆为三条 → [[rag-architecture]] / [[agent-tool-use]] / [[01_resources/repos/langchain-intro|LangChain 简介]]

## 关联知识

- [[rag-architecture]]
- [[agent-tool-use]]

## 待验证

- [ ] 是否所有 type 都需要原子化（resource 可适当放宽？）
