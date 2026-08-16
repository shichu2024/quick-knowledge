# quick-knowledge

> 个人知识库 × AI 技能框架 —— 用一套技能，把碎片信息蒸馏成可复用的个人资产。

[English](./README_EN.md) · [日本語](./README_JA.md) · [한국어](./README_KO.md) · [Español](./README_ES.md)

---

## 这是什么

`quick-knowledge` 是一组基于 [Agent Skills 协议](https://agentskills.io) 的知识库技能。在任何兼容 runtime（Claude Code / Codex / Cursor / OpenCode 等）里，用一句话完成 **采集 → 入库 → 连接 → 复盘**。

它解决三件事：

| 痛点 | quick-knowledge 的应对 |
|------|----------------------|
| **腐烂** —— 笔记越积越多，从不回看 | 强制 Review 闭环 + 置信度衰减 |
| **孤岛** —— 记了但找不回来，彼此不连接 | Connect 闭环 + 双链 + MOC |
| **高摩擦** —— 分类、命名、模板让人累 | 采集阶段不分类，AI 负责 Normalize |

---

## 效果示例

```
你：「抓一下这篇 https://example.com/rag-best-practices」
→ quick-kb-capture：网页正文 → Markdown，写入 00_inbox/

你：「入库这条」
→ quick-kb-ingest：抽取原子观点，建议 concept 标签与关系，写入 02_areas/（concept）或 01_resources/（resource）

你：「我笔记里关于 RAG 怎么说？」
→ quick-kb-query：基于库内笔记回答，每句结论挂 [[引用]]

你：「我要设计一个插件系统，怎么做？」
→ quick-kb-advisor：调取你的历史经验/原则，给三段建议（你的历史/你的原则/建议路径）

你：「每周复盘」
→ quick-kb-review：扫孤立笔记、置信度衰减、低复用高占用清单
```

---

## 安装

### 方式 1 · 通用一行命令（推荐，所有 runtime）

```bash
npx skills add shichu2024/quick-knowledge
```

默认安装全部技能（免逐个选中）：

```bash
npx skills add shichu2024/quick-knowledge --skill '*'
```

### 方式 2 · Claude Code marketplace

在 Claude Code 里：

```
/plugin marketplace add shichu2024/quick-knowledge
/plugin install quick-knowledge
```

### 方式 3 · 手动安装（按 runtime）

| Runtime | 安装路径 |
|---------|---------|
| Claude Code | `~/.claude/skills/quick-knowledge/` |
| Codex CLI | `~/.codex/skills/quick-knowledge/` |
| Cursor | `~/.cursor/skills/quick-knowledge/` |
| OpenCode | `~/.opencode/skills/quick-knowledge/` |

克隆仓库后把 `skills/` 拷贝到对应目录即可（agent 已合并入 skills：`quick-kb-{manager,memory,research}-agent`）。

### 初始化 vault

安装技能后，在任意空目录说一句：

```
初始化我的知识库
```

技能会在当前目录生成完整目录骨架 + 系统模板 + `kb.config.yaml`。vault 位置完全由你决定，与技能安装位置解耦。

---

## 使用 · 五分钟跑通

1. **初始化**：「初始化我的知识库」
2. **第一条 capture**：「抓 https://example.com/article」
3. **第一次 ingest**：「入库 inbox 这条」
4. **第一次 query**：「我笔记里关于 X 怎么说？」
5. **第一次 advisor**（v0.3+）：「我要做 X，怎么做？」

详见 [docs/quick-start.md](./docs/quick-start.md)。

---

## 工作原理

### 六大闭环

```
Capture   ──▶  Ingest   ──▶  Normalize  ──▶  Connect  ──▶  Query    ──▶  Review
采集           入库           规整              连接          查询          复盘
                                                                      │
                                                                      ▼
                                                                   回到 Capture
```

### 三个 Agent（输入域不重叠）

| Agent | 角色 | 输入域 |
|-------|------|--------|
| **quick-kb-manager-agent** | 知识库管家 · 整理与结构 | 库内结构（关系、孤立、死链） |
| **quick-kb-research-agent** | 研究员 · 外部资料处理 | 外部资料（URL/PDF/长文） |
| **quick-kb-memory-agent** | 长期记忆调取 · 核心差异化 | 库内认知资产（experience/pattern/principle/belief） |

### Frontmatter 正交字段（V2）

- `status` —— 文档生命周期（10 态，含 ingested/superseded 等归档与派生态）
- `maturity` —— 知识成熟度（6 态：captured → … → teachable）
- `confidence` —— 验证深度（0-100 整数，全库统一量纲）
- `value` —— 价值维度（{reuse, impact, uniqueness, ks}）
- `relations` —— 类型化关系（4 正向键 supports / contradicts / evolves / supersedes + 反向键与派生键 derived_from / source_of / refines 等）
- `source` —— 溯源（object 格式：type / url / note / capture_type 等，链回 inbox 原始素材）
- `context` —— 适用情境

### Knowledge Score

```
KS = confidence × log2(1 + reuse) × impact
```

---

## 仓库结构

```
quick-knowledge/
├── skills/             # 技能（14 个技能 + 3 个 agent skill，共 17 个）
│   ├── quick-kb-init/            # 初始化（自带模板 + schema + 指纹校验）
│   ├── quick-kb-capture/         # 采集（5 类源 + AI 润色提议）
│   ├── quick-kb-ingest/          # 入库（原子观点 + 写入前校验）
│   ├── quick-kb-daily/           # 每日日志
│   ├── quick-kb-connect/         # 双链 + MOC + canvas
│   ├── quick-kb-query/           # 事实型问答（strict 强制引用）
│   ├── quick-kb-review/          # 周期复盘 + 健康检查
│   ├── quick-kb-advisor/         # 决策辅助（三段式）
│   ├── quick-kb-project/         # 项目全生命周期 + Decision Ledger
│   ├── quick-kb-goal/            # 目标 + 学习路径
│   ├── quick-kb-normalize/       # 批量规整（幂等 + 可回滚）
│   ├── quick-kb-archive/         # 安全归档（copy + stub）
│   ├── quick-kb-stats/           # 健康仪表盘
│   ├── quick-kb-import/          # 外部库导入（Obsidian/Notion/Logseq）
│   ├── quick-kb-manager-agent/   # 知识库管家（9 能力）
│   ├── quick-kb-research-agent/  # 研究员
│   └── quick-kb-memory-agent/    # 长期记忆
├── templates/          # 中英双语模板（14 类 × 2）
├── references/         # 字段规范、wikilink/评分/写入校验规则、偏差检查
├── bench/              # 行为评测（SkillOpt × golden cases）
├── examples/demo-vault/  # 示例 vault
└── docs/               # 设计文档、开发文档、CHANGELOG
```

---

## 路线图

| 阶段 | 代号 | 状态 | 主要内容 |
|------|------|------|---------|
| v0.1 | mvp | ✅ 已完成 | init/capture/ingest/daily + 中文模板 |
| v0.2 | loops | ✅ 已完成 | connect/query/review + manager/quick-kb-research-agent + 英文模板 |
| v0.3 | assistant | ✅ 已完成 | quick-kb-memory-agent + advisor/project/goal + 认知资产模板 |
| v0.4 | extensions | ✅ 已完成 | normalize/archive/stats/import + kb.config 完整 + 多语言 README |
| v1.0 | release | ✅ 已完成 | CONTRIBUTING/COMMUNITY/LICENSE + CI + demo-vault 发布 |
| v1.1 | flow-restructure | ✅ 已完成 | 顶层目录 `NN_` 前缀 + 路径硬约束（⚠️ BREAKING） |
| v1.2 | ai-polish | ✅ 已完成 | capture / daily 用户手敲输入的 AI 润色提议（三选一） |
| v1.3 | skillopt-integration | ✅ 已完成 | 行为评测 + 技能文本优化（SkillOpt × 51 golden cases × nightly mock workflow） |
| v1.4 | nested-domain + hardening | ✅ 已完成 | 嵌套 domain_taxonomy + 模板全量铺设（12→14）+ schema 校验 |
| v1.5–v1.6 | consistency + 规范化 | ✅ 已完成 | confidence 0-100 统一 · JSON Schema 校验 · archive copy+stub · wikilink 命名约定 · canvas 规范 |
| v1.7 | automation & integration | ✅ 已完成 | agent §0 契约 · polish_mode 三档 · 近似/循环检测 · 降级可观测性 |
| v1.8 | e2e-calibration | ✅ 已完成 | init 资源自包含（模板+schema+指纹）· 全技能写入前校验层 · 口径统一 |
| v1.8.1–v1.9.3 | 测试校准系列 | ✅ 已完成 | 13 轮外部测试报告校准：schema/词表对齐 · 降级阈值表 · 冷启动排序 · source 格式统一 object · 结构漂移防御 |

详见 [docs/](./docs/) 目录。

---

## 行为评测（Behavior Testing · v1.3+）

v0.1–v1.2 的 CI 全是静态结构校验（frontmatter / wikilink / 占位符）——**无法回答「SKILL.md 改了一行，capture 行为是否退化」**。v1.3 引入 [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) 作为行为评测引擎补齐这一层：

- 自定义 benchmark `bench/quickkb/`（dataloader + rollout + adapter + 4 scorers）
- 51 个 golden case：45 单点 × 9 维度 + 6 J 类端到端流程衔接
- nightly mock 后端 workflow，**永不阻塞 PR merge**（non-blocking 信号）
- 永不自动部署优化产物——SkillOpt 产出的 `best_skill.md` 经人工 review 后单独 commit
- **发布回归**：每次发版前跑 capture / flow bench，结果记录于 [CHANGELOG](./docs/CHANGELOG.md) 对应版本的「评测」段

自 v1.8 起另有一条**测试校准循环**：外部测试报告（13+ 轮）逐条对照仓库真相源复核，甄别虚假问题后仅修复真缺陷——每轮的校准结论、拒绝修复清单与方法学约束沉淀在 [docs/dev/](./docs/dev/) 各版校准文档与 CHANGELOG。

详见 [`docs/dev/v1.3-skillopt-integration.md`](./docs/dev/v1.3-skillopt-integration.md)。

---

## 设计文档

- [DESIGN.md](./docs/DESIGN.md) —— 完整设计（真相源）
- [SKILLS_SPEC.md](./docs/SKILLS_SPEC.md) —— 技能详细规格
- [AGENTS_SPEC.md](./docs/AGENTS_SPEC.md) —— Agent 详细规格（含排序公式）
- [CHANGELOG.md](./docs/CHANGELOG.md) —— 版本变更记录（含每版评测结果）
- [dev/](./docs/dev/) —— 各阶段开发文档与校准文档

---

## 致谢

- [Agent Skills 协议](https://agentskills.io) —— 技能格式标准
- [Obsidian](https://obsidian.md) —— Markdown 知识库生态
- [Zettelkasten](https://zettelkasten.de) —— 原子化笔记与双链思想
- [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) —— README 多语言、SKILL.md 写法、skills.sh 分发模式参考

---

## License

[MIT](./LICENSE)
