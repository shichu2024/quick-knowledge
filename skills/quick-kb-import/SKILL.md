---
name: quick-kb-import
description: |
  从外部库批量导入。支持 Obsidian vault / Notion 导出 / Logseq。
  转换 frontmatter 为 quick-knowledge 格式 → 写入 00_inbox/ 作为待 Ingest 候选（不直接入库）→ 输出导入报告。
  重复检测基于 (title + domain) 或 source.url。
  触发词（中文）：导入 / import / 从 Obsidian / 从 Notion / 从 Logseq
  Triggers (EN): import from / migrate from / ingest external
version: v0.4
phase: v0.4
applies_to: 读外部源 · 写 00_inbox/ · 不删原库
source_of_truth:
  - docs/DESIGN.md §3 / §10
  - docs/SKILLS_SPEC.md §11
  - docs/dev/v0.4-extensions.md WP4
  - references/v0.4-deviation-check.md §3.2
---

# quick-kb-import（v0.4）

> **外部库导入**：把 Obsidian / Notion / Logseq 笔记导入 quick-knowledge 的 00_inbox/。**不直接入库**，走正常 Ingest 流程。

---

## 1. 何时调用

- 用户说「导入我的 Obsidian vault / 从 Notion 迁移 / import from logseq」
- 切换到 quick-knowledge 时的一次性迁移

**不调用**：
- 单条素材抓取（→ quick-kb-capture）
- 已在库内的笔记规整（→ quick-kb-normalize）

---

## 2. v0.4 范围

### 做

- 解析 3 种外部源格式
- 转换为 quick-knowledge frontmatter（不完美字段标 status: draft）
- 写入 `00_inbox/imported/<source>/`（inbox 子目录，便于清理）
- 重复检测（避免重复导入）
- 导入报告

### 不做

- ❌ 不删原库
- ❌ 不直接入库（统一进 inbox）
- ❌ 不做语义抽取（→ ingest 后续处理）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| 来源 `source` | 是 | — | `obsidian` / `notion` / `logseq` |
| 路径 `path` | 是 | — | 外部源根目录（或 Notion 导出 zip 解压后路径） |
| 过滤 `filter` | 否 | — | 文件名 glob（如 `*.md`）或子目录限定 |
| 重复策略 `dedupe` | 否 | `skip` | `skip`（跳过）/ `overwrite`（覆盖）/ `rename`（加后缀） |
| 试运行 `dry_run` | 否 | `false` | 仅扫描报告，不写入 inbox |

---

## 4. 各来源解析规则

### 4.1 Obsidian vault

**特征**：
- `.obsidian/` 目录存在
- 笔记为 .md，含 `[[wikilink]]` 与 YAML frontmatter
- 路径结构通常 `Concepts/` `Resources/` `Daily/` 等

**解析**：
- 直接读 .md 内容
- 保留 frontmatter 原字段，补 quick-knowledge 缺失字段
- `[[wikilink]]` 保留（quick-knowledge 兼容 Obsidian 语法）
- 文件路径 → 推断 type（如 `Concepts/X.md` → type: concept）

### 4.2 Notion 导出

**特征**：
- Notion Export → Markdown（CSV 也可，但本技能仅支持 Markdown）
- 每条笔记为单独 .md
- frontmatter 可能缺失，正文含 Notion-specific 结构（如 toggle、callout）

**解析**：
- 标题从 H1 或文件名提取
- frontmatter 通常需补全（标 status: draft）
- Notion callout → 引用块；toggle → 折叠段（保留即可）
- 数据库视图（CSV 部分）跳过，提示用户手动处理

### 4.3 Logseq

**特征**：
- `journals/` 目录（每日笔记，文件名 YYYY-MM-DD.md）
- `pages/` 目录（概念笔记）
- outline 风格（每行以 `-` 开头为列表项）

