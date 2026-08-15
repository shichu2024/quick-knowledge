---
name: quick-kb-review
description: |
  周期复盘 + 知识库健康检查。快照采集、刷新 value.reuse、四维度（knowledge/project/goal/daily）分析、健康报告 + 待办清单。KS 排序、结构演化、deprecated 自动降级推迟 v0.3。
  触发词（中文）：复盘本周 / 复盘这个月 / 年度复盘 / 扫一下孤立笔记 / KB 体检
  Triggers (EN): weekly review / monthly review / kb health check
version: v1.9.0
phase: v0.2
applies_to: 05_outputs/reviews/<period>/ + 各笔记 value.reuse
source_of_truth:
  - docs/DESIGN.md §6.6（价值维度）· §7.1（manager）
  - docs/SKILLS_SPEC.md §7
  - docs/dev/v0.2-loops.md WP6
  - references/filename-summary-rules.md（review 报告文件名 summary 提炼）
---

# quick-kb-review（v0.2 基础版）

> 周期复盘 + 健康检查。**只标记不删除**；deprecated 等状态变化由人确认。

---

## 1. 何时调用

- 用户说「复盘本周」「扫一下孤立笔记」「KB 体检」
- 定期提醒（用户自定义周期）

## 2. v0.2 范围

### 做

- 周期快照采集（daily/weekly/monthly/quarterly/yearly/adhoc）
- 调 `quick-kb-manager-agent` intent=`refresh_value`（返回结构见其 §0）刷新 `value.reuse`（入链数 + 查询命中数 + Connect 推荐频次）
- 四维度分析：knowledge / project / goal / daily
- 健康报告 + 待办清单（按优先级）
- 主动提醒（manager 事件子集）：Review 完成 → 提示处理高价值低复用笔记

### 不做（推迟 v0.3）

- ❌ Knowledge Score 排序（依赖 maturity）
- ❌ 结构演化建议（detect_structure_drift，依赖 KS）
- ❌ deprecated 自动降级提示（依赖 maturity）

---

## 3. 输入

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `period` | ✓ | — | `daily` / `weekly` / `monthly` / `quarterly` / `yearly` / `adhoc` |
| `focus` | 否 | `all` | `knowledge` / `project` / `goal` / `daily` / `all` |
| `range` | 否 | 当前周期 | 自定义，如 `2026-W32` 或 `2026-08` |

---

## 4. 工作流

### 步骤 1 · 快照采集

按 `period` 扫描对应数据源：

| period | 数据源 |
|--------|--------|
| daily | 05_outputs/daily/YYYY/MM/YYYY-MM-DD.md |
| weekly | 05_outputs/daily/YYYY/MM/ 当周 + 04_projects/*/notes 当周更新 |
| monthly | weekly 复盘 + 全月 daily |
| quarterly | monthly 复盘聚合 |
| yearly | quarterly 复盘聚合 |
| adhoc | 当前全库快照 |

### 步骤 2 · 价值刷新

调 `quick-kb-manager-agent`（intent=`refresh_value`）：

```
quick-kb-manager-agent(
  intent: "refresh_value",
  payload: {
    snapshot: {{全库快照}},
    query_log: {{读取 99_system/workflows/.query-log.jsonl}}
  }
) → {
  found: [{ path: "...", new_reuse: 12, old_reuse: 8 }, ...]
}
```

写回每条笔记的 `value.reuse`。

**recency_factor 计算（v1.7）**：在 refresh_value 时按 `references/scoring.md` §recency 规则计算时效性因子：

- `updated` 距今 ≤ 30 天 → 1.0
- 30-90 天 → 0.8
- 90-180 天 → 0.65
- > 180 天 → 0.5

该因子用于 KS 排序（review 的 KS 排序在 v0.3 启用）。

### 步骤 3 · 四维度分析

#### 3.1 knowledge 维度

- **孤立笔记率**：调 `quick-kb-manager-agent`（intent=`detect_orphans`）→ 无入链无出链 / 总数
- **重复嫌疑**：调 `quick-kb-manager-agent`（intent=`recommend_relations`）找相似度 > 0.85 但未建立 evolves/supersedes 的对
- **死链**：调 `quick-kb-manager-agent`（intent=`repair_deadlinks`）
- **frontmatter 缺失率**：与 `quick-kb-stats` §4.1 同口径——必填字段集为 `title` / `type` / `created` / `updated` / `status` / `confidence`（`maturity` / `value` / `relations` / `context` 为 v0.2+ 字段，对 v0.1 旧笔记不视为缺失）；扫描范围跳过 `98_archive/` 与 `99_system/`（除非显式 scope）；**分母排除含 `capture_type` 的 inbox 采集素材**（v1.9.0，设计上无 type/status）。健康指标表中该指标注明「口径：quick-kb-stats §4.1」，与 stats 计算结果必然相等
- **inbox 周转**：从 query-log 与 inbox 时间戳估算 captured_at → ingest 间隔

#### 3.2 value 维度（v0.2 简化版）

按 reuse + confidence 简单排序（不计算 KS）：

- **高价值低置信**（reuse 高但 confidence < 60）→ 该去验证了
- **低复用高占用**（confidence 高但 reuse = 0）→ 该连 MOC 或归档

#### 3.3 structure 维度（v0.2 仅基础）

- 各 domain 笔记数分布
- 近期增速（v0.2 仅报告数据，不做升格建议；v0.3 detect_structure_drift 接入）

#### 3.4 project 维度

- 活跃项目进度偏离
- 阻塞项（04_projects/*/notes 中 status=blocked 或含「卡点」关键词）

