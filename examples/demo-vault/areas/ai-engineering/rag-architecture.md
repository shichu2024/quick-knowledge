---
title: RAG 架构设计
type: concept
created: 2026-08-08
updated: 2026-08-08
tags:
  - ai/rag
  - eng/architecture
status: active
domain: ai-engineering
confidence: 60
source:
  - note: "[[inbox/clips/20260808-1000-rag-article]]"
  - url: https://example.com/rag-guide
---

# RAG 架构设计

## 核心定义

RAG（Retrieval-Augmented Generation）是把外部知识检索与 LLM 生成结合的架构模式，让模型基于私有/最新数据回答，避免幻觉与知识截止问题。

## 为什么有用

- LLM 知识有截止日期，无法回答最新信息
- 私有数据未进入训练集
- 直接微调成本高、更新慢
- RAG 把「知识」从模型权重搬到外部向量库，更新成本低

## 关键组成

1. **索引管线**：文档加载 → 切分 → 向量化 → 写入向量库
2. **检索器**：query 向量化 → ANN 检索 → top-k 召回
3. **生成器**：召回片段拼 prompt → LLM 生成答案
4. **reranker**（可选）：cross-encoder 对召回结果重排

## 应用场景

- 企业知识库问答
- 代码助手（检索代码仓库）
- 长文档智能问答
- 客服系统（结合产品文档）

## 示例

用户问「我们公司差旅政策是什么」：
1. query → vector
2. 从内部 policy 向量库召回 top-5 片段
3. rerank 取 top-3
4. 拼 prompt：「根据以下资料回答：[片段] 问题：差旅政策？」
5. LLM 生成带引用的答案

## 关联知识

- [[vector-database]]
- [[resources/articles/2024-rag-survey|2024 RAG 综述]]
- [[resources/repos/langchain-intro|LangChain 简介]]

## 待验证

- [ ] 多模态 RAG 的具体实现细节（v0.1 假设单模态）
