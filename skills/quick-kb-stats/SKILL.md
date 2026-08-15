---
name: quick-kb-stats
description: |
  输出 vault 健康仪表盘。总笔记数 / type 分布 / 孤立率 / frontmatter 缺失率 / 置信度分布 / maturity 6 态分布 / KS Top 10 / 高价值低置信 / 低复用高占用 / inbox 周转时长。
  只读，不改笔记。
  触发词（中文）：KB 统计 / 健康度 / 仪表盘 / vault 状态
  Triggers (EN): kb stats / vault health / dashboard
version: v1.9.1
phase: v0.4
applies_to: 只读全库 · 输出 05_outputs/reviews/adhoc/
source_of_truth:
  - docs/DESIGN.md §6.5（KS）/ §6.4（maturity）/ §6.3（captured_at）
  - docs/SKILLS_SPEC.md §11
  - docs/dev/v0.4-extensions.md WP3
  - references/wikilink-conventions.md（v1.6 · 死链统计口径）
---

# quick-kb-stats（v0.4）

> **健康仪表盘**：一次性输出 vault 的健康指标快照。只读。

---

## 1. 何时调用

- 用户说「KB 统计一下 / 看看健康度 / vault 仪表盘」
- 周期性 review 之前先看 stats
- normalize/archive 大批量操作后验证效果

---

## 2. v0.4 范围

### 做

- 计算全部指标（见 §4）
- 输出 Markdown 报告到 `05_outputs/reviews/adhoc/stats-YYYY-MM-DD.md`
- 输出 Obsidian Bases 视图配置（如启用）
- 与上次 stats 对比（若存在）

### 不做

- ❌ 不修改任何笔记
- ❌ 不主动建议修复（用户基于报告决定）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| 范围 `scope` | 否 | `all` | `all` / `<domain>` / `inbox` / `<type>` |
| 项 `metrics` | 否 | 全部 | 指定输出哪些指标（逗号分隔） |
| 对比 `compare` | 否 | `true` | 是否与上次 stats 对比 |
| 输出 `output` | 否 | `write` | `write` / `stdout`（仅终端） |

---

## 4. 指标清单（DESIGN §6.5 / dev doc WP3）

| 指标 | 计算 | 来源字段 |
|------|------|---------|
| 总笔记数 | 计数 | 全库 .md 文件数 |
| 各 type 分布 | 按 type 计数 + 占比 | frontmatter.type |
| 各 status 分布 | 按 status 计数 | frontmatter.status |
| 孤立笔记率 | (无入链 AND 无出链) / 总数 | wikilink 图谱 |
| frontmatter 缺失率 | 缺失必填字段的笔记数 / 总数 | 详见 §4.1 |
| 置信度分布 | 直方图（0-30 / 31-60 / 61-85 / 86-100 · 0-100 量纲） | frontmatter.confidence |
| maturity 6 态分布 | captured/understood/validated/applied/teachable/deprecated 计数 | frontmatter.maturity |
| Knowledge Score Top 10 | 按 KS 降序前 10 | frontmatter.value.ks（或实时计算） |
| 高价值低置信清单 | KS ≥ 中位数 AND confidence < 60（0-100 量纲） | KS + confidence |
| 低复用高占用清单 | confidence ≥ 70（0-100 量纲） AND value.reuse = 0 | confidence + value.reuse |
| inbox 周转时长 | 平均 captured_at → status 离开 inbox 的天数 | frontmatter.captured_at + 历史 |
| 死链数 | 找不到对应文件的 [[X]] 数（按 [`wikilink-conventions.md`](../../references/wikilink-conventions.md) §8 口径判定） | wikilink 扫描 |
| MOC 数 | 06_wiki/mocs/ 下文件数 | 文件路径 |
| 孤立 MOC | 无入链的 MOC | wikilink 图谱 |
| domain 分布 | 按 domain 计数 + 占比 | frontmatter.domain |
| 近 30/90 天活跃度 | 近 N 天 updated 的笔记数 | frontmatter.updated |

### 4.1 frontmatter 必填字段（v0.4 视角）

