---
name: quick-kb-manager-agent
description: |
  知识库管家 + 知识架构师（技能化封装）。维护索引、关系、价值、结构。
  能力：tidy_inbox / build_moc / recommend_relations / detect_orphans / repair_deadlinks / refresh_value（含 KS 排序）/ proactive_remind / detect_structure_drift / promote_maturity（v1.8.2）。
  可被其他技能（connect / review / ingest / normalize）通过 Skill 工具显式调用，也可由用户直接调用执行单项能力。
  触发词（中文）：建 MOC / 推荐关系 / 找孤立笔记 / 修死链 / 刷新价值 / 结构漂移
  Triggers (EN): build moc / recommend relations / find orphans / repair deadlinks / refresh value / structure drift
version: v1.9.0
phase: v0.3
applies_to: 读写 frontmatter（value.reuse / value.ks）· 写入 06_wiki/mocs/ · 只读全库快照
source_of_truth:
  - docs/DESIGN.md §7.1
  - docs/AGENTS_SPEC.md §1
  - docs/dev/v0.2-loops.md WP2
  - docs/dev/v0.3-assistant.md WP1 / WP10
---

# quick-kb-manager-agent（v0.3）

> **角色**：知识库管家 + 知识架构师。偏「整理与结构」。维护索引、关系、价值、结构。
>
> **不读**：任务语义（quick-kb-memory-agent 域）、外部资料（quick-kb-research-agent 域）。

---

## 0. 被调用契约

本技能通过 Skill 工具调用，入参与返回结构严格如下：

```
manager_agent(
  intent: "tidy_inbox" | "build_moc" | "recommend_relations"
        | "detect_orphans" | "repair_deadlinks" | "refresh_value"
        | "proactive_remind" | "detect_structure_drift"
        | "promote_maturity",
  payload: {
    inbox_notes?: Note[],             // tidy_inbox 用
    scope?: string,                    // build_moc 用（domain/tag/note-path）
    note?: Note,                       // recommend_relations 用
    candidate_pool?: Note[],           // recommend_relations 用
    snapshot?: Note[],                 // detect_orphans / repair_deadlinks / refresh_value / detect_structure_drift / promote_maturity 用
    query_log?: QueryLogEntry[],       // refresh_value 用
    event?: "ingest_new" | "review_done" | "stale_applied_notes",  // proactive_remind 用
    context?: Record<string, unknown> // proactive_remind 用
  },
  options: {
    max_results?: number,              // 默认 5
    threshold?: number,                // 默认 0.6（相似度阈值）
    window_months?: number,            // detect_structure_drift 用，默认 6
    stale_days?: number                // promote_maturity 用（停滞判定天数），默认 90
  }
) → ManagerAgentResult
```

**返回结构**（ManagerAgentResult）：

```typescript
interface ManagerAgentResult {
  found: Array<{
    // 通用 Note 字段，或特定 intent 的专用结构：
    cluster?: string,                   // tidy_inbox 用
    notes?: Note[],                    // tidy_inbox 用
    suggested_priority?: "high" | "medium" | "low",  // tidy_inbox 用
    path?: string,                     // build_moc 用
    action?: "created" | "updated",   // build_moc 用
    target?: string,                   // recommend_relations 用（wikilink）
    type?: string,                     // recommend_relations 用（supports/evolves/contradicts/supersedes）
    similarity?: number,               // recommend_relations 用
    reason?: string,                   // recommend_relations / repair_deadlinks 用
    suggested_action?: string          // repair_deadlinks / detect_structure_drift 用
  }>,
  conflicts?: Array<{                  // recommend_relations 产出 contradicts 候选
    a: Note,
    b: Note,
    context_a: string,
    context_b: string
  }>,
  reasoning: string,                   // 可解释性（为什么这么聚类/推荐/标记）
  suggestions?: Array<{               // proactive_remind / detect_structure_drift 输出
    type: "promote_to_domain" | "split_subdomain" | string,
    target_tag?: string,
    reason: string,
    recommended_action: string,
    severity?: "info" | "warning"
  }>,
  degraded?: boolean,                  // 是否走了降级路径
  meta: { agent: "manager", latency_ms?: number, version: "v0.3" }
}
```

