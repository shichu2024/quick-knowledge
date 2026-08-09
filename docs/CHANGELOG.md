# 变更记录（CHANGELOG）

> 倒序排列，最新版本在上。每条记录含：版本号、日期、变更摘要、变更明细、变更原因。

---

## v1.0 · 2026-08-09 · release（公开发布）

**摘要**：对外发布到 GitHub + skills marketplace。无新功能，全是发布打磨。

### 新增交付

- **治理文档**：`CONTRIBUTING.md` / `COMMUNITY.md` / `CODE_OF_CONDUCT.md`
- **LICENSE**：MIT
- **GitHub 模板**：`.github/ISSUE_TEMPLATE/{bug,feature,config}.yml` + `PULL_REQUEST_TEMPLATE.md`
- **CI 基础检查**：`.github/workflows/ci.yml` + `scripts/check-frontmatter.mjs` + `scripts/check-links.mjs`
  - 4 个 job：frontmatter / wikilink / placeholder / demo-vault 结构
- **demo-vault 完善**（覆盖 v0.1-v0.4）：
  - 7 条认知资产笔记（principle/belief/pattern×2/experience×3）
  - Decision Ledger（含 expected/actual/lesson 完整闭环 + derived_to）
  - 项目 README（plugin-system）+ 目标 README（learn-plugin-design）
  - MOC（含冲突对照段）+ 周复盘（含 KS Top 3 + 结构演化）
- **skills marketplace 配置**：`.claude-plugin/marketplace.json` + `plugin.json`
- **用户文档体系**：`docs/quick-start.md`（v0.4 已有，打磨）+ `docs/user-guide.md`（新增进阶指南）

### 不包含

- 录屏 / 发布社交材料（推后到发布周内补完）
- CONTRIBUTING 实战示例（社区首贡献后补）

---

## v0.4 · 2026-08-09 · extensions（扩展与多语言）

**摘要**：补齐运维性技能与国际化。无结构性新概念。

### 新增技能（4 个）

- `quick-kb-normalize` —— 批量规整（related→relations 迁移 / dry-run / 可回滚）
- `quick-kb-archive` —— 通用归档（任意对象 / 不死链 / 可恢复）
- `quick-kb-stats` —— 健康仪表盘（孤立率/KS Top/置信度/maturity 分布）
- `quick-kb-import` —— 外部库导入（Obsidian/Notion/Logseq → inbox）

### 新增配置

- `references/kb-config-schema.md` —— kb.config.yaml 完整 schema + 校验规则 + 各技能读取映射

### 新增文档

- 5 语种 README（中/英/日/韩/西）+ `docs/quick-start.md`（5 分钟上手）

### 偏差检查

- `references/v0.4-deviation-check.md` —— 无重大偏差，3 处细微补充

---

## v0.3 · 2026-08-09 · assistant（个人助手）

**摘要**：从「带引用的 RAG」升级为「个人决策助手」。引入 memory-agent + 认知资产层 + Decision Ledger 派生闭环。**核心差异化阶段**。

### 新增 Agent

- **`quick-kb-memory-agent`**（核心）—— 长期记忆调取。5 个 intent：
  - `recall_similar` —— 经验召回（按 AGENTS_SPEC §3.5 排序公式）
  - `check_beliefs` —— 原则/假设一致性判定
  - `detect_repeat_mistakes` —— 历史失败模式重演检测
  - `proactive_suggest` —— 4 个 memory 提醒事件
  - `present_conflicts` —— ADR-011 冲突呈现

### 新增技能（3 个）

- `quick-kb-advisor` —— 决策辅助（三段输出：你的历史/你的原则/建议路径）
- `quick-kb-project` —— 项目全生命周期（archive 含 lesson 派生 experience）
- `quick-kb-goal` —— 目标管理（含 research-agent 学习路径 + memory 召回）

### 新增模板（中英 14 个）

- `decision.md`（Decision Ledger 8 字段）
- `principle.md` / `belief.md` / `pattern.md` / `experience.md`（4 类认知资产）
- `goal.md` / `project.md`

### 新增文档

- `references/frontmatter-v0.3.md` —— maturity 6 态 + KS 公式 + value.impact/uniqueness
- `references/conflict-presentation-rule.md` —— ADR-011 落地说明
- `references/proactive-reminders-v0.3.md` —— 全量 7 类事件

### 升级

