---
name: quick-kb-project
description: |
  项目全生命周期管理。init：建目录 + README + 主动召回相似项目经验；update：追加进展；archive：补 Decision Ledger + lesson 派生 experience + 迁移归档。
  触发词（中文）：开个项目 / 项目 X / 归档项目
  Triggers (EN): new project / archive project
version: v1.8.2
phase: v0.3
applies_to: 写 04_projects/<slug>/ · 98_archive/projects/ · 07_principles/experiences/（派生）
source_of_truth:
  - docs/DESIGN.md §7.4 / §8.4（Decision Ledger）
  - docs/SKILLS_SPEC.md §10
  - docs/AGENTS_SPEC.md §3 / §3.8
  - docs/dev/v0.3-assistant.md WP5
  - references/filename-summary-rules.md（progress 文件名 summary 提炼）
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

- init：建目录 + README + Decision Ledger 骨架 + 调 `quick-kb-memory-agent` 召回相似项目经验
- update：追加进展到 `progress/`，更新 _moc.md
- **archive 闭环（核心）**：
  1. 扫 `decisions/`，补全每条 Decision Ledger 的 `actual` 与 `lesson`
  2. 每条 lesson 自动派生为独立 `experience` 笔记
  3. 原 decision 建立指向派生 experience 的 wikilink（`derived_from`）
  4. 项目目录迁移到 `98_archive/projects/<slug>/`
  5. 生成归档复盘草稿（expected vs actual 偏差分析）

### 不做（v0.4+）

- 不做项目立项调研（外部资料由 capture/ingest 先入库）
- 不写 review 周报（归 review 技能）

---

## 3. 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 操作 `action` | 是 | `init` / `update` / `archive` |
| 项目 `project` | 是 | 名称（slug） |
| 描述 `description` | init 时必填 | 项目要解决什么问题 |
| 关联目标 `goal` | 否 | goal slug |
| 模板 `template` | 否 | 默认读 vault `99_system/templates/{lang}/project.md`（由 init 铺设；v1.5 WP1 统一表述） |
| 归档复盘 `retrospective` | archive 时可选 | 是否生成复盘草稿 |

---

## 4. 工作流 · init

```
1. 校验：04_projects/<slug>/ 不存在（幂等：已存在则报错并指引用 update）

2. 创建结构：
   04_projects/<slug>/
   ├── _readme.md         # 用 99_system/templates/{lang}/project.md（v1.5 WP1）
   ├── _moc.md            # 项目内索引
   ├── notes/             # 项目笔记
   ├── decisions/         # Decision Ledger
   ├── progress/          # 进展日志
   └── refs/              # 参考资料 wikilink

3. 填充 _readme.md：
   - title / context / deadline / domain
   - relations.supports: [<关联 goal>]
   - 留空：经验复用建议（待 step 5 填）

4. 主动召回（核心 · 调 `quick-kb-memory-agent` intent=`proactive_suggest`，event_type=`new_project_init`）：
   - 入参/返回结构见 memory-agent SKILL.md §0 契约
   - 限流：库内 < 50 条时关闭；同事件去重

5. 把召回结果写入 _readme.md 的「经验复用建议」段：
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
   - **DECISION 编号规则（v1.7 WP5-E）**：
     - 项目内自增，格式 `DEC-001` / `DEC-002` ...
     - 跨项目不重复利用编号
     - 归档时编号保留

7. 询问关联 goal（若 goal 提供）：
   - 在 _readme.md 的 relations.supports 引用
   - 在 03_goals/<goal-slug>/goal.md 的「关联项目」段引用本项目

8. 更新顶层 _moc.md（若有）加入项目入口
```

### 4.1 写入前校验（v1.8 WP2 · 适用于 init / update / archive 所有写入）

落盘前按 [`write-validation-rules.md`](../../references/write-validation-rules.md) 校验，任一失败 → 按规则修正后才写入，不得静默落盘不合规内容；无文件索引可查时在输出中 ⚠ 标注：

- **linked_principles / relations.supports（关联 goal）引用必须用实际文件名**：对照 vault 文件名索引，禁止别名或编号占位（如 `[[principle-001]]` → 须写实际文件名 `[[principle/<实际 basename>]]`）
- **decision 引用格式 `[[dec-001]]`，禁止双前缀**（如 `[[decisions/dec-001]]`）
- **wikilink 目标存在性**：经验复用段、派生 experience、`derived_from` / `derived_to` 等所有 `[[X]]` 目标必须已存在于库内

---

## 5. 工作流 · update

