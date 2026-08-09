# 用户进阶指南 · User Guide

> 假设你已完成 [quick-start.md](./quick-start.md)。本文档覆盖六大闭环的进阶用法、主动提醒机制、Decision Ledger 实践、与 Obsidian 协作。

---

## 1. 六大闭环详解

### Capture（采集）

**目标**：低摩擦地把外部素材放进 `00_inbox/`，**不追求分类**。

| 触发词 | 用途 |
|--------|------|
| 「抓 <url>」 | 网页正文 → Markdown |
| 「抓 <pdf-url>」 | PDF 文本提取 |
| 「读 <本地路径>」 | 本地文件入库 |
| 「抓和 X 的这次对话」 | AI 对话归档（v0.2+） |

**关键**：capture 阶段只填 `title` + `captured_at` + `source.url` + `status: inbox`。**不要在 capture 时纠结 type/domain/tags**，留给 ingest。

**降级**：付费墙 / 404 → 抓取部分正文 + 标 `partial: true`。

---

### Ingest（入库）

**目标**：把 inbox 素材蒸馏为正式笔记。

```
入库 inbox 最新那条
```

技能会：
1. 调 research-agent 抽取**原子观点**（一笔记一观点）
2. 推断 type / domain / 初始 confidence
3. 检测与既有笔记的关系（manager-agent / memory-agent）
4. 移到对应目录

**进阶**：
- 多观点素材 → 拆分为多条原子笔记
- 与既有笔记相似度 > 0.85 → 询问是否合并
- 与既有笔记冲突 → 触发 `ingest_conflict_detected` 提醒

---

### Normalize（规整 · v0.4）

**目标**：批量升级历史笔记的 frontmatter。

```
规整全库
规整 00_inbox/imported/  # 仅处理导入的
规整 v0.1 旧笔记 dry-run  # 预览
```

**幂等**：多次运行结果一致。**可回滚**：所有改动写入 `_normalize_log/`。

---

### Connect（连接）

**目标**：建立笔记间的关系。

支持的 `relations` 类型：
- `supports` —— A 支撑 B（A 是 B 的证据/基础）
- `contradicts` —— A 与 B 冲突（必须各自声明 `context`）
- `evolves` —— A 演化为 B（如 belief → principle）
- `supersedes` —— A 取代 B（如新版模式取代旧版）

```
连接 [[X]] 和 [[Y]]
建立 [[X]] supports [[Y]]
建 MOC：插件系统
```

---

### Query（查询）

**目标**：基于库内笔记回答事实型问题，**每句结论挂引用**。

```
我笔记里关于 RAG 怎么说？       # strict 模式（默认）
关于 RAG 多模态（含推测）        # hybrid 模式
```

**冲突呈现（ADR-011）**：召回涉及 `contradicts` 时双方同时呈现 + 各自 context，不擅自选边。

---

### Review（复盘）

**目标**：周期性健康检查 + 价值刷新。

```
复盘本周
复盘这个月
KB 体检           # ad-hoc
```

**关键产出**：
- 孤立笔记清单
- 高价值低置信笔记（KS 高但 confidence < 60 → 该验证了）
- 低复用高占用笔记（confidence 高但 reuse=0 → 该连 MOC 或归档）
- 结构演化建议（子领域增速异常 → 升格建议）

---

## 2. 三个 Agent 的协作

```
你的请求
   │
   ▼
quick-kb-* 技能
   │
   ├──▶ manager-agent  （库内结构：关系、孤立、死链、KS）
   ├──▶ research-agent （外部资料：URL/PDF 抽取）
   └──▶ memory-agent   （库内认知资产：experience/pattern/principle/belief）
```

**核心差异化**：memory-agent 让 quick-knowledge 不是「带引用的 RAG」，而是「个人助手」——它调取你的历史经验，而不是通用文档。

详见 [`AGENTS_SPEC.md`](./AGENTS_SPEC.md)。

---

## 3. 主动提醒机制（v0.3+）

知识主动找人，而非人找知识。**7 类事件**：

| 事件 | 触发 agent | 示例 |
|------|-----------|------|
| 新建项目 | memory | 「你过去有 3 个类似项目：[[X]] [[Y]] [[Z]]」 |
| 新建目标 | memory | 「该领域有 2 条原则、1 个失败教训」 |
| Capture 素材 | memory | 「这条与你 [[X]] 相关；注意 [[Y]] 与之冲突」 |
| Ingest 检测冲突 | memory | 「新结论与 [[Z]] 在 context: <...> 下冲突」 |
| Ingest 新笔记 | manager | 「新笔记与 [[X]] 相似度 0.88，建议建 supports」 |
| Review 完成 | manager | 「3 条高价值低置信笔记待验证」 |
| 长期未触碰 applied | manager | 「[[A]] 已 6 月未触碰，是否仍 applied？」 |

