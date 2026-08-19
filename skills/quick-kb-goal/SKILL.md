---
name: quick-kb-goal
description: |
  目标管理 + 学习路径 + 进展记录 + 归档。create：调 quick-kb-research-agent 生成学习路径 + 调 quick-kb-memory-agent 召回领域 principle/belief；progress：追加 + 里程碑；complete/cancel：归档 + 状态传播。
  触发词（中文）：新建目标 / 学 X 这个目标 / 更新目标进度 / 完成目标
  Triggers (EN): new goal / learning path for / update goal progress
version: v1.12.0
phase: v0.3
applies_to: 写 03_goals/<slug>/ · 98_archive/goals/ · 读写相关笔记 status
source_of_truth:
  - docs/DESIGN.md §7.4
  - docs/SKILLS_SPEC.md §9
  - docs/AGENTS_SPEC.md §1（关系推荐规则）· §2（学习路径生成）· §3（经验召回规则）
  - docs/dev/v0.3-assistant.md WP6
  - references/filename-summary-rules.md（progress 文件名 summary 提炼）
---

# quick-kb-goal（v0.3）

> **目标全生命周期**：create → progress → complete/cancel。核心是 create 时调 `quick-kb-research-agent`（intent=`process_resource`/`summarize`）生成学习路径 + 调 `quick-kb-memory-agent`（intent=`recall_similar`）召回领域认知资产。

> ⚠ **写入硬约束（v1.10.3 · 无论读到本文档哪一段）**：写入的任何 `[[X]]`（goal.md / progress / 学习路径内）目标 X 必须已存在于 vault 文件名索引——不存在 → 降级为 `**X**` 加粗，**禁止写入死链**。规则全文见 [`references/write-validation-rules.md`](../../references/write-validation-rules.md) §2。

---

## 1. 何时调用

| 操作 | 触发词 |
|------|--------|
| `create` | 「新建目标 / 学 X 这个目标 / new goal」 |
| `progress` | 「更新目标进度 / update goal progress」 |
| `complete` | 「完成目标」 |
| `cancel` | 「取消目标」 |
| `path` | 「重新生成学习路径」 |

---

## 2. v0.3 范围

### 做

- create：建 goal.md + 调 `quick-kb-research-agent`（intent=`summarize`）生成学习路径 + 调 `quick-kb-memory-agent`（intent=`recall_similar`）召回领域 principle/belief
- progress：追加进展 + 里程碑勾选 + 路径动态调整建议
- complete/cancel：归档 + 状态传播 + 复盘联动

### 不做（v0.4+）

- 不调外部课程平台 API（学习路径基于库内 + 公开知识摘要）
- 不自动标完成（必须用户确认）

---

## 3. 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| 操作 `action` | 是 | `create` / `progress` / `complete` / `cancel` / `path` |
| 目标 `goal` | 是 | 名称（slug） |
| 描述 `description` | create 时必填 | 目标情境：为什么立这个目标 |
| 成功标准 `success_criteria` | create 时必填 | 可验证的完成标准 |
| 截止 `deadline` | 否 | YYYY-MM-DD |
| 领域 `domain` | 否 | 如 systems-programming（与 concept 笔记 domain 一致） |
| 路径来源 `path_source` | 否 | `recommend`（默认）/ `manual` |

---

## 4. 工作流 · create

```
1. 目标澄清：与用户确认
   - 目标一句话定义
   - 成功标准（可验证）
   - deadline
   - 关联领域 domain
   - 情境 context（为什么立这个目标）

2. 生成 03_goals/<slug>/goal.md（用 vault `99_system/templates/{lang}/goal.md`，由 init 铺设；v1.5 WP1 统一表述）：
   - title / context / deadline / domain
   - 成功标准（success_criteria）
   - 学习路径段：留空待 step 4
   - 里程碑段：基于 deadline 推算 3-5 个建议，用户确认
   - 进度记录段：留空
   - 关联项目段：留空

3. 建立子目录：
   03_goals/<slug>/
   ├── goal.md
   ├── _moc.md            # 目标内索引
   └── progress/          # 进展日志

4. 学习路径推荐（path_source=recommend）：
   4.1 调 `quick-kb-research-agent` intent=`summarize`（length=`detailed`）生成路径：
       - 入参/返回结构见 research-agent SKILL.md §0 契约
   4.2 库内关联：扫库内已存在的相关 concept 笔记（按 domain tag + 标题关键词匹配）
   4.3 路径节点写入 goal.md「学习路径」段：
       1. 基础概念（X 周） → [[已有 concept 1]] / [建议 Capture 缺口]
       2. 进阶主题（X 周） → [[已有 concept 2]]
       3. 实战项目（X 周） → [建议新开 project]

5. 主动召回（核心 · 调 `quick-kb-memory-agent` intent=`proactive_suggest`，event_type=`new_goal_create`）：
   - 入参/返回结构见 memory-agent SKILL.md §0 契约
   - 写入 goal.md「相关笔记」段：
      ### 领域原则
      - [[principle/xxx]] · 适用性
      ### 待验证假设
      - [[belief/yyy]]
      ### ⚠ 失败教训（如有）
      - [[experience/zzz]] · 教训：<lesson>

6. 询问关联项目（可选）：
   - 若用户已有相关 project，建立双向 wikilink
   - goal.md「关联项目」段 + project _readme「relations.supports」

7. 更新顶层 _moc.md：纳入新目标入口
```