```
1. 校验：04_projects/<slug>/ 存在

2. 追加进展：
   - progress/<YYYY-MM-DD>-<summary>.md（用 daily 模板简化版）
     - **summary 提炼**严格按 [`filename-summary-rules.md`](../../references/filename-summary-rules.md) §2 机械判定：
       - **Step 1 强制纯日期清单**（命中任一即 `progress/<YYYY-MM-DD>.md`）：① 进展字段全空 ② 实质字符 < 5 ③ 仅元描述无事件词
       - **Step 2 未命中 → 必须提炼** 2-5 词 ASCII kebab-case（如 `auth-impl` / `demo-dry-run` / `vector-db-blocker` / `m2-done`）
     - **禁止语义绕过**：严禁用「进展太短」「卡点描述笼统」「里程碑完成不是主题」等借口退化为纯日期
     - 错误反例：输入「今天实现了登录流程」→ ❌ `progress/2026-08-13.md`（借口「实现太简单」）→ ✅ `progress/2026-08-13-auth-impl.md`
     - 错误反例：输入「卡在向量库选型上」→ ❌ 纯日期（借口「卡点太短」）→ ✅ `progress/2026-08-13-vector-db-blocker.md`
     - 同日已有 `progress/<YYYY-MM-DD>*.md` → 编辑既有文件，不重新提炼 summary，不改名
   - 含：完成 / 卡点 / 下一步

3. 更新 _readme.md：
   - updated: <date>
   - 里程碑勾选（若用户提供）
   - 关键决策若变化 → 在 decisions/ 新增 Decision Ledger

4. 更新 _moc.md：纳入新笔记的索引

5. Decision Ledger 回填提醒（输出报告段）：
   扫描 decisions/*.md，对 frontmatter 中 actual: "" 或 lesson: "" 的条目：
   - N 天 = today - decision.created_at（created_at 取文件名日期或 frontmatter date 字段）
   - 在 update 输出报告中列出：
     「⏳ DEC-00X 实施已 N 天，请回填 actual/lesson」
   - 若无未回填条目 → 输出「✅ 所有 Decision Ledger 已回填」
```

---

## 6. 工作流 · archive（核心闭环）

