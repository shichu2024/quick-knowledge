---
version: v1.6.0
updated: 2026-08-13
phase: v1.6 规范化
applies_to: 全部技能写入 wikilink 时 · quick-kb-stats 死链统计 · quick-kb-archive 归档标注 · quick-kb-connect MOC 写入
source_of_truth:
  - references/frontmatter-v0.2.md §3（relations 字段 wikilink）
  - docs/dev/v1.5-cross-skill-consistency.md WP9
---

# Wikilink 命名约定

> 本文件锁定 quick-knowledge 全库 wikilink 的写法约定。所有技能写入 wikilink（正文或 frontmatter.relations 内）必须遵守。stats 死链统计口径以此为准。

---

## 1. 默认形式：basename

```markdown
[[vector-database]]
```

- **basename** = 文件名去扩展名（`vector-database.md` → `vector-database`）
- **不含路径**：不写 `[[02_areas/ai-engineering/vector-database]]`
- **不含扩展名**：不写 `[[vector-database.md]]`
- **小写 kebab-case**：与笔记文件名一致（文件名规范由 normalize 保证）

> Obsidian / json-canvas 解析时 basename 形式会自动匹配全库唯一笔记。

---

## 2. 重名消解：path-qualified

当全库存在同名笔记时（如 `02_areas/ai-engineering/rag.md` 与 `02_areas/product-design/rag.md`），basename 形式有歧义 → 用 path-qualified 形式：

```markdown
[[ai-engineering/rag]]
[[product-design/rag]]
```

**规则**：
- 路径前缀取**最短唯一**子路径（不一定从 vault 根开始）
- 路径段不含扩展名
- normalize `schema_check` 子动作能识别 basename 歧义并列出冲突清单，提示用户改用 path-qualified 形式

---

## 3. 别名（aliases）

笔记 frontmatter 可声明 `aliases`：

```yaml
---
title: 向量数据库选型
aliases:
  - vector-db-selection
  - VDB 选型
---
```

正文 / 其他笔记的 relations 中可写：

```markdown
[[vector-db-selection|向量数据库选型]]
```

**规则**：
- 别名形式必须用 `[[alias|显示文本]]` 格式（pipe 后是显示文本）
- 别名唯一性责任在笔记作者；歧义时 normalize 报告中提示

---

## 4. 归档笔记（与 quick-kb-archive §4 step 6 联动）

笔记归档后，所有指向该笔记的 wikilink **不删除**，加「 (已归档)」后缀：

```markdown
原：[[vector-database]]
归档后：[[vector-database]] (已归档)
```

**严格模式**（`kb.config.yaml.dead_link_strict: true`）→ 改为 path-qualified 别名形式：

```markdown
[[98_archive/concepts/vector-database|vector-database (已归档)]]
```

**幂等**：已含「(已归档)」后缀的不重复添加。

---

## 5. relations 字段内的 wikilink（frontmatter）

frontmatter `relations` 各子键的元素也是 wikilink，遵守同样的 basename / path-qualified / 别名规则：

```yaml
relations:
  supports: ["[[vector-database]]", "[[chunking-strategy]]"]
  evolves: ["[[ai-engineering/rag]]"]   # 重名时用 path-qualified
  derived_from:
    - "[[04_projects/foo/decisions/2026-08-13-auth]]"   # 路径较深时可写全路径
```

**特例**：Decision Ledger 等深路径对象，basename 容易重名（多个 `2026-08-13-auth` 在不同项目下），**强制写全路径**（path-qualified 从 vault 根）。

---

## 6. canvas 内的节点引用

canvas 节点的 `file` 字段是**相对路径**（含扩展名），与 wikilink 形式不同：

```json
{ "id": "vector-database", "file": "02_areas/ai-engineering/vector-database.md" }
```

详见 [`json-canvas-schema.md`](./json-canvas-schema.md) §3。

---

## 7. 不允许的形式

| 形式 | 错误原因 |
|------|---------|
| `[[vector-database.md]]` | 含扩展名 |
| `[[02_areas/ai-engineering/vector-database]]` | 默认场景不需要全路径（重名才需要） |
| `[[Vector Database]]` | 含空格大写（与文件名规范不一致；应用 alias） |
| `[[vector database]]` | 同上 |
| `[[vector-database]]（已归档）` | 用了全角括号；标准是半角 `(已归档)` |
| `[[http://example.com]]` | 外部 URL 应用 `<http://...>` 而非 wikilink |

---

## 8. stats 死链统计口径

quick-kb-stats 死链统计按本约定判定：

1. 解析每个 wikilink：
   - basename 形式 → 全库搜唯一匹配的 `.md`
   - path-qualified → 按相对路径解析
   - 别名 → 查 frontmatter `aliases`
2. 解析失败 → 死链
3. basename 形式命中多个文件 → 歧义死链（报告中提示改用 path-qualified）

---

## 9. 自检

- [ ] 写入的 wikilink 是 basename 形式（除非重名 path-qualified）
- [ ] frontmatter relations 元素是 wikilink 字符串（非 bare 路径）
- [ ] 归档笔记的指向已加 `(已归档)` 后缀
- [ ] Decision Ledger 等深路径对象用全路径 wikilink
- [ ] canvas `file` 字段用相对路径（非 wikilink 形式）

---

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.6.0 | 2026-08-13 | 初始版本：定义 basename 默认 / path-qualified 消歧 / 别名 / 归档后缀 / canvas 区别 |
