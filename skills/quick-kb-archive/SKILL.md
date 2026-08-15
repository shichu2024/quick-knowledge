---
name: quick-kb-archive
description: |
  通用归档技能。安全归档任意对象（不限于 project/goal）：concept/resource/idea/decision 等。
  状态检查 → 迁移到 98_archive/ → 更新指向归档对象的 wikilinks（避免死链）→ 可恢复。
  通用归档不派生 experience；仅当归档对象 type=project 时，执行 lesson → experience 草稿半自动化（status: draft，需用户确认后激活）。
  触发词（中文）：归档 / archive / 把 X 收起来
  Triggers (EN): archive / put away / move to archive
version: v1.8.2
phase: v0.4
applies_to: 写 98_archive/ · 更新 wikilinks · 不删笔记
source_of_truth:
  - docs/DESIGN.md §10 / §6.1（status 流转）
  - docs/SKILLS_SPEC.md §11
  - docs/AGENTS_SPEC.md §1
  - docs/dev/v0.4-extensions.md WP2
  - references/wikilink-conventions.md（v1.6 · 归档后缀约定）
  - references/json-canvas-schema.md（v1.6 · canvas 节点归档处理）
---

# quick-kb-archive（v0.4）

> **通用归档**：任意对象的归档操作。与 v0.3 `quick-kb-project archive` 区别：
>
> | 技能 | 适用对象 | 是否派生 experience | 是否更新 status |
> |------|---------|-------------------|---------------|
> | `quick-kb-project archive` | 项目（含 decisions/） | ✅ Decision Ledger → experience | status → archived |
> | `quick-kb-archive`（本技能） | 任意对象（concept/resource/idea/...） | 仅 project 类型派生（草稿，步骤 10） | status → archived |

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
- **copy + stub 模式归档**（v1.5 WP5 定档）：
  - 原位置保留 stub 文件（frontmatter 加 `status: archived` + `archive_meta.redirect_to: [[98_archive/<type>/<slug>]]` + 正文一行「已归档，见 [[...]]」）
  - 完整内容复制到 `98_archive/<type>/<slug>.md`
  - 理由：保留 wikilink 解析路径（原位置仍可访问），断链率最低；stub 是显式标记，不依赖隐式元数据
- 更新指向归档对象的 wikilinks（target 字符串加「(已归档)」后缀）
- status → archived
- 生成归档记录（archive_index）
- 可恢复（unarchive）

### 不做

- ❌ 不删除笔记（永远可恢复）
- ❌ 通用类型不派生 experience → 仅 type=project 时派生 experience 草稿（步骤 10，v1.7 WP7-D）
- ❌ 不改 relations 的**类型结构**（supports 仍 supports）—— 但 relations 内的 **target 字符串**可加「(已归档)」后缀（v1.5 WP5 边界澄清）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| 目标 `target` | 是 | — | 笔记路径 / wikilink / 批量清单（逗号分隔） |
| 操作 `action` | 否 | `archive` | `archive` / `unarchive` / `check`（仅状态检查） |
| 原因 `reason` | 否 | — | 用户自定义归档原因（写入 archive_index）；**v1.7 WP5-F：建议从 kb.config.yaml 的 archive_reasons 词表中选择** |

---

## 4. 工作流 · archive