```
1. 状态检查：
   - 扫描 decisions/，列出 actual / lesson 仍为空的 Decision Ledger
   - 列出 notes/ 未关联 _moc 的笔记
   - 提示用户：「以下决策尚未补 actual/lesson，是否在归档前补齐？」

1.5 归档前置门控（未回填 Decision Ledger 拦截）：
   若步骤 1 扫描到以下任一情况的 Decision Ledger 条目（v1.5 WP4 · 字段缺失与空字符串等价）：
   - actual 字段缺失 OR actual == "" OR actual == null
   - lesson 字段缺失 OR lesson == "" OR lesson == null
   - ⛔ 中止归档，输出警告：
     「⚠ 以下 Decision Ledger 尚未回填 actual/lesson：
       - DEC-00X（<title>）actual: <状态> lesson: <状态>
       ...
      请先补齐，或对无需回填的决策填写 lesson: skipped，
      或使用 --force 强制归档。」
   - 用户须满足以下任一条件才能继续归档：
     a) 所有 Decision Ledger 的 actual 与 lesson 均已回填（含 lesson: skipped）
     b) 显式传入 --force 参数（跳过拦截，但警告仍写入归档日志）
   - 幂等：二次调用若条件已满足则直接放行，不重复警告

2. 决策闭环（对每条 Decision Ledger）：
   2.1 补 actual（如未填）：与用户交互询问「实际结果如何？」
   2.2 补 lesson（如未填）：与用户交互询问「从这次决策中学到什么？」
   2.3 计算 outcome（基于 actual vs expected · v1.5 WP4 关键字清单明示）：
       - success：actual 显著好于 expected，OR actual 文本命中关键字
         「超预期 / 显著好于 / 提前完成 / 优于 expected / 顺利 / 一次过 / 已落地」
       - failure：actual 显著差于 expected，OR actual 文本命中关键字
         「未达成 / 显著差于 / 回滚 / 失败 / 延期严重 / 放弃 / 重做」
       - mixed：actual 文本命中「部分 OK / 部分 miss / 混合 / 一半 / 局部」，OR 部分 expected 达成部分未达成
       - 多个候选关键字命中冲突时：failure 优先（保守判定）

3. lesson 派生 experience（V2 关键 · v1.5 WP4 支持多对一）：
   对每条 Decision Ledger 的 lesson：
   3.1 派生判定（v1.5 WP4 · 多对一合并）：
       对当前 decision 的 lesson，先判定是否与已派生的某条 experience 主题重合：
       - 重合条件：同 domain AND lesson 含相同主题词（如「认证」「选型」「重试」）
       - 重合 → 并入既有 experience：
         · experience 文件「事件经过」段追加本 decision 摘要
         · experience.relations.derived_from 追加本 decision wikilink（list 追加，幂等）
         · outcome 若与既有 experience 的 outcome 冲突 → experience 升级为 mixed
       - 不重合 → 走 3.2 新建流程
   3.2 新建 experience（不重合时）：
       在 07_principles/experiences/<YYYY-MM-DD>-<topic>.md 创建新笔记（用 experience.md 模板）
   3.3 填充关键字段（无论新建还是并入，确保以下字段齐全）：
       - title: <事件一句话 · 含时间/项目>
       - context: <原 decision 的 problem + 项目 context>
       - 事件经过: <原 decision 的 options/chosen/reason 摘要>
       - 结果: <原 decision 的 actual>
       - 教训: <原 decision 的 lesson>  ← 核心派生
       - relations.derived_from: [<原 decision wikilink>, ...]   ← v1.5 WP4 · 必为 YAML list
       - outcome: step 2.3 计算结果
       - source.note: [[<原 decision>]]
       - tags: [experience/<topic>, project/<slug>]
   3.4 在原 Decision Ledger 中：
       - 添加 relations.derived_to: [<新 experience wikilink>]（双向引用 · v1.5 WP4 · 必为 YAML list）
       - status: active → archived
   3.5 检查可升格：lesson 中是否含可抽象的 principle/pattern 候选
       - 若用户确认 → 在 07_principles/principles/ 或 07_principles/patterns/ 新建
       - relations.evolves: [[<派生 experience>]]
   3.6 contradicts 消解扫描（保守启发式 · 宁可漏消解不误消解）：
       遍历本项目 Decision Ledger 的所有 lesson，对每条 lesson：
       a) 全库扫描 frontmatter relations.contradicts 对，收集现存矛盾对列表
       b) 对每对矛盾（笔记 A ↔ 笔记 B），检查 lesson 文本是否同时提及
          A 与 B 双方——命中条件（全部满足才视为消解）：
          · lesson 中出现 A 的笔记 title（或 wikilink [[A]]），且
          · lesson 中出现 B 的笔记 title（或 wikilink [[B]]），或
          · lesson 中同时命中 A 与 B 的 domain 关键词
            （domain 关键词 = 双方 frontmatter domain 字段的交集词）
       c) 若 lesson 同时命中双方 → 视为该 lesson 消解此矛盾对：
          · 在笔记 A 与笔记 B 的 frontmatter 追加：
            relations.resolved_by: [[07_principles/experiences/<派生 experience>]]
          · 在笔记 A 与笔记 B 的 context 段追加标注：
            「已由 [[07_principles/experiences/<派生 experience>]] 消解
             （场景：<lesson 一句话摘要>）」
       d) 若 lesson 仅命中一方 → 不动（宁可漏消解不误消解）
       e) 幂等：笔记 frontmatter 已含 resolved_by 指向同一 experience → 跳过

4. 迁移目录：
   04_projects/<slug>/ → 98_archive/projects/<slug>/
   （保留所有子目录与 wikilink 完整性）

5. 更新 _readme.md：
   - status: active → archived
   - maturity: applied → teachable
   - 归档日期字段
   - 派生 experience 索引

6. 归档复盘草稿（可选 · retrospective=true）：
   在 98_archive/projects/<slug>/retrospective.md 生成：
   ## 决策复盘
   | 决策 | expected | actual | 偏差 | lesson → experience |
   |------|---------|--------|------|---------------------|
   | [[decisions/001]] | ... | ... | ±X% | [[experience/...]] |

7. 引用清理（可选 · 调 `quick-kb-manager-agent` intent=`repair_deadlinks`；返回结构见其 §0）：
   - 顶层 _moc.md 移除项目入口或迁到 archive 区
   - goal 的「关联项目」段标注「已归档」
```

---

## 7. 输出示例

### init 成功输出

```
✅ 项目已创建：04_projects/<slug>/
   - _readme.md（已填充基础字段）
   - _moc.md（索引骨架）
   - notes/ decisions/ progress/ refs/（空目录）

🧠 经验召回（new_project_init 事件 · 由 quick-kb-memory-agent 执行；规则见其 SKILL.md §3.4）：
   - 高相关 experience: 2 条
   - 可应用 pattern: 1 条
   - 失败教训: 1 条
   已写入 _readme.md「经验复用建议」段

📝 首条 Decision Ledger（可选）：
   - decisions/<YYYY-MM-DD>-<topic>.md 已创建（待补 actual/lesson）

🔗 关联目标：
   - 03_goals/<goal-slug>/goal.md 已添加项目引用
```

### archive 成功输出