**限流**：单会话 ≤ 3 条；库 < 50 条时关闭。可在 `kb.config.yaml` 配置。

---

## 4. Decision Ledger 实践

### 何时开 Decision Ledger

任何「在多个方案间做选择」的决策都应开。

```
在 [[04_projects/plugin-system]] 开 Decision：隔离方案选型
```

### 8 字段闭环

```yaml
problem:   # 决策问题
options:   # 候选方案
chosen:    # 选了哪个
reason:    # 为什么选
rejected:  # 为什么不选其他
expected:  # 预期效果
actual:    # 实际结果（待补）
lesson:    # 学到什么（待补）
```

### 归档派生 experience（v0.3 核心闭环）

```
归档项目 [[04_projects/plugin-system]]
```

技能会：
1. 扫所有 decisions/，补全 actual + lesson
2. 自动计算 outcome（success / failure / mixed）
3. **每条 lesson 派生为独立 experience 笔记**到 `07_principles/experiences/`
4. 原 decision 建立 `derived_to`，新 experience 建立 `derived_from`

→ 此后这些 experience 可被 memory-agent 召回，影响你的未来决策。**这是 quick-knowledge 区别于通用 Wiki 工具的关键机制**。

---

## 5. 认知资产（v0.3）

| type | 用途 | maturity 起点 |
|------|------|--------------|
| `principle` | 跨项目方法论 / 价值观底线 | validated |
| `belief` | 待验证假设 | captured |
| `pattern` | 可复用解决模式 | applied |
| `experience` | 具体历史事件 / 教训 | applied |

**升格路径**：
- belief 验证通过 → principle 或 pattern（`maturity: validated/applied`）
- experience 中提炼出可抽象规律 → pattern 或 principle（`relations.evolves`）
- belief 被反证 → `maturity: deprecated` + 强化 `contradicts`

---

## 6. 与 Obsidian 协作（可选）

quick-knowledge 与 Obsidian 兼容（共用 wikilink + frontmatter）。

### 启用 Obsidian 集成

1. 在 vault 目录用 Obsidian 打开（自动生成 `.obsidian/`）
2. `kb.config.yaml.obsidian.enabled: true`（自动检测）
3. 启用 Bases / Canvas / Defuddle 三个官方插件

### 依赖与降级（详见 [`references/obsidian-integration.md`](../references/obsidian-integration.md)）

| 功能 | 依赖 | 降级 |
|------|------|------|
| Canvas 可视化 | Obsidian Canvas | quick-kb-connect 仅生成 Markdown MOC |
| Bases 视图 | Obsidian Bases | quick-kb-stats 输出纯 Markdown 表 |
| 网页干净正文 | Defuddle | 降为 readability 规则 |

---

## 7. 配置 · kb.config.yaml

完整 schema 见 [`references/kb-config-schema.md`](../references/kb-config-schema.md)。

最小配置（零配置可用）：

```yaml
language: zh
```

进阶示例（自定义 memory 权重）：

```yaml
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
```

---

## 8. 常见问题

### Q：库内 < 50 条时很多功能不工作？

A：memory-agent / 主动提醒在 < 50 条时关闭（避免噪音）。可手动覆盖：

```yaml
memory_agent:
  min_notes: 10
proactive_reminders:
  quiet_below_notes: 10
```

### Q：如何回滚 normalize？

A：`quick-kb-normalize action=rollback`，按 `_normalize_log/` 的 diff 恢复。

### Q：v0.1 旧笔记怎么升级？

A：`quick-kb-normalize scope=legacy`，自动迁移 `related → relations` + 补全字段。

### Q：归档的笔记还能被召回吗？

A：能。memory-agent 默认排除 `98_archive/`，但可通过 `proactive_reminders` 或显式 query 找回。

### Q：与 nuwa-skill / 其他 skills 的关系？

A：quick-knowledge 是聚焦「个人知识库」的技能包，可与任意其他 skills 共存。

---

## 9. 下一步

- 完整设计：[DESIGN.md](./DESIGN.md)
- 技能规格：[SKILLS_SPEC.md](./SKILLS_SPEC.md)
- Agent 规格（含排序公式）：[AGENTS_SPEC.md](./AGENTS_SPEC.md)
- 各阶段开发文档：[dev/](./dev/)
- 示例 vault：[examples/demo-vault/](../examples/demo-vault/)
