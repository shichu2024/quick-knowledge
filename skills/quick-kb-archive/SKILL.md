---
name: quick-kb-archive
description: |
  通用归档技能。安全归档任意对象（不限于 project/goal）：concept/resource/idea/decision 等。
  状态检查 → 迁移到 98_archive/ → 更新指向归档对象的 wikilinks（避免死链）→ 可恢复。
  与 v0.3 project.archive 不同：本技能不触发 lesson 派生，纯归档操作。
  触发词（中文）：归档 / archive / 把 X 收起来
  Triggers (EN): archive / put away / move to archive
version: v0.4
phase: v0.4
applies_to: 写 98_archive/ · 更新 wikilinks · 不删笔记
source_of_truth:
  - docs/DESIGN.md §10 / §6.1（status 流转）
  - docs/SKILLS_SPEC.md §11
  - docs/AGENTS_SPEC.md §1
  - docs/dev/v0.4-extensions.md WP2
---

# quick-kb-archive（v0.4）

> **通用归档**：任意对象的归档操作。与 v0.3 `quick-kb-project archive` 区别：
>
> | 技能 | 适用对象 | 是否派生 experience | 是否更新 status |
> |------|---------|-------------------|---------------|
> | `quick-kb-project archive` | 项目（含 decisions/） | ✅ Decision Ledger → experience | status → archived |
> | `quick-kb-archive`（本技能） | 任意对象（concept/resource/idea/...） | ❌ 纯归档 | status → archived |

---

## 1. 何时调用

- 用户说「归档这条笔记 / archive [[X]] / 把这些收起来」
- review 阶段建议归档低价值笔记后用户确认
- stats 显示「低复用高占用」清单后用户批量处理

**不调用**：
- 项目归档（→ quick-kb-project archive）
- 目标归档（→ quick-kb-goal complete/cancel）

---

## 2. v0.4 范围

### 做

- 状态检查（提醒未关闭的关联项）
- 迁移到 `98_archive/<type>/` 子目录
- 更新指向归档对象的 wikilinks
- status → archived
- 生成归档记录（archive_index）
- 可恢复（unarchive）

### 不做

- ❌ 不删除笔记（永远可恢复）
- ❌ 不派生 experience（归 project archive）
- ❌ 不改 frontmatter 的 relations 内容（仅 status）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| 目标 `target` | 是 | — | 笔记路径 / wikilink / 批量清单（逗号分隔） |
| 操作 `action` | 否 | `archive` | `archive` / `unarchive` / `check`（仅状态检查） |
| 原因 `reason` | 否 | — | 用户自定义归档原因（写入 archive_index） |

---

## 4. 工作流 · archive

```
1. 解析 target：
   - 单条 / 多条 / wikilink 形式 [[X]]
   - 校验文件存在

2. 状态检查（check 阶段）：
   对每条 target：
   - 扫描其 relations.supports / evolves 的反向引用
   - 列出引用此笔记的其他笔记（manager_agent.repair_deadlinks 子能力）
   - 提醒：
     · 「[[X]] 被 [[Y]] / [[Z]] 引用，归档后这些引用会标注『已归档』」
     · 「[[X]] 有未关闭的 decision（若 type=decision）→ 建议先走 project archive」

3. 与用户确认（必须）：
   - 列出影响（被引用数、关联未关闭项）
   - 询问：是否继续？
   - 用户确认后进入迁移

4. 迁移：
   - 决定目标路径：98_archive/<type>/<原相对路径>
     · 98_archive/concepts/<...>
     · 98_archive/resources/<...>
     · 98_archive/ideas/<...>
     · 98_archive/decisions/<...>（孤立 decision，非项目内）
     · 98_archive/materials/<...>（过期素材）
   - 移动文件（保留原相对结构）

5. 更新原笔记 frontmatter：
   - status: active/draft → archived
   - updated: <date>
   - 追加 archive_meta 段（v0.4 新增可选字段）：
     archived_at: <date>
     archive_reason: <reason>

6. 更新指向此笔记的 wikilinks（关键）：
   - 扫描全库含 [[X]] 的笔记
   - 在每处添加标注：「[[X]] (已归档)」
   - 不删除 wikilink（保持可追溯）
   - 若 dead link 严格模式开启（kb.config.yaml）→ 改为 [[98_archive/<type>/X|X (已归档)]]

7. 写入 archive_index：
   98_archive/_index.md 追加：
   - [[98_archive/<type>/<原路径>|<title>]] · 归档于 <date> · 原因：<reason>

8. 输出汇总报告
```

