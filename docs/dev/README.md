# quick-knowledge · 开发文档总览

> 本目录指导 quick-knowledge 各阶段的具体开发工作。设计依据：
> - [`docs/DESIGN.md`](../DESIGN.md)（V2）
> - [`docs/SKILLS_SPEC.md`](../SKILLS_SPEC.md)（V2）
> - [`docs/AGENTS_SPEC.md`](../AGENTS_SPEC.md)（V1）
>
> 开发文档面向**实现者**，含工作包拆分、并行建议、验收标准。用户文档（README/指南）在 v1.0 阶段统一产出。

---

## 1. 阶段路线图

| 阶段 | 代号 | 目标 | 核心交付 |
|------|------|------|---------|
| **v0.1** | `mvp` | 跑通 Capture→Ingest 最小闭环 | init / capture / ingest(简化) / daily + 中文模板 + demo-vault |
| **v0.2** | `loops` | 六闭环打通 | connect / query / review + manager/research agent + 完整 frontmatter + Obsidian 集成 |
| **v0.3** | `assistant` | 升级为个人决策助手 | advisor / quick-kb-memory-agent / goal / project + 认知资产 + maturity + Decision Ledger + 主动提醒全量 |
| **v0.4** | `extensions` | 运维扩展 + 国际化 | normalize / archive / stats / import + config 完整 + README 多语言 |
| **v1.0** | `release` | 对外发布 | 完整文档/示例 + CONTRIBUTING/COMMUNITY + marketplace |
| **v1.1** | `flow-restructure` | 目录流转制 + 路径硬约束 | 顶层目录 `NN_` 前缀 + source.url 绝对路径禁令（⚠️ BREAKING） |
| **v1.2** | `ai-polish` | 用户手敲输入的 AI 润色提议 | capture 步骤 2.5 + daily 步骤 3.5 + 三选一确认 + 原文保存 |
| **v1.3** | `skillopt-integration` | 行为评测与技能文本优化 | 自定义 SkillOpt benchmark `quickkb`（dataloader + rollout + adapter + 4 scorers）+ 51 golden cases（45 单点 + 6 J 类端到端）+ nightly mock 后端 workflow |
| **v1.4** | `nested-domain` + `test-feedback-hardening` | 嵌套 domain（已发布 v1.4.0）+ 测试反馈硬化（计划 v1.4.1+） | **Part A**：`domain_taxonomy` schema + flat→嵌套迁移 + ingest/init/connect/query/normalize 支持 + 日期类文件名 LLM 摘要 / **Part B**：init 铺全 12 模板 + schema 升级 / connect MOC 字段硬约束 + 反向关系补全 / import 量表统一 + 弱键去重 / 跨技能状态联动 / references 公开 counting/scoring/polish 规则 |
| **v1.5–v1.6** | `cross-skill-consistency` | 测试报告校准制确立（测试4 起） | confidence 0-100 统一 / JSON Schema 校验 / project 多对一派生 / archive copy+stub / canvas 规范 / wikilink 命名约定 |
| **v1.7** | `automation-and-integration` | agent 契约化 + 自动化 | agent §0 调用契约 / polish_mode 三档 / 循环检测 + 冲突消歧 / slug-rules / 模板 12→14 / 降级可观测性 |
| **v1.8** | `e2e-calibration` | 写入前校验层（测试7 起） | init 资源自包含（模板+schema+指纹）/ write-validation-rules 接入 7 写入型技能 / import 口径统一 / archive 语义修正 / 17 技能版本同步 |
| **v1.8.1–v1.9.3** | `test-calibration` | 测试校准系列（测试8~13，CHANGELOG 记录） | schema/词表对齐 / 降级阈值表 / 冷启动排序 / 虚假问题甄别方法论 / source 格式统一 object / 结构漂移防御 |

---

## 2. 阶段依赖关系（DAG）

```
v0.1 (mvp) ──▶ v0.2 (loops) ──▶ v0.3 (assistant) ──▶ v0.4 (extensions) ──▶ v1.0 (release)
```