**解析**：
- journals/ → quick-knowledge 的 `daily/<YYYY-MM-DD>.md`（type: daily）
- pages/ → inbox（type 推断）
- 保留 outline 结构
- Logseq 的 `[[page]]` 与 quick-knowledge wikilink 兼容

---

## 5. 工作流

```
1. 校验源路径（存在 / 是预期格式）
   - 检测 .obsidian/ → obsidian
   - 检测 journals/ + pages/ → logseq
   - 其他 → notion（按文件结构判断）

2. 收集候选文件：
   - 按 source 特定规则遍历
   - 应用 filter（若提供）

3. 对每个候选文件：

   3.1 解析原文 + 现有 frontmatter

   3.2 转换 frontmatter 为 quick-knowledge 格式：
       - title: 从 H1 / 文件名 / 原 title
       - type: 按路径推断（4.1-4.3）；不确定 → idea
       - created / updated: 从原笔记或文件 mtime
       - captured_at: <import date>（标识为导入）
       - status: 原 status 若有效则保留，否则 inbox（type 确定则 draft）
       - confidence: 原 confidence 若在 [0,1] 保留；若在 (1,100] 则除以 100 归一；缺失默认 0.5
       - tags: 原 tags 直接迁移
       - domain: 缺失（待 ingest 时填）
       - source.kind: <obsidian|notion|logseq>
       - source.original_path: <原路径>
       - source.imported_at: <date>

   3.3 重复检测（两级）：

       【强键 —— 命中则自动 skip，计入「重复」类】
       · 强键 1：hash(title + (domain || '')) 命中既有笔记
       · 强键 2：source.url 与既有笔记的 source.url 完全相等

       【弱键 —— 命中则标注，不改变导入行为】
       · 弱键条件 A：|sorted(tags_A) ∩ sorted(tags_B)| ≥ 2 且
                      Levenshtein(title_A, title_B) / max(len(A), len(B)) < 0.3
       · 弱键条件 B：source.url 去除 "https://"、"www."、尾部 "/" 后，
                      Jaccard(A, B) > 0.7 或包含关系成立
       · 弱键命中 → 导入报告中加 ⚠「疑似重复 [[X]]，人工确认是否跳过」

       【强键命中后的 dedupe 策略】
       · skip → 跳过（默认）
       · overwrite → 覆盖（保留原 captured_at）
       · rename → 加 -import-<N> 后缀

   3.4 写入 00_inbox/imported/<source>/<原文件名>.md
       - 保留原文（不动正文）
       - frontmatter 用转换后的版本

4. 生成导入报告：
   - 扫描数 / 成功数 / 重复跳过数 / 失败数
   - ⚠ 疑似重复清单（所有弱键命中对）
   - 失败原因清单（frontmatter 损坏等）
   - 推荐下一步：quick-kb-ingest 批量入库

5. 提示用户：
   「导入完成。建议运行 quick-kb-ingest 把 00_inbox/imported/ 的笔记入库为正式 concept/resource/...
    或运行 quick-kb-normalize 规整 frontmatter 后再 ingest」
```

---

## 6. 输出示例

````markdown
# Import Report · 2026-08-09 · source=obsidian

源路径：`./old-vault`

## 统计

| 项 | 数量 |
|----|------|
| 扫描 | 124 |
| 成功导入 | 98 |
| 重复跳过 | 21 |
| 失败 | 5 |

## 重复跳过（21 条）

- [[concept/RAG]] · dedupe_key 命中既有 [[concept/RAG-architecture]]
- [[concept/vector-db]] · ...
- ... 完整清单见 00_inbox/imported/_skipped-2026-08-09.md

## 失败（5 条）

- `Corrupted Note.md` · YAML frontmatter 解析失败
- `Untitled.md` · 缺 title 无法推断
- ... 完整清单见 00_inbox/imported/_failed-2026-08-09.md

## ⚠ 疑似重复清单

> 弱键命中（非自动跳过），人工确认是否需要去重：

