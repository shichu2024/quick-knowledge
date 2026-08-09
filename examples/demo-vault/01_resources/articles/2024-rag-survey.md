---
title: 2024 RAG 综述
type: resource
created: 2026-08-08
updated: 2026-08-08
tags:
  - articles/ai
  - ai/rag
status: active
domain: ai-engineering
confidence: 40
source:
  - url: https://example.com/rag-survey
  - author: "Example Research Group"
  - published: 2024-09-01
  - note: "[[00_inbox/clips/20260808-1000-rag-article]]"
---

# 2024 RAG 综述

## 一句话概括

一篇系统梳理 RAG 架构演进的综述文章，覆盖 Naive RAG → Advanced RAG → Modular RAG 三代。

## 关键观点

1. **三代演进**：Naive（索引-检索-生成）→ Advanced（多路召回 + rerank）→ Modular（检索器/路由器/生成器可组合）
2. **检索质量上限决定生成质量**：再好的 LLM 也救不回错的召回
3. **微调 vs RAG 不是二选一**：微调适合风格/格式，RAG 适合事实/知识

## 我为什么收藏

作为 [[rag-architecture]] 概念笔记的来源依据，方便日后回查原始综述。

## 关键摘录

> "Retrieval quality is the ceiling of generation quality; no LLM can recover from a wrong retrieval."

## 相关笔记

- [[rag-architecture]]
- [[vector-database]]

## 待行动

- [ ] 实测 Modular RAG 的 routing 策略
