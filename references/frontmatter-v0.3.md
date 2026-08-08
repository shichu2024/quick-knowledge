---
version: V1
updated: 2026-08-09
phase: v0.3
applies_to: v0.3 技能产出的所有正式笔记
source_of_truth: docs/DESIGN.md §6
supersedes: references/frontmatter-v0.2.md（v0.2 字段仍兼容，v0.3 起知识型笔记加 maturity）
---

# v0.3 · Frontmatter 完整规范（含 maturity / KS）

> 本文件锁定 v0.3 阶段所有技能产出的 frontmatter 字段范围。在 v0.2 基础上为知识型笔记启用 `maturity`（6 态），为 value 启用 `impact`/`uniqueness`，引入 Knowledge Score 排序。
>
> **真相源**：`docs/DESIGN.md` §6。

---

## 1. 与 v0.2 的差异

| 字段 | v0.2 | v0.3 | 备注 |
|------|------|------|------|
| `maturity` | ❌ | ✓ 知识型笔记必填 | 6 态，DESIGN §6.4 |
| `value.impact` | ❌ | ✓ 可选手填（1-5） | DESIGN §6.6 |
| `value.uniqueness` | ❌ | ✓ 可选自动估算（1-5） | DESIGN §6.6 |
| `type` 子集 | concept/resource/idea/daily/moc/review | + **principle/belief/pattern/experience**（认知资产） | DESIGN §6.2 |
| KS 公式 | ❌ 不计算 | ✓ review 时由 manager 计算排序 | DESIGN §6.6 |

> v0.2 旧笔记不强制回填；可通过 v0.4 normalize 批量补齐。

---

## 2. 字段清单（正式笔记 · v0.3 全量）

| 字段 | 必填 | 类型 | v0.3 说明 | DESIGN |
|------|------|------|----------|--------|
| `title` | ✓ | string | 笔记标题 | §6.1 |
| `type` | ✓ | enum | 完整 14 类（见 §3） | §6.2 |
| `created` | ✓ | ISO date | YYYY-MM-DD | §6.1 |
| `updated` | ✓ | ISO date | YYYY-MM-DD | §6.1 |
| `tags` | ✓ | string[] | 受控标签 | §6.1 |
| `status` | ✓ | enum | 完整 6 态（inbox/draft/active/done/cancelled/archived） | §6.3 |
| `maturity` | **知识型必填** | enum | 6 态（见 §4） | §6.4 |
| `confidence` | ✓ | number 0-100 | ingest 时初值；review 调整 | §6.5 |
| `relations` | ✓（结构） | object | 类型化关系 | §6.7 |
| `context` | 可选 | string | 自由文本适用上下文 | §6.8 |
| `value` | ✓（结构） | object | reuse（自动）/ impact（手填）/ uniqueness（估算） | §6.6 |
| `source` | 可选 | list | 原始来源 | §6.1 |
| `domain` | 可选 | string | 所属领域（认知资产 4 类无 domain） | §6.1 |

---

## 3. type 枚举（完整 14 类 · DESIGN §6.2）

| 类别 | type | 主要存放 |
|------|------|---------|
| 知识 | concept | areas/ |
| 知识 | **principle** | principles/principles/ |
| 知识 | **belief** | principles/beliefs/ |
| 知识 | **pattern** | principles/patterns/ |
| 知识 | **experience** | principles/experiences/ |
| 资源 | resource | resources/ |
| 文档 | daily | outputs/daily/ |
| 文档 | review | outputs/reviews/ |
| 文档 | decision | outputs/decisions/ 或 projects/<slug>/decisions/ |
| 文档 | moc | wiki/mocs/ |
| 实体 | goal | goals/<slug>/ |
| 实体 | project | projects/<slug>/ |
| 入口 | idea | inbox/ideas/ |

### 3.1 认知资产 4 类（v0.3 新增）

| type | 含义 | 核心字段 |
|------|------|---------|
| `principle` | 个人原则 · 跨项目方法论、价值观底线 | maturity 通常 ≥ validated |
| `belief` | 待验证的个人假设/判断 | maturity 通常 captured/understood |
| `pattern` | 可复用的解决模式 | maturity 通常 ≥ applied |
| `experience` | 具体历史事件/教训（含失败） | 来自 Decision Ledger 的 lesson 派生 |

**核心区别**（ADR-007）：
- 这 4 类**无 `domain`**（横切）
- 允许领域覆盖：如 `areas/front-end/principles.md` 是该领域专属原则集
- 是 quick-knowledge 与通用 Wiki 的本质差异

---

## 4. maturity 6 态（DESIGN §6.4）

```
captured → understood → validated → applied → teachable
                                            │
                                            └─（长期未触碰/被推翻）─→ deprecated
```