**字段约定**：
- `refresh_value` 会写回 `value.reuse` 和 `value.ks` 到 frontmatter（v0.3 新增）
- `build_moc` 产出写入 `06_wiki/mocs/` 目录，基于 `templates/zh/moc.md`
- `recommend_relations` 相似度 > 0.85 建议 evolves/contradicts，> 0.6 建议 supports
- `detect_structure_drift` 触发条件：子领域近 6 月 ≥ 30 条 OR 占比 ≥ 40%
- `proactive_remind` 遵守限流：单次调用 ≤ 3 条，库 < 50 条关闭

---

## 1. 能力清单

| intent | v0.2 | v0.3 | 输入 | 输出 |
|--------|------|------|------|------|
| `tidy_inbox` | ✓ | ✓ | inbox 笔记列表 | 聚类 + 入库优先级排序 |
| `build_moc` | ✓ | ✓ | 领域名 / 标签 | MOC 笔记（写入 `06_wiki/mocs/`） |
| `recommend_relations` | ✓ | ✓ | 单条笔记 | 候选 `relations.{supports/evolves}` 列表 |
| `detect_orphans` | ✓ | ✓ | 全库快照 | 孤立笔记清单（无入链无出链） |
| `repair_deadlinks` | ✓ | ✓ | 全库快照 | 死链清单 + 修复建议 |
| `refresh_value` | ✓（仅 reuse） | **✓（含 KS 排序）** | 全库快照 + 查询日志 | 更新 reuse + 重算 KS |
| `proactive_remind` | ✓（3 manager 事件） | **✓（manager 事件基于 maturity）** | 事件 + 上下文 | 主动建议列表 |
| `detect_structure_drift` | ✗ | **✓ 新增** | 全库快照 | 子领域升格/拆分建议 |
| `promote_maturity` | ✗ | **✓（v1.8.2）** | 全库快照 | maturity 停滞评估 + 晋升/降级建议清单 |

---

## 2. 调用契约

按 [`AGENTS_SPEC.md` §通用约定](../../docs/AGENTS_SPEC.md)：

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
- MOC 笔记写入 `06_wiki/mocs/<domain>-moc.md`，基于 [`templates/zh/moc.md`](../../templates/zh/moc.md)
- 已存在 MOC → diff merge（保留人工修订章节，仅刷新自动生成区）

**示例**：

```
manager_agent.build_moc(payload: { scope: "ai-engineering" })
 → {
     found: [{ path: "06_wiki/mocs/ai-engineering-moc.md", action: "created" }],
     reasoning: "扫描 12 条 ai-engineering 笔记，聚为 3 类：RAG/Agent/工具调用"
   }
```

### 3.3 `recommend_relations`

**输入**：`{ note: Note, candidate_pool?: Note[] }`

