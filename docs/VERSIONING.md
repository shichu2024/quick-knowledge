# 设计文档版本化规范

> 本文件规定 `docs/` 下设计文档的版本管理规则。目的：保留每次重大变更的历史，让设计演进可追溯。

---

## 1. 版本命名

- 主版本号：`V1`、`V2`、`V3` ……（大写 V + 阿拉伯数字，递增）
- 不使用次版本号（`V1.1` 这类）。小修订见 §3。

## 2. 何时升版本

满足以下任一条件，必须升一个主版本：

| 变更类型 | 示例 |
|---------|------|
| 新增/删除设计字段 | 新增 `maturity`、`value` 字段 |
| 改动枚举值 | `type` 增加 `principle` |
| 改动目录结构 | 新增 `principles/` 根目录 |
| 改动闭环模型 | 六闭环增加/重命名 |
| 改动技能清单 | 新增 `quick-kb-advisor` |
| 改动 agent 设计 | 新增 `memory-agent` |
| 修改核心设计决策 | 新增/推翻一条 ADR |
| 价值公式/哲学的根本性调整 | 改动「知识库价值」定义 |

## 3. 不升版本的小修订

以下变更不升版本，仅记录到 `CHANGELOG.md` 的「修订」区：

- 修复 typo、措辞优化、段落重排
- 补充示例、补充说明
- 调整格式（表格对齐、列表层级）
- 更新外部链接

## 4. 升版本工作流

每次升版本时，**先归档，再更新**：

```
1. 把当前主文档复制到 archive：
   docs/DESIGN.md      →  docs/archive/V<n>/DESIGN.md
   docs/SKILLS_SPEC.md →  docs/archive/V<n>/SKILLS_SPEC.md
   （<n> 为归档的版本号，即"将要被替换的旧版本"）

2. 在主文档 frontmatter 更新 version 字段为新版本号，updated 字段更新日期。

3. 在 docs/CHANGELOG.md 顶部追加新版本记录（倒序，最新在上）。
```

## 5. 目录结构

```
docs/
├── DESIGN.md                  # 主文档，始终是最新版（frontmatter 标 version）
├── SKILLS_SPEC.md             # 技能规格，同上
├── VERSIONING.md              # 本文件
├── CHANGELOG.md               # 版本变更记录
└── archive/                   # 历史版本归档
    ├── V1/                    #   每个目录是一个完整历史快照
    │   ├── DESIGN.md
    │   └── SKILLS_SPEC.md
    ├── V2/
    └── ...
```

## 6. frontmatter 约定

主文档顶部必须有 YAML frontmatter：

```yaml
---
version: V1
updated: 2026-08-08
---
```

归档副本保留其被归档时的 version 与 updated 字段，**不修改**。

## 7. 适用范围

- **适用**：`DESIGN.md`、`SKILLS_SPEC.md`、未来新增的核心设计文档。
- **不适用**：README（用户文档，独立维护）、模板文件（按模板自身版本管理）、技能源码（按 git 提交管理）。