| 导入项 | 已有笔记 | 命中类型 |
|--------|---------|---------|
| `[[concept/RAG-impl]]` | `[[concept/RAG-architecture]]` | tags∩≥2 + 标题距离<0.3 |
| `[[resource/anthropic-blog]]` | `[[resource/anthropic-home]]` | url 相似度>0.7 |
| ... | ... | ... |

## 推荐下一步

1. 检查 00_inbox/imported/obsidian/ 的笔记
2. 运行 quick-kb-normalize scope=00_inbox/imported 规整 frontmatter
3. 运行 quick-kb-ingest 入库为正式笔记
4. 失败清单可手动修复后再次 import（dedupe 保护不会重复）
````

---

## 7. 幂等保证

- **重复检测**：基于 (title + domain) 或 source.url 哈希
- **二次导入同源**：已导入的笔记自动 skip（dedupe_key 命中）
- **dry-run**：仅扫描 + 报告，不写 inbox
- **dedupe 索引**：每次导入追加到 `00_inbox/imported/_dedupe-index.jsonl`，便于跨次去重

---

## 8. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| 源路径不存在 | 报错退出 |
| 源格式识别失败 | 询问用户显式指定 source |
| 单条笔记解析失败 | 计入失败列表，继续处理其他 |
| frontmatter 字段类型异常（如 confidence 非 number） | 标 status: draft + 加入失败清单 |
| wikilink 指向源库不存在于 quick-knowledge | 保留 wikilink，待 connect/repair_deadlinks 后续处理 |

---

## 路径约束（硬性）

- **禁止绝对路径** —— import 报告与笔记产物中，`源路径` 字段不得使用 `file://`、`C:\`、`/Users/...` 等绝对路径
- **源路径相对化** —— 源 vault 必须以相对路径（如 `./old-vault`、`../obsidian-export`）登记；若源在 vault 外部，先复制到 `01_resources/migrations/<source>/`
- **source.url 仅两种合法形态** —— `https://原始来源 URL` 或 `01_resources/...` 相对路径

## 9. 边界

- **不删原库**：只读源路径，所有写入仅 00_inbox/
- **不直接入库**：导入笔记统一进 inbox，走正常 Ingest 流程
- **不做语义抽取**：原文照搬；frontmatter 字段如 type 推断不确定 → idea
- **不处理附件**：图片/PDF 等附件跳过，提示用户手动迁移

---

## 10. 自检清单

- [ ] 3 种 source 解析规则正确实现
- [ ] frontmatter 转换为 quick-knowledge 格式
- [ ] 不完美字段标 status: draft
- [ ] 重复检测基于 (title + domain) 或 source.url
- [ ] 3 种 dedupe 策略（skip/overwrite/rename）正确
- [ ] 写入 00_inbox/imported/<source>/（不污染主 inbox）
- [ ] 导入报告含扫描/成功/重复/失败统计
- [ ] dry-run 不写入
- [ ] 二次导入同源 skip 已导入项
- [ ] _dedupe-index.jsonl 跨次去重
- [ ] 失败笔记不阻塞整体流程

---

## 11. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| dedupe_key 用 hash(title + domain) | dev doc 仅说「重复检测」，未指定算法 | references/v0.4-deviation-check.md §3.2 |
| 写入 00_inbox/imported/<source>/ 子目录 | 便于用户一次性清理或归档；不污染主 inbox | 实现简化，不偏离设计 |
| 不处理附件 | 附件迁移涉及路径引用变更，复杂度高；推迟 v1.0 | docs/dev/v0.1-mvp.md → v1.0 |
| 新增 _dedupe-index.jsonl | 支持跨次导入去重；防止 normalize/ingest 后重复键失效 | docs/dev/v0.4-extensions.md WP4 关键点「重复检测」 |
| Notion CSV 数据库视图跳过 | CSV 结构差异大；本技能仅处理 Markdown 导出 | 实现简化 |