---

## 5. 工作流 · unarchive

```
1. 解析 target（同 archive）

2. 反向迁移：
   98_archive/<type>/<...> → <原路径>
   - 从 archive_meta 读原路径（若记录）
   - 若原路径已不存在 → 恢复到原位置
   - 若原路径已被新笔记占用 → 询问用户（覆盖 / 重命名 / 取消）

3. 更新 frontmatter：
   - status: archived → active（或原值，若 archive_meta 记录）
   - 移除 archive_meta 段
   - updated: <date>

4. 更新 wikilinks：
   - 移除「(已归档)」标注
   - 恢复 [[X]] 原形

5. 从 98_archive/_index.md 移除条目

6. 输出报告
```

---

## 6. 工作流 · check（仅检查）

```
1. 解析 target
2. 跑 §4 的 step 2（状态检查）
3. 输出影响报告（不执行归档）

适用：用户先看影响再决定是否 archive
```

---

## 7. 输出示例

### archive 成功

```
✅ 已归档：3 条笔记

📋 处理详情：
   - [[concept/X]] → 98_archive/concepts/X.md
     · 被 5 处引用 → 已标注「(已归档)」
     · status: active → archived
   - [[resource/Y]] → 98_archive/resources/Y.md
     · 被 0 处引用（无影响）
   - [[idea/Z]] → 98_archive/ideas/Z.md
     · 被 2 处引用 → 已标注

📝 archive_index 已更新：98_archive/_index.md
```

### unarchive 成功

```
✅ 已恢复：[[concept/X]] → concepts/X.md
   - status: archived → active
   - 5 处 wikilink 已恢复
   - 98_archive/_index.md 移除条目
```

### check 输出

```
🔍 归档影响预览（不执行）

将归档：3 条笔记
   - [[concept/X]]
     · ⚠ 被 5 处引用：[[Y1]] [[Y2]] [[Y3]] [[Y4]] [[Y5]]
     · 这些引用将标注「(已归档)」
   - [[decision/D]]
     · ⚠ 含未关闭 decision（actual/lesson 未填）
     · → 建议先 quick-kb-project archive（可派生 experience）

→ 确认后运行 quick-kb-archive action=archive
```

---

## 8. 幂等保证

- **archive**：已归档的笔记二次归档报错（不重复迁移）
- **unarchive**：非 archived 状态的笔记无法 unarchive
- **wikilink 标注**：已含「(已归档)」的不重复添加

---

## 9. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| manager-agent 不可用 | wikilink 扫描降为全库 Grep `[[X]]` |
| 98_archive/ 目录不存在 | 自动创建 |
| archive_meta 字段缺失 | unarchive 时询问用户原位置 |
| 原路径被占用（unarchive） | 询问用户：覆盖 / 重命名 / 取消 |

---

## 10. 自检清单

- [ ] target 解析正确（单条/多条/wikilink）
- [ ] check 模式不执行归档
- [ ] archive 前用户确认（必须）
- [ ] 迁移到正确的 98_archive/<type>/ 子目录
- [ ] frontmatter status → archived
- [ ] archive_meta 段记录 archived_at + reason + 原路径
- [ ] 指向归档对象的 wikilinks 全部标注「(已归档)」
- [ ] 98_archive/_index.md 追加条目
- [ ] unarchive 完整恢复（含 wikilink）
- [ ] 已归档笔记二次归档报错
- [ ] decision 类型提醒先走 project archive

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 新增 archive_meta 字段（archived_at / reason / 原路径） | dev doc 要求「可恢复」，需记录原位置 | docs/dev/v0.4-extensions.md WP2 |
| wikilink 标注「(已归档)」而非删除 | dev doc 要求「不删除可恢复」+「不产生死链」 | docs/dev/v0.4-extensions.md WP2 + DESIGN §10 |
| 新增 check / unarchive action | dev doc 要求「可恢复」，unarchive 为反向操作；check 为预览 | docs/dev/v0.4-extensions.md WP2 |
| 不派生 experience | 与 project archive 区分；纯归档无 lesson 闭环 | docs/SKILLS_SPEC.md §11 边界 |
