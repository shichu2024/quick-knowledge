# demo-vault · quick-knowledge v0.1 示例

> 本目录演示「在空目录运行 `quick-kb-init` 后，使用 `quick-kb-capture` + `quick-kb-ingest` + `quick-kb-daily` 一段时间后」vault 应有的形态。
>
> 所有笔记均为虚构示例，便于新用户直观看到 v0.1 的产出。

---

## 如何使用

1. **浏览目录结构** —— 对比 [`docs/DESIGN.md` §4](../../docs/DESIGN.md#4-目录结构) 看每个目录的用途
2. **从 inbox 顺藤摸瓜**：
   - `inbox/clips/20260808-1000-rag-article.md` → `areas/ai-engineering/rag-architecture.md`（看 ingest 如何把 web-clip 转 concept）
   - `inbox/ideas/20260808-1415-observation-on-agent-tools.md` 顶部「已入库」callout → `areas/ai-engineering/agent-tool-use.md`
3. **看日志如何演进**：`outputs/daily/2026/08/2026-08-07.md` 与 `2026-08-08.md`，注意 wikilinks 与待入库段
4. **看 frontmatter 一致性**：所有正式笔记仅含 v0.1 子集字段（无 maturity/relations/context/value），对照 [`references/frontmatter-v0.1.md`](../../references/frontmatter-v0.1.md)

---

## 包含的样例（共 11 条）

### Inbox 原始素材（3 条）

| 文件 | 类型 | 状态 |
|------|------|------|
| `inbox/ideas/20260807-0930-rag-chunking-strategy.md` | idea | 待 ingest |
| `inbox/ideas/20260808-1415-observation-on-agent-tools.md` | idea | 已入库（顶部有 callout） |
| `inbox/clips/20260808-1000-rag-article.md` | web-clip | 已入库 |

### 正式笔记（6 条）

| 路径 | type | 来源 |
|------|------|------|
| `areas/ai-engineering/rag-architecture.md` | concept | 抽取自 RAG 文章 |
| `areas/ai-engineering/vector-database.md` | concept | 抽取自 RAG 文章 |
| `areas/ai-engineering/agent-tool-use.md` | concept | 抽取自 idea |
| `areas/general/atomic-notes-principle.md` | concept | 抽取自 daily 反思 |
| `resources/articles/2024-rag-survey.md` | resource | web-clip 整体摘要 |
| `resources/repos/langchain-intro.md` | resource | 早期资源 |

### 日志（2 条）

| 路径 | 内容 |
|------|------|
| `outputs/daily/2026/08/2026-08-07.md` | 含反问记录、待入库段 |
| `outputs/daily/2026/08/2026-08-08.md` | 含 wikilinks、capture 建议 |

---

## 系统文件

- `.kb-initialized` —— init 标记
- `system/config/kb.config.yaml` —— 最小配置
- `system/templates/zh/` —— 在主仓库 [`templates/zh/`](../../templates/zh/) 下（demo 不重复铺设）
- `wiki/_index.md` —— 全局导航占位
- `inbox/_readme.md` —— inbox 用法说明

---

## 不包含的内容

为避免冗余，本 demo **不重复铺设**：

- 仓库已有的 4 个模板文件（见 [`templates/zh/`](../../templates/zh/)）
- 4 个技能 SKILL.md（见 [`skills/`](../../skills/)）
- 所有空目录的 `.gitkeep`（实际 init 会创建；本 demo 仅含被样例笔记使用的目录）
- v0.2+ 才有的内容：`relations` / `context` / `value` 字段、MOC、`principles/` 下的认知资产、英文模板

如需查看完整骨架，在自己的空目录运行 `quick-kb-init` 即可。
