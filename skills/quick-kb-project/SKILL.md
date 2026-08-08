---
name: quick-kb-project
description: |
  项目全生命周期管理。init：建目录 + README + 主动召回相似项目经验；update：追加进展；archive：补 Decision Ledger + lesson 派生 experience + 迁移归档。
  触发词（中文）：开个项目 / 项目 X / 归档项目
  Triggers (EN): new project / archive project
version: v0.3
phase: v0.3
applies_to: 写 projects/<slug>/ · archive/projects/ · principles/experiences/（派生）
source_of_truth:
  - docs/DESIGN.md §7.4 / §8.4（Decision Ledger）
  - docs/SKILLS_SPEC.md §10
  - docs/AGENTS_SPEC.md §3 / §3.8
  - docs/dev/v0.3-assistant.md WP5
---

# quick-kb-project（v0.3）

> **项目全生命周期**：init → update → archive。核心是 archive 时的「Decision Ledger → experience 派生闭环」，让项目经验沉淀为长期记忆。

---

## 1. 何时调用

| 操作 | 触发词 |
|------|--------|
| `init` | 「开个项目 / 新项目 / new project」 |
| `update` | 「更新项目 X / 项目 X 进展」 |
| `archive` | 「归档项目 X / archive project」 |

---

## 2. v0.3 范围

### 做

- init：建目录 + README + Decision Ledger 骨架 + memory-agent 主动召回
- update：追加进展到 `progress/`，更新 _moc.md
- **archive 闭环（核心）**：
  1. 扫 `decisions/`，补全每条 Decision Ledger 的 `actual` 与 `lesson`
  2. 每条 lesson 自动派生为独立 `experience` 笔记
  3. 原 decision 建立指向派生 experience 的 wikilink（`derived_from`）
  4. 项目目录迁移到 `archive/projects/<slug>/`
  5. 生成归档复盘草稿（expected vs actual 偏差分析）

### 不做（v0.4+）

- 不调 research-agent 做项目立项调研（外部资料由 capture/ingest 先入库）
- 不写 review 周报（归 review 技能）

---

## 3. 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 操作 `action` | 是 | `init` / `update` / `archive` |
| 项目 `project` | 是 | 名称（slug） |
| 描述 `description` | init 时必填 | 项目要解决什么问题 |
| 关联目标 `goal` | 否 | goal slug |
| 模板 `template` | 否 | 默认 `templates/{zh,en}/project.md` |
| 归档复盘 `retrospective` | archive 时可选 | 是否生成复盘草稿 |

---

## 4. 工作流 · init

```
1. 校验：projects/<slug>/ 不存在（幂等：已存在则报错并指引用 update）

2. 创建结构：
   projects/<slug>/
   ├── _readme.md         # 用 templates/zh/project.md
   ├── _moc.md            # 项目内索引
   ├── notes/             # 项目笔记
   ├── decisions/         # Decision Ledger
   ├── progress/          # 进展日志
   └── refs/              # 参考资料 wikilink

3. 填充 _readme.md：
   - title / context / deadline / domain
   - relations.supports: [<关联 goal>]
   - 留空：经验复用建议（待 step 5 填）

4. 主动召回（核心 · 触发 memory 事件 new_project_init）：
   memory_agent.proactive_suggest({
     event_type: "new_project_init",
     current_context: <description>,
     constraints: <team/tech stack if known>
   })
   → suggestions: [
       { related_notes: [...相似 projects/experiences], message: "..." }
     ]

5. 把召回结果写入 _readme.md 的「经验复用建议」段：
   ## 经验复用建议（来自 memory-agent）
   ### 高相关 experience
   - [[experience/xxx]] · 相关点：<why>
   ### 可应用 pattern
   - [[pattern/yyy]] · 适用条件：<context>
   ### 相关 principle
   - [[principle/zzz]] · 适用性：<context>
   ### ⚠ 失败教训（如有）
   - [[experience/2024-xxx]] · 教训：<lesson 摘要> —— 注意 <...>

6. Decision Ledger 引导（可选 · 若用户已描述初始方案选型）：
   - 在 decisions/<YYYY-MM-DD>-<topic>.md 用 decision.md 模板
   - 必填：problem / options / chosen / reason / expected
   - 留空：actual / lesson（待 archive 补）

7. 询问关联 goal（若 goal 提供）：
   - 在 _readme.md 的 relations.supports 引用
   - 在 goals/<goal-slug>/goal.md 的「关联项目」段引用本项目

8. 更新顶层 _moc.md（若有）加入项目入口
```

