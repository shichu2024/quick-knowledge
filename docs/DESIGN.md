---
version: V2
updated: 2026-08-09
---

# quick-knowledge · 设计文档

> 个人知识库 × AI 技能框架 —— 用一套技能，把碎片信息蒸馏成可复用的个人资产。

---

## 目录

- [1. 项目愿景](#1-项目愿景)
- [2. 设计哲学](#2-设计哲学)
- [3. 六大闭环](#3-六大闭环)
- [4. 目录结构](#4-目录结构)
- [5. 技能清单](#5-技能清单)
- [6. 元数据规范（Frontmatter）](#6-元数据规范frontmatter)
- [7. Agent 设计](#7-agent-设计)
- [8. 模板系统](#8-模板系统)
- [9. Obsidian 集成](#9-obsidian-集成)
- [10. 多语言策略](#10-多语言策略)
- [11. 仓库结构](#11-仓库结构)
- [12. 安装与分发](#12-安装与分发)
- [13. 路线图](#13-路线图)
- [14. 设计决策记录](#14-设计决策记录)

---

## 1. 项目愿景

### 1.1 一句话定位

`quick-knowledge` 是一组基于 [Agent Skills 协议](https://agentskills.io) 的知识库技能，让你在任何兼容 runtime（Claude Code、Codex、Cursor、OpenCode 等）里，用一句话完成「采集 → 入库 → 连接 → 复盘」。

### 1.2 它解决什么问题

大多数个人知识库死于三件事：

| 死因 | 表现 | quick-knowledge 的应对 |
|------|------|----------------------|
| **腐烂** | 笔记越积越多，从不回看 | 强制 Review 闭环 + 置信度衰减 |
| **孤岛** | 记了但找不回来，彼此不连接 | Connect 闭环 + 双链 + MOC |
| **高摩擦** | 分类、命名、模板让人累 | 采集阶段不追求分类，AI 负责 Normalize |

---

## 2. 设计哲学

### 2.1 五条原则

1. **采集即廉价，入库即严肃**
   Capture 阶段零摩擦（不分类、不命名），Ingest 阶段才做结构化。把认知负担推迟到「决定保留它」的那一刻。

2. **AI 负责规范化，人负责判断**
   标题归一、标签补全、双链推荐由 AI 完成；是否采纳、置信度多少由人决定。

3. **强制引用，禁止空答**
   Query 闭环回答问题时必须引用已有笔记或原始来源。没有引用的答案视同幻觉。

4. **置信度可衰减，结论可过期**
   每条笔记带 `confidence` 分数。Review 闭环会主动标记长期未验证、被新证据推翻的结论。

5. **框架通用，路径无关**
   仓库不含任何绝对路径。所有路径用相对于 vault 根目录的引用，便于发布到 GitHub 后任意环境使用。

### 2.2 不做什么（反向边界）

- **不做数据库** —— 知识库就是 Markdown 文件集合，不引入 SQLite/向量库等运行时依赖。
- **不做云同步** —— 同步交给 git / Obsidian Sync / iCloud 等既有方案。
- **不做笔记应用的替代品** —— 与 Obsidian 深度协作，而非竞争。
- **不在采集阶段追求完整分类** —— 一切归类留到 Ingest。

---

## 3. 六大闭环

所有技能都围绕六个闭环组织。每个闭环有明确的输入、输出、负责技能和健康指标。

```
┌─────────────────────────────────────────────────────────────┐
│                       quick-knowledge                         │
│                                                               │
│   Capture ──▶ Ingest ──▶ Normalize ──▶ Connect                │
│     │           │           │              │                  │
│     ▼           ▼           ▼              ▼                  │
│   inbox      areas       resources        wiki/MOC            │
│   projects   outputs     goals           (双链)               │
│                                                               │
│         Query ◀────────────────────────┘                      │
│           │                                                   │
│           ▼                                                   │
│         Review ──────────────▶ 回到 Capture / Ingest          │
└─────────────────────────────────────────────────────────────┘
```

| 闭环 | 职责 | 主技能 | 输入 | 输出 | 健康指标 |
|------|------|--------|------|------|---------|
| **Capture** | 把网页/PDF/聊天/灵感低摩擦放入 00_inbox | `quick-kb-capture` | URL、文件、文本、语音转写 | 00_inbox 原始素材 | 00_inbox 周转时长（应 < 7 天） |
| **Ingest** | 保留原始资料，生成结构化笔记 | `quick-kb-ingest` | 00_inbox 素材 | 02_areas/01_resources/04_projects 下的正式笔记 | 入库笔记平均 frontmatter 完整度 |
| **Normalize** | 统一标题、标签、日期、来源字段 | `quick-kb-ingest` / `quick-kb-normalize` | 已入库但字段不全的笔记 | 规范化后的笔记 | frontmatter 缺失率（应 < 5%） |
| **Connect** | 建立双链、主题索引、知识地图 | `quick-kb-connect` + quick-kb-manager-agent | 规范化笔记 | MOC、wikilinks、canvas | 孤立笔记率（应 < 15%） |
| **Query** | 回答时必须引用已有笔记或原始来源 | `quick-kb-query` | 自然语言问题 | 带引用的答案 | 引用命中率（应 > 80%） |
| **Review** | 检查孤立笔记、重复、死链、过期结论 | `quick-kb-review` | 全库快照 | 健康报告 + 待办清单 | Review 闭环完成率 |

> 闭环不是单向流水线。Review 的产出会回流到 Capture（补采证）、Ingest（重新归档）、Connect（修复死链）。这是「闭环」而非「管线」的含义。

---

## 4. 目录结构

vault 根目录采用 **PARA + 系统层** 混合模型，并加两位数字前缀实现「输入 → 沉淀 → 目标 → 执行 → 产出 → 索引 → 元层 → 归档 → 系统」的流转可视化（见 ADR-015）。所有目录名使用英文小写，保证跨平台一致。

```
<vault-root>/
├── 00_inbox/                       # 灵感库 · Capture 入口（最上游输入）
│   ├── ideas/                      #   碎片化想法
│   ├── clips/                      #   网页摘录、PDF 摘要
│   ├── meetings/                   #   会议记录
│   ├── ai-dialogs/                 #   AI 对话精华
│   └── reading/                    #   阅读笔记（待入库）
│
├── 01_resources/                   # 外部资源 · 长期参考（原材料输入）
│   ├── articles/                   #   文章与网页收藏
│   ├── books/                      #   书籍与读书笔记
│   ├── courses/                    #   课程与讲座
│   └── repos/                      #   开源项目与技术资料
│
├── 02_areas/                       # 领域知识 · 核心沉淀
│   ├── <domain-slug>/              #   如 front-end、ai-engineering
│   │   ├── _moc.md                 #     领域 MOC
│   │   └── <sub-area>/             #     子领域
│   └── general/                    #   通用认知
│
├── 03_goals/                       # 目标管理 · 方向牵引
│   └── <goal-slug>/
│       ├── goal.md                 #   目标定义 + 学习路径
│       ├── progress/               #   日期进展记录
│       └── _moc.md                 #   目标相关笔记索引
│
├── 04_projects/                    # 项目实践 · 执行落地
│   ├── <project-slug>/             #   进行中项目
│   └── _template/                  #   项目模板（软链引用 99_system/templates）
│
├── 05_outputs/                     # 产出与复盘 · 成果输出
│   ├── daily/                      #   每日日志（按年月分子目录）
│   │   └── YYYY/MM/
│   ├── reviews/                    #   周期复盘
│   │   ├── weekly/
│   │   ├── monthly/
│   │   ├── quarterly/
│   │   └── yearly/
│   ├── decisions/                  #   方案决策记录（ADR 风格）
│   └── works/                      #   个人产出（文章/分享/方案）
│
├── 06_wiki/                        # 知识索引 · Connect 产物（全局导航）
│   ├── _index.md                   #   全局导航页
│   ├── mocs/                       #   领域/专题 MOC
│   └── maps/                       #   知识地图（canvas）
│
├── 07_principles/                  # 认知资产 · 跨领域元沉淀（区别于通用 Wiki 的核心）
│   ├── principles/                 #   个人原则（跨项目方法论、价值观底线）
│   │   ├── engineering.md
│   │   └── management.md
│   ├── beliefs/                    #   待验证假设
│   ├── patterns/                   #   可复用解决模式
│   └── experiences/                #   经历教训（具体事件）
│
├── 98_archive/                     # 归档中心 · 已退出流转
│   ├── projects/                   #   已完结项目
│   ├── goals/                      #   已完成/取消目标
│   ├── reviews/                    #   历史复盘
│   └── materials/                  #   过期素材
│
└── 99_system/                      # 系统与工具 · 底层支撑
    ├── skills/                     #   知识库技能（本框架本体，含 manager/memory/research 三类 agent 以 skill 形式分发）
    ├── templates/                  #   笔记/wiki/目标/项目模板（中英双语）
    │   ├── zh/
    │   └── en/
    ├── attachments/                #   附件资源
    ├── workflows/                  #   工作流文档
    ├── prompts/                    #   复用 prompt
    └── config/                     #   框架配置（kb.config.yaml）
```

> **流转顺序**：`00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 98 → 99`。IDE 文件浏览器按字典序自然排列即得到流转管线视图。详见 ADR-015。

### 4.1 命名约定

| 对象 | 规则 | 示例 |
|------|------|------|
| 文件名 | kebab-case，无空格、无中文 | `rag-architecture.md` |
| 顶层目录 | 两位数字前缀 + 下划线 + kebab-case | `02_areas/`、`99_system/` |
| 子目录 | kebab-case，单数，无前缀 | `02_areas/ai-engineering/` |
| 嵌套 domain 子目录 | 同子目录规则；允许在 `02_areas/<顶层>/` 下再嵌套，深度建议 ≤ 3；嵌套结构由 `kb.config.yaml.domain_taxonomy` 约束 | `02_areas/programming/python/threading.md` |
| 日期 | ISO 8601 | `2026-08-08` |
| 日期类文件 | `<date-token>-<summary>.md`，summary 由 LLM 从内容提炼 2-5 词 kebab-case（限 30 字符）；同日期已有旧文件 → 编辑不改名（稳定性约束）；不可提炼 → 退为纯日期 | `2026-08-12-rag-eval-debug.md`、`2026-W32-stability.md` |
| 子目录年月 | `YYYY/MM` | `05_outputs/daily/2026/08/` |
| Inbox 临时文件 | 时间戳前缀 | `20260808-1430-想法.md` |

> **日期类文件命名适用范围**：daily 日志、review 报告（weekly/monthly/quarterly/yearly/adhoc）、goal 与 project 的 `progress/` 子目录文件。stats 报告保留 `stats-YYYY-MM-DD.md` 形态不变。

> **嵌套 domain 规则（v1.4+）**：`domain` frontmatter 字段可含 `/`（如 `programming/python`）。ingest 时若 `kb.config.yaml.domain_taxonomy` 命中顶层 key 且能从 tags/title 推断子域，落盘到 `02_areas/<key>/<sub>/<slug>.md`；未配置 taxonomy 或未命中时退为单层 `02_areas/<domain>/<slug>.md`（向后兼容）。旧 flat 笔记可通过 `quick-kb-normalize action=regroup` 批量升级。

### 4.2 kb.config.yaml

vault 根目录的 `99_system/config/kb.config.yaml` 是唯一可选配置文件，记录用户偏好（语言、默认领域、标签词表等）。未配置时全部走默认值，保证零配置可用。

```yaml
# 示例（可选）
language: zh                     # zh | en，决定模板语言
default_domain: ai-engineering   # 默认领域
domains:
  - ai-engineering
  - front-end
  - general
tags_vocabularly:                # 受控标签词表（可选）
  - ai/rag
  - ai/agent
  - eng/architecture
review:
  inbox_max_age_days: 7
  orphan_threshold: 0.15
  confidence_decay_months: 6
```

---

## 5. 技能清单

### 5.1 核心技能（10 个）

| 技能 | 闭环 | 一句话职责 | 触发示例 |
|------|------|-----------|---------|
| `quick-kb-init` | — | 初始化 vault 目录骨架与系统文件 | 「初始化知识库」 |
| `quick-kb-capture` | Capture | 多源低摩擦采集到 inbox | 「记一下这个想法…」「收藏这个网页」 |
| `quick-kb-ingest` | Ingest + Normalize | 00_inbox 素材正式入库 | 「处理 inbox」「把这条入库」 |
| `quick-kb-connect` | Connect | 建 MOC、双链、知识地图 | 「连一下这几条」「建个 MOC」 |
| `quick-kb-query` | Query | 强制引用的检索回答（事实型） | 「我笔记里关于 X 怎么说的」 |
| `quick-kb-advisor` | Query+ | 基于个人经验辅助决策（思考型） | 「我要设计个插件系统，怎么搞」 |
| `quick-kb-review` | Review | 周期复盘 + 健康检查 | 「复盘本周」「扫一下孤立笔记」 |
| `quick-kb-daily` | Capture | 每日日志，描述不足时反问补充 | 「今天的日志」「记日志」 |
| `quick-kb-goal` | — | 目标 + 学习路径 + 进展 | 「新建目标：学 Rust」「更新目标进度」 |
| `quick-kb-project` | — | 项目全生命周期 | 「开个项目」「归档项目 X」 |

### 5.2 扩展技能（按需启用）

| 技能 | 职责 |
|------|------|
| `quick-kb-normalize` | 批量规整历史笔记的 frontmatter、标签、标题 |
| `quick-kb-archive` | 归档已完成项目/目标，迁移到 archive |
| `quick-kb-stats` | 输出 vault 健康仪表盘（孤立率、重复率、置信度分布） |
| `quick-kb-import` | 从 Obsidian/Notion/Logseq 等外部库批量导入 |

### 5.3 技能通用规范

每个技能必须满足：

1. **单个 SKILL.md**，含 `name` + `description` frontmatter（带中英触发词）。
2. **零绝对路径** —— 所有路径相对于 vault 根。
3. **幂等** —— 同一输入多次执行结果一致。
4. **不破坏原始资料** —— Capture 的原始素材永远保留，Ingest 只生成派生笔记。
5. **可解释** —— 每次写入都告诉用户「写了什么、为什么、在哪」。

详细技能规格见 [`SKILLS_SPEC.md`](./SKILLS_SPEC.md)。

---

## 6. 元数据规范（Frontmatter）

### 6.1 标准字段

所有正式笔记（非 00_inbox 原始素材）使用以下 frontmatter：

```yaml
---
title: RAG 架构设计                    # 必填 · 笔记标题
type: concept                          # 必填 · 见下方枚举
created: 2026-08-08                    # 必填 · ISO 日期
updated: 2026-08-08                    # 必填 · 最后修改日期
tags:                                  # 必填 · 受控标签（domain/topic）
  - ai/rag
status: active                         # 必填 · 文档生命周期（见 6.3）
maturity: applied                      # 知识型笔记 · 知识成熟度（见 6.4）
confidence: 80                         # 0-100 · 验证深度（见 6.5）
value:                                 # 可选 · 价值维度（见 6.6，多为自动计算）
  reuse: 12                            #   自动：入链数 + 查询命中次数
  impact: 4                            #   可选：1-5 主观影响力
relations:                             # 类型化关系（见 6.7）；related 作为通用回退仍兼容
  supports:                            #   本笔记支持/被某笔记支撑
    - "[[Vector Database]]"
  contradicts: []                      #   与之冲突（上下文相关，非对错）
  evolves: []                          #   由某笔记演化而来
  supersedes: []                       #   取代了某条过期笔记
context: "通用场景；创业团队请同时参考 [[模块化单体]]"  # 可选 · 自由文本适用上下文（见 6.8）
source:                                # 原始来源 · object 格式（v1.9.3 对齐 frontmatter-schema-v1）
  url: https://example.com/article
  note: "[[原始摘录]]"
domain: ai-engineering                 # 所属领域（对应 02_areas/）
---
```

### 6.2 type 枚举（笔记类型）

| 值 | 含义 | 主要存放 |
|----|------|---------|
| `concept` | 概念、原理、心智模型 | `02_areas/` |
| `resource` | 外部资源摘要 | `01_resources/` |
| `meeting` | 会议记录 | `00_inbox/meetings/` → 归档 |
| `daily` | 每日日志 | `05_outputs/daily/` |
| `review` | 周期复盘 | `05_outputs/reviews/` |
| `decision` | 方案决策 | `05_outputs/decisions/` |
| `goal` | 目标 | `03_goals/` |
| `project` | 项目说明 | `04_projects/` |
| `moc` | 主题索引 | `06_wiki/mocs/` |
| `idea` | 灵感（inbox） | `00_inbox/ideas/` |
| **`principle`** | 个人原则 · 跨项目方法论、价值观底线 | `07_principles/principles/` |
| **`belief`** | 待验证的个人假设/判断 | `07_principles/beliefs/` |
| **`pattern`** | 可复用的解决模式 | `07_principles/patterns/` |
| **`experience`** | 具体历史事件/教训 | `07_principles/experiences/` |

> 后四类是**个人认知资产**，是 quick-knowledge 区别于通用 Wiki 的本质。它们没有 `domain`（横切），但可在领域专属目录里以同名文件覆盖（如 `02_areas/front-end/principles.md`）。

### 6.3 status 枚举（文档生命周期）

`status` 只描述「这条笔记作为文档处于什么阶段」，与知识是否成熟无关。

| 值 | 适用 type | 含义 |
|----|----------|------|
| `inbox` | idea/resource | 待 Ingest |
| `draft` | * | 草稿，未完成 |
| `active` | project/goal | 进行中 |
| `done` | goal/project | 已完成 |
| `cancelled` | goal/project | 已取消 |
| `archived` | * | 已归档 |

### 6.4 maturity 枚举（知识成熟度）

`maturity` 只对**知识型笔记**（concept/principle/belief/pattern/experience）有意义，描述「这条知识在你脑中成熟到什么程度」。文档型笔记（daily/review/decision/moc）不需要此字段。

```
captured ─▶ understood ─▶ validated ─▶ applied ─▶ teachable
                                                │
                                                └─（长期未触碰或被推翻）─▶ deprecated
```

| 值 | 含义 | confidence 通常区间 |
|----|------|------------------|
| `captured` | 刚记下，只是知道存在 | 0-30 |
| `understood` | 能讲清是什么 | 31-60 |
| `validated` | 多源/实践验证 | 61-80 |
| `applied` | 在真实场景用过 | 81-90 |
| `teachable` | 能教他人，可写可讲 | 91-100 |
| `deprecated` | 已过期/被推翻，保留作历史 | — |

> confidence 是连续数值、由人填；maturity 是离散阶段、反映角色转变。两者**相关但不绑定** —— 一条 `applied` 的经验 confidence 可以是 85，但一条 `teachable` 的官方文档条款 confidence 也可以是 98。Review 闭环会按时间对长期未触碰的 maturity 自动降级为 `deprecated`（见 ADR-004）。

> **deprecated 强制关联**（V2 新增）：将某条笔记降为 `deprecated` 时，**必须**在 `relations.supersedes`（被新笔记取代）或 `relations.contradicts`（与之冲突）中至少填一项，记录"它为什么过期"。这是为了避免"AI 不知道该信哪条"（见 ADR-011）。

### 6.5 confidence 评分参考

| 分数 | 含义 |
|------|------|
| 0-30 | 道听途说，未经任何验证 |
| 31-60 | 单一来源，待交叉验证 |
| 61-80 | 多源验证，实践中有效 |
| 81-95 | 长期实践验证，可教学他人 |
| 96-100 | 一手实验/官方文档/铁律 |

### 6.6 价值维度与 Knowledge Score

单一 confidence 不够：一条"绝对正确但永远不会用到"的笔记价值为零。引入价值维度，但**自动化优先**，避免采集阶段增加摩擦。

| 字段 | 来源 | 说明 |
|------|------|------|
| `value.reuse` | **自动** | 入链数 + 查询命中次数 + Connect 推荐频次，Review 时由系统刷新 |
| `value.impact` | 可选手动 | 1-5，用户主观影响力；未填按 3 计 |
| `value.uniqueness` | 可选/自动估算 | 1-5，基于标签稀缺度估算；可被用户覆盖 |

**Knowledge Score**（Review 排序用，不强制写入笔记）：

```
KS = confidence × log2(1 + reuse) × impact
```

Review 闭环优先处理两类笔记：
- **高价值低置信**（KS 高但 confidence < 60）→ 该去验证了
- **低复用高占用**（confidence 高但 reuse = 0）→ 该连接到 MOC 或归档

### 6.7 关系类型化（relations）

V1 的扁平 `related` 字段无法表达"为什么关联"。V2 升级为类型化关系：

| 关系 | 含义 | 方向 |
|------|------|------|
| `supports` | A 支撑/佐证 B | 对称 |
| `contradicts` | A 与 B 冲突（上下文相关，非对错） | 对称 |
| `evolves` | A 由 B 演化/扩展开来 | 有向（B→A） |
| `supersedes` | A 取代了过期的 B | 有向（A→B） |

```yaml
relations:
  supports: ["[[Vector Database]]"]
  contradicts: ["[[模块化单体更适合创业团队]]"]   # 上下文冲突，不是它错
  evolves: ["[[RAG 基础概念]]"]
  supersedes: ["[[2024 微服务最优论]]"]           # 取代了这条过期笔记
```

**冲突处理原则**（V2 核心）：
- 个人知识一定会随上下文变化而冲突（"微服务适合大型系统" vs "模块化单体适合创业团队"都成立）。
- `contradicts` 不代表某一方错误 —— 而是标注**适用上下文不同**，由 `context` 字段（6.8）区分。
- Query/advisor 在召回冲突笔记时，必须**同时呈现**并标注各自的 context，由用户判断，AI 不擅自选边。

**向后兼容**：V1 的扁平 `related: [...]` 仍然有效，被视作未类型化的弱关联。`quick-kb-normalize` 可批量迁移 `related` → `relations.supports`。

### 6.8 上下文字段（context）

```yaml
context: "创业团队 <50 人，迭代周期 1 周"
```

- **自由文本**，不强制结构化（避免采集摩擦）。
- 描述本笔记**适用的情境**（团队规模、阶段、技术栈、领域）。
- AI 在 Ingest 时从正文提取候选 context，由用户确认。
- 含 wikilink 时可关联到对比情境笔记：`context: "通用场景；创业团队请参考 [[模块化单体]]"`。
- 与 `contradicts` 配合使用：冲突的两条笔记各自声明 context，AI 不会"不知道信谁"。

> 反馈建议用结构化 `context: { team_size, stage }`；本设计选择自由文本 + 可选键值，原因是强制结构化会显著增加采集摩擦，违反原则 1（采集即廉价）。结构化键值可在 `kb.config.yaml` 中声明受控词表，由 AI 在 Ingest 时归一。

### 6.9 最小 frontmatter

00_inbox 原始素材只要求两个字段，降低采集摩擦：

```yaml
---
title:
captured_at: 2026-08-08T14:30
---
```

Ingest 时由 AI 补齐其余字段。

---

### 6.10 AI 润色提议（v1.2+）

**问题**：用户在 capture / daily 时往往输入过简（「修 bug」「开会」「学了很多」），事后回看自己都看不懂。

**机制**：在写入前，AI 主动生成一份润色版，连同原文一并呈现，用户三选一：

```
✨ AI 润色提议：
原文：{用户输入}
润色：{AI 扩写版}

[1] 用润色版   [2] 保留原文   [3] 再改一版
```

**适用范围**：仅限**用户手敲输入**——idea / meeting / ai-dialog / reading-note / daily 4 段。
**不适用**：web-clip / pdf 抓取正文（外部来源逐字保留，不进润色）。

**触发条件**（任一满足）：
- 字符数 < 50
- 无标点（。！？.!?）且无换行
- 用户显式说「润色 / 扩展 / 优化 / polish / expand」

**原文保存**（不违反「不改正文」原则）：
- 用户选 [1] 时，润色版进正文，原文存入 `source.original_text`
- frontmatter 加 `ai_polished: true`
- daily 用 `<!-- original: ... -->` 行内 HTML 注释保留原句

**与 ingest 的区别**：
| 维度 | AI 润色（v1.2） | Ingest |
|------|----------------|--------|
| 时机 | capture / daily 写入前 | capture 之后，按需调用 |
| 输入 | 用户的原始输入 | 已 capture 的 inbox 内容 / 外部资料 |
| 输出 | 同语义的扩写版 | 结构化的原子观点 |
| 职责 | 改写 | 抽取 + 分类 + 关联 |

**与 daily 反问机制的互补**：
- 反问（v0.2）：让用户**自己补全** vague input（被动）
- 润色（v1.2）：AI **主动扩写**（主动）
- 两者串联：先反问补全明显缺失，再润色提议优化表达

详见 ADR-016。

---

### 6.11 行为评测与技能文本优化（v1.3+）

**问题**：v0.1–v1.2 的 CI 全部是静态结构校验（frontmatter 字段、wikilink 死链、占位符、demo-vault 目录），**零行为测试**——CI 无法回答「SKILL.md 改了一行，capture 行为是否退化」「v1.2 步骤 2.5 是否真的在正确场景触发」。

**机制**：v1.3 引入 [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)（文本空间技能优化器，MIT，PyPI `skillopt`）作为行为评测 + 技能文本优化引擎：

1. **自定义 benchmark `quickkb`**（`bench/quickkb/`）：把 14 个 SKILL.md 当作「被优化的权重」，遵循 SkillOpt 的 4 件套契约（SplitDataLoader + rollout helper + EnvAdapter + YAML config）
2. **51 个 golden case**（`bench/cases/`）：
   - 45 单点 case 覆盖 9 维度（source-routing / v1.2-polish / triggers / auto-detect / dedup / frontmatter / degradation / edge / feedback）
   - 6 J 类端到端 case 串起 7 阶段流程（输入→沉淀→目标→执行→产出→索引→系统），fixture-based 验证相邻技能的数据契约
3. **4 个评分器**（`bench/quickkb/scoring/`）：`routing.py`（路径）+ `frontmatter.py`（字段正则）+ `behavior.py`（润色/去重/注入）+ `flow.py`（流程契约）
4. **nightly mock 后端 workflow**（`.github/workflows/skillopt.yml`）：non-blocking，永不阻塞 PR；产物 `bench/reports/<run-id>/` 保留 30 天

**适用范围**：仅评测，**不自动部署**。SkillOpt 产出的 `best_skill.md` 永远经人工 review 后单独 commit。
**不适用**：v1.3 不接入 SkillOpt-Sleep（夜间收割本地会话，隐私边界未定，留 v1.4+）。

**与现有 CI 的关系**：

| 维度 | v0.1–v1.2 CI（结构） | v1.3 SkillOpt 评测（行为） |
|------|--------------------|--------------------------|
| 检查对象 | 静态文件（frontmatter / wikilink / 占位符） | 模型按 SKILL.md 执行后的产物（路径 / 字段 / 反馈文本） |
| 阻塞 merge | ✅ 阻塞 | ❌ 不阻塞（仅 nightly 信号） |
| 频次 | 每次 PR | nightly + 手动 dispatch |
| 后端 | Node.js 脚本 | SkillOpt + LLM（mock / chat / exec） |

详见 ADR-017 + [`docs/dev/v1.3-skillopt-integration.md`](./dev/v1.3-skillopt-integration.md)。

---

## 7. Agent 设计

### 7.1 quick-kb-manager-agent

**职责**：知识库管家 + 知识架构师，偏「整理与结构」。

| 能力 | 说明 |
|------|------|
| 整理 inbox | 按主题聚类 00_inbox 素材，推荐入库优先级 |
| 创建/更新 MOC | 扫描某领域笔记，生成或刷新 MOC |
| 推荐关联知识 | 给一条笔记，找出语义和标签相关的其他笔记 |
| 检测孤立笔记 | 列出无入链无出链的笔记，建议归档或连接 |
| 修复死链 | 找到指向已删除/改名的 wikilink |
| **识别结构演化** | 监测某子领域笔记数量增速，自动建议拆分/升格为新领域（如「MCP 半年 40 篇」→ 建议独立成 `areas/mcp/`） |
| **价值刷新** | Review 时重算 `value.reuse`，更新 Knowledge Score 排序 |

> 原反馈建议单列 Knowledge Architect Agent；本设计将其能力并入 manager，避免 agent 数量膨胀。结构演化建议作为 Review 闭环的输出之一，由人确认后执行。

**触发**：`quick-kb-connect`、`quick-kb-review` 内部调用，或用户直接唤起。

### 7.2 quick-kb-research-agent

**职责**：知识库研究员，偏「提取」（面向外部资料）。

| 能力 | 说明 |
|------|------|
| 处理 resources | 阅读长文/书籍摘录，抽取核心观点 |
| 提取核心观点 | 生成原子化笔记（一笔记一观点） |
| 交叉验证 | 比对多源，调整 `confidence` |
| 生成摘要 | 给原始资料生成结构化摘要卡 |

**触发**：`quick-kb-ingest`、`quick-kb-capture`（处理网页/PDF 时）内部调用。

### 7.3 quick-kb-memory-agent

**职责**：长期记忆调取者，偏「旧经验」（面向库内已有笔记）。

> 这是 quick-knowledge 作为「个人 AI 助手」而非「带引用的 RAG」的关键。quick-kb-research-agent 读新资料，quick-kb-memory-agent 调旧记忆。两者正交。

| 能力 | 说明 |
|------|------|
| 经验召回 | 给一个当前任务/问题，找出历史上类似情境的笔记（experience/pattern/decision） |
| 关联提醒 | 在事件触发时（见 7.6）主动推送「你之前在 X 项目遇到过类似问题：[[链接]]」 |
| 防重复犯错 | 检测当前计划是否与某条 `experience` 教训冲突，提出警告 |
| 信念核对 | 决策前检索相关的 `belief`/`principle`，提示是否一致 |
| **冲突感知** | 召回结果含 `contradicts` 关系时，**同时呈现冲突双方**及其 `context`，不擅自选边（见 ADR-011） |
| **失败案例优先** | 排序时 `experience`（特别是失败教训）权重高于普通 concept |

> 召回排序公式、输入输出契约、降级路径详见 [`AGENTS_SPEC.md`](./AGENTS_SPEC.md) §3。

**触发**：`quick-kb-advisor`、`quick-kb-project`（新开项目时）、`quick-kb-goal` 内部调用，或用户直接唤起（「我之前是不是做过类似的东西？」）；以及 7.6 主动提醒机制的事件触发。

**降级**：库内笔记 < 50 条时经验召回价值有限，agent 会返回「库内经验不足，以下基于通用建议」。

### 7.4 Agent 文件位置

agent 以**独立 skill** 形式分发，随 `npx skills add` 一起安装到 `skills/` 目录：

```
skills/
├── quick-kb-manager-agent/SKILL.md
├── quick-kb-research-agent/SKILL.md
└── quick-kb-memory-agent/SKILL.md
```

每个 agent skill 文件含：角色定义、可用工具、输入输出契约、调用示例。不绑定特定 runtime，任何支持 Agent Skills 的 runtime 都能加载。其他技能（advisor / ingest / connect 等）通过 Skill 工具按 intent 显式调用这三个 agent skill。

> 完整的输入/输出契约、排序公式、降级路径见 [`AGENTS_SPEC.md`](./AGENTS_SPEC.md)。

### 7.5 Agent 协作模型

```
外部资料 ──▶ quick-kb-research-agent ──▶ 新知识入库
                                       │
当前任务 ──▶ quick-kb-memory-agent  ──▶ 旧经验召回
                                       │
结构演化 ◀── quick-kb-manager-agent ◀── 全库状态
```

三个 agent 角色不重叠：
- **research**：读"外面"，产新笔记
- **memory**：读"里面"，调旧经验
- **manager**：管"结构"，维护索引与价值

### 7.6 主动提醒机制（V2 新增）

> V1 是「用户调用 → 系统响应」的被动模型。V2 引入**事件驱动的主动提醒**：知识主动找人，而非人找知识。

| 事件 | 触发 agent | 提醒示例 |
|------|-----------|---------|
| 新建项目（`quick-kb-project/init`） | quick-kb-memory-agent | 「你过去有 3 个类似项目：[[BI 插件体系]]、[[工作流引擎]]、[[MCP 工具设计]]，是否复用经验？」 |
| 新建目标（`quick-kb-goal/create`） | quick-kb-memory-agent | 「该目标关联领域 [[前端工程]] 有 2 条原则、1 个失败教训，建议先看」 |
| Capture 某主题素材 | quick-kb-memory-agent | 「这条素材与你 [[2024 RAG 实践]] 相关；注意 [[2025 RAG 失败教训]] 与之冲突」 |
| Ingest 新笔记 | quick-kb-manager-agent | 「新笔记与 [[既有笔记 X]] 语义相似度 0.88，建议建立 `supports`/`evolves` 关系」 |
| Ingest 检测冲突 | quick-kb-memory-agent | 「新结论与 [[2024 微服务最优论]] 在 `context: 创业团队` 下冲突，建议加 `contradicts` 并各自声明 context」 |
| Review 完成 | quick-kb-manager-agent | 「3 条高价值低置信笔记待验证；MCP 子领域建议升格独立」 |
| 长期未触碰某 `applied` 笔记 | quick-kb-manager-agent | 「[[某经验]] 已 6 个月未触碰，是否仍 `applied`？或降为 `deprecated`？」 |

**设计原则**：
- **提醒是建议，不是阻塞** —— 用户可忽略、可关闭某类提醒（`kb.config.yaml` 配置）。
- **去重与限流** —— 同一事件最多触发一次提醒；单次会话内提醒总数 ≤ 3。
- **可观测** —— 每条提醒都说明「为什么提醒、关联了哪些笔记」。
- **降级** —— 库内笔记 < 50 条时关闭主动提醒，避免噪音。

---

## 8. 模板系统

### 8.1 模板清单（中英双语）

`system/templates/` 下每类模板同时提供 `zh/` 和 `en/` 版本：

```
system/templates/
├── zh/
│   ├── note-concept.md
│   ├── note-resource.md
│   ├── note-meeting.md
│   ├── note-idea.md
│   ├── daily.md
│   ├── review-weekly.md
│   ├── review-monthly.md
│   ├── review-quarterly.md
│   ├── review-yearly.md
│   ├── decision.md
│   ├── moc.md
│   ├── goal.md
│   ├── project.md
│   ├── principle.md              # 个人原则
│   ├── belief.md                 # 待验证假设
│   ├── pattern.md                # 可复用模式
│   └── experience.md             # 经历教训
└── en/
    └── ...（同名文件）
```

### 8.2 模板设计原则

- **占位符用 `{{var}}`**，便于 AI 填充。
- **必填字段用注释标注**：`# required`。
- **示例值内联**，让用户知道填什么。
- **模板即文档**，顶部含 1-2 行使用说明。

### 8.3 模板示例（concept）

```markdown
---
title: {{title}}
type: concept
created: {{date}}
updated: {{date}}
tags:
  - {{domain}}/{{topic}}
status: active
maturity: understood
confidence: 50
relations:
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
context: {{适用上下文，可选}}
source: {}                            # object 格式（v1.9.3 对齐 schema；空时可不写）
domain: {{domain}}
---

# {{title}}

## 核心定义
{{一句话说清这个概念是什么}}

## 为什么有用
{{解决了什么问题}}

## 关键组成
-

## 应用场景
-

## 关联知识
- [[相关概念]]

## 待验证
- [ ]
```

### 8.4 模板示例（decision · Decision Ledger）

V2 强化：决策记录是个人成长最核心的数据。模板含完整的 **预期 vs 实际 vs 教训** 闭环，lesson 由 `quick-kb-project` 归档时自动派生为 `experience` 笔记。

```markdown
---
title: {{决策标题，如"插件运行时选 Web Worker"}}
type: decision
created: {{date}}
updated: {{date}}
tags:
  - decision/{{domain}}
status: active                # active → done（决策落地）/ superseded（被新决策取代）
decision_id: {{YYYYMMDD-slug}}   # 与文件名一致，便于引用
context: {{决策时的上下文：团队/阶段/约束}}
relations:
  supports: []
  contradicts: []            # 与之冲突的历史决策
  evolves: []                # 由此决策演化的后续
  supersedes: []             # 取代了哪条旧决策
related_goal: "[[相关目标]]"  # 可选
related_project: "[[相关项目]]" # 可选
---

# {{决策标题}}

## 问题（Problem）
{{要解决什么问题，为什么现在需要决策}}

## 备选方案（Options）
1. **方案 A**：{{简述}} · 优点 / 缺点
2. **方案 B**：{{简述}} · 优点 / 缺点
3. **方案 C**：{{简述}} · 优点 / 缺点

## 选择（Chosen）
**方案 {{X}}**

## 理由（Reason）
{{为什么选这个；引用相关 principle/pattern：[[链接]]}}

## 拒绝原因（Rejected）
- 方案 {{Y}}：{{为什么不行}}
- 方案 {{Z}}：{{为什么不行}}

## 预期（Expected）
{{决策时预期会发生什么。决策落地后填写下方 actual}}

## 实际（Actual）
{{落地后的真实结果。可空，待项目归档或 review 时补}}

## 教训（Lesson）
{{expected ≠ actual 时学到了什么。自动派生为 [[experience 笔记]]}}

## 引用
- [[相关 principle]]
- [[相关 experience]]
```

> Decision Ledger 是 **ADR（Architecture Decision Record）** 的个人化变体：增加了 expected/actual/lesson 闭环，让每个决策长期产出经验。`supersedes` 关系记录决策更替链（A→B→C）。

---

## 9. Obsidian 集成

### 9.1 为什么选 Obsidian

- 本地优先的 Markdown 文件，与「知识库就是文件集合」的设计契合。
- 原生支持 wikilinks、frontmatter、canvas、Bases。
- 拥有成熟的技能生态（[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)）。

### 9.2 与 kepano/obsidian-skills 的关系

`quick-knowledge` **依赖** obsidian-skills 提供的底层能力，而非重新实现：

| obsidian-skill | quick-knowledge 如何使用 |
|----------------|------------------------|
| `obsidian-markdown` | 写入笔记时遵守 wikilink、callout、properties 规范 |
| `obsidian-bases` | 生成 inbox/areas/goals 的 .base 视图做仪表盘 |
| `json-canvas` | Connect 闭环生成知识地图 .canvas |
| `obsidian-cli` | 与 Obsidian 应用交互（打开笔记、触发命令） |
| `defuddle` | Capture 闭环抓取网页时提取干净正文 |

### 9.3 集成方式

1. **依赖声明**：在框架文档中说明使用前应先安装 obsidian-skills。
2. **能力探测**：技能运行时检测 obsidian-skills 是否存在，缺失时降级为纯 Markdown 模式（不生成 .base/.canvas，保留 .md）。
3. **不重复造轮子**：wikilink 语法、callout 类型、frontmatter 字段名严格对齐 obsidian-markdown 的规范。

### 9.4 非 Obsidian 用户

quick-knowledge 同样适用于纯文件/VSCode/Cursor 用户。所有 .md 文件可独立读写，只有 .base/.canvas 是 Obsidian 专属。降级路径在技能内部实现，对用户透明。

---

## 10. 多语言策略

### 10.1 三层语言策略

| 层级 | 文件 | 语言策略 |
|------|------|---------|
| **设计文档** | `docs/` | 中文为主 |
| **README / 用户指南** | 根目录 `README.md` + `README_EN.md` 等 | 多语言，参考 nuwa-skill 模式（中/英/日/韩/西） |
| **模板文件** | `system/templates/zh/`、`en/` | 双语，按 `kb.config.yaml` 的 `language` 字段选用 |

### 10.2 README 多语言矩阵

```
README.md          # 中文（主）
README_EN.md       # English
README_JA.md       # 日本語（按需）
README_KO.md       # 한국어（按需）
```

中文为主，其他语言通过顶部语言切换栏互相链接，模式对齐 nuwa-skill。

### 10.3 技能内描述的多语言

每个 SKILL.md 的 `description` 字段同时含中英触发词，参考 nuwa-skill 写法：

```yaml
description: |
  初始化个人知识库目录结构与系统文件。
  触发词：「初始化知识库」「quick-kb-init」「setup kb」。
  English triggers: "init knowledge base", "setup kb".
```

---

## 11. 仓库结构

本仓库（即将发布到 GitHub）的结构：

```
quick-knowledge/
├── README.md                       # 中文 README（主）
├── README_EN.md                    # English README
├── LICENSE                         # MIT
├── CONTRIBUTING.md
├── COMMUNITY.md
├── docs/                           # 设计文档（本目录）
│   ├── DESIGN.md                   #   本文件
│   ├── SKILLS_SPEC.md              #   技能详细规格
│   ├── AGENTS_SPEC.md              #   agent 详细规格（memory/manager/research）
│   ├── VERSIONING.md               #   版本化规则
│   ├── CHANGELOG.md                #   变更记录
│   └── archive/                    #   历史版本归档
├── skills/                         # 技能源码
│   ├── quick-kb-init/SKILL.md
│   ├── quick-kb-capture/SKILL.md
│   ├── quick-kb-ingest/SKILL.md
│   ├── quick-kb-connect/SKILL.md
│   ├── quick-kb-query/SKILL.md
│   ├── quick-kb-advisor/SKILL.md
│   ├── quick-kb-review/SKILL.md
│   ├── quick-kb-daily/SKILL.md
│   ├── quick-kb-goal/SKILL.md
│   └── quick-kb-project/SKILL.md
├── templates/                      # 双语模板
│   ├── zh/
│   └── en/
├── references/                     # 方法论参考文档
│   ├── six-loops.md                #   六大闭环详解
│   ├── metadata-schema.md          #   元数据规范
│   └── obsidian-integration.md     #   Obsidian 集成指南
├── examples/                       # 示例 vault
│   └── demo-vault/                 #   一个可运行的 demo 知识库
└── scripts/                        # 辅助脚本
    └── health-check.sh             #   健康检查脚本
```

> **注意**：本仓库本身是「技能框架」，不含具体用户的笔记。用户安装后在自选目录运行 `quick-kb-init` 生成自己的 vault（见第 4 节结构）。

---

## 12. 安装与分发

### 12.1 一行命令（推荐）

```bash
npx skills add <github-user>/quick-knowledge
```

### 12.2 手动安装（按 runtime）

| Runtime | 安装路径 |
|---------|---------|
| Claude Code | `~/.claude/skills/quick-knowledge/` |
| Codex CLI | `~/.codex/skills/quick-knowledge/` |
| Cursor | `~/.cursor/skills/quick-knowledge/` |
| OpenCode | `~/.opencode/skills/quick-knowledge/` |

### 12.3 初始化用户 vault

安装技能后，用户在任意空目录运行：

```
初始化我的知识库
```

技能会在当前目录生成第 4 节的目录骨架 + 系统文件。vault 位置完全由用户决定，与技能安装位置解耦。

---

## 13. 路线图

### v0.1 · MVP（2 周）

- [ ] `quick-kb-init` + `quick-kb-capture` + `quick-kb-ingest` + `quick-kb-daily`
- [ ] 中文模板（concept、idea、daily、resource）
- [ ] 基础 frontmatter 规范
- [ ] demo-vault 示例

### v0.2 · 闭环完整（2 周）

- [ ] `quick-kb-connect` + `quick-kb-query` + `quick-kb-review`
- [ ] quick-kb-manager-agent + quick-kb-research-agent
- [ ] Obsidian-skills 集成（降级路径）
- [ ] 英文模板

### v0.3 · 个人助手（2 周）

- [ ] `quick-kb-advisor`（基于个人经验辅助决策）
- [ ] `quick-kb-memory-agent`（长期记忆调取）
- [ ] `quick-kb-goal`（含学习路径推荐）
- [ ] `quick-kb-project`（含归档）
- [ ] **认知资产**：principle/belief/pattern/experience 模板与 `principles/` 目录
- [ ] **maturity 字段**与 Knowledge Score 计算
- [ ] decision、review 系列模板

### v0.4 · 扩展与多语言（2 周）

- [ ] `quick-kb-normalize` / `quick-kb-archive` / `quick-kb-stats`
- [ ] README 多语言（英/日/韩）
- [ ] `kb.config.yaml` 完整支持

### v1.0 · 发布（1 周）

- [ ] 完整文档与示例
- [ ] CONTRIBUTING + COMMUNITY
- [ ] 发布到 skills marketplace

### v1.1 · 目录流转制（已发布 2026-08-09）

- [x] 顶层目录 `NN_` 前缀（BREAKING，ADR-015）
- [x] 文档引用绝对路径硬约束

### v1.2 · AI 润色提议（已发布 2026-08-09）

- [x] capture / daily 写入前的 AI 润色提议步骤（ADR-016）
- [x] `source.original_text` / `<!-- original: -->` 原文保存机制
- [x] `kb.config.capture_ai` 配置段

### v1.3 · SkillOpt 行为评测（已发布 2026-08-11）

- [x] 自定义 SkillOpt benchmark `quickkb`（dataloader + rollout + adapter，ADR-017）
- [x] 4 个评分器：routing / frontmatter / behavior / flow
- [x] 51 个 golden case（45 单点 × 9 维度 + 6 J 类端到端流程）
- [x] nightly mock 后端 workflow（non-blocking，`.github/workflows/skillopt.yml`）

---

## 14. 设计决策记录

记录关键设计取舍，便于未来回溯。

### ADR-001 · 选用 PARA 而非单纯分类树

**背景**：知识库需要同时容纳「有截止日期的项目」和「长期积累的领域」。
**决策**：projects（临时）/ areas（长期）/ resources（外部）/ archive 分离，即 PARA 模型。
**代价**：用户需理解四类差异；inbox 作为缓冲降低归类压力。

### ADR-002 · Capture 不分类

**背景**：采集阶段强制分类会导致用户放弃记录。
**决策**：Capture 一律进 inbox 子目录（按素材类型而非主题），Ingest 阶段才决定去向。
**代价**：inbox 需要定期清理，依赖 Review 闭环兜底。

### ADR-003 · 强制引用而非自由问答

**背景**：自由问答会让 AI 编造内容，污染知识库信任度。
**决策**：Query 技能在回答时必须给出 `[[]]` 引用或 `source` 链接，否则回答「知识库中未找到，以下为推测」。
**代价**：召回率低于自由问答，但可信度优先。

### ADR-004 · 文档状态与知识成熟度分离

**背景**：原 `status` 同时承载「文档阶段（inbox/draft/done）」和「知识阶段（learning/mastered/stale）」两个维度，耦合后语义混乱。
**决策**：拆为正交两字段 —— `status` 只描述文档生命周期；`maturity`（captured→understood→validated→applied→teachable→deprecated）描述知识成熟度；`confidence` 是连续数值，由 maturity 推荐区间但不强制。
**代价**：多一个字段；好处是「一个已归档项目里仍 teachable 的经验」可以正确表达（status=archived, maturity=teachable）。
**反馈来源**：外部评审「问题 1 · 缺少知识生命周期模型」（采纳并简化为 6 态）。

### ADR-005 · 不引入数据库

**背景**：是否用 SQLite/向量库存索引？
**决策**：不引入。所有索引由 MOC 笔记 + Obsidian Bases 视图承担。
**代价**：超大规模 vault（>1 万条）检索会变慢；本框架面向个人，暂不优化该规模。

### ADR-006 · 框架与用户 vault 分离

**背景**：框架本身要不要就是一个 vault？
**决策**：分离。框架仓库只含技能/模板/agent，用户 vault 由 `quick-kb-init` 在用户目录生成。
**代价**：需要 init 步骤；好处是框架可独立升级，不污染用户数据。

### ADR-007 · 认知资产作为一等公民

**背景**：个人知识库与通用 Wiki 的本质区别在于「记的是谁的、谁的判断」。
**决策**：新增 `principles/` 根目录，承载 principle/belief/pattern/experience 四类认知资产，作为独立 type 枚举。它们横切领域、无 `domain`，但允许领域目录覆盖（领域专属原则）。
**代价**：用户需区分"客观概念"与"个人判断"；好处是 advisor/quick-kb-memory-agent 能基于"这个人相信什么、犯过什么错"提供个性化决策。
**反馈来源**：外部评审「问题 2 · 缺少个人认知模型」（采纳）。

### ADR-008 · 价值维度自动化优先

**背景**：单 `confidence` 不够（一条永远用不到的高置信笔记价值为零）；但让用户手填 reuse/impact/uniqueness 违反"采集零摩擦"。
**决策**：`value.reuse` 由 quick-kb-manager-agent 在 Review 时自动计算（入链数 + 查询命中数）；`impact`/`uniqueness` 可选手动，未填走默认值。综合 Knowledge Score 用于排序，不强制写入笔记。
**代价**：reuse 需要查询日志支撑（早期 vault 数值偏低）；好处是零额外摩擦。
**反馈来源**：外部评审「问题 5 · 缺少知识评分体系」（部分采纳，拒绝手填三分数）。

### ADR-009 · Memory Agent 与 Research Agent 正交

**背景**：是否需要一个"调旧经验"的 agent？
**决策**：新增 quick-kb-memory-agent。quick-kb-research-agent 读外部新资料（产新笔记），quick-kb-memory-agent 调库内旧经验（防重复犯错、关联提醒）。两者输入域不重叠。
**代价**：库内笔记 < 50 条时 memory 召回价值有限，需降级提示；好处是 quick-knowledge 从「带引用的 RAG」升级为「个人决策助手」。
**反馈来源**：外部评审「问题 3 · Agent 设计偏弱」（采纳 quick-kb-memory-agent；将 Knowledge Architect 能力并入 manager 而非单列）。

### ADR-010 · query 与 advisor 并列而非替换

**背景**：Query 应该升级为"辅助思考"吗？
**决策**：保留 `quick-kb-query`（事实型，强制引用，回答"是什么/有没有"），新增 `quick-kb-advisor`（思考型，基于个人认知资产综合建议，回答"怎么做"）。两者并列，触发语义不同。
**代价**：用户需区分两种问法；好处是事实检索不滑向主观推测、决策辅助不被引用严格性束缚。
**反馈来源**：外部评审「问题 4 · Query 设计需要升级」（部分采纳，新增并列技能而非替换）。

### ADR-011 · 关系类型化与冲突管理

**背景**：V1 只有扁平 `related`，无法表达"为什么关联"；个人知识随上下文变化必然冲突（"微服务适合大系统" vs "模块化单体适合创业团队"都成立），无冲突管理会让 AI 不知信谁。
**决策**：（1）`related` 升级为类型化 `relations: { supports, contradicts, evolves, supersedes }`，扁平 `related` 保留为兼容回退；（2）新增自由文本 `context` 字段声明适用情境；（3）`maturity=deprecated` 必须关联 `supersedes` 或 `contradicts` 至少一项；（4）Query/advisor 召回冲突笔记时必须同时呈现并标注 context，不擅自选边。
**代价**：frontmatter 更重；好处是冲突显式化、可追溯，长期不出现"AI 不知道信哪个"。
**反馈来源**：外部评审「问题 1 · 缺少知识冲突管理」（采纳核心；将结构化 `context: {team_size,stage}` 改为自由文本以防摩擦）。

### ADR-012 · Decision Ledger 强化

**背景**：V1 已有 `type: decision` 和 `outputs/decisions/`，但模板字段不够结构化，缺少"预期 vs 实际 vs 教训"闭环。
**决策**：decision 模板强化为 Decision Ledger 风格 —— problem/options/chosen/reason/rejected/**expected/actual/lesson**；lesson 字段在项目归档或 review 时由 AI 自动派生为独立 `experience` 笔记；决策更替通过 `relations.supersedes` 链式记录。
**代价**：单个决策笔记字段较多；好处是每个决策长期产出可复用经验，是个人成长最核心的数据。
**反馈来源**：外部评审「问题 2 · 缺少 Decision Ledger」（采纳；模板增强而非新增目录，因 `outputs/decisions/` 已存在）。

### ADR-013 · 主动提醒机制

**背景**：V1 是"用户调用 → 系统响应"的被动模型；个人助手的关键差异是"知识主动找人"。
**决策**：不新增提醒技能，而是引入**事件驱动的主动提醒机制**（§7.6）—— 在 project/init、goal/create、capture、ingest、review 等技能工作流的关键节点，由 quick-kb-memory-agent/quick-kb-manager-agent 主动推送提醒（相似经验、冲突警告、结构演化建议等）。
**代价**：需要限流与去重避免噪音；好处是用户无需主动检索即可受益于历史经验。
**权衡**：提醒是建议非阻塞；可在 `kb.config.yaml` 关闭某类提醒；库内笔记 < 50 条时关闭。
**反馈来源**：外部评审「问题 4 · 缺少主动提醒机制」（采纳为机制而非新技能）。

### ADR-014 · Memory Agent 详细规格独立成文

**背景**：V1 在 DESIGN §7.3 给了 quick-kb-memory-agent 能力表，但无输入/输出/排序公式等详细规格；advisor 调用它却无契约，存在退化成普通 RAG 的风险。
**决策**：新建 `docs/AGENTS_SPEC.md`，规格化 manager/research/memory 三 agent，重点是 quick-kb-memory-agent 的召回排序公式 `similarity × recency × impact × confidence` 与降级路径。
**代价**：多一个文档维护；好处是 agent 行为可预期、可被任意技能按契约调用。
**反馈来源**：外部评审「问题 3 · Memory Agent 需要更详细设计」（完全采纳）。

### ADR-015 · 目录加两位数字前缀实现流转可视化

**背景**：v1.0 vault 顶层目录采用扁平命名（inbox/ areas/ ... archive/ system/）。IDE 文件浏览器按字典序展示，archive 与 areas 相邻、inbox 与 goals 相邻，丢失了「输入 → 沉淀 → 目标 → 执行 → 产出 → 索引 → 系统」的流转语义。用户肉眼无法判断笔记处在管线哪个阶段。
**决策**：v1.1 起所有 vault 顶层目录加 `NN_` 前缀，按流转顺序编号：00_inbox（输入）/ 01_resources（原材料）/ 02_areas（沉淀）/ 03_goals（牵引）/ 04_projects（执行）/ 05_outputs（产出）/ 06_wiki（索引）/ 07_principles（元层）/ 98_archive（退出）/ 99_system（底层）。98/99 借鉴 UNIX 高编号表底层的传统。
**代价**：BREAKING CHANGE。v1.0 vault 无法自动迁移，用户需手动 `mv`（迁移指南见 `docs/dev/v1.1-restructure.md`）。目录名长度增加 3 字符。
**否决的替代方案**：
- 用 `_` 前缀做置顶（Obsidian 兼容但失去排序能力）
- 用 emoji 前缀（跨平台渲染不一致、IDE 文本搜索不友好）
- 用 `.inbox` 隐藏目录（破坏用户直观浏览）
- 仅靠 README 文档说明流转顺序（不解决 IDE 字典序问题）
**反馈来源**：用户在 v1.0 发布后的指令（2026-08-09）——「知识库目录按输入→沉淀→目标→执行→产出→索引→系统的流转逻辑排序，加上两位数字前缀固定顺序」。

---

### ADR-016 · AI 润色提议：用户确认才改写，原文永不丢

**情境**：用户反馈 capture / daily 时输入过简，事后看不懂。AI 直接静默改写又违反「不改正文」原则（ADR-002 衍生）。

**决策**：v1.2 起，在 capture / daily 写入前加入「AI 润色提议」步骤——AI 主动生成扩写版，用户三选一（用润色 / 保留原文 / 再改一版）。**用户选 [1] 才写润色版**，且原文必须存入 `source.original_text`（capture）或 `<!-- original: ... -->` 行内注释（daily）。

**代价**：
- 增加一次交互（用户需选一次）→ 缓解：触发条件用启发式，长输入根本不进润色流程
- prompt 注入风险 → 缓解：润色 prompt 固化在 kb.config，用户输入仅作「待扩写素材」加引号传入

**否决的替代方案**：
- AI 静默自动改写（违反「不改正文」，破坏信任）
- 纯触发词模式（用户得记额外命令，反摩擦）
- 全局开关 + 自动润色（用户失去逐条决策权）
- 仅扩展到所有 capture 类型（web-clip 抓取正文是外部来源，逐字保留是更强原则）

**与 ADR-002 的关系**：ADR-002 决定「capture 阶段不分类」，本 ADR 决定「capture 阶段可选改写」。两者都强调「降低采集摩擦」——润色提议不改「采集零等待」原则，因为它是**异步可选**的（用户可一直选 [2] 走原流程）。

**反馈来源**：用户在 v1.1 发布后的指令（2026-08-09）——「记录灵感、每日事务等用户输入项时，可以提供 AI 优化的描述（用户可以自定义选择是否优化），因为大部分时候用户输入的过于简单」。

---

### ADR-017 · 引入 SkillOpt 做行为评测（v1.3+）

**情境**：v0.1–v1.2 全部 CI 都是静态结构校验（frontmatter 字段、wikilink 死链、占位符、demo-vault 目录）。SKILL.md 改一行就可能让 capture 行为退化（如 v1.2 加步骤 2.5），而 CI 完全察觉不到。需要行为评测补齐测试能力。

**决策**：v1.3 引入 [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) 作为外部库（pip install skillopt），写自定义 benchmark `quickkb`：
- 4 件套：`QuickkbDataLoader`（SplitDataLoader 子类）+ `run_batch`（rollout helper）+ `QuickkbAdapter`（EnvAdapter 子类）+ YAML config
- 51 个 golden case：45 单点 × 9 维度 + 6 J 类端到端流程衔接
- 4 个评分器：routing（路径）/ frontmatter（字段）/ behavior（润色/去重/注入）/ flow（流程契约）
- nightly mock 后端 workflow，**永不阻塞 merge**

**代价**：
- 引入 Python 依赖（`requirements-bench.txt` 单独分离，主项目仍纯 Node.js + markdown）
- SkillOpt 上游 API 漂移风险（v0.2 → v0.3 可能改 EnvAdapter 接口）→ 缓解：锁版本 `skillopt>=0.2.0,<0.3.0`
- mock 后端测出的优化在真实环境可能失效 → 缓解：MVP 不自动部署，永远人工 review

**否决的替代方案**：
- 直接用 SkillOpt 内置 benchmark（DocVQA / ALFWorld / OfficeQA / SearchQA 等都是外部 QA 任务，无法验证「文件真的被写到对的地方」，语义不匹配）
- 自己写测试框架（重复造轮子，且无法享受 SkillOpt 的 Reflect → Aggregate → Update 优化循环）
- 把行为评测放进 PR 阻塞 CI（行为评测需要 LLM 调用，成本高 + 易抖动，应作信号而非 gate）

**与 v1.2 的关系**：v1.2 的「AI 润色提议」是首个被 v1.3 行为评测显式覆盖的特性（B 类 8 个 case 验证润色触发 / 三选一 / 降级路径 / web-clip 优先级边界）。SkillOpt 让 v1.2 之后的所有 SKILL.md 改动有了回归测试网。

**与 SkillOpt-Sleep 的边界**：v1.3 只用 SkillOpt 的「研究引擎」（train/eval），**不接入 SkillOpt-Sleep**（夜间收割本地会话）——Sleep 涉及读取本地 Claude Code/Codex 会话 JSONL，隐私边界需要单独 ADR-018 设计，留 v1.4+。

**反馈来源**：用户在 v1.2 发布后的指令（2026-08-10）——「现在想要利用 SkillOpt 来完善当前技能库的测试」。

---

## 附：参考项目

- [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) —— README 多语言、SKILL.md 写法、skills.sh 分发模式。
- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) —— Obsidian 集成的底层技能（markdown/bases/canvas/cli/defuddle）。
- [Agent Skills 协议](https://agentskills.io) —— 跨 runtime 技能规范。
- PARA 方法论（Tiago Forte）—— projects/areas/resources/archive 分类法。
- Zettelkasten —— 原子化笔记与双链思想。
