# 变更记录（CHANGELOG）

> 倒序排列，最新版本在上。每条记录含：版本号、日期、变更摘要、变更明细、变更原因。

---

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