---

## 5. 工作流 · update

```
1. 校验：projects/<slug>/ 存在

2. 追加进展：
   - progress/<YYYY-MM-DD>.md（用 daily 模板简化版）
   - 含：完成 / 卡点 / 下一步

3. 更新 _readme.md：
   - updated: <date>
   - 里程碑勾选（若用户提供）
   - 关键决策若变化 → 在 decisions/ 新增 Decision Ledger

4. 更新 _moc.md：纳入新笔记的索引
```

---

## 6. 工作流 · archive（核心闭环）

```
1. 状态检查：
   - 扫描 decisions/，列出 actual / lesson 仍为空的 Decision Ledger
   - 列出 notes/ 未关联 _moc 的笔记
   - 提示用户：「以下决策尚未补 actual/lesson，是否在归档前补齐？」

2. 决策闭环（对每条 Decision Ledger）：
   2.1 补 actual（如未填）：与用户交互询问「实际结果如何？」
   2.2 补 lesson（如未填）：与用户交互询问「从这次决策中学到什么？」
   2.3 计算 outcome（基于 actual vs expected）：
       - actual 显著好于 expected OR 关键字命中成功 → success
       - actual 显著差于 expected OR 命中失败 → failure
       - 部分 OK 部分 miss → mixed

3. lesson 派生 experience（V2 关键）：
   对每条 Decision Ledger 的 lesson：
   3.1 在 principles/experiences/<YYYY-MM-DD>-<topic>.md 创建新笔记
       （用 experience.md 模板）
   3.2 填充关键字段：
       - title: <事件一句话 · 含时间/项目>
       - context: <原 decision 的 problem + 项目 context>
       - 事件经过: <原 decision 的 options/chosen/reason 摘要>
       - 结果: <原 decision 的 actual>
       - 教训: <原 decision 的 lesson>  ← 核心派生
       - derived_from: [[projects/<slug>/decisions/<原 decision>]]
       - outcome: step 2.3 计算结果
       - source.note: [[<原 decision>]]
       - tags: [experience/<topic>, project/<slug>]
   3.3 在原 Decision Ledger 中：
       - 添加 derived_to: [[principles/experiences/<新笔记>]]（双向引用）
       - status: active → archived
   3.4 检查可升格：lesson 中是否含可抽象的 principle/pattern 候选
       - 若用户确认 → 在 principles/principles/ 或 principles/patterns/ 新建
       - relations.evolves: [[<派生 experience>]]

4. 迁移目录：
   projects/<slug>/ → archive/projects/<slug>/
   （保留所有子目录与 wikilink 完整性）

5. 更新 _readme.md：
   - status: active → archived
   - maturity: applied → teachable
   - 归档日期字段
   - 派生 experience 索引

6. 归档复盘草稿（可选 · retrospective=true）：
   在 archive/projects/<slug>/retrospective.md 生成：
   ## 决策复盘
   | 决策 | expected | actual | 偏差 | lesson → experience |
   |------|---------|--------|------|---------------------|
   | [[decisions/001]] | ... | ... | ±X% | [[experience/...]] |

7. 引用清理（manager-agent.repair_deadlinks 可后续做）：
   - 顶层 _moc.md 移除项目入口或迁到 archive 区
   - goal 的「关联项目」段标注「已归档」
```

---

## 7. 输出示例

### init 成功输出

