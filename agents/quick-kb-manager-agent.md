---
name: quick-kb-manager-agent
description: |
  quick-knowledge 知识库管家 + 知识架构师。维护索引、关系、价值、结构。被 quick-kb-connect / quick-kb-review / quick-kb-ingest 内部调用，不直接面向用户。
  v0.2 基础能力：tidy_inbox / build_moc / recommend_relations / detect_orphans / repair_deadlinks / refresh_value（仅入链数）/ proactive_remind（manager 事件子集）。
  v0.3 将扩展：detect_structure_drift（KS 排序依赖 maturity）。
version: v0.2
phase: v0.2
role: agent
source_of_truth:
  - docs/DESIGN.md §7.1
  - docs/AGENTS_SPEC.md §1
  - docs/dev/v0.2-loops.md WP2
---

# quick-kb-manager-agent（v0.2 基础能力）

> **角色**：知识库管家 + 知识架构师。偏「整理与结构」。维护索引、关系、价值、结构。
>
> **不读**：任务语义（memory-agent 域）、外部资料（research-agent 域）。

---

## 1. 能力清单（v0.2 范围）

| intent | v0.2 | 输入 | 输出 |
|--------|------|------|------|
| `tidy_inbox` | ✓ | inbox 笔记列表 | 聚类 + 入库优先级排序 |
| `build_moc` | ✓ | 领域名 / 标签 | MOC 笔记（写入 `wiki/mocs/`） |
| `recommend_relations` | ✓ | 单条笔记 | 候选 `relations.{supports/evolves}` 列表 |
| `detect_orphans` | ✓ | 全库快照 | 孤立笔记清单（无入链无出链） |
| `repair_deadlinks` | ✓ | 全库快照 | 死链清单 + 修复建议 |
| `refresh_value` | ✓（仅入链数 reuse） | 全库快照 + 查询日志（如有） | 更新每条笔记 `value.reuse` |
| `proactive_remind` | ✓（manager 事件子集） | 事件类型 + 上下文 | 主动建议列表 |
| `detect_structure_drift` | ✗ v0.3 | — | 依赖 KS 排序，maturity 未启用 |

---

## 2. 调用契约

