---
title: Agent 工具调用的观察
captured_at: 2026-08-08T14:15
capture_type: idea
source:
  - person: "自己的观察"
suggested_tags:
  - ai/agent
  - eng/architecture
---

# Agent 工具调用的观察

> [!info] 已入库
> - [[areas/ai-engineering/agent-tool-use]]（concept · 2026-08-08）

发现 Agent 在工具数量 >10 个时，选择准确率明显下降。可能的原因：
- 工具描述长度溢出 context
- 工具名称相似度高（search vs search_docs vs search_web）

可能解法：
- 工具二级分类（retrieval / action / observation）
- 用 retrieval agent 先筛工具，再让主 agent 调用
- 工具描述精炼到一句话

这个值得 concept 化。