| 值 | 含义 | confidence 通常区间 |
|----|------|------------------|
| `captured` | 刚记下，只是知道存在 | 0-30 |
| `understood` | 能讲清是什么 | 31-60 |
| `validated` | 多源/实践验证 | 61-80 |
| `applied` | 在真实场景用过 | 81-90 |
| `teachable` | 能教他人，可写可讲 | 91-100 |
| `deprecated` | 已过期/被推翻，保留作历史 | — |

### 4.1 适用范围

- **知识型笔记**（concept/principle/belief/pattern/experience）**必填**
- **文档型笔记**（daily/review/decision/moc）**不需要**
- 资源型（resource）可选（一般 captured/understood）

### 4.2 deprecated 强制关联（ADR-011）

降为 `deprecated` 时**必须**在 `relations.supersedes`（被新笔记取代）或 `relations.contradicts`（与之冲突）中至少填一项。

理由：避免「AI 不知道该信哪条」。

### 4.3 confidence vs maturity

- confidence：连续数值（0-100），由人填，AI 推荐
- maturity：离散阶段，反映角色转变
- 两者**相关但不绑定** —— 一条 `applied` 的经验 confidence 可以是 85，但一条 `teachable` 的官方文档条款也可以是 98

---

## 5. Knowledge Score（DESIGN §6.6）

```
KS = confidence × log2(1 + reuse) × impact
```

- `confidence`：0-100
- `reuse`：`value.reuse`（自动）
- `impact`：`value.impact`（1-5，未填按 3 计）

**KS 不强制写入笔记**，仅 review 时由 manager-agent 计算排序用。

### 5.1 优先处理两类

- **高价值低置信**（KS 高但 confidence < 60）→ 该去验证了
- **低复用高占用**（confidence 高但 reuse = 0）→ 该连 MOC 或归档

### 5.2 value 字段（v0.3 全量）

```yaml
value:
  reuse: 12         # 自动 · 入链 + 推荐频次 + 查询命中
  impact: 4         # 可选手填 · 1-5 · 默认 3
  uniqueness: 3     # 可选/自动估算 · 1-5 · 基于标签稀缺度
```

---

## 6. 完整示例（concept · 知识型）

```yaml
---
title: RAG 架构设计
type: concept
created: 2026-08-09
updated: 2026-08-09
tags:
  - ai/rag
  - eng/architecture
status: active
maturity: understood           # v0.3 新增
confidence: 60
relations:
  supports: ["[[Vector Database]]"]
  contradicts: []
  evolves: ["[[RAG 基础概念]]"]
  supersedes: []
context: "通用 RAG 架构；创业团队请参考 [[轻量 RAG 方案]]"
value:                         # v0.3 完整
  reuse: 12
  impact: 4                    # v0.3 新增
  uniqueness: 3                # v0.3 新增
source:
  - note: "[[inbox/clips/20260809-1000-rag-article]]"
domain: ai-engineering
---
```

## 7. 认知资产示例（experience · 由 Decision Ledger 派生）

```yaml
---
title: 2024 插件沙箱逃逸教训
type: experience
created: 2024-XX-XX
updated: 2026-08-09
tags:
  - eng/security
  - lesson/plugin-sandbox
status: active
maturity: applied              # 经验已应用
confidence: 85
relations:
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
context: "BI Engine 内部工具，团队 8 人，进程级隔离方案"
value:
  reuse: 5
  impact: 5
  uniqueness: 4
source:
  - note: "[[projects/bi-engine/decisions/001-隔离方案]]"
derived_from: "[[决策 001：选型 Y]]"   # v0.3 派生关系
# domain 字段不写（认知资产横切）
---

# 2024 插件沙箱逃逸教训

## 事件
{{具体历史事件}}

## 教训（lesson）
{{从 Decision Ledger 派生}}

## 适用范围
{{context 详述}}
```

---

## 8. Inbox 最小集（不变）

仍遵循 DESIGN §6.9：`title` + `captured_at`。

---

## 9. 校验规则（v0.3 增量）

在 v0.2 校验基础上：

1. **知识型笔记**必须有 `maturity`（concept/principle/belief/pattern/experience）
2. 文档型笔记（daily/review/decision/moc）**不应**有 `maturity`（如出现 → 警告）
3. `maturity: deprecated` 必须有 `relations.supersedes` 或 `relations.contradicts` 至少一项
4. 认知资产 4 类（principle/belief/pattern/experience）**不应**有 `domain`
5. `value.impact` 未填 → review 时按 3 计（不阻塞）

---

## 10. 升级路径

- **v0.2 → v0.3**：v0.3 技能开始写 maturity + 完整 value；认知资产目录启用；KS 排序在 review 落地
- **v0.3 → v0.4**：normalize 批量回填历史笔记；archive/stats/import 扩展技能；config 完整支持
- **v0.4 → v1.0**：发布打磨，无新字段
