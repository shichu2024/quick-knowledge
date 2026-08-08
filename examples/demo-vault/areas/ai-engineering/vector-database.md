---
title: 向量数据库
type: concept
created: 2026-08-08
updated: 2026-08-08
tags:
  - ai/rag
  - eng/storage
status: active
domain: ai-engineering
confidence: 60
source:
  - note: "[[inbox/clips/20260808-1000-rag-article]]"
---

# 向量数据库

## 核心定义

专门存储与检索高维向量的数据库，核心能力是 ANN（Approximate Nearest Neighbor）搜索 —— 给定 query 向量，快速找到最相似的 top-k。

## 为什么有用

传统数据库基于精确匹配（B-tree），无法处理「语义相似」。向量库用 HNSW / IVF 等索引算法把检索复杂度从 O(n) 降到 O(log n) 级别。

## 关键组成

| 组成 | 说明 |
|------|------|
| 索引算法 | HNSW（图）/ IVF（聚类）/ LSH（哈希） |
| 距离度量 | cosine / L2 / dot product |
| 元数据过滤 | 标签、时间、来源等 |
| 持久化 | 内存 / 磁盘 / 混合 |

## 应用场景

- RAG 中的知识检索
- 推荐系统的物品召回
- 图像/音频相似度搜索
- 去重与聚类

## 示例

主流选型对比（截至 2026）：

| 类型 | 代表 | 适用 |
|------|------|------|
| 专用 | Pinecone / Weaviate | 大规模、纯检索 |
| 混合 | pgvector / Milvus | 业务数据 + 向量 |
| 内嵌 | Chroma / SQLite-vss | 原型/小规模 |

## 关联知识

- [[rag-architecture]]
- [[resources/articles/2024-rag-survey|2024 RAG 综述]]

## 待验证

- [ ] pgvector 在千万级向量下的性能表现