#### 3.5 goal 维度

- 目标进展（03_goals/*/progress/）
- 学习路径完成度（v0.3 goal 技能完善）

#### 3.6 daily 维度

- 时间分布（按 daily 笔记数量）
- 重复模式（关键词共现）

### 步骤 4 · 生成健康报告

写入 `05_outputs/reviews/<period>/` 下，文件名规则：
- **新建**：`<date-token>-<summary>.md`，其中 summary **必须**按 [`filename-summary-rules.md`](../../references/filename-summary-rules.md) §2 机械判定提炼 2-5 词 kebab-case（如 `rag-focus-week` / `q3-stabilization`）
  - weekly → `YYYY-Wxx-<summary>.md`
  - monthly → `YYYY-MM-<summary>.md`
  - quarterly → `YYYY-Qx-<summary>.md`
  - yearly → `YYYY-<summary>.md`
  - adhoc → `YYYY-MM-DD-<summary>.md`
- **旧文件优先**：同周期若已存在任何形式的报告（纯日期 / 已带 summary）→ **编辑既有文件，不重新提炼 summary，不改名**（与 daily §步骤 1 同样的稳定性约束）
- **summary 提炼机械判定**（按 [`filename-summary-rules.md`](../../references/filename-summary-rules.md) §2）：
  - **Step 1 强制纯周期 token**（命中任一即 `<date-token>.md`）：① 报告四维度全空 ② 实质字符 < 5 ③ 仅元描述无事件词
  - **Step 2 未命中 → 必须提炼** 2-5 词 ASCII kebab-case（如 `rag-eval` / `stabilization` / `auth-incident` / `m2-review`）
- **禁止语义绕过**：严禁用「维度多 / 主题分散 / 数据稀疏 / 周报难归纳」等借口退化为纯周期 token
  - 错误反例：主线是 RAG 评估调试 → ❌ `2026-W32.md`（借口「周报维度多」）→ ✅ `2026-W32-rag-eval.md`
  - 错误反例：季度稳定化为主 → ❌ `2026-Q3.md`（借口「季度主题分散」）→ ✅ `2026-Q3-stabilization.md`

#### 健康指标表

```markdown
## 健康指标

| 指标 | 当前 | 阈值 | 状态 |
|------|------|------|------|
| inbox 周转 | 4.2 天 | <7 天 | ✓ |
| 孤立笔记率 | 22% | <15% | ⚠ 超标 |
| frontmatter 缺失（口径：quick-kb-stats §4.1） | 3% | <5% | ✓ |
| 死链 | 2 条 | — | → 修复 |
| 重复嫌疑 | 1 对 | — | → 合并或 evolves |
| 高价值低置信 | 3 条 | — | → 优先验证 |
| 低复用高占用 | 5 条 | — | → 连 MOC 或归档 |
```

#### 维度详情

按 focus 段落展开各维度的发现。

### 步骤 5 · 产出待办（按优先级）

```markdown
## 待办（按优先级）

1. **[高]** 这 3 条高价值低置信笔记该去验证了：[[X]] [[Y]] [[Z]]
   → 调用 quick-kb-ingest 或手动调整 confidence

2. **[高]** 这 2 条死链需修复：[[A]] → [[B]]（已改名）
   → 调用 quick-kb-connect 修复

3. **[中]** 这 1 对重复嫌疑建议合并：[[P]] / [[Q]]
   → 调用 quick-kb-ingest（合并）或 quick-kb-connect（建立 evolves）

4. **[中]** inbox 有 5 条 >7 天未处理
   → 调用 quick-kb-ingest inbox

5. **[中]** 这 3 条孤立笔记建议归档或连接：[[I]] [[J]] [[K]]
   → 调用 quick-kb-connect 或 quick-kb-archive（v0.4）

6. **[低]** 这 5 条低复用高占用笔记该连 MOC 或归档
   → 调用 quick-kb-connect 或人工判断
```

每条待办挂一个可执行技能调用。

### 步骤 6 · 主动提醒（manager 事件子集）

调 `quick-kb-manager-agent`（intent=`proactive_remind`，event=`review_done`，context: `{ snapshot }`）：

- 提示处理高价值低复用笔记（已在 §5 待办）
- 长期未触碰笔记（updated > 6 个月）→ 提示重审
- 库 < 50 条时关闭

### 步骤 7 · 反馈输出

```
✓ Review 完成（period: weekly, range: 2026-W32）
  报告：05_outputs/reviews/weekly/2026-W32.md
  价值刷新：N 条笔记 value.reuse 更新
  待办：6 项（高 × 2 / 中 × 3 / 低 × 1）

  下一步建议：
    → 优先处理高价值低置信笔记 [[X]] [[Y]] [[Z]]
```

---

## 5. 输出契约

### 5.1 报告路径

- weekly：`05_outputs/reviews/weekly/YYYY-Wxx-<summary>.md`
- monthly：`05_outputs/reviews/monthly/YYYY-MM-<summary>.md`
- quarterly：`05_outputs/reviews/quarterly/YYYY-Qx-<summary>.md`
- yearly：`05_outputs/reviews/yearly/YYYY-<summary>.md`
- adhoc：`05_outputs/reviews/adhoc/YYYY-MM-DD-<summary>.md`

> `<summary>` **必须**按 [`filename-summary-rules.md`](../../references/filename-summary-rules.md) §2 机械判定提炼 2-5 词 ASCII kebab-case；同周期已存在旧文件 → 编辑不改名（详见 §步骤 4）。**禁止**用「维度多 / 主题分散」等语义借口退化为纯周期 token。

### 5.2 报告结构

- 健康指标表
- 维度详情（按 focus）
- 待办清单（含技能调用）
- 主动提醒（来自 `docs/AGENTS_SPEC.md` 附录的提醒规则）

---

## 6. 边界

- **只标记不删除** —— deprecated 是状态，不直接归档
- **不自动降级 maturity** —— v0.2 此字段未启用；v0.3 才有降级建议
- **不自动改 status** —— 仅建议，由人确认
- **降级**：仅做基于规则的最小检查（孤立笔记、死链、frontmatter 缺失）

## 7. 降级路径

| 场景 | 降级行为 |
|------|---------|
| 无 query-log | refresh_value 仅算入链数（按 AGENTS_SPEC §1.1 降级条款） |
| 无 query-log | refresh_value 仅算入链数 |
| 库内笔记 < 50 | 主动提醒关闭；仍出报告但提示「样本太少，建议先积累」 |
| 范围内无 daily 笔记 | 跳过 daily 维度，提示「无日志可分析」 |

---

## 8. 幂等保证

- 同 period/range 二次运行：覆盖报告文件（review 是衍生品）
- value.reuse 刷新：基于当前快照重算，幂等
- 待办去重：同一笔记不在多条待办中重复出现

---

## 9. 自检清单

- [ ] 报告写入正确路径
- [ ] **新建报告文件名含 summary 段**（除非 §步骤 4 Step 1 命中纯周期条件）
- [ ] **未用「维度多 / 主题分散 / 数据稀疏 / 周报难归纳」等语义借口退化纯周期 token**
- [ ] 同周期已有报告文件时，编辑不改名
- [ ] 健康指标表含全部指标（含阈值对照）
- [ ] value.reuse 刷新（二选一 · v1.5 WP8）：
      · 正常态：调 quick-kb-manager-agent（intent=refresh_value）
      · 降级态：手动统计每条笔记的入链数作为 reuse 近似值 + ⚠ 标注「未含查询命中数 + Connect 推荐频次」
- [ ] 待办清单按优先级排序，每条挂技能调用
- [ ] 无 v0.3 字段（maturity/KS/structure drift）出现在报告
- [ ] 主动提醒遵守限流（≤3 / 库 <50 关闭）

---

## 10. 与设计文档的偏差说明

| 偏差点 | 原因 | 真相源 |
|--------|------|-------|
| KS 排序推迟 v0.3 | 依赖 maturity（v0.3） | dev/v0.2-loops.md WP6 |
| 结构演化建议推迟 v0.3 | 依赖 detect_structure_drift（依赖 KS） | dev/v0.2-loops.md WP6 |
| value 排序简化为 reuse + confidence | v0.2 无 impact | frontmatter-v0.2.md §4.2 |
| 长期未触碰检测基于 updated 而非 maturity | maturity 未启用 | DESIGN §6.4 v0.3 启用 |
