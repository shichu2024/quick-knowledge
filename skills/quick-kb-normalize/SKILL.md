---
name: quick-kb-normalize
description: |
  批量规整历史笔记。补全 frontmatter、归一标签（对照受控词表）、related→relations 迁移、标题规范化（kebab-case 文件名）。
  幂等（多次运行结果一致）+ 可解释（每条改动带 why）+ 可回滚（写 diff 到 _normalize_log/）+ dry-run 预览。
  触发词（中文）：规整笔记 / normalize / 批量修复 / 迁移 related
  Triggers (EN): normalize notes / batch fix frontmatter / migrate related field
version: v0.4
phase: v0.4
applies_to: 读写 frontmatter（不改正文）· 跨 inbox / areas / principles
source_of_truth:
  - docs/DESIGN.md §4.2 / §6.7
  - docs/SKILLS_SPEC.md §11
  - docs/AGENTS_SPEC.md §1
  - docs/dev/v0.4-extensions.md WP1
  - references/v0.4-deviation-check.md
---

# quick-kb-normalize（v0.4）

> **批量规整**：把旧笔记（v0.1 / v0.2 / 外部导入）的 frontmatter 升级到当前版本格式。
>
> **不改正文，仅元数据**。每条改动可解释、可回滚、幂等。

---

## 1. 何时调用

- 用户说「规整笔记 / normalize / 批量修复 frontmatter」
- 升级 quick-knowledge 版本后首次运行（自动建议）
- 导入外部笔记（quick-kb-import）完成后建议运行

---

## 2. v0.4 范围

### 做

- 扫描指定范围（domain / 全库 / 仅旧版本笔记）
- 补全 frontmatter 缺失字段（取默认值 + 上下文推断）
- 归一标签（对照 `kb.config.yaml` tags_vocabulary）
- **`related` → `relations` 迁移**（V2 关键）
- 标题规范化（文件名 kebab-case）
- 写入 `_normalize_log/<YYYY-MM-DD>-<scope>.diff.md`
- 支持 `dry-run` 预览

### 不做

- ❌ 不改正文内容（仅 frontmatter）
- ❌ 不删除笔记
- ❌ 不重建 wikilink（归 connect/repair_deadlinks）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| 范围 `scope` | 否 | `all` | `all` / `<domain>` / `legacy`（仅 v0.1 旧笔记） |
| 操作 `action` | 否 | `run` | `run` / `dry-run`（仅预览不写入） / `rollback`（按 log 回滚） |
| 项 `items` | 否 | — | 指定具体笔记路径（逗号分隔），覆盖 scope |
| 跳过 `skip` | 否 | — | 跳过的检查项：`tags / relations / fields / filename` |

---

## 4. 工作流

```
1. 收集候选：
   - 按 scope 决定扫描范围
   - 若 scope=legacy：仅扫 frontmatter 含 version ≤ v0.1 OR 缺 version 的笔记

2. 对每条候选笔记执行（顺序）：

   2.1 字段补全（fields）：
       - type 缺失 → 推断（按路径：00_inbox/→idea, 07_principles/→按子目录）
       - status 缺失 → inbox / draft（按位置）
       - created / updated 缺失 → 取文件 mtime
       - confidence 缺失 → 50（默认）
       - maturity 缺失 → captured（v0.3+ 笔记）
       - value 缺失 → { reuse: 0, impact: 3, uniqueness: 3 }
       - relations 缺失 → { supports: [], contradicts: [], evolves: [], supersedes: [] }
       - context 缺失 → ""（留空，由用户后续填）

   2.2 标签归一（tags）：
       - 读取 kb.config.yaml.tags_vocabulary（若存在）
       - 对每个 tag：
         · 命中受控词表 → 保留
         · 拼写变体（大小写/连字符）→ 修正为标准形
         · 不在词表 → 保留并标注（写入 _normalize_log 待用户确认）
       - 去重

   2.3 related → relations 迁移（核心）：
       若 frontmatter 含 legacy `related: [[X]] [[Y]]`：
       - 对每个 related 条目 X：
         · 调 manager_agent.recommend_relations(target=当前笔记, candidate=X)
         · 相似度 ≥ 0.6 → 分类为 supports / contradicts / evolves / supersedes
         · 相似度 < 0.6 或不可判断 → 保留在 related（兼容字段）
       - 迁移完成后 relations 字段更新，related 字段保留剩余未分类项

   2.4 标题规范化（filename）：
       - 文件名 → kebab-case
       - 与库内既有文件冲突 → 加后缀 -2 / -3
       - 更新所有引用此文件的 wikilink（调 manager_agent.repair_deadlinks 子能力）

3. 写入策略：
   - 修改前先备份当前 frontmatter 到 _normalize_log/<date>-<scope>.diff.md
   - 每条改动附 why 字段（"缺 confidence，默认 50" / "related→supports，相似度 0.78"）
   - dry-run 模式：仅写 log，不修改原文件

4. 输出汇总报告：
   - 扫描数 / 修改数 / 跳过数 / 失败数
   - Top-N 改动类型分布
   - 待用户确认的不确定项（如不在词表的标签）
```