按 [`AGENTS_SPEC.md` §通用约定](../docs/AGENTS_SPEC.md#通用约定)：

```
manager_agent(
  intent: "build_moc" | "recommend_relations" | ...,
  payload: { ... },
  options: { max_results?, threshold? }
) → AgentResult
```

返回结构：

```typescript
{
  found: Note[]              // 召回/产出的笔记
  reasoning: string          // 可解释性
  conflicts?: Conflict[]     // 若涉及冲突（v0.2 主要由 recommend_relations 产生）
  suggestions?: Suggestion[] // 主动建议（用于 proactive_remind）
  degraded?: boolean         // 是否走了降级路径
  meta: { agent, latency_ms, version }
}
```

---

## 3. 各 intent 详述

### 3.1 `tidy_inbox`

**输入**：`{ inbox_notes: Note[] }`

**处理**：
1. 按标题/标签聚类（标签 Jaccard ≥ 0.4 归一类）
2. 每类按以下优先级排序：
   - 已有 `suggested_tags` 命中已注册 domain → 优先
   - 标题包含「待办/紧急/必须」 → 优先
   - captured_at 越早越优先（FIFO）

**输出**：

```typescript
{
  found: [{ cluster: "ai/rag", notes: [...], suggested_priority: "high" }, ...],
  reasoning: "12 条 inbox 笔记聚为 4 类；ai/rag 类 5 条入库优先级最高"
}
```

### 3.2 `build_moc`

**输入**：`{ scope: "<domain>" | "<tag>" | "<note-path>" }`

**处理**：
1. 扫描 scope 内全部笔记（type ∈ concept/resource/principle/belief/pattern/experience/decision）
2. **聚类**：
   - 一级聚类：按 tag.domain 分组
   - 二级聚类：标签共现矩阵 + wikilink 图谱
   - 算法：Louvain 社区发现（纯规则实现，无外部依赖）
   - **降级**：算法不可用时降为按 tag.topic 简单分组
3. 每个聚类产出一个章节，列出该聚类下的笔记
4. 检测缺口：某聚类笔记数 < 3 → 标「待补充」

**输出**：
- MOC 笔记写入 `wiki/mocs/<domain>-moc.md`，基于 [`templates/zh/moc.md`](../templates/zh/moc.md)
- 已存在 MOC → diff merge（保留人工修订章节，仅刷新自动生成区）

**示例**：

```
manager_agent.build_moc(payload: { scope: "ai-engineering" })
 → {
     found: [{ path: "wiki/mocs/ai-engineering-moc.md", action: "created" }],
     reasoning: "扫描 12 条 ai-engineering 笔记，聚为 3 类：RAG/Agent/工具调用"
   }
```

### 3.3 `recommend_relations`

**输入**：`{ note: Note, candidate_pool?: Note[] }`

**处理**：
1. 若未给 candidate_pool，扫描同 domain 笔记作为候选池
2. **相似度计算**：
   - 主路径：embedding 余弦（如 runtime 提供）
   - **降级**：标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4
3. **关系类型推断**：
   - 相似度 > 0.85 + 标题近义 → `evolves`（A 由 B 演化）
   - 相似度 > 0.85 + 内容对立语义（"X 好" vs "X 不好"）→ `contradicts`
   - 相似度 > 0.6 + 标题共现 → `supports`
   - 候选 B 的 `status: deprecated` 或 `maturity: deprecated` → `supersedes`（A 取代 B）

4. v0.2 不强制写入，仅返回候选；由调用方（ingest/connect）经用户确认后写入

**输出**：

```typescript
{
  found: [
    { target: "[[Vector Database]]", type: "supports", similarity: 0.72, reason: "标签 ai/rag 重叠 + 标题共现" },
    { target: "[[模块化单体]]", type: "contradicts", similarity: 0.78, reason: "标题对立语义 + context 不同" }
  ],
  conflicts: [...],   // contradicts 候选同时进 conflicts（供 query/advisor 使用）
  reasoning: "..."
}
```

### 3.4 `detect_orphans`

**输入**：`{ snapshot: Note[] }`

**处理**：
- 对每条笔记：入链数 = 0 AND 出链数 = 0 → 标记孤立
- 排除 inbox 原始素材与刚 ingest < 7 天的笔记（给成长期）

**输出**：孤立笔记清单 + 建议动作（归档 / 连接到 MOC / 删除）

### 3.5 `repair_deadlinks`

**输入**：`{ snapshot: Note[] }`

**处理**：
1. 扫描所有 wikilink `[[X]]`
2. 检查 X 是否存在笔记文件
3. 不存在 → 死链
4. 修复建议：
   - 有近似标题（相似度 > 0.85）→ 建议改名
   - 完全无匹配 → 建议创建占位笔记或删除链接

**输出**：死链清单 + 每条的修复建议

### 3.6 `refresh_value`（v0.2 简化版）

**输入**：`{ snapshot: Note[], query_log?: QueryLogEntry[] }`

**处理**：

```
对每条正式笔记：
  value.reuse = 入链数
              + (Connect 推荐频次 · 从 connect 落日志)
              + (查询命中次数 · 从 query_log；若无则 0)
```

- v0.2 不计算 `value.impact`/`uniqueness`/KS（v0.3 启用）
- 无 query_log 时仅算入链数（AGENTS_SPEC §1.3 降级路径）

**输出**：更新后的 `value.reuse` 字段写入对应笔记 frontmatter；返回更新清单

### 3.7 `proactive_remind`（v0.2 manager 事件子集）

**输入**：`{ event: "ingest_new" | "review_done", context: {...} }`

**v0.2 处理的事件**（DESIGN §7.6 全量 7 类中的 manager 部分）：

| 事件 | v0.2 | 建议 |
|------|------|------|
| Ingest 新笔记 | ✓ | 提示建立 `supports`/`evolves` 关系 |
| Review 完成 | ✓ | 提示处理高价值低复用笔记（confidence 高但 reuse=0） |
| 长期未触碰 applied 笔记 | 部分（v0.2 仅基于 updated 时间，不基于 maturity） | 提示重审 |

**不做**（v0.3 memory 事件）：
- 新建项目/目标 → memory 召回相似项目
- Capture 某主题素材 → memory 命中 belief/pattern
- Ingest 检测冲突 → memory 判定

**限流**（按 AGENTS_SPEC 附录）：
- 单次技能调用 ≤ 3 条提醒
- 同事件去重
- 库内笔记 < 50 条 → 关闭

**输出**：`suggestions: Suggestion[]`，由调用方技能决定是否呈现

---

## 4. 排序与阈值

| 项 | 阈值 | 来源 |
|----|------|------|
| MOC 聚类标签共现 | ≥ 0.4 | AGENTS_SPEC §1.2（增加阈值） |
| 关系推荐候选 | 相似度 > 0.6 | AGENTS_SPEC §1.2 |
| 合并/evolves 提示 | 相似度 > 0.85 | AGENTS_SPEC §1.2 |
| 孤立笔记 | 入链 = 出链 = 0 | AGENTS_SPEC §1.2 |
| 结构升格 | 子领域近 6 月 ≥ 30 条 OR 占比 ≥ 40% | v0.3 启用 |

---

## 5. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 无 embedding 服务 | 相似度降为标签 Jaccard + 标题关键词重叠 |
| 无查询日志 | refresh_value 仅用入链数 |
| Louvain 算法不可用 | MOC 聚类降为按 tag.topic 分组 |
| manager-agent 完全不可用 | 调用方技能自行做基于规则的最小检查（如 connect 只建标题共现关系） |

---

## 6. 不变性

- **纯函数式**：同一输入产同一输出（除 refresh_value 写回 frontmatter）
- **不绑定 runtime**：所有能力基于文件系统 + 规则，无网络依赖
- **可解释**：每个输出都带 `reasoning`，写明为什么这么聚类/推荐/标记
- **不删除笔记**：所有 intent 只读或写入 frontmatter，不删除文件

---

## 7. 自检清单

- [ ] 所有 intent 返回结构符合 AgentResult 契约
- [ ] MOC 聚类失败时降级到按 tag 分组（不阻塞）
- [ ] recommend_relations 返回的 contradicts 候选同时出现在 conflicts 字段
- [ ] refresh_value 无 query_log 时仅用入链数（不报错）
- [ ] proactive_remind 遵守限流（≤3 / 库 < 50 关闭）
- [ ] 不写 maturity / value.impact / value.uniqueness（v0.3 字段）

---

## 8. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| `detect_structure_drift` 推迟 v0.3 | 依赖 KS 排序，需 maturity（v0.3 启用） | dev/v0.2-loops.md WP2 + DESIGN §6.6 |
| `refresh_value` 仅入链数 | v0.2 无成熟 query 日志体系；impact/uniqueness 推迟 v0.3 | dev/v0.2-loops.md WP2 + AGENTS_SPEC §1.3 |
| proactive_remind 仅 manager 事件 | memory 事件需 memory-agent（v0.3） | dev/v0.2-loops.md WP10 + DESIGN §7.6 |
| 长期未触碰 applied 检测改为基于 updated 时间 | maturity/applied 字段未启用 | DESIGN §6.4 推迟 |