**线性依赖**：每个阶段以前一阶段的交付物为基础。
**阶段内并行**：各阶段拆为多个工作包（WP），WP 间大量可并行（详见各阶段文档）。

---

## 3. V2 新增内容的阶段归属

V2 相对 V1 的新增内容按依赖关系分配到各阶段：

| V2 新增 | 归属 | 理由 |
|---------|------|------|
| `relations`（类型化关系） | v0.2 | connect 闭环需要 |
| `context` 字段 | v0.2 | 与 relations 同步落地 |
| `value.reuse`（自动） | v0.2 | quick-kb-manager-agent 在 review 时计算 |
| `maturity`（6 态） | v0.3 | 个人助手差异化的核心 |
| Knowledge Score 排序 | v0.3 | 依赖 maturity + value |
| 认知资产（`principles/` + 4 类 type） | v0.3 | advisor / quick-kb-memory-agent 依赖 |
| Decision Ledger 强化 | v0.3 | project 技能一起交付 |
| `quick-kb-memory-agent` | v0.3 | advisor 依赖 |
| 冲突呈现规则 | v0.3 | quick-kb-memory-agent 规格 |
| 主动提醒机制 | v0.2（manager 事件） / v0.3（memory 事件，全量） | 分批交付 |
| `related`→`relations` 迁移 | v0.4 | normalize 技能承担 |

---

## 4. 共用实现规范（所有阶段必须遵守）

### 4.1 SKILL.md frontmatter

每个技能一个目录 `skills/<skill-name>/SKILL.md`：

```yaml
---
name: quick-kb-<name>
description: |
  <中文一句话职责>
  触发词：「...」「...」
  English triggers: "...", "..."
---

# <技能标题>
<技能本体，按 SKILLS_SPEC 对应章节实现>
```

### 4.2 agent skill frontmatter

每个 agent 以独立 skill 形式分发，文件位于 `skills/quick-kb-<role>-agent/SKILL.md`：

```yaml
---
name: quick-kb-<role>-agent
description: <一句话角色定义 + 触发词>
version: <vx.y>
phase: <vx.y>
applies_to: <读写范围>
source_of_truth:
  - docs/DESIGN.md §7
  - docs/AGENTS_SPEC.md
---

# <Agent 标题>
<按 AGENTS_SPEC 对应章节实现：能力清单、输入输出契约、排序公式、降级路径>
```

> v0.3+ 起，agent 文件从原 `agents/` 目录迁入 `skills/`，使其能随 `npx skills add` 与其他技能一起加载，并支持 Skill 工具按 intent 显式调用。

### 4.3 命名

- 文件/目录：kebab-case，无空格无中文
- 日期：ISO 8601（`YYYY-MM-DD`）
- 时间戳前缀（inbox）：`YYYYMMDD-HHMM-<slug>.md`
- **零绝对路径**：所有路径相对 vault 根

### 4.4 幂等性

同一输入多次执行结果一致。重复 `init` 不破坏已有文件（跳过 + 报告）；重复 `ingest` 不产生重复笔记（去重检测）。

### 4.5 不破坏原始资料

- Capture 的原始素材永不删除
- Ingest 只生成派生笔记
- Archive 只迁移不删除
- 降级（maturity/状态）只标记不删除

### 4.6 降级路径（每个技能/agent 必须声明）

| 缺失依赖 | 降级行为 |
|---------|---------|
| Obsidian-skills 缺失 | 跳过 .base/.canvas 生成，纯 Markdown |
| 无 embedding 服务 | similarity 降为标签 Jaccard + 标题关键词 |
| 库内笔记 < 50 条 | 关闭主动提醒与 memory 召回，避免噪音 |
| quick-kb-research-agent / quick-kb-memory-agent 不可用 | 调用方技能回退到内置 LLM 直接处理 |

### 4.7 可解释性

每次写入/召回向用户说明：「做了什么、为什么、关联了什么、关联得分」。召回结果含 `contradicts` 时必须同时呈现双方与各自 `context`（ADR-011）。

### 4.8 测试要求