- `title` / `type` / `created` / `updated` / `status` / `confidence`
- 注：`maturity` / `value` / `relations` / `context` 为 v0.2+ 字段，对 v0.1 旧笔记不视为缺失
- **分母排除规则（v1.9.0）**：`00_inbox/` 下含 `capture_type` 的采集素材**设计上无** `type` / `status` 等字段——缺失率分母**仅计正式笔记**（排除含 `capture_type` 的 inbox 素材），inbox 素材另报「inbox frontmatter 覆盖率」（含 `captured_at` + `capture_type` 即合规）。避免把设计性缺字段计为 32%+ 的失真缺失率
- **本字段集为全技能统一的缺失率口径**（quick-kb-review 复盘复用）：报告输出该指标时注明「口径：quick-kb-stats §4.1」，确保同 vault 双技能计算结果必然相等

---

## 5. 工作流

```
1. 扫描全库（或 scope 指定范围）
   - 收集所有 .md 文件路径
   - 跳过 98_archive/ 与 99_system/ 目录（除非显式 scope）

2. 解析 frontmatter（YAML 区块）
   - 解析失败的笔记计入「frontmatter 损坏」类

3. 构建 wikilink 图谱：
   - 扫所有 [[X]] 引用
   - 计算每条笔记的入链数 / 出链数
   - 识别死链

4. 计算各指标（§4 表）

5. KS Top 10：
   - 若 frontmatter 已有 value.ks → 直接读
   - 否则实时计算：KS = confidence × log2(1 + reuse) × impact
   - 仅 maturity ≥ applied 的笔记参与排序
   - **冷启动说明（v1.9.0）**：新库全部笔记 maturity=captured（ingest 禁写、由 normalize 初始化）时 KS 恒空——报告中输出提示「冷启动：尚无 applied+ 笔记，跑 quick-kb-manager-agent intent=promote_maturity 评估晋升」，不算异常

6. inbox 周转时长：
   - 扫已离开 inbox 的笔记（status ≠ inbox 且 captured_at 存在）
   - 计算 (离开日期 - captured_at).days
   - 取平均 / 中位数 / P90
   - 注：离开日期不可考时记为 N/A

7. 与上次 stats 对比（若 05_outputs/reviews/adhoc/ 有历史）：
   - 总数变化、孤立率变化、KS Top 10 变化

8. 生成报告：
   - Markdown 格式
   - 含指标表 + 高价值低置信清单 + 低复用高占用清单 + KS Top 10 + 对比段
   - 输出到 05_outputs/reviews/adhoc/stats-YYYY-MM-DD.md
```

---

## 6. 输出示例

````markdown
# Vault 健康仪表盘 · 2026-08-09

> 范围：全库（不含 98_archive/system） · 总笔记数：87

## 总览

| 指标 | 当前 | 上次（2026-07-12） | 变化 |
|------|------|-------------------|------|
| 总笔记数 | 87 | 72 | +15 |
| 孤立笔记率 | 12.6%（11 条） | 18.1%（13 条） | ↓ 5.5% |
| frontmatter 缺失率 | 8.0%（7 条） | 22.2%（16 条） | ↓ 14.2% |
| 死链数 | 3 | 8 | -5 |
| 平均 inbox 周转 | 4.2 天 | 6.8 天 | ↓ 2.6 天 |

## Type distribution

| type | 数量 | 占比 |
|------|------|------|
| concept | 32 | 36.8% |
| resource | 21 | 24.1% |
| experience | 12 | 13.8% |
| idea | 9 | 10.3% |
| pattern | 6 | 6.9% |
| principle | 4 | 4.6% |
| belief | 3 | 3.4% |

## Maturity 6 态分布

```
captured   : 18 ████████
understood : 12 █████
validated  : 15 ██████
applied    : 28 ███████████
teachable  : 11 ████
deprecated :  3 █
```

## Maturity 转换漏斗（v1.7）

| 当前态 | 笔记数 | 上游来源 | 转换率 |
|--------|--------|---------|--------|
| captured | 18 | — | — |
| understood | 12 | captured→understood | 67% |
| validated | 15 | understood→validated | 125% |
| applied | 28 | validated→applied | 187% |
| teachable | 11 | applied→teachable | 39% |
| deprecated | 3 | any→deprecated | — |

⚠ 停滞态（笔记数 > 0 且转换率 = 0%）：无

## 置信度分布

| 区间 | 数量 |
|------|------|
| 0-30 | 5 |
| 31-60 | 21 |
| 61-85 | 43 |
| 86-100 | 18 |