### 4.1 写入前校验（v1.8 WP2 · 适用于 create / progress / complete / path 所有写入）

落盘前按 [`write-validation-rules.md`](../../references/write-validation-rules.md) 校验，任一失败 → 按规则修正后才写入，不得静默落盘不合规内容；无文件索引可查时在输出中 ⚠ 标注：

- **linked_principles / linked_goals 引用必须用实际文件名**：对照 vault 文件名索引，禁止别名或编号占位（如 `[[principle-001]]` → 须写实际文件名 `[[principle/<实际 basename>]]`）
- **decision 引用格式 `[[dec-001]]`，禁止双前缀**（如 `[[decisions/dec-001]]`）
- **wikilink 目标存在性**：所有写入的 `[[X]]`（学习路径节点 / 相关笔记段 / 进度记录 wikilink 等）目标必须已存在于库内

---

## 5. 工作流 · progress

```
1. 校验：03_goals/<slug>/ 存在

2. 追加进展：
   - progress/<YYYY-MM-DD>-<summary>.md（结构：完成 / 学到 / 想法 / 卡点）
     - **summary 提炼**严格按 [`filename-summary-rules.md`](../../references/filename-summary-rules.md) §2 机械判定：
       - **Step 1 强制纯日期清单**（命中任一即 `progress/<YYYY-MM-DD>.md`）：① 进展字段全空 ② 实质字符 < 5 ③ 仅元描述无事件词
       - **Step 2 未命中 → 必须提炼** 2-5 词 summary（语言跟随 vault 语言，zh 库保留中文如 `rag基线评估`；en 库 ASCII kebab-case 如 `chunk-eval-baseline` / `m2-done`，见 filename-summary-rules §5.3）
     - **禁止语义绕过**：严禁用「进展太短」「学习笼统」「里程碑完成不是主题」等借口退化为纯日期
     - 错误反例：输入「完成 milestone 2」→ ❌ `progress/2026-08-13.md`（借口「里程碑不是主题」）→ ✅ `progress/2026-08-13-m2-done.md`
     - 同日已有 `progress/<YYYY-MM-DD>*.md` → 编辑既有文件，不重新提炼 summary，不改名
   - 更新 goal.md 的 updated 字段
   - 在 goal.md「进度记录」段添加 wikilink（用实际文件 basename：`[[progress/YYYY-MM-DD-<summary>]]` 或 `[[progress/YYYY-MM-DD]]`）

3. 里程碑更新：
   - 询问用户：本次进展完成哪个里程碑？
   - 勾选对应 [x]
   - 若全部完成 → 提示用户考虑 complete

4. 路径动态调整：
   - 若用户进展明显快于/慢于预期 → 建议调整后续节点的预估周数
   - 若用户学到的新内容不在路径中 → 建议插入节点
   - 若路径某节点已通过其他方式掌握 → 建议跳过

5. 学习成果入库：
   - 若用户描述了学到的新概念 → 询问是否 quick-kb-ingest 为 concept 笔记
   - 若用户描述了踩坑 → 询问是否记录为 experience（独立于 project 也可）

6. 更新 _moc.md
```

---

## 6. 工作流 · complete / cancel

```
1. 用户确认：complete/cancel 必须二次确认（不自动）

2. 状态传播：
   - goal.md:
     · status: active → done（complete） / cancelled（cancel）
     · maturity: applied → teachable（complete，知识已掌握）
   - 关联项目（如有）：
     · 询问是否同步归档（不强制）
   - 相关 concept 笔记：
     · 若 status 是 draft → 建议转 active（学习产出已稳定）

3. 归档：
   03_goals/<slug>/ → 98_archive/goals/<slug>/
   （保留 progress 历史可追溯）

4. 复盘联动：
   生成 05_outputs/reviews/goal-<slug>-<YYYY-MM-DD>.md（草稿）：
   ## 目标复盘：<goal>
   ### 成功标准达成情况
   - [x] 标准 1 · 完成于 <date>
   - [ ] 标准 2 · 未达成（cancel 时）/ 部分达成
   ### 学习路径回顾
   - 实际耗时 vs 预估
   - 哪些节点最有价值
   - 哪些节点可以省略
   ### 后续行动
   - 是否要 Capture 这次学习的经验？
   - 是否要立进阶目标？

5. 引用清理（可选 · 调 `quick-kb-manager-agent` intent=`repair_deadlinks`；返回结构见其 §0）：
   - 顶层 _moc.md 移除目标入口或迁到 archive 区
   - 关联 project 的 relations.supports 标注「已达成/已取消」
```

---

## 7. 工作流 · path（重新生成路径）

