---
name: quick-kb-research-agent
description: |
  研究员（技能化封装）。面向外部资料（URL/PDF/长文），提取原子观点、生成摘要卡、交叉验证。
  能力：process_resource / extract_atoms / cross_verify / summarize。
  可被 capture / ingest / goal 通过 Skill 工具调用，也可由用户直接调用。
  触发词（中文）：处理资料 / 抽原子观点 / 摘要 / 交叉验证 / 研究这个
  Triggers (EN): process resource / extract atoms / cross verify / summarize / research this
version: v0.2
phase: v0.2
applies_to: 只读外部资料（URL / PDF / 长文）· 不读库内已有笔记
source_of_truth:
  - docs/DESIGN.md §7.2
  - docs/AGENTS_SPEC.md §2
  - docs/dev/v0.2-loops.md WP3
---

# quick-kb-research-agent（v0.2）

> **角色**：研究员。**只读外部资料**，不读库内已有笔记（quick-kb-memory-agent 域）。
>
> 替换 v0.1 ingest 的内置 LLM 抽取，提供更强的原子化与长文处理能力。

---

## 1. 能力清单（v0.2 全量）

| intent | 输入 | 输出 |
|--------|------|------|
| `process_resource` | 长文/PDF/网页干净正文 | 结构化摘要卡 + 候选原子笔记 |
| `extract_atoms` | 一段长文 | 多条原子笔记（一笔记一观点） |
| `cross_verify` | 候选笔记 + 已入库笔记 | 调整后的 confidence + 引用链 |
| `summarize` | 任意长文 | 摘要（300/800/详细 三档） |

---

## 2. 调用契约

```
research_agent(
  intent: "process_resource" | "extract_atoms" | ...,
  payload: { source_text?, url?, file_path?, candidates? },
  options: { summary_length?, max_atoms? }
) → AgentResult
```

返回结构同 AGENTS_SPEC §通用约定。

---

## 3. 各 intent 详述

### 3.1 `process_resource`

**输入**：`{ source_text?: string, url?: string, file_path?: string }`

**处理**：
1. **抓取/解析**：
   - URL → 调用 obsidian-skills/defuddle（缺失时基础 HTML→MD）
   - PDF → 文本提取（runtime 提供）
   - 长文本 → 直接处理
2. **失败降级**：抓取失败 → 仅基于已有正文片段生成摘要，标 `partial: true`
3. **生成摘要卡**：3 档（300 字 / 800 字 / 详细大纲），由 options.summary_length 选择
4. **抽原子笔记**：调 `extract_atoms`
5. **保留原始**：`source.raw` 指向原始素材路径（永不删）

**输出**：

```typescript
{
  found: [
    { type: "summary_card", body: "...", length: 800 },
    { type: "atom_note", title: "...", body: "...", tags: [...] },
    ...
  ],
  reasoning: "从 5000 字文章抽取 3 条原子观点 + 1 张摘要卡",
  degraded: false
}
```

### 3.2 `extract_atoms`

**输入**：`{ text: string, hint?: { domain?, known_tags? } }`

**原子化规则**（AGENTS_SPEC §2.2）：

1. **一笔记一观点**：含「且/并且/同时/此外」的复合句优先拆分
2. **保留可独立成立的论点**：依赖上下文的细节并入主观点
3. **类型推断**：每条原子笔记判断 type（v0.2 仅 concept/resource）
4. **tag 推断**：基于 hint.domain 与正文关键词
5. **confidence 初值**（0-100 整数量纲 · v1.5 WP2 全局统一）：
   - 单一非一手来源 → 30-40
   - 多源佐证 → 60-75
   - 含一手实验/官方文档 → 80-95
   - 推测/无来源 → ≤30 并建议 `maturity: captured`（v0.3 才有 maturity 字段，v0.2 仅记录初值）

**输出**：