- `frontmatter`：maturity（6 态）+ value.impact/uniqueness + 14 type 枚举（含 4 类认知资产）
- `manager-agent`：v0.2→v0.3，新增 `detect_structure_drift` + KS 排序 refresh_value
- `KS 公式`：`KS = confidence × log2(1 + reuse) × impact`（仅 maturity ≥ applied 参与 Top-N）
- `memory-agent 排序`：`score = sim^0.45 × recency^0.20 × impact^0.15 × conf^0.20` + 类型加权 + 失败加权

---

## v0.2 · 2026-08-09 · loops（闭环完整）

**摘要**：补齐六大闭环 + 两个 agent + 英文模板。从「单点 capture」到「闭环系统」。

### 新增技能（3 个）

- `quick-kb-connect` —— 类型化关系（supports/contradicts/evolves/supersedes）+ MOC + canvas
- `quick-kb-query` —— strict 模式（默认）+ ADR-011 冲突呈现 + `.query-log.jsonl`
- `quick-kb-review` —— 4 维分析（knowledge/value/structure/daily）+ 健康报告

### 新增 Agent（2 个）

- `quick-kb-manager-agent` —— 库内结构（tidy_inbox/build_moc/recommend_relations/detect_orphans/repair_deadlinks/refresh_value + manager 事件子集）
- `quick-kb-research-agent` —— 外部资料（process_resource/extract_atoms/cross_verify/summarize）

### 升级

- `frontmatter`：新增 relations/context/value.reuse
- `capture`：扩展 PDF/meeting/AI dialog/reading + defuddle
- `ingest`：用 research-agent 替代内置 LLM；冲突检测（manager-agent 降级）
- `templates`：5 个英文版本同步

### 新增文档

- `references/frontmatter-v0.2.md` / `v0.2-deviation-check.md`
- `references/obsidian-integration.md`（5 依赖 + 降级 + 测试矩阵）
- `references/proactive-reminders-v0.2.md`（manager 事件子集）

---

## v0.1 · 2026-08-08 · mvp（最小可用）

**摘要**：从「设计文档」到「能跑通」。建立基础 capture → ingest → daily 流程。

### 新增技能（4 个）

- `quick-kb-init` —— 创建完整 vault 骨架 + 最小 kb.config.yaml + 4 中文模板
- `quick-kb-capture` —— idea + web-clip（基础 HTML→MD + 标题相似度去重）
- `quick-kb-ingest` —— 内置 LLM 抽取原子观点 + confidence 初始值
- `quick-kb-daily` —— 4 段（做了/学到/想法/卡点）+ max 2 轮追问

### 新增模板

- `templates/zh/`：note-concept / note-idea / note-resource / daily

### 新增示例

- `examples/demo-vault/`：11 条样例（3 inbox + 6 formal + 2 daily），演示完整 ingest 链

### 新增文档

- `references/frontmatter-v0.1.md` —— v0.1 字段子集（confidence 可选）
- `docs/dev/v0.1-mvp.md` —— 开发文档

---

<!-- =========================== 设计文档版本（与上面实现阶段独立） =========================== -->

## V2 · 2026-08-09 · 知识冲突 / Decision Ledger / Memory Agent 规格 / 主动提醒

**摘要**：补齐 V1 的四个结构性缺口 —— 知识冲突管理、决策闭环、memory-agent 详细规格、事件驱动的主动提醒机制。

### 变更明细

#### DESIGN.md

- **§6.1 标准字段**：`related` 升级为类型化 `relations`（supports/contradicts/evolves/supersedes），新增可选 `context` 字段。
- **§6.4 maturity**：`deprecated` 强制关联 `supersedes`/`contradicts` 至少一项。
- **新增 §6.7 关系类型化**、**§6.8 上下文字段**，原 §6.7 顺延为 §6.9。
- **§7.3 memory-agent**：能力表加"冲突感知"与"失败案例优先"；引用 AGENTS_SPEC。
- **§7.4**：引用 AGENTS_SPEC。
- **新增 §7.6 主动提醒机制**：7 类事件 → 触发 agent → 提醒示例。
- **§8.3 concept 模板**：`related` → `relations` + `context`。
- **新增 §8.4 Decision Ledger 模板**：problem/options/chosen/reason/rejected/expected/actual/lesson 闭环；lesson 派生为 experience。
- **§11 仓库结构**：加入 AGENTS_SPEC/VERSIONING/CHANGELOG/archive。
- **新增 ADR-011**（关系类型化与冲突管理）、**ADR-012**（Decision Ledger 强化）、**ADR-013**（主动提醒机制）、**ADR-014**（memory-agent 详细规格独立成文）。

#### SKILLS_SPEC.md

