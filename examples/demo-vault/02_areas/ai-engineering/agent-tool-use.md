---
title: Agent 工具调用
type: concept
created: 2026-08-08
updated: 2026-08-08
tags:
  - ai/agent
  - eng/architecture
status: active
domain: ai-engineering
confidence: 40
source:
  - note: "[[00_inbox/ideas/20260808-1415-observation-on-agent-tools]]"
---

# Agent 工具调用

## 核心定义

LLM Agent 通过结构化协议（如 OpenAI function calling）调用外部工具，把「语言模型」扩展为「能行动的智能体」。工具可以是检索、API 调用、代码执行等。

## 为什么有用

- LLM 本身只能生成文本，无法触达实时信息或外部操作
- 工具调用让 Agent 解决「我不知道」「我不能做」两类问题
- 是 RAG、深度搜索、自动化工作流的基础

## 关键组成

1. **工具描述**：name + description + JSON schema 参数
2. **选择策略**：LLM 基于 query 推断调哪个工具
3. **执行层**：runtime 实际调用工具，返回结果
4. **反思循环**：失败重试、多步规划

## 应用场景

- 检索型问答（RAG 即工具）
- 多步推理（搜索 → 阅读 → 总结）
- 自动化（写文件、发请求、跑测试）
- Agent-to-Agent 协作

## 示例

工具数量与选择准确率（个人观察）：

| 工具数 | 选择准确率（直觉） |
|--------|------------------|
| ≤ 5 | ~95% |
| 5-10 | ~85% |
| > 10 | 明显下降，需 rerank |

可能解法：
- 工具二级分类（retrieval / action / observation）
- retrieval agent 先筛工具
- 描述精炼到一句话

## 关联知识

- [[rag-architecture]]（RAG 是 Agent 的核心工具之一）

## 待验证

- [ ] 工具数量阈值的具体数据（需实测）
- [ ] 二级分类方案在不同场景的迁移性