```typescript
{
  found: [
    {
      type: "atom_note",
      note_type: "concept" | "resource",
      title: "...",
      body: "完整章节正文",
      tags: ["ai/rag", "eng/architecture"],
      confidence: 60,                    // 0-100 量纲
      source_excerpt: "抽取自原文的依据片段"
    },
    ...
  ],
  reasoning: "..."
}
```

### 3.3 `cross_verify`

**输入**：`{ candidates: Note[], existing_notes: Note[] }`

**处理**：
1. 对每条候选笔记，与 existing_notes 比对相似度（标签 Jaccard + 标题关键词）
2. 相似度 > 0.6 的既有笔记 → 提升候选 confidence（多源佐证）
3. 相似度 > 0.85 → 建议合并或建立 `evolves`/`supersedes`
4. 内容对立 → 建议建立 `contradicts`（v0.2 仅返回候选，由 ingest 决定是否写入）

**输出**：

```typescript
{
  found: [
    {
      candidate: "...",
      adjusted_confidence: 75,    // 从 60 提升
      related_existing: ["[[已有笔记]]"],
      suggested_relation: "evolves",
      reason: "..."
    }
  ],
  conflicts: [...]  // 对立候选进 conflicts
}
```

### 3.4 `summarize`

**输入**：`{ text: string, length: "short" | "medium" | "detailed" }`

**处理**：
- short (300 字) · medium (800 字) · detailed (大纲 + 关键句)
- 保留 source.raw 指向原文
- 不引入外部知识（防幻觉）

**输出**：`{ found: [{ type: "summary_card", body: "...", length }] }`

---

## 4. 抽取规则（核心）

### 4.1 原子化启发式

| 信号 | 处理 |
|------|------|
| 「且/并且/同时/此外/另外」 | 优先在连接词处拆分 |
| 段首「首先/其次/最后」 | 每点独立成笔记 |
| 「例如/比如」 | 并入主观点，不独立 |
| 单段超过 300 字 | 评估是否含多观点 |
| 标题层级（h2/h3） | 每个标题对应一个观点候选 |

### 4.2 类型判断

- 含「定义/是/指」→ concept
- 含「文章/书/项目/工具/研究」+ 外部作者 → resource
- v0.2 不产出 principle/belief/pattern/experience/decision（v0.3+）

### 4.3 confidence 初值（AGENTS_SPEC §2.2）

| 来源 | confidence |
|------|-----------|
| 单一非一手来源 | 30-40 |
| 多源佐证 | 60-75 |
| 含一手实验/官方文档 | 80-95 |
| 推测/无来源 | ≤30 |

---

## 5. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 本技能完全不可用 | ingest 回退为「模板套用 + 字段填充」，不抽原子观点；多观点素材作为单条入库，待人工拆分 |
| 抓取失败（404/付费墙） | 仅基于已有正文片段生成摘要，标 `partial: true` |
| PDF 解析失败 | 提示用户提供纯文本版；标 `partial: true` |
| defuddle 不可用 | 用基础 HTML→MD |

---

## 6. 不变性

- **只读外部资料**：不读库内已有笔记（避免与 quick-kb-memory-agent 域重叠）
- **保留原始**：source.raw 永久指向原始素材
- **不提升 confidence 至 81+**：除非确证为一手实验/官方文档
- **可解释**：每条原子笔记附 `source_excerpt`

---

## 7. 自检清单

- [ ] process_resource 产出摘要卡 + N 条原子笔记
- [ ] extract_atoms 严格遵守一笔记一观点
- [ ] confidence 初值符合规则（不超范围）
- [ ] cross_verify 候选 relations 准确（supports/evolves/contradicts/supersedes）
- [ ] 抓取失败时正确标 partial
- [ ] 不读库内笔记（输入域隔离）
- [ ] 不产出 v0.3+ type（principle/belief/pattern/experience）

---

## 8. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 作为独立技能而非内部 agent | 跨 runtime 契约统一以 skill 形式分发；随 npx 安装自动可用 | 本技能定位调整 |

其余无偏差。AGENTS_SPEC §2 全部能力在 v0.2 实现，不推迟。
