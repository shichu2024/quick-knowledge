# kb.config.yaml · 完整 Schema（v0.4）

> **真相源**：`docs/DESIGN.md §4.2` · `docs/AGENTS_SPEC.md §3.5` · `docs/dev/v0.4-extensions.md WP5`
>
> 各技能 / agent 读取自己相关的配置段。**缺失字段走默认值**（零配置可用）。

---

## 1. 完整 Schema

```yaml
# quick-knowledge vault 配置 · v0.4
# 生成者：quick-kb-init（首次初始化）
# 修改者：用户手动 / quick-kb-init upgrade

# ─── 基础 ──────────────────────────────────────────
language: zh                       # zh | en · 默认模板语言
default_domain: ai-engineering     # 新笔记缺 domain 时的默认值
version: v0.4                      # 配置版本（用于 normalize 识别 legacy）

# ─── 已注册领域 ───────────────────────────────────
domains:
  - ai-engineering
  - systems-programming
  - frontend
  - devops
  # ... 用户可扩展

# ─── 受控标签词表 ─────────────────────────────────
tags_vocabulary:
  - concept/rag
  - concept/llm
  - concept/vector-db
  - pattern/isolation
  - experience/lesson-security
  - experience/lesson-performance
  # ... 用户可扩展；normalize 时对照此表归一

# ─── Review 阈值 ──────────────────────────────────
review:
  inbox_max_age_days: 7            # inbox 笔记超过此天数提醒 ingest
  orphan_threshold: 0.15           # 孤立率超过此值 review 警告
  confidence_decay_months: 6       # confidence 衰减周期
  structure_drift_count: 30        # 子领域近 N 月新增 ≥ 此值 → 升格建议
  structure_drift_ratio: 0.40      # 或占比 ≥ 此值 → 升格建议
  stale_applied_months: 6          # maturity: applied 超此未更新 → stale 提醒

# ─── 主动提醒（DESIGN §7.6）──────────────────────
proactive_reminders:
  enabled: true                    # 总开关
  quiet_below_notes: 50            # 库内 < 此数关闭提醒
  max_per_session: 3               # 单会话呈现上限（memory + manager 合并）
  max_per_skill_call: 2            # 单次技能调用上限
  suppress: []                     # 关闭某类事件
    # 可选值：
    #   - new_project_init          (memory)
    #   - new_goal_create           (memory)
    #   - capture_topic_match       (memory)
    #   - ingest_conflict_detected  (memory)
    #   - ingest_new                (manager)
    #   - review_done               (manager)
    #   - stale_applied_notes       (manager)

# ─── Memory-Agent 排序权重（AGENTS_SPEC §3.5）───
memory_agent:
  min_notes: 50                    # 低于此关闭召回
  default_options:
    max_results: 5
    min_similarity: 0.55
    prefer_failures: true
  weights:                         # 覆盖默认权重（必须 4 项和 = 1.0）
    similarity: 0.45
    recency: 0.20
    impact: 0.15
    confidence: 0.20

# ─── Research-Agent ──────────────────────────────
research_agent:
  extract_max_atoms: 8             # 单次抽取原子观点上限
  cross_verify_min_confidence: 50  # 低于此值 cross_verify 触发

# ─── Obsidian 集成（可选）─────────────────────────
obsidian:
  enabled: false                   # 检测到 .obsidian/ 自动 true
  bases: true                      # 生成 Bases 视图配置
  canvas: true                     # 支持 canvas 文件
  defuddle: false                  # 启用 defuddle 抓取

# ─── Wikilink 严格模式 ───────────────────────────
wikilink:
  strict_dead_link: false          # true: 死链报错；false: warning
  archive_annotation: true         # 归档后 wikilink 加「(已归档)」标注

# ─── 工作流日志 ──────────────────────────────────
workflows:
  query_log: true                  # 落 .query-log.jsonl
  reminder_state: false            # v0.4 启用：记录已 dismiss 提醒
```

---