```
✅ 项目已归档：98_archive/projects/<slug>/

📋 决策闭环：
   - 补全 Decision Ledger: 3 条
   - 派生 experience 笔记: 3 条
     - [[experience/2026-XX-XX-xxx]]
     - [[experience/2026-XX-XX-yyy]]
     - [[experience/2026-XX-XX-zzz]]

🔗 contradicts 消解（若命中）：
   - [[concept/A]] ↔ [[concept/B]] 已由 [[experience/2026-XX-XX-xxx]] 消解
   - 已写入双方 resolved_by + context.conflict_note

📊 复盘草稿：98_archive/projects/<slug>/retrospective.md

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
  - 已迁移到 98_archive/ 的项目二次 archive 报错

---

## 9. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| `07_principles/` 目录不存在（init） | 跳过「经验复用建议」段，标注「⚠ 未启用认知资产层」 |
| 库内 < 50 条（init） | 主动召回关闭（限流）；README 段留空 |
| 无 embedding 服务 | similarity 按 [`scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」计算（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4） |
| `07_principles/experiences/` 目录不存在（archive） | 自动创建（v0.3 已建） |
| Decision Ledger 模板缺失 | 报错并指引用户先运行 quick-kb-init 同步模板 |

---

## 10. 自检清单

### init

- [ ] 04_projects/<slug>/ 创建完整子目录结构
- [ ] _readme.md 含 frontmatter（type: project, status: active）
- [ ] 经验召回（二选一 · v1.5 WP8）：
      · 正常态：调 quick-kb-memory-agent（intent=proactive_suggest，new_project_init 事件）
      · 降级态：手动 Grep `07_principles/experiences/` 全部失败案例 + ⚠ 标注（库内 < 50 条时关闭）
- [ ] 召回结果写入「经验复用建议」段（按 experience/pattern/principle 分类）
- [ ] 失败教训显式 ⚠ 标注
- [ ] 关联 goal 双向 wikilink
- [ ] 写入前校验（§4.1）已执行（引用实际文件名 / decision 引用无双前缀 / wikilink 目标存在）

### update

- [ ] progress/ 追加新进展（不覆盖）
- [ ] **新建 progress 文件名含 summary 段**（除非 §5 步骤 2 Step 1 命中纯日期条件）
- [ ] **未用「进展太短 / 卡点笼统 / 里程碑不是主题」等语义借口退化纯日期**
- [ ] 同日已有 progress 文件时，编辑不改名
- [ ] _readme.md 的 updated 字段刷新
- [ ] Decision Ledger 回填提醒：扫描 actual/lesson 为空的条目并输出「⏳ DEC-00X 实施已 N 天」

### archive

- [ ] 归档前置门控：未回填 Decision Ledger 存在时中止归档（除非 --force 或 lesson: skipped）
- [ ] **字段缺失与空字符串等价拦截**（v1.5 WP4 · actual/lesson 缺失 OR == "" OR == null）
- [ ] 所有 Decision Ledger 的 actual/lesson 补全
- [ ] **Decision Ledger 文件名统一为 `<YYYY-MM-DD>-<topic>.md`**（v1.5 WP4 · 禁用 NNN 序号制）
- [ ] 每条 lesson 派生为独立 experience 笔记 OR 并入同主题既有 experience（v1.5 WP4 · 多对一）
- [ ] 派生 experience 的 `relations.derived_from` **必为 YAML list**（v1.5 WP4）
- [ ] 原 Decision Ledger 的 `relations.derived_to` **必为 YAML list**
- [ ] outcome 计算关键字命中冲突时 failure 优先（保守判定 · v1.5 WP4）
- [ ] contradicts 消解扫描：lesson 同时命中双方才标记 resolved_by；仅命中一方不动
- [ ] resolved_by 双向写入 + context.conflict_note 标注
- [ ] 项目目录迁移到 98_archive/projects/
- [ ] _readme.md status → archived, maturity → teachable
- [ ] 复盘草稿含 expected vs actual 偏差分析
- [ ] 派生的 experience 文件名唯一（slug + 日期）

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 新增 `update` 工作流的 progress/ 子目录 | SKILLS_SPEC §10 工作流只列 init/archive；但 DESIGN §8.4 提及项目应有进展记录 | docs/DESIGN.md §8.4 |
| 派生 experience 自动计算 outcome | SKILLS_SPEC §10 工作流第 2 步只说「派生 experience」，未指定 outcome；但召回排序依赖 outcome（失败加权） | docs/AGENTS_SPEC.md §3.5 类型加权 |
| `_moc.md` 项目内索引页 | SKILLS_SPEC §10 工作流第 4 步明确要求 | docs/SKILLS_SPEC.md §10 |
| 不做项目立项调研 | 项目立项的外部资料应先 capture/ingest 入库；advisor 阶段也不调外部 | docs/DESIGN.md §7 边界 |