---

## 5. 输出示例

### run 模式

```
✅ normalize 完成（scope=all）

📊 统计：
   - 扫描：87 条
   - 修改：62 条
   - 跳过：23 条（已规范）
   - 失败：2 条（详见 log）

📋 Top 改动：
   - 字段补全：54 处（confidence 32 / context 12 / value 10）
   - 标签归一：18 处
   - related → relations：12 处（supports 9 / evolves 3 / 保留 related 4）
   - 文件名规范化：7 处

📝 diff 已备份：_normalize_log/2026-08-09-all.diff.md

⚠ 待确认：
   - 3 个标签不在受控词表：[ "ai-coding", "self-host", "edge-computing" ]
     → 是否加入 tags_vocabulary？（kb.config.yaml）
```

### dry-run 模式

```
🔍 dry-run 预览（不修改文件）

📊 拟修改：62 条（同 run 模式统计）
📋 完整 diff 见：_normalize_log/2026-08-09-all.preview.md
→ 确认后运行 quick-kb-normalize action=run
```

### rollback 模式

```
🔄 回滚：_normalize_log/2026-08-09-all.diff.md
   - 已恢复 62 条笔记的 frontmatter
   - 文件名回滚（含 wikilink 恢复）
```

---

## 6. diff log 格式

```markdown
# Normalize Log · 2026-08-09 · scope=all

## [[concepts/ai-engineering]]

### 字段补全
- + confidence: 50  # 默认值
- + value: { reuse: 0, impact: 4, uniqueness: 3 }  # 默认值

### 标签归一
- AI-Engineering → ai-engineering  # 大小写归一

### related → relations
- [[vector-db]] → relations.supports  # 相似度 0.82
- [[unknown-note]] → 保留 related  # 相似度 0.32，不可判断

---

## [[00_inbox/my-idea]]

### 字段补全
- + status: inbox  # 按路径推断
...
```

---

## 7. 幂等保证

- 同一笔记多次运行 normalize：
  - 已规范的字段 → 跳过（diff log 不记录）
  - related 已迁移的 → 不重复迁移
- **幂等键**：`(笔记路径, frontmatter 哈希)`；若上次运行后 frontmatter 未变，跳过

---

## 8. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| kb.config.yaml 不存在 | tags_vocabulary 跳过；其他正常 |
| manager-agent 不可用 | related → relations 退化为「全部移到 relations.supports」+ 标注「⚠ 未分类，待人工」 |
| 笔记 frontmatter 已损坏 | 跳过该条 + 写入失败列表（不阻塞） |
| 文件名冲突无法解决 | 跳过重命名 + 写入待处理清单 |

---

## 9. 边界

- **不改正文**：仅修改 frontmatter（YAML 区块）
- **不删笔记**：归 archive 技能
- **不重建死链**：归 connect / repair_deadlinks
- **不动 07_principles/ 下的认知资产正文**：仅补全 frontmatter

---

## 10. 自检清单

- [ ] scope 扫描正确（all / domain / legacy）
- [ ] 字段补全取默认值（非空字符串）
- [ ] 标签归一对照 tags_vocabulary
- [ ] related → relations 调用 manager_agent（相似度阈值 0.6）
- [ ] 不可判断的 related 保留（不强行分类）
- [ ] 文件名 kebab-case 化 + 冲突解决
- [ ] wikilink 引用同步更新（重命名后）
- [ ] dry-run 不修改原文件
- [ ] diff log 含每条改动的 why
- [ ] rollback 能完整恢复
- [ ] 幂等：第二次运行无改动
- [ ] 失败笔记不阻塞整体流程

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| dry-run 默认 false（dev doc 测试要点提及但 WP1 关键点未列） | dev doc 测试用例要求支持 dry-run，列在偏差检查文件补充 | references/v0.4-deviation-check.md §3.1 |
| related → relations 阈值用 0.6 | 与 manager-agent recommend_relations 一致（AGENTS_SPEC §1.2） | docs/AGENTS_SPEC.md §1.2 |
| 文件名冲突用 -2/-3 后缀 | 简单确定性策略；不引入 hash 防止用户认知负担 | 实现简化 |
| rollback 模式 | dev doc WP1 关键点「可回滚」要求；以 diff log 为源 | docs/dev/v0.4-extensions.md WP1 |
