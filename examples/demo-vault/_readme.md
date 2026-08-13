# demo-vault · quick-knowledge v0.1-v1.0 完整示例

> 本目录演示「一个长期使用 quick-knowledge 的真实 vault 应有的形态」。所有笔记均为虚构示例，覆盖 v0.1-v0.4 全部能力。

---

## 如何浏览

### 推荐顺序（从碎片到沉淀）

1. **Capture → Ingest 链**（v0.1）
   - `00_inbox/clips/20260808-1000-rag-article.md`（web-clip 原始素材）
   - → `02_areas/ai-engineering/rag-architecture.md`（抽取为 concept）

2. **Decision Ledger → experience 派生闭环**（v0.3 关键差异化）
   - `04_projects/bi-engine/decisions/2024-02-isolation-choice.md`（含 expected/actual/lesson 完整闭环）
   - → `07_principles/experiences/2024-plugin-sandbox-escape.md`（lesson 派生为独立 experience，含 `derived_from`）

3. **认知资产层**（v0.3）
   - `07_principles/principles/boundary-over-reuse.md`（原则）
   - `07_principles/patterns/process-level-isolation.md`（模式）
   - `07_principles/beliefs/micro-frontend-default.md`（待验证假设）
   - `07_principles/experiences/`（4 条经验：含失败/成功/混合）

4. **冲突对照**（v0.3 ADR-011）
   - `07_principles/patterns/process-level-isolation.md` contradicts `07_principles/patterns/in-process-sandbox.md`
   - `07_principles/experiences/2023-mid-team-microfrontend-overhead.md` contradicts `07_principles/experiences/2023-large-team-microfrontend-success.md`

5. **项目 + 目标**（v0.3）
   - `04_projects/plugin-system/_readme.md`（含 quick-kb-memory-agent 召回的「经验复用建议」段）
   - `03_goals/learn-plugin-design/_readme.md`（含 quick-kb-research-agent 学习路径）

6. **MOC**（v0.2）
   - `06_wiki/mocs/isolation-patterns.md`（聚合本主题所有笔记，含冲突对照段）

7. **复盘**（v0.2）
   - `05_outputs/reviews/weekly/2026-W32.md`（含 KS Top 3、孤立率、跨维度分析）

8. **日志**（v0.1）
   - `05_outputs/daily/2026/08/2026-08-07.md` / `2026-08-08.md`

---

## 包含的样例（共 19 条）

### v0.1（11 条 · 已有）

- inbox：3 条（ideas/clips）
- 正式笔记：6 条（concept / resource）
- daily：2 条

### v0.3 新增（8 条）

- **认知资产**（7 条）：
  - `07_principles/principles/boundary-over-reuse.md`
  - `07_principles/beliefs/micro-frontend-default.md`
  - `07_principles/patterns/process-level-isolation.md`
  - `07_principles/patterns/in-process-sandbox.md`（deprecated，contradicts 上一条）
  - `07_principles/experiences/2024-plugin-sandbox-escape.md`（failure，含 `derived_from`）
  - `07_principles/experiences/2023-mid-team-microfrontend-overhead.md`（mixed）
  - `07_principles/experiences/2023-large-team-microfrontend-success.md`（success，contradicts 上一条）
- **Decision Ledger**：`04_projects/bi-engine/decisions/2024-02-isolation-choice.md`（8 字段完整闭环 + `derived_to`）
- **项目**：`04_projects/plugin-system/_readme.md`（含 quick-kb-memory-agent 召回段）
- **目标**：`03_goals/learn-plugin-design/_readme.md`（含 quick-kb-research-agent 学习路径）
- **MOC**：`06_wiki/mocs/isolation-patterns.md`（含冲突对照段）
- **复盘**：`05_outputs/reviews/weekly/2026-W32.md`（含 KS Top 3 + 跨维度分析）

---

## 演示的关键机制

| 机制 | 演示笔记 | 阶段 |
|------|---------|------|
| 六大闭环全链路 | 00_inbox → 02_areas → 06_wiki/mocs → 05_outputs/reviews | v0.1-v0.2 |
| Frontmatter V2 正交字段 | 所有正式笔记（status/maturity/confidence/value/relations/context） | v0.2-v0.3 |
| Decision Ledger → experience 派生 | bi-engine decision → 2024-plugin-sandbox-escape | v0.3 |
| quick-kb-memory-agent 召回排序 | failure experience（×1.2 加权）排前 | v0.3 |
| ADR-011 冲突呈现 | process-level vs in-process；mid-team vs large-team | v0.3 |
| KS 公式（confidence × log2(1+reuse) × impact） | reviews/weekly Top 3 | v0.3-v0.4 |
| quick-kb-manager-agent.detect_structure_drift | reviews/weekly 「结构演化」段 | v0.3 |
| 主动提醒（new_project_init） | 04_projects/plugin-system 的「经验复用建议」段 | v0.3 |

---

## 系统文件

- `.kb-initialized` —— init 标记
- `99_system/config/kb.config.yaml` —— 最小配置
- `00_inbox/_readme.md` —— inbox 用法说明

---

## 不包含的内容

为避免冗余，本 demo **不重复铺设**：

- 仓库已有的模板文件（见 [`templates/`](../../templates/)）
- 14 个技能 SKILL.md（见 [`skills/`](../../skills/)）
- 3 个 agent 规格（v0.3+ 已合并入 skills：[`quick-kb-manager-agent`](../../skills/quick-kb-manager-agent/) / [`quick-kb-memory-agent`](../../skills/quick-kb-memory-agent/) / [`quick-kb-research-agent`](../../skills/quick-kb-research-agent/)）
- 所有空目录的 `.gitkeep`（实际 init 会创建）
- `98_archive/` 目录（demo 聚焦 active 状态笔记）
- v0.4 扩展技能产物（normalize/archive/stats/import 的运行结果，由用户实际运行时生成）

如需查看完整骨架，在自己的空目录运行 `quick-kb-init` 即可。