**处理**：
1. 若未给 candidate_pool，扫描同 domain 笔记作为候选池
2. **相似度计算**：
   - 主路径：embedding 余弦（如 runtime 提供）
   - **降级**：按 [`references/scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4）
3. **关系类型推断**：
   - 相似度 > 0.85 + 标题近义 → `evolves`（A 由 B 演化）
   - 相似度 > 0.85 + 内容对立语义（"X 好" vs "X 不好"）→ `contradicts`
   - 相似度 > 0.6 + 标题共现 → `supports`
   - 候选 B 的 `status: deprecated` 或 `maturity: deprecated` → `supersedes`（A 取代 B）

4. 不强制写入，仅返回候选；由调用方（ingest/connect）经用户确认后写入

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

### 3.6 `refresh_value`（写回型操作 · 非纯函数）

> **写回型操作（非纯函数）**：本 intent 会把计算结果写回笔记 frontmatter（`value.reuse` / `value.ks`），是 §6 不变量「纯函数式」的两个例外之一（另一个是 `detect_structure_drift`）。

**输入**：`{ snapshot: Note[], query_log?: QueryLogEntry[] }`

**处理**：

```
对每条正式笔记：
  value.reuse = 入链数
              + (Connect 推荐频次 · 从 connect 落日志)
              + (查询命中次数 · 从 query_log；若无则 0)
```

- v0.3 已计算 `value.impact`/`uniqueness`/KS（基于 maturity 字段启用）
- 无 query_log 时仅算入链数（AGENTS_SPEC §1.3 降级路径）

**v0.3 KS 重算**（WP10）：
对每条知识型笔记（type∈{concept, resource, idea, principle, belief, pattern, experience, decision}），重算：

```
KS = confidence × log2(1 + reuse) × impact
```

- 仅 `maturity ≥ applied` 的笔记参与 KS Top-N 排序
- 写入 frontmatter 的 `value.ks` 字段（v0.3 新增字段，可选）

**输出**：更新后的 `value.reuse` + `value.ks` 字段写入对应笔记 frontmatter；返回更新清单

### 3.7 `proactive_remind`（v0.3 manager 事件全量）

**输入**：`{ event: "ingest_new" | "review_done" | "stale_applied_notes", context: {...} }`

**v0.3 处理的事件**（DESIGN §7.6 全量 7 类中的 manager 部分）：

| 事件 | v0.2 | v0.3 | 建议 |
|------|------|------|------|
| Ingest 新笔记 | ✓ | ✓ | 提示建立 `supports`/`evolves` 关系 |
| Review 完成 | ✓ | ✓ | 提示处理高价值低复用笔记（KS 高但 reuse=0） |
| 长期未触碰 applied 笔记 | updated 时间 | **改为基于 maturity: applied 且 updated > 6 月** | 提示重审或降为 deprecated |

**不做**（memory 事件，归 quick-kb-memory-agent）：
- 新建项目/目标 → memory 召回相似项目
- Capture 某主题素材 → memory 命中 belief/pattern
- Ingest 检测冲突 → memory 判定

**v0.3 stale_applied_notes 检测改进**：
- v0.2：扫所有笔记 updated > 6 月（误报多）
- v0.3：仅扫 `maturity: applied` 且 updated > 6 月的笔记（精准，因 captured/understood 阶段笔记长期不更新是正常的）

**限流**（按 AGENTS_SPEC 附录）：
- 单次技能调用 ≤ 3 条提醒
- 同事件去重
- 库内笔记 < 50 条 → 关闭
- v0.3：与会话内 memory 事件合并计数 ≤ 3

**输出**：`suggestions: Suggestion[]`，由调用方技能决定是否呈现

### 3.8 `detect_structure_drift`（v0.3 新增）

**输入**：`{ snapshot: Note[], window_months?: number = 6 }`

**处理**：
1. 按 domain/tag 聚合笔记数量
2. 对每个子领域计算：
   - 近 `window_months` 月新增数 `recent_count`
   - 总数 `total_count`
   - 占同 domain 比例 `share = total_count / domain_total`
3. 触发升格/拆分建议的条件（任一）：
   - `recent_count >= 30`
   - `share >= 0.40` 且 `total_count >= 20`
   - 增速同比上 `window_months` 翻倍以上

**输出**：

```typescript
{
  suggestions: Array<{
    type: "promote_to_domain" | "split_subdomain",
    target_tag: string,
    reason: string,             // 含 recent_count / share 数据
    recommended_action: string  // 如「建议把 tag:plugin/* 升格为独立 domain」
  }>
}
```

**示例**：
```
[promote_to_domain] tag:mcp/* 近 6 月新增 38 条（占 systems 子领域 45%）
  建议升格为独立 domain: mcp
  → quick-kb-init 升级 domain 字典 + 建 _moc.md
```

**不做**（manager 边界）：
- 不实际改 domain 字典（由用户确认后 quick-kb-init 执行）
- 不删除原标签

### 3.9 `promote_maturity`（v1.8.2 新增 · 写回型操作）

**输入**：`{ snapshot: Note[], stale_days?: number = 90 }`

**处理**（maturity 6 态词表：captured → understood → validated → applied → teachable；deprecated 为终态）：
1. 对每条含 maturity 的笔记计算晋升信号：
   - `inlink_count`：被其他笔记 `[[]]` 引用次数
   - `confidence`：0-100（缺失按 50 计）
   - `age_days`：created 至今天数
   - `stalled_days`：updated 至今天数
2. 晋升/降级建议规则（满足任一即列入清单）：

| 当前态 | 建议动作 | 触发条件（任一） |
|--------|---------|----------------|
| captured | → understood | confidence ≥ 60 且 inlink_count ≥ 1 |
| understood | → validated | confidence ≥ 70 且 inlink_count ≥ 2 |
| validated | → applied | relations 非空 且 applied 证据：正文含应用段落（**双语关键词**：中文「应用/落地/实践/上线」，英文 applied / deployed / in production / shipped；v1.9.0——纯中文关键词会导致英文笔记永不晋升）或 value.reuse > 0（已被引用复用） |
| applied | → teachable | inlink_count ≥ 5 且 confidence ≥ 75 |
| 任意非终态 | ⚠ 停滞提示 | stalled_days ≥ stale_days 且无晋升信号 |
| applied/teachable | → deprecated 建议 | 与既有笔记建立 supersedes 被取代关系 |

3. 输出建议清单，**写回需用户确认**：`auto_write=false`（默认）仅输出建议；`auto_write=true` 时按清单写回 maturity 并记 why

**输出**：

```typescript
{
  suggestions: Array<{
    note: string,                  // wikilink
    from: string, to: string,      // maturity 态
    reason: string,                // 含 confidence / inlink_count / stalled_days 数据
    action: "promote" | "stalled" | "deprecate"
  }>,
  written: boolean                 // auto_write 是否写回
}
```

**不做**（manager 边界）：
- 不删除笔记、不改 confidence（晋升建议只动 maturity）
- `stalled` 建议不自动降级 maturity，仅提醒用户处理（归档走 quick-kb-archive）

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
| 无 embedding 服务 | 相似度按 [`references/scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」计算（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4） |
| 无查询日志 | refresh_value 仅用入链数；KS 中 reuse 项降级 |
| Louvain 算法不可用 | MOC 聚类降为按 tag.topic 分组 |
| maturity 字段缺失（旧 v0.1 笔记） | refresh_value KS 排序跳过；stale_applied 退化为 updated 时间；promote_maturity 跳过该笔记并建议「先跑 quick-kb-normalize 补 maturity: captured（v1.9.0 起全量补全）」 |
| 本技能完全不可用 | 调用方技能自行做基于规则的最小检查（如 connect 只建标题共现关系） |

---

## 6. 不变性

- **纯函数式**：同一输入产同一输出（除 refresh_value / detect_structure_drift 写回 frontmatter）
- **不绑定 runtime**：所有能力基于文件系统 + 规则，无网络依赖
- **可解释**：每个输出都带 `reasoning`，写明为什么这么聚类/推荐/标记
- **不删除笔记**：所有 intent 只读或写入 frontmatter，不删除文件
- **不擅自升格 domain**：detect_structure_drift 只产出建议，由用户确认后 quick-kb-init 执行

---

## 7. 自检清单

- [ ] 所有 intent 返回结构符合 AgentResult 契约
- [ ] MOC 聚类失败时降级到按 tag 分组（不阻塞）
- [ ] recommend_relations 返回的 contradicts 候选同时出现在 conflicts 字段
- [ ] refresh_value 无 query_log 时仅用入链数（不报错）
- [ ] refresh_value 重算 KS（仅对 maturity ≥ applied 的笔记参与 Top-N）
- [ ] proactive_remind 遵守限流（≤3 / 库 < 50 关闭 / 与 memory 合并计数）
- [ ] stale_applied_notes 基于 maturity: applied 而非 updated 时间
- [ ] detect_structure_drift 输出含 reason 数据（recent_count / share）
- [ ] detect_structure_drift 不实际改 domain 字典
- [ ] promote_maturity 默认 auto_write=false 仅输出建议；写回时每条含 reason（confidence / inlink_count / stalled_days）
- [ ] promote_maturity 的 stalled 建议不自动降级 maturity（仅提醒）

---

## 8. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| refresh_value 写入 value.ks 新字段 | KS 是 v0.3 引入的核心排序指标，需持久化以便 review 直接读 | docs/DESIGN.md §6.5 KS 公式 |
| detect_structure_drift 不实际改 domain | 避免自动改字典导致大规模 tag 重写；只产建议 | docs/AGENTS_SPEC.md §1.6 + DESIGN §6.6 |
| stale_applied_notes v0.3 改为基于 maturity | maturity 字段 v0.3 启用，比 updated 时间更精准 | docs/DESIGN.md §7.6 + §6.4 |
| KS 公式中 reuse 与 impact 都参与 | DESIGN §6.5 明确；confidence 字段已必填 | docs/DESIGN.md §6.5 |
| 作为独立技能而非内部 agent | 跨 runtime 契约统一以 skill 形式分发；随 npx 安装自动可用 | 本技能定位调整 |