```
✅ 项目已创建：projects/<slug>/
   - _readme.md（已填充基础字段）
   - _moc.md（索引骨架）
   - notes/ decisions/ progress/ refs/（空目录）

🧠 memory-agent 召回（new_project_init 事件）：
   - 高相关 experience: 2 条
   - 可应用 pattern: 1 条
   - 失败教训: 1 条
   已写入 _readme.md「经验复用建议」段

📝 首条 Decision Ledger（可选）：
   - decisions/<YYYY-MM-DD>-<topic>.md 已创建（待补 actual/lesson）

🔗 关联目标：
   - goals/<goal-slug>/goal.md 已添加项目引用
```

### archive 成功输出

```
✅ 项目已归档：archive/projects/<slug>/

📋 决策闭环：
   - 补全 Decision Ledger: 3 条
   - 派生 experience 笔记: 3 条
     - [[experience/2026-XX-XX-xxx]]
     - [[experience/2026-XX-XX-yyy]]
     - [[experience/2026-XX-XX-zzz]]

📊 复盘草稿：archive/projects/<slug>/retrospective.md

🔄 状态更新：
   - status: active → archived
   - maturity: applied → teachable
```

---

## 8. 幂等保证

- **init**：项目已存在则报错，不覆盖；幂等键 = slug
- **update**：同日多次 update 追加到同一 progress 文件，不覆盖
- **archive**：
  - 已补 actual/lesson 的 Decision Ledger 跳过，不重复询问
  - 已派生的 experience 检查 derived_from，避免重复创建
  - 已迁移到 archive/ 的项目二次 archive 报错

---

## 9. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| memory-agent 不可用（init） | 跳过「经验复用建议」段，标注「⚠ 未启用记忆召回」 |
| 库内 < 50 条（init） | memory-agent.proactive_suggest 自动关闭（限流）；README 段留空 |
| `principles/experiences/` 目录不存在（archive） | 自动创建（v0.3 已建） |
| Decision Ledger 模板缺失 | 报错并指引用户先运行 quick-kb-init 同步模板 |

---

## 10. 自检清单

### init

- [ ] projects/<slug>/ 创建完整子目录结构
- [ ] _readme.md 含 frontmatter（type: project, status: active）
- [ ] memory-agent 被调用（new_project_init 事件）
- [ ] 召回结果写入「经验复用建议」段（按 experience/pattern/principle 分类）
- [ ] 失败教训显式 ⚠ 标注
- [ ] 关联 goal 双向 wikilink

### update

- [ ] progress/ 追加新进展（不覆盖）
- [ ] _readme.md 的 updated 字段刷新

### archive

- [ ] 所有 Decision Ledger 的 actual/lesson 补全
- [ ] 每条 lesson 派生为独立 experience 笔记
- [ ] 派生 experience 含 derived_from + outcome + source.note
- [ ] 原 Decision Ledger 含 derived_to（双向引用）
- [ ] 项目目录迁移到 archive/projects/
- [ ] _readme.md status → archived, maturity → teachable
- [ ] 复盘草稿含 expected vs actual 偏差分析
- [ ] 派生的 experience 文件名唯一（slug + 日期）

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 新增 `update` 工作流的 progress/ 子目录 | SKILLS_SPEC §10 工作流只列 init/archive；但 DESIGN §8.4 提及项目应有进展记录 | docs/DESIGN.md §8.4 |
| 派生 experience 自动计算 outcome | SKILLS_SPEC §10 工作流第 2 步只说「派生 experience」，未指定 outcome；但 memory-agent 排序依赖 outcome（失败加权） | docs/AGENTS_SPEC.md §3.5 类型加权 |
| `_moc.md` 项目内索引页 | SKILLS_SPEC §10 工作流第 4 步明确要求 | docs/SKILLS_SPEC.md §10 |
| 不调 research-agent 做立项调研 | 项目立项的外部资料应先 capture/ingest 入库；advisor 阶段也不调外部 | docs/DESIGN.md §7 边界 |