## Knowledge Score Top 10

| # | 笔记 | KS | type | maturity |
|---|------|----|------|---------|
| 1 | [[RAG 架构设计]] | 184.2 | concept | teachable |
| 2 | [[2024 沙箱逃逸教训]] | 167.5 | experience | teachable |
| 3 | [[插件隔离模式]] | 142.1 | pattern | applied |
| ... | | | | |

## 高价值低置信（KS ≥ 中位数 AND confidence < 60）

- [[某新 concept]] · KS 78 / confidence 45 → 建议验证
- [[某待验 belief]] · KS 65 / confidence 40 → 建议验证或 deprecated

## 低复用高占用（confidence ≥ 70 AND reuse = 0）

- [[某 concept]] · confidence 85 / reuse 0 → 建议连 MOC 或归档
- [[某 pattern]] · confidence 80 / reuse 0 → 建议检查适用性

## 待修复

- frontmatter 损坏：2 条（[[X]] [[Y]]）
- 死链：3 处（[[Z1]] [[Z2]] [[Z3]]）
- → 建议 quick-kb-normalize + quick-kb-connect

## Obsidian Bases 视图（可选）

```bases
filters: type = "concept" AND maturity = "applied"
sorts: confidence DESC
view: table
```
````

---

## 7. Obsidian Bases 集成（可选）

若检测到库为 Obsidian vault（含 `.obsidian/`）：
- 报告末尾追加 Bases 配置片段
- 用户可粘贴到 `.obsidian/bases/kb-stats.base` 启用交互视图

若未启用 Obsidian：跳过此段，不影响主报告。

---

## 8. 幂等保证

- 同一天多次 stats：
  - 默认覆盖 `05_outputs/reviews/adhoc/stats-YYYY-MM-DD.md`
  - 保留 `stats-YYYY-MM-DD-HHMM.md`（备份）以备对比
- 全只读，对库无副作用

---

## 9. 降级路径

| 缺失依赖 | 降级行为 |
|---------|---------|
| frontmatter 损坏笔记 | 计入「损坏」类，不阻塞 |
| value.ks 字段未填 | 实时计算（DESIGN §6.5 公式） |
| captured_at 字段未填 | inbox 周转时长记为 N/A |
| 全库 < 20 条 | 仍输出报告，但标注「样本量不足，趋势不稳定」 |
| Obsidian 未启用 | 跳过 Bases 配置段 |

---

## 10. 边界

- **只读**：绝不修改笔记
- **不主动修复**：报告归报告，修复归 normalize/connect/review
- **不算复杂网络指标**（PageRank 等）：v0.4 范围内不实现，留待工具集成

---

## 11. 自检清单

- [ ] 总笔记数正确（不含 98_archive/system）
- [ ] type / status / maturity / domain 分布加总 = 总数
- [ ] 孤立率定义正确（无入链 AND 无出链）
- [ ] KS Top 10 仅 maturity ≥ applied 参与
- [ ] KS 实时计算公式：confidence × log2(1 + reuse) × impact
- [ ] 高价值低置信阈值正确（KS ≥ 中位数 AND confidence < 60）
- [ ] 低复用高占用阈值正确（confidence ≥ 70 AND reuse = 0）
- [ ] inbox 周转时长含平均 / 中位数 / P90
- [ ] 对比段引用上次 stats（若存在）
- [ ] 报告路径正确：05_outputs/reviews/adhoc/stats-YYYY-MM-DD.md
- [ ] Obsidian Bases 段仅 Obsidian vault 启用时输出
- [ ] 不修改任何笔记

---

## 12. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| 新增「死链数 / domain 分布 / 近 N 天活跃度」指标 | dev doc §4 指标表未列但 review/stats 实践常用 | docs/DESIGN.md §6 + 实现补强 |
| maturity 6 态分布以条形图 ASCII 呈现 | 报告可读性；Obsidian Bases 启用时同时给交互视图 | docs/dev/v0.4-extensions.md WP3 |
| inbox 周转时长含 P90 | dev doc 仅说「平均」；P90 更能反映异常长尾 | docs/dev/v0.4-extensions.md WP3 增强可观测 |
| KS 实时计算（value.ks 缺失时） | 避免强制依赖 normalize 先填字段 | docs/DESIGN.md §6.5 |