- **§2 capture**：工作流加"主动提醒"步（命中 belief/pattern/contradicts 苗头时）。
- **§3 ingest**：工作流加"关系类型化"与"冲突检测与主动提醒"步；输出示例 frontmatter 升级为 `relations` + `context`。
- **§6 advisor**：明确引用 AGENTS_SPEC §3 的 memory-agent 契约。
- **§10 project(init)**：新增"主动相似项目召回"步与"决策骨架"步；archive 工作流新增"Decision Ledger 闭环 + lesson 派生 experience"。
- **附录 A**：新增"主动提醒"与"派生"两行；引用 AGENTS_SPEC。

#### 新增文件

- **docs/AGENTS_SPEC.md**（V1）：三个 agent 的输入/输出契约、降级路径；memory-agent 召回排序公式 `similarity × recency × impact × confidence` + 类型加权；冲突呈现规则；主动提醒协议与限流。

### 变更原因

外部评审第二轮反馈指出四个缺口：

| 反馈点 | 处理 | 对应 ADR |
|--------|------|---------|
| 缺少知识冲突管理 | 升级 `related` 为类型化 `relations` + 自由文本 `context`；拒绝结构化 `context:{team_size,stage}` 防摩擦 | ADR-011 |
| 缺少 Decision Ledger | 强化 `outputs/decisions/` 模板为 expected/actual/lesson 闭环（已存在目录，仅增强模板） | ADR-012 |
| Memory Agent 缺规格 | 新建 AGENTS_SPEC.md，含排序公式与降级 | ADR-014 |
| 缺少主动提醒 | 事件驱动机制（§7.6），非新技能 | ADR-013 |

### 不兼容变更

- **frontmatter**：`related` 仍兼容（视作未类型化弱关联），但 V2 笔记推荐用 `relations`。
- **迁移路径**：`quick-kb-normalize` 可批量迁移 `related` → `relations.supports`。
- **maturity=deprecated**：V2 起新降级必须关联，V1 既有 deprecated 笔记在首次 Review 时补关联或保留告警。

### 归档

V1 完整快照见 `docs/archive/V1/`。

---

## V1 · 2026-08-08 · 首个稳定设计

**摘要**：建立 quick-knowledge 知识库技能框架的完整设计基线。

### 核心内容

- **价值公式**：知识库价值 = 知识密度 × 调用频次 × 验证深度
- **六大闭环**：Capture / Ingest / Normalize / Connect / Query / Review
- **目录结构**：PARA + 系统层 + `principles/`（认知资产）
- **技能清单**：10 核心 + 4 扩展
- **元数据规范**：`status`（文档状态）+ `maturity`（知识成熟度）正交双字段，加 `confidence` 与 `value`
- **Agent 设计**：manager / research / memory 三 agent 协作
- **多语言**：设计文档中文，模板与 README 中英双语
- **Obsidian 集成**：依赖 kepano/obsidian-skills，非 Obsidian 环境降级

### 已采纳的外部反馈

本版本在初始草稿基础上融合了首轮外部评审反馈：

| 反馈点 | 处理方式 |
|--------|---------|
| 缺少知识生命周期模型 | 拆分 `status`/`maturity` 为正交双字段，maturity 收敛为 6 态 |
| 缺少个人认知模型 | 新增 `principles/` 根目录 + 4 类认知资产 type |
| Agent 设计偏弱 | 新增 memory-agent；Knowledge Architect 能力并入 manager |
| Query 需要升级 | 不替换 query，并列新增 quick-kb-advisor |
| 缺少知识评分体系 | 引入价值维度，自动化优先；拒绝手填三分数 |

详见 `DESIGN.md` 的 ADR-004、ADR-007、ADR-008、ADR-009、ADR-010。

### 备注

- 初始草稿（融合反馈前的版本）未归档，因为版本规范在本版本才建立。
- 自 V2 起，每次迭代将严格按 `VERSIONING.md` §4 工作流执行。

### 涉及文件

- `docs/DESIGN.md`（主设计文档，14 节）
- `docs/SKILLS_SPEC.md`（技能详细规格，11 节 + 附录）

---

<!-- 模板：未来版本按此格式追加

## V2 · YYYY-MM-DD · 简短标题

**摘要**：一句话说明本版核心变更。

### 变更明细

#### DESIGN.md
- 第 X 节：...
- 新增 ADR-011：...

#### SKILLS_SPEC.md
- 第 X 节：...

### 变更原因
（为什么做这些变更 —— 外部反馈 / 实践发现 / 新需求）

### 不兼容变更
（如有，明确列出对已有 vault / frontmatter 的影响与迁移路径）

-->