每个技能/agent 需准备：
- demo-vault 中的样例输入
- 期望输出（frontmatter、文件路径、召回排序）
- 边界用例（空输入、重复输入、降级路径、冲突情境）

---

## 5. 工作包（Work Package）

每个阶段拆为多个 WP。WP 是**可并行交付的最小单元**：
- 独立可验证
- 可分配给单个 agent/人完成
- 有明确依赖关系

WP 标记：`WPn · <名称>`，每个 WP 含：交付物、依赖、关键实现点、验收点。

---

## 6. 各阶段文档统一结构

每个 `vX.Y-*.md` 文档遵循：
1. 目标
2. 范围（in / out scope）
3. 交付物清单（表格）
4. 工作包详述（WP1..WPn）
5. 并行执行建议（依赖图）
6. 验收标准（DoD）
7. 风险与降级
8. 测试要点

---

## 7. 文档清单

- [`v0.1-mvp.md`](./v0.1-mvp.md) —— MVP 最小采集闭环
- [`v0.2-loops.md`](./v0.2-loops.md) —— 六闭环完整
- [`v0.3-assistant.md`](./v0.3-assistant.md) —— 个人助手
- [`v0.4-extensions.md`](./v0.4-extensions.md) —— 扩展与多语言
- [`v1.0-release.md`](./v1.0-release.md) —— 发布
- [`v1.1-restructure.md`](./v1.1-restructure.md) —— 目录流转制 + 路径硬约束（迁移指南）
- [`v1.2-ai-polish.md`](./v1.2-ai-polish.md) —— AI 润色提议（capture / daily）
- [`v1.3-skillopt-integration.md`](./v1.3-skillopt-integration.md) —— SkillOpt 行为评测与技能文本优化（设计阶段）
- [`v1.4-nested-domain-and-hardening.md`](./v1.4-nested-domain-and-hardening.md) —— 嵌套 domain（Part A 已实施）+ 测试反馈硬化（Part B 计划中）
- [`v1.5-cross-skill-consistency.md`](./v1.5-cross-skill-consistency.md) —— 跨技能一致性（测试4 校准 · 9 WP，v1.4.2~v1.6.0 落地：confidence 量纲统一 / schema 校验 / archive copy+stub / canvas 与 wikilink 约定）
- [`v1.7-automation-and-integration.md`](./v1.7-automation-and-integration.md) —— 自动化与集成（测试5/6 校准 · 7 WP：agent §0 契约 / polish_mode / 循环检测 / 模板 12→14）
- [`v1.8-e2e-calibration.md`](./v1.8-e2e-calibration.md) —— E2E 校准与写入校验层（测试7 校准 · 5 WP：init 资源自包含 / write-validation-rules / 口径统一 / archive 语义 / 版本元数据）
- [`v1.9.3-test12-13-calibration.md`](./v1.9.3-test12-13-calibration.md) —— source 格式统一 + 漂移防御（测试12/13 校准 · 6 WP：source object / normalize 迁移 / init 负向断言 / 近似重复 / MOC 排除 / 跨语言弱键）

> v1.8.1–v1.9.2 为纯校准小版本（测试8~11），无独立 dev 文档——校准结论、拒绝修复清单与评测结果见 [`../CHANGELOG.md`](../CHANGELOG.md) 对应条目。

---

## 8. 开发流程建议

1. **按阶段顺序开发**，每阶段完成后归档（参考 [`VERSIONING.md`](../VERSIONING.md)）。
2. **阶段内按 WP 并行**，先完成关键路径上的 WP（通常是基础规范类）。
3. **每完成一个 WP**：跑该 WP 的测试用例 → 标记完成 → 进入下一 WP。
4. **每阶段收尾**：对照该阶段文档的 DoD 清单逐项验收 → 在 `CHANGELOG.md` 加一条开发进度记录（区别于设计文档的版本记录）。
5. **跨阶段一致性**：任何设计变更若影响已完成阶段，先升设计文档版本（归档 → 更新 → CHANGELOG），再回头补改实现。
