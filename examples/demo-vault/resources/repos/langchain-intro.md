---
title: LangChain 简介
type: resource
created: 2026-08-07
updated: 2026-08-07
tags:
  - repos/framework
  - ai/agent
status: active
domain: ai-engineering
confidence: 40
source:
  - url: https://github.com/langchain-ai/langchain
  - author: "LangChain AI"
---

# LangChain 简介

## 一句话概括

构建 LLM 应用的开源框架，提供 prompt/chain/agent/memory/document loader 等抽象，是早期 RAG/Agent 原型的事实标准。

## 关键观点

1. **Chain 抽象**：把 prompt + LLM + parser 串成可复用流水线
2. **Agent 抽象**：基于 tool calling 的多步推理循环
3. **生态丰富**：100+ 文档加载器、向量库集成、工具集成
4. **代价**：抽象层过厚，调试与定制成本高

## 我为什么收藏

作为 [[agent-tool-use]] 的实现参考，理解主流框架如何处理工具描述与选择。

## 关键摘录

> "LangChain aims to make it easy to build applications that leverage language models."

## 相关笔记

- [[agent-tool-use]]
- [[rag-architecture]]

## 待行动

- [ ] 评估是否迁移到更轻量的替代（如 LlamaIndex / 自研）
