---
title: RAG 分块策略想法
captured_at: 2026-08-07T09:30
capture_type: idea
source:
  - person: "自己的胡思乱想"
suggested_tags:
  - ai/rag
  - eng/architecture
---

# RAG 分块策略想法

如果按语义切分而非固定长度，召回精度应该会高很多。固定 512 token 经常把一个完整论点切成两半。

具体可以试试：
- 先用 heading 切粗块
- 再用语义相似度合并相邻小块
- 长表格整体保留不切

值得找几篇文章验证一下，可能写成一条 concept。

## 可能的下一步

- [ ] 值得展开 → 调用 `quick-kb-ingest` 转为正式 concept（待处理）
- [ ] 暂存，待后续判断