```
1. 校验：03_goals/<slug>/goal.md 存在
2. 备份当前路径到 goal.md 的「路径历史」段（追加，不删除）
3. 重新调 `quick-kb-research-agent` intent=`summarize`（返回结构见其 §0）生成路径（基于当前库内笔记 + 已完成里程碑）
4. 新路径写入「学习路径」段
5. 询问用户：是否保留旧里程碑节点？
```

---

## 8. 输出示例

### create 成功输出

```
✅ 目标已创建：03_goals/<slug>/goal.md

🎯 成功标准：
   - [ ] 标准 1
   - [ ] 标准 2

🧠 认知资产召回（new_goal_create 事件）：
   - 领域原则: 2 条
   - 待验证假设: 1 条
   - 失败教训: 1 条
   已写入「相关笔记」段

📚 学习路径（由 quick-kb-research-agent 生成；规则见其 SKILL.md §3.4）：
   1. 基础（2 周） → [[已有 concept]] / [Capture 缺口: X]
   2. 进阶（3 周） → ...
   3. 实战（4 周） → [新开 project]

📅 里程碑：
   - M1：<...> · 2026-XX-XX
   - M2：<...> · 2026-XX-XX
```

### complete 成功输出

```
✅ 目标已完成：98_archive/goals/<slug>/

📊 里程碑达成：3/3
📝 复盘草稿：05_outputs/reviews/goal-<slug>-<date>.md

🔄 状态传播：
   - status: active → done
   - maturity: applied → teachable
   - 关联 concept（2 条）建议转 active
```

---

## 9. 幂等保证

- **create**：目标已存在则报错，不覆盖；幂等键 = slug
- **progress**：同日多次 progress 追加到同一文件，不覆盖
- **complete/cancel**：已归档的目标二次操作报错
- **path**：旧路径自动备份到「路径历史」段，不丢失

---

## 10. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 学习路径生成失败（create） | 学习路径降为 manual，goal.md 段标注「⚠ 路径推荐失败，请手动填写」 |
| `07_principles/` 目录不存在（create） | 跳过「相关笔记」段召回，标注「⚠ 未启用认知资产层」 |
| 库内 < 50 条（create） | 主动召回关闭（限流）；路径仅基于公开知识生成 |
| 无 embedding 服务 | similarity 按 [`scoring.md`](../../references/scoring.md)「无 embedding 降级相似度公式」计算（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4） |
| goal 模板缺失 | 报错并指引用户先运行 quick-kb-init 同步模板 |

---

## 11. 自检清单

### create

- [ ] 03_goals/<slug>/goal.md 创建
- [ ] frontmatter 含 type: goal, status: active, deadline, domain
- [ ] 成功标准可验证（非空泛描述）
- [ ] 学习路径生成（二选一 · v1.5 WP8）：
      · 正常态：调 quick-kb-research-agent（intent=summarize）
      · 降级态：goal.md 学习路径段标「⚠ 路径推荐失败，请手动填写」
- [ ] 认知资产召回（二选一 · v1.5 WP8）：
      · 正常态：调 quick-kb-memory-agent（intent=proactive_suggest，限定 07_principles/<domain>/）
      · 降级态：手动 Grep 07_principles/<domain>/ 全部 principle/belief + ⚠ 标注
- [ ] 学习路径每节点关联库内笔记 OR 标 [Capture 缺口]
- [ ] 写入前校验（§4.1）已执行（引用实际文件名 / decision 引用无双前缀 / wikilink 目标存在）
- [ ] 里程碑 3-5 个，每个带目标日期
- [ ] _moc.md 创建

### progress

- [ ] progress/<date>.md 追加（不覆盖）
- [ ] **新建 progress 文件名含 summary 段**（除非 §5 步骤 2 Step 1 命中纯日期条件）
- [ ] **未用「进展太短 / 学习笼统 / 里程碑不是主题」等语义借口退化纯日期**
- [ ] 同日已有 progress 文件时，编辑不改名
- [ ] goal.md「进度记录」段添加 wikilink
- [ ] 里程碑勾选状态正确

### complete / cancel

- [ ] 用户二次确认
- [ ] goal.md status/maturity 更新
- [ ] 目录迁移到 98_archive/goals/
- [ ] 复盘草稿生成
- [ ] 状态传播至关联笔记（询问而非强制）

---

## 12. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 新增 `path` 工作流（重新生成） | SKILLS_SPEC §9 未列 path action 但 dev doc WP6 提及「路径动态调整」 | docs/dev/v0.3-assistant.md WP6 关键点 |
| complete 时关联项目归档需询问 | SKILLS_SPEC §10 同样设计，避免目标完成时强制归档进行中项目 | docs/SKILLS_SPEC.md §10 边界 |
| 复盘草稿路径用 05_outputs/reviews/ | SKILLS_SPEC §9 工作流第 2 步明确 | docs/SKILLS_SPEC.md §9 |
| 认知资产召回限 domain 内 | DESIGN §7.6 new_goal_create 示例「关联领域 [[前端工程]] 有 2 条原则」 | docs/DESIGN.md §7.6 |