## 2. 校验规则

| 字段 | 校验 | 失败降级 |
|------|------|---------|
| `language` | 枚举 `zh` / `en` | 默认 `zh` + 警告 |
| `memory_agent.weights.*` | 4 项和 = 1.0 | 不修正 + 警告（用默认） |
| `tags_vocabulary` | 列表唯一 | 去重 + 警告 |
| `proactive_reminders.suppress` | 枚举值合法 | 忽略非法项 + 警告 |
| `review.orphan_threshold` | 范围 [0, 1] | 默认 0.15 + 警告 |
| `memory_agent.min_notes` | 整数 ≥ 0 | 默认 50 |
| `version` | 与库内 quick-knowledge 版本兼容 | 触发 normalize 建议 |

**校验失败不阻塞使用**：所有字段都有默认值，缺失即用默认。

---

## 3. 各技能读取的配置段

| 技能 / Agent | 读取段 | 关键字段 |
|-------------|--------|---------|
| `quick-kb-capture` | `language` | 默认模板语言 |
| `quick-kb-ingest` | `language` / `tags_vocabulary` | 模板 + 标签归一 |
| `quick-kb-normalize` | `tags_vocabulary` / `version` | 标签归一 + legacy 识别 |
| `quick-kb-connect` | `wikilink.strict_dead_link` | 死链处理策略 |
| `quick-kb-query` | `wikilink.strict_dead_link` / `workflows.query_log` | 严格模式 + 日志 |
| `quick-kb-advisor` | `memory_agent.*` | 召回参数 |
| `quick-kb-project archive` | `language` / `wikilink.archive_annotation` | 归档标注 |
| `quick-kb-archive` | `wikilink.archive_annotation` | 归档标注 |
| `quick-kb-stats` | `obsidian.bases` / `review.*` | 报告字段 |
| `quick-kb-import` | `language` / `domains` / `tags_vocabulary` | 字段补全 |
| `manager-agent` | `review.*` / `proactive_reminders.*` | 阈值 + 限流 |
| `memory-agent` | `memory_agent.*` / `proactive_reminders.*` | 排序 + 限流 |
| `research-agent` | `research_agent.*` | 抽取参数 |

---

## 4. 配置示例 · 最小配置（零配置可用）

```yaml
# 不写也行，全部走默认值
language: zh
```

---

## 5. 配置示例 · 进阶（自定义 memory 权重）

```yaml
language: en
default_domain: systems-programming
domains:
  - systems-programming
  - devops

memory_agent:
  min_notes: 30                    # 库小时也启用召回
  weights:
    similarity: 0.55               # 更看重语义相似
    recency: 0.10
    impact: 0.15
    confidence: 0.20

proactive_reminders:
  suppress:
    - stale_applied_notes          # 关闭老旧笔记提醒
  max_per_session: 5               # 提高上限

review:
  orphan_threshold: 0.20           # 放宽孤立率阈值
```

---

## 6. 校验工具

`references/kb-config-schema.yaml`（YAML Schema 文件）可供外部工具校验：

```bash
# 用 yaml-validator 校验（示例）
yaml-validator --schema references/kb-config-schema.yaml kb.config.yaml
```

quick-kb-init upgrade 时自动跑一次校验，写 warning 到 `99_system/workflows/.config-check.log`。

---

## 7. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 新增 `wikilink.archive_annotation` / `workflows.reminder_state` | dev doc 未列但实现必需 | docs/dev/v0.4-extensions.md WP5（完整支持的 spirit） |
| weights 4 项和校验为 1.0 | AGENTS_SPEC §3.5 公式归一要求 | docs/AGENTS_SPEC.md §3.5 |
| `tags_vocabulary` 缺失时 normalize 不阻塞 | dev doc 要求零配置可用 | docs/dev/v0.4-extensions.md WP5 关键点 |
| Obsidian 检测自动启用 | 用户无需手动改 `obsidian.enabled` | docs/references/obsidian-integration.md |