```
1. 解析 target：
   - 单条 / 多条 / wikilink 形式 [[X]]
   - 校验文件存在

2. 状态检查（check 阶段）：
   对每条 target：
   - 扫描其 relations.supports / evolves 的反向引用
   - 列出引用此笔记的其他笔记（调 `quick-kb-manager-agent` intent=`repair_deadlinks`）
   - 提醒：
     · 「[[X]] 被 [[Y]] / [[Z]] 引用，归档后这些引用会标注『已归档』」
     · 「[[X]] 有未关闭的 decision（若 type=decision）→ 建议先走 project archive」

3. 与用户确认（必须）：
   - 列出影响（被引用数、关联未关闭项）
   - 询问：是否继续？
   - 用户确认后进入迁移

4. 迁移（**copy + stub 模式 · v1.5 WP5 定档**）：
   4.0 **goal/project status 传播（v1.7 WP7-C）**：
       - 若归档对象 type=goal：
         · 扫描 goal frontmatter.linked_projects（若存在）
         · 对每个关联 project：
           - 若 project status=active → 在报告提示「⚠ 关联 project <X> 仍 active，是否一并归档？」
           - 不自动归档（避免误操作），仅提示
       - 若归档对象 type=project：
         · 扫描 project 关联的 goal（通过 frontmatter.relations.supports）
         · 若 goal status=active → 在报告提示「⚠ 本项目关联的 goal <X> 仍 active，是否一并归档？」
         · 不自动归档，仅提示
   4.1 决定归档目标路径：98_archive/<type>/<原相对路径>
       · 98_archive/concepts/<...>
       · 98_archive/resources/<...>
       · 98_archive/ideas/<...>
       · 98_archive/decisions/<...>（孤立 decision，非项目内）
       · 98_archive/materials/<...>（过期素材）
   4.2 **copy**：完整内容复制到归档路径（保留原 frontmatter 全字段 + 正文）
   4.3 **stub**：原位置文件改写为 stub，含：
       - frontmatter：status: archived + updated: <date> + archive_meta 段（见 5）
       - 正文：仅一行「> 已归档，完整内容见 [[98_archive/<type>/<slug>]]」
       - 理由：保留原 wikilink 解析路径，断链率最低

5. 更新 stub frontmatter（原文件位置）：
   - status: active/draft → archived
   - updated: <date>
   - 追加 archive_meta 段（v0.4 + v1.5 WP5）：
     archived_at: <date>
     archive_reason: <reason>
     redirect_to: [[98_archive/<type>/<slug>]]   # v1.5 WP5 新增

6. 更新指向此笔记的 wikilinks（v1.5 WP5 边界澄清）：
   - 扫描全库含 [[X]] 的笔记（含 frontmatter.relations 内的 target 与正文 wikilink）
   - **relations 类型结构不动**（supports 仍 supports，evolves 仍 evolves）
   - **target 字符串可加后缀**：[[X]] → [[X]]（已归档）或改为 [[98_archive/<type>/X|X (已归档)]]
   - 不删除 wikilink（保持可追溯）
   - 严格模式（kb.config.yaml.dead_link_strict=true）→ 改为 path-qualified 形式
   - 幂等：已含「(已归档)」后缀的不再重复添加

7. 写入 archive_index（v1.5 WP5 命名统一）：
   98_archive/_archive-index.md 追加：
   - [[98_archive/<type>/<原路径>|<title>]] · 归档于 <date> · 原因：<reason>

8. canvas 节点处理（v1.6 WP9-3 · 若 vault 含 .canvas 文件）：
   扫描 `06_wiki/maps/*.canvas`，对每个引用归档笔记的节点（按 `file` 字段或 `id` 匹配 basename）：
   - `file` → 更新为 stub 路径（`02_areas/<domain>/<slug>.md`，原位置保留 stub）
   - `label` → 追加「 (已归档)」后缀
   - `color` → 改为 `"1"`（红 · 视觉提示已归档）
   - `id` → **保持不变**（稳定性约束，改名会破坏 edge 引用）
   - edges → **不动**（保留历史关系；归档不等于关系消失）
   详见 [`json-canvas-schema.md`](../../references/json-canvas-schema.md) §5
   - 若 vault 无 .canvas 文件 → 跳过本步，报告中不提示

9. contradicts 提示（concept 类型 · 仅提示不自动改）：
   若归档对象 type=concept 且其 frontmatter relations 含 contradicts 字段：
   - 列出该 concept 参与的所有 contradicts 对
   - 在汇总报告中标注：
     「⚠ [[concept/X]] 参与 contradicts 关系（对方：[[concept/Y]]）
      → 建议人工评估：归档后该矛盾对是否已被某 experience 消解？
      （archive 技能不知 lesson 上下文，不自动修改 relations）」

10. project archive lesson 派生半自动化（v1.7 WP7-D）：
    若归档对象 type=project：
    - 扫描项目 decisions/ 目录的 ADR 文件
    - 对每条含 lesson 字段的 ADR（lesson 非空/非 null）：
      · 在 07_principles/<domain>/ 生成 experience 笔记草稿
      · 草稿 frontmatter：
        - type: experience
        - status: draft（需用户确认后改为 active）
        - title: <ADR.lesson 一句话>
        - outcome: <ADR.actual>（若已填）
        - trigger: <ADR.context>
        - relations.derived_from: [[<原 ADR>]]
      · 草稿正文：
        - 事件经过：从 ADR.options + chosen + reason 提炼
        - 结果：ADR.actual
        - 教训：ADR.lesson
      · 在归档报告中列出：「📝 派生 experience 草稿：[[...]]」
    - 对不含 lesson 的 ADR 跳过，不生成草稿

11. 输出汇总报告
```

---

## 5. 工作流 · unarchive

```
1. 解析 target（同 archive · 支持归档副本路径或原 stub 路径）

2. 反向迁移（copy + stub 反向 · v1.5 WP5）：
   98_archive/<type>/<...> → <原路径>
   - 从 archive_meta.redirect_to 或 archive_meta 读原路径（若记录）
   - 用归档副本完整内容覆盖原 stub
   - 若原路径已被新笔记占用（非 stub）→ 询问用户（覆盖 / 重命名 / 取消）
   - 删除归档副本（unarchive 后归档路径不保留）

3. 更新 frontmatter（原位置恢复后的文件）：
   - status: archived → active（或原值，若 archive_meta 记录）
   - 移除 archive_meta 段
   - updated: <date>

4. 更新 wikilinks：
   - 移除「(已归档)」标注
   - 恢复 [[X]] 原形

5. 从 98_archive/_archive-index.md 移除条目（v1.5 WP5 命名统一）

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
   - [[concept/X]] → 98_archive/concepts/X.md（copy）+ 原位置保留 stub（v1.5 WP5）
     · 被 5 处引用 → wikilink target 加「(已归档)」后缀
     · status: active → archived
     · ⚠ 参与 contradicts（对方：[[concept/Y]]）→ 建议人工评估是否消解
   - [[resource/Y]] → 98_archive/resources/Y.md
     · 被 0 处引用（无影响）
   - [[idea/Z]] → 98_archive/ideas/Z.md
     · 被 2 处引用 → 已标注

📝 archive_index 已更新：98_archive/_archive-index.md（v1.5 WP5 命名统一）
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
| wikilink 索引不可用 | wikilink 扫描降为全库 Grep `[[X]]` |
| 98_archive/ 目录不存在 | 自动创建 |
| archive_meta 字段缺失 | unarchive 时询问用户原位置 |
| 原路径被占用（unarchive） | 询问用户：覆盖 / 重命名 / 取消 |

---

## 10. 自检清单

- [ ] target 解析正确（单条/多条/wikilink）
- [ ] check 模式不执行归档
- [ ] archive 前用户确认（必须）
- [ ] **copy + stub 模式**（v1.5 WP5）：归档副本完整 + 原位置 stub 含 redirect_to
- [ ] stub frontmatter 含 archive_meta 段（archived_at + reason + redirect_to）
- [ ] relations 类型结构不动，target 字符串加「(已归档)」后缀（v1.5 WP5 边界）
- [ ] 归档 index 命名为 `_archive-index.md`（v1.5 WP5 统一）
- [ ] frontmatter status → archived
- [ ] 指向归档对象的 wikilinks 全部标注「(已归档)」
- [ ] unarchive 完整恢复（含 wikilink + 移除归档副本 + 反向 canvas 处理）
- [ ] **canvas 节点归档处理**（v1.6 WP9-3 · 若 vault 含 .canvas）：file 指向 stub + label 含「(已归档)」+ color 改红 + id/edges 不动
- [ ] 已归档笔记二次归档报错
- [ ] decision 类型提醒先走 project archive
- [ ] concept 且含 contradicts 时报告中提示「建议人工评估是否消解」

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 新增 archive_meta 字段（archived_at / reason / 原路径） | dev doc 要求「可恢复」，需记录原位置 | docs/dev/v0.4-extensions.md WP2 |
| wikilink 标注「(已归档)」而非删除 | dev doc 要求「不删除可恢复」+「不产生死链」 | docs/dev/v0.4-extensions.md WP2 + DESIGN §10 |
| 新增 check / unarchive action | dev doc 要求「可恢复」，unarchive 为反向操作；check 为预览 | docs/dev/v0.4-extensions.md WP2 |
| 仅 type=project 派生 experience 草稿（其余类型不派生） | 与 project archive 区分：通用归档无 lesson 闭环；project 类型走步骤 10 草稿半自动化（v1.7 WP7-D） | docs/SKILLS_SPEC.md §11 边界 + docs/dev/v1.7-automation-and-integration.md WP7 |
| v1.5 WP5 定档 copy + stub 模式 | 原 spec 「迁移」语义模糊（move vs copy）；copy+stub 保留原 wikilink 解析路径，断链率最低 | docs/dev/v1.5-cross-skill-consistency.md WP5 |
| v1.5 WP5 relations 边界澄清 | 「不改 relations」原指类型结构不动；target 字符串加后缀属 wikilink 维护范畴 | 同上 |
| v1.5 WP5 index 命名统一 `_archive-index.md` | 原 `_index.md` 与目录默认索引混淆 | 同上 |
| v1.6 WP9-3 增加 canvas 节点归档处理 | 原 spec 未定义 canvas 节点处理；stub 模式下 file 指向 stub 保证 Obsidian 双击仍能打开 | docs/dev/v1.5-cross-skill-consistency.md WP9 + references/json-canvas-schema.md §5 |
