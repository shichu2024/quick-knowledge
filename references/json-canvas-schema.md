---
version: v1.6.0
updated: 2026-08-13
phase: v1.6 规范化
applies_to: quick-kb-connect §步骤 4 · quick-kb-archive §4（canvas 节点处理）
source_of_truth:
  - skills/quick-kb-connect/SKILL.md §步骤 4 / §5.3
  - skills/quick-kb-archive/SKILL.md §4 step 6
  - docs/dev/v1.5-cross-skill-consistency.md WP9
  - https://jsoncanvas.org/（对外规范）
---

# JSON Canvas 规范 · quick-knowledge 扩展

> 本文件锁定 quick-knowledge 在 [JSON Canvas](https://jsoncanvas.org/) 之上的字段约定与边着色规则。connect 技能生成 `.canvas` 时必须遵守；archive 技能处理归档笔记的 canvas 节点时按 §4 规则。

---

## 1. 文件位置

`06_wiki/maps/<domain>.canvas`

> **嵌套 domain（v1.4+）**：`scope` 含 `/` 时，canvas 文件名用 `-` 连接：`scope=programming/python` → `06_wiki/maps/programming-python.canvas`。与 MOC 命名约定一致（见 `frontmatter-v0.2.md` §5.2）。

---

## 2. 顶层结构

```json
{
  "nodes": [...],
  "edges": [...]
}
```

无顶层 metadata 字段（与 json-canvas.org 规范一致）。

---

## 3. nodes 字段

每个 node 必填字段 + quick-knowledge 扩展：

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `id` | ✓ | string | **必为笔记的 basename（去扩展名）**；同名时加路径前缀 `programming-python-vector-db`（v1.6 唯一性约束） |
| `type` | ✓ | enum | `"file"` / `"text"` / `"link"` / `"group"`。quick-knowledge 默认 `"file"`（指向笔记） |
| `file` | ✓（type=file 时） | string | 笔记相对路径（相对 vault 根），如 `"02_areas/ai-engineering/rag-architecture.md"` |
| `label` | 否 | string | 节点显示名；缺省取笔记 frontmatter `title`。归档节点追加「 (已归档)」（见 §4） |
| `x` / `y` | ✓ | number | 坐标（建议按 domain 子簇聚类，同簇节点紧凑摆放） |
| `width` / `height` | ✓ | number | 默认 250 × 60（file 节点） |
| `color` | 否 | enum | 按 type 区分：concept 默认不填；principle `"1"`（红）；belief `"2"`（橙）；experience `"3"`（黄）；pattern `"4"`（绿）。取值对齐 Obsidian 颜色枚举 |

### 3.1 group 节点（v1.6 引入）

按 domain 子主题聚类时用 `type: "group"`：

```json
{
  "id": "group-rag",
  "type": "group",
  "label": "RAG 子主题",
  "x": 0, "y": 0, "width": 600, "height": 400
}
```

---

## 4. edges 字段

每条 edge 表示一条 relation：

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `id` | ✓ | string | `{fromNode}-{type}-{toNode}` 格式（如 `rag-arch-evolves-vector-db`）；幂等 |
| `fromNode` | ✓ | string | 源节点 id（对应正向关系的发起方） |
| `toNode` | ✓ | string | 目标节点 id |
| `color` | ✓ | enum | **按 relations 类型着色**（见 §4.1） |
| `label` | 否 | string | 关系的可选说明（如 contradicts 场景的 context 摘要） |
| `toEnd` | 否 | enum | 箭头样式：有向关系（evolves/supersedes/derived_from）用 `"arrow"`；对称关系（supports/contradicts）缺省（无箭头） |

### 4.1 边着色规则（核心 · 按 relations 类型）

| relations 类型 | `color` 值 | Obsidian 颜色 | 语义 |
|---------------|-----------|--------------|------|
| `supports` | `"4"` | 绿 | 支撑 / 佐证 |
| `contradicts` | `"1"` | 红 | 冲突（上下文相关） |
| `evolves` | `"5"` | 紫 | 演化（有向） |
| `supersedes` | `"2"` | 橙 | 取代（有向） |
| `derived_from` | `"3"` | 黄 | 派生来源（有向） |
| `refines` | `"6"` | 青 | 精炼（有向） |

> 颜色枚举对齐 Obsidian / json-canvas.org 标准（`"1"` ~ `"6"`）。新增关系类型时复用最近语义的颜色，不引入新值。

### 4.2 双向关系的边策略

- **对称关系**（supports / contradicts）：生成**一条无向边**（不指定 `toEnd`），fromNode 取 basename 字典序较小的一方（幂等保证）
- **有向关系**（evolves / supersedes / derived_from / refines）：生成**一条有向边**，方向与 relations 字段语义一致（A.evolves = [B] → edge fromNode=A, toNode=B）

### 4.3 反向键不重复生成边

relations 反向键（`evolved_by` / `superseded_by` / `source_of` / `refined_by`）是 connect 自动补全的便利字段（见 `frontmatter-v0.2.md` §3.0.1），**canvas 不为反向键单独生成边**——否则每对关系会画两条边。

---

## 5. archive 处理（与 quick-kb-archive §4 step 6 联动）

笔记归档时，所有引用该笔记的 canvas 节点按以下规则更新：

| 字段 | 更新规则 |
|------|---------|
| `file` | 更新为 stub 路径（`02_areas/<domain>/<slug>.md`，原位置保留 stub · 见 archive SKILL §4 copy+stub 模式） |
| `label` | 追加「 (已归档)」后缀 |
| `color` | 改为 `"1"`（红）—— 视觉提示该节点已归档 |
| `id` | **保持不变**（id 是稳定性约束，改名会破坏 edge 引用） |
| edges | **不动**（保留历史关系；归档不等于关系消失） |

> 理由：stub 仍在原位置（copy + stub 模式），`file` 字段指向 stub 保证 Obsidian 双击节点仍能打开；id 不变保证 edges 的 `fromNode`/`toNode` 引用不断。

---

## 6. 幂等

- 同 scope 二次运行 → 覆盖（canvas 是衍生品，可重建）
- 节点 id / edge id 命名稳定 → 重建后布局坐标可保留（若用户手调了 x/y，二次生成时读旧 canvas 的坐标覆盖新计算值）

---

## 7. 降级

| 场景 | 降级行为 |
|------|---------|
| json-canvas 技能 / Obsidian 不可用 | 跳过 `.canvas` 生成，报告「Obsidian-skills 缺失，仅产出 MOC；安装后运行 connect action=canvas 补全」 |
| 范围内笔记 < 3 条 | 不生成 canvas（同 MOC 阈值），提示「笔记太少」 |
| 边着色遇到未枚举的关系类型 | 用 `"6"`（青）兜底 + 在生成报告中 ⚠ 标注 |

---

## 8. 自检（connect / archive 执行后）

- [ ] 每个节点 `id` 唯一（basename 冲突时已加路径前缀）
- [ ] 每条 edge 的 `color` 严格按 §4.1 着色表
- [ ] 对称关系只生成一条无向边；有向关系方向与 relations 字段一致
- [ ] 反向键（evolved_by 等）未重复生成边
- [ ] archive 后归档节点的 `file` 指向 stub、`label` 含「(已归档)」、`color` 改红；`id` 与 edges 未动

---

## 9. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.6.0 | 2026-08-13 | 初始版本：定义节点 / 边字段 + 着色规则 + archive 处理规则 |
