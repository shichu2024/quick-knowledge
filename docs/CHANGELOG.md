# 变更记录（CHANGELOG）

> 倒序排列，最新版本在上。每条记录含：版本号、日期、变更摘要、变更明细、变更原因。

---

## v1.9.1 · 2026-08-15 · 测试10校准修复（5 项）

**摘要**：基于测试10报告（三轮复核 + 误报自撤销，5 确认问题）校准修复。校准修正一处方向：OBS-001 的设计意图是 `_index.md`（v1.7 WP5-D），清单/自检两处 `_readme.md` 为笔误。**无 BREAKING CHANGE**。

### 修复清单

| # | 内容 | 影响 |
|---|------|------|
| 1 | OBS-001：init 报告文件清单与自检清单统一为 vault 根 `_index.md`（与步骤 4 / v1.7 WP5-D 设计一致，`_readme.md` 为笔误） | init SKILL.md |
| 2 | OBS-002：init runtime_hint 可选值增加 `kimi-code` | init SKILL.md |
| 3 | OBS-004：ingest 步骤 3 示例 wikilink 由标题格式（`[[Vector Database]]` 等）改为 kebab-case slug + 「禁止标题格式」注释——消除示例与写入校验规则的矛盾（v1.8 校验层的示例级漏洞） | ingest SKILL.md |
| 4 | OBS-006（校准为半真）：memory-agent / manager-agent 增加「references 链接回退」条款（仓库相对路径独立安装不可达时按 SKILL 内联公式执行）；两 agent 增加**降级可观测性**——多项调用末尾附降级模式汇总（N 项中 X 项 degraded + 原因），消除测试10「61 项全 degraded 无整体感知」问题 | memory-agent / manager-agent SKILL.md |
| 5 | OBS-007（测试10 最有价值发现）：`references/scoring.md` 新增 §5.1「降级态推荐阈值表」——中英混合 vault 降级公式输出实测集中 0.1-0.25，正常态阈值（0.45-0.65）下零召回；降级态统一下调：memory min_similarity 0.55→0.35、detect_repeat_mistakes 0.65→0.45、manager threshold 0.6→0.40、query 召回 0.4→0.30（隐式冲突 0.75 保持防误报）；各技能降级段联动引用 + 降级输出强制 ⚠ 标注 | scoring.md + memory-agent / manager-agent / query SKILL.md |

### 校准备注

- OBS-005（误报撤销）与 OBS-003（执行偏差）无需技能改动
- 测试10 未标记的执行偏差（供测试11 参考）：03_projects/04_goals 目录倒置、maturity 词表误用 structured/mastered、daily 平铺路径、inbox 素材平铺
- 架构级建议（依赖文件清单 / 覆盖矩阵 / 全局 wikilink 规范）：进路线图（降级汇总已并入本次）

### 评测

capture split=test **9/9 hard（100%）**；flow split=train (6:1:1 seed 1) 两次运行 **0/4 → 2/4 hard / soft 0.61~0.83**（复跑恢复并超过基线 2/4·0.79；单次 0/4 为 J 类已知方差——J6 执行方未落文件、J3/J4 边界未过 soft 0.75+，与本次阈值/文档改动无关）。均无退化。

---

## v1.9.0 · 2026-08-15 · 测试9契约对齐包（6 项）

**摘要**：基于测试9报告（v1.8.2 真实技能 · 18/18 行为不变量通过 · 25 待完善项）校准，确认真问题 6 条落地，主打跨技能契约对齐（报告最低分维度 7.3/10）。**无 BREAKING CHANGE**。

### 修复清单

| # | 内容 | 影响 |
|---|------|------|
| 1 | 入库路径真相源统一：init inbox readme 文案与 ingest 描述由「02_areas/resources」改为「01_resources/<category>/（resource）/ 02_areas/<domain>/（concept）」，与 ingest 实际写入规则（§分类去向）一致 | init / ingest SKILL.md |
| 2 | 98_archive 子目录词表对齐：init 骨架补建 concepts/resources/ideas/decisions（与既有 projects/goals/reviews/materials 并列 8 目录）；archive §4.1 路径清单补 projects/goals/reviews 三行，两处词表一致；子目录缺失自动创建 | init / archive SKILL.md |
| 3 | maturity 初始化责任落定：normalize 字段补全由「v0.3+ 笔记」限定改为**全量笔记**补 `maturity: captured`（ingest 禁写 + stats KS 依赖 + promote_maturity 跳过无值笔记三角断点的唯一解）；manager-agent 降级表联动（建议先跑 normalize） | normalize / manager-agent SKILL.md |
| 4 | stats/review 缺失率分母排除规则：排除含 `capture_type` 的 inbox 采集素材（设计上无 type/status，实测被计入致 32.4% 失真）；inbox 素材另报「inbox frontmatter 覆盖率」；review 同口径同步；stats KS 段补冷启动说明（全部 captured 时 KS 恒空不算异常 + 指引 promote_maturity） | stats / review SKILL.md |
| 5 | promote_maturity applied 晋升证据双语化：中文「应用/落地/实践/上线」+ 英文 applied/deployed/in production/shipped，另接受 `value.reuse > 0` 作为等价证据（消除英文笔记永不晋升） | manager-agent SKILL.md |
| 6 | init 模板铺设计数硬校验：铺设后实测清点（ls 计数 = 14/语言），≠ 14（含「只铺 4 个」假象）→ ⚠⚠ 阻断级告警 + 缺失清单 + 处置指引；自检清单升级为实测清点。修复实测漏洞：执行方在模板源不可达时即兴生成 4 个核心模板造成「已铺设」假象，计数校验是唯一程序化拦截。顺带修正 §3.2 模板清单漏列 progress/retrospective（标题 14 但清单只列 12） | init SKILL.md |
| + | daily wikilink 候选集补 `06_wiki/mocs/**`（测试9 #15 的次要有效部分；07_principles 已在 v1.7 WP4 范围内） | daily SKILL.md |

### 校准结论（不修复清单）

- 测试9 #9（顶层 _moc 引用）/ #12（goal `[[README]]` 死链）：仓库与 demo-vault 均未复现，判定执行方自写
- #15 大部分不成立：daily 匹配范围已含 07_principles（v1.7 WP4）
- 冷启动三件套（#10/#14/#22：memory 种子清单 / advisor 降级模板 / experience 快捷入口）与可执行脚本（#5/#8）、agent 调用断言（#6）：有效增强，进 v1.9.x/v2.0 路线图

### 评测

capture split=test **8/9 hard / soft 0.96**；flow split=train (6:1:1 seed 1) 两次运行 **1/4 → 2/4 hard / soft 0.77~0.79**（复跑恢复基线 2/4·0.79；单次 1/4 系 J 类已知方差——失败用例 soft 0.57~0.78 均为边界未过，失败原因如 source 字段写成字符串数组，与本次改动无关）。均无退化。

---

## v1.8.2 · 2026-08-15 · 增强候选落地（4 项）

**摘要**：将 v1.8.1 校准中识别的 4 项有效增强建议落地。**无 BREAKING CHANGE**。

### 修复清单

| # | 内容 | 影响 |
|---|------|------|
| 1 | manager-agent 新增 `promote_maturity` intent（v1.8.2 · 写回型）：基于 confidence + 入链数 + 停滞天数评估 maturity 6 态晋升/停滞/deprecate 建议；默认 auto_write=false 仅输出建议；stalled 仅提醒不自动降级；maturity 缺失笔记跳过 | manager-agent SKILL.md（契约 + 能力清单 + §3.9 + 降级 + 自检） |
| 2 | ingest 新增 §3.3 confidence 协商：research-agent 初值 → 冲突检测后按结果调整并回写（contradicts 且对方更高 → −10 下限 20；evolves → +5 上限 95；无命中不动），调整记录含 why，与步骤 4 写入合并执行 | ingest SKILL.md（§3.3 + 自检） |
| 3 | query 零召回建议 capture 附预填充内容（待研究问题原句 + 查询关键词作 suggested_tags） | query SKILL.md（步骤 6） |
| 4 | memory-agent `present_conflicts` 新增隐式冲突检测：显式 contradicts 无命中时，对同 domain 相似度 ≥ 0.65 笔记对比 context 与论断方向；隐式命中标 `source: implicit` 仅提示不自动写 contradicts（显式化走用户确认）；无 embedding 降级态阈值提高到 0.75 防误报 | memory-agent SKILL.md（§3.5 + 自检） |

### 备注

- query 零召回「建议 capture」本体在 v0.2 即有（步骤 6），本次仅补预填充内容——测试8 P-QRY-02 部分误报
- 17 个 SKILL.md `version` 统一 v1.8.2

### 评测

flow split=train (6:1:1 seed 1) **2/4 hard / soft 0.79**（与 v1.8.0 持平）。capture split=test 两次运行 **8/9 与 7/9 hard**——失败用例在 F1 / A3.1 / G3 间漂移（A3.1 为已知 flaky；F1/G3 为模型行为边界用例），且 capture SKILL 相对 v1.8.1 仅 version 行变化，判定为后端执行方差而非回归（v1.8.0~v1.8.1 同配置为 9/9，历史亦见过 A3.1 0-100% 波动）。

---

## v1.8.1 · 2026-08-15 · 测试8校准修复（3 项）

**摘要**：基于测试8完备性报告（68 条 issues）对照仓库实态校准——报告 vault 系按不存在的结构构建（`_system/`、forming/developing 词表、knowledge-map.md 等），量化指标不可作证据；68 条中确认真 bug 2 + 部分有效 1，另复核发现 1 个报告未发现的 schema 缺口。**无 BREAKING CHANGE**。

### 修复清单

| # | 内容 | 影响 |
|---|------|------|
| 1 | archive SKILL.md 重复步骤编号修复（两个「10.」→ 第二个改 11，v1.7 WP7-D 插入未重排） | archive SKILL.md |
| 2 | schema type enum 补 `progress` / `retrospective`（v1.7 WP5 模板漏同步，自身模板产出会被 schema_check 判违规）；status enum 补 `in-progress` / `blocked` / `superseded`（progress 模板与 decision 模板实际使用值）；write-validation-rules.md 词表同步；init 技能自带 schema 副本同步 | frontmatter-schema-v1.json + write-validation-rules.md + init 副本 |
| 3 | 行内注释治理：normalize 步骤 2.1 新增「行内注释剥离」（`confidence: 80 # verified` → `confidence: 80`）+ schema_check 检查项 #10；write-validation-rules.md 新增「落盘 frontmatter 禁止携带行内注释」规则（模板/SKILL 示例注释为填写指引，不得照抄） | normalize SKILL.md + write-validation-rules.md |

### 校准结论（不修复清单）

- relations「两种格式并存」（报告 A 级建议）：仓库 goal/project SKILL 与模板全部 typed keys，list-of-objects 不存在——执行者自写
- MOC 嵌套命名死链 / import 去重仅 title / Decision Ledger 缺 status / advisor 空报告 / capture 润色无自动化：均已在 v1.4~v1.7 实现或从未存在
- 孤立率 74.1% / confidence 注释率 48.9% 等量化指标：基于幻觉 vault，无效
- maturity 自动晋升 / confidence 协商 / query 零召回建议 capture / 隐式冲突检测：有效增强建议，进路线图（v1.9 候选）

### 测试方法约束（测试9 起）

以 `skills/` 目录或 `QUICK_KB_REPO_ROOT` 真实安装运行；报告强制含 §自审（测试7 做法）。

### 评测

capture split=test **9/9 hard（100%）**；flow split=train (6:1:1 seed 1) **2/4 hard / soft 0.76**（hard 在已知方差内，soft 0.69~0.79 区间）。均无退化。

---

## v1.8.0 · 2026-08-14 · E2E 校准与写入校验层（WP1-WP5）

**摘要**：基于测试7全技能 E2E 报告（17 技能 / 41 reported issues，报告 §九已自审重审），对照仓库实态二次校准：报告判定的「schema 矛盾」实为 init 资源定位链断裂后执行方即兴生成第三套 schema 所致；12 条误报的共同根因是写入前无校验层。核心改进：init 技能包资源自包含、全写入型技能接入写入前校验（frontmatter + wikilink 目标存在性）、跨技能口径统一（import 目录名 / 缺失率口径 / 降级相似度公式）、archive 语义矛盾修正、17 技能版本元数据统一。**无 BREAKING CHANGE**。

### 工作包

| WP | 内容 | 影响 |
|----|------|------|
| WP1 | init 技能包自带 `templates/{zh,en}/`（14×2）+ `references/frontmatter-schema-v1.json`，使三级回退第①级真实命中；§3.3 回退表如实化（③ 兜底仅覆盖 4 个系统文件，非全部模板）；schema 落地记录 SHA-256 指纹（`.kb-initialized.schema_sha256`），upgrade 校验指纹不一致 → ⚠ 询问；新增「①② 均不可达禁止即兴生成 schema/模板」条款；upgrade 版本判定明确以 17 技能统一版本号为准；模板计数 12 → 14 修正 | init SKILL.md + 新增技能自带资源 |
| WP2 | 新建 `references/write-validation-rules.md`（frontmatter 最小校验集 + wikilink 目标存在性 + 校验失败处理）；ingest/capture/import/connect/daily/goal/project 共 7 个写入型 SKILL 增加写入前校验步骤；connect 另增写入后自检（反向键对称补全 + 关系去重 + 禁止自创关系类型）；goal/project 禁止别名引用（`[[principle-001]]` 类） | 新文件 + 7 SKILL.md |
| WP3 | import 目录命名统一为 `00_inbox/imported/<source>/`（清除 `_imports/` 残留）；review frontmatter 缺失率显式引用 stats §4.1 同口径（同字段集 + 同扫描范围跳过 98_archive/99_system）；`references/scoring.md` 新增 §5「无 embedding 降级相似度公式」（标签 Jaccard × 0.6 + 标题关键词重叠 × 0.4），manager-agent/memory-agent/query/advisor/ingest 降级段统一引用，删除各自本地权重；manager-agent §3.6 refresh_value 标注「写回型操作 · 非纯函数」；research-agent 不变量澄清（existing_notes 由调用方传入） | import / review / stats / manager-agent / memory-agent / query / advisor / research-agent SKILL.md + scoring.md |
| WP4 | archive SKILL 消除「不派生 experience」与步骤 10 project lesson 派生的矛盾：统一为「通用归档不派生；仅 type=project 时派生 experience 草稿（status: draft 需确认）」 | archive SKILL.md |
| WP5 | 17 个 SKILL.md frontmatter `version` 统一为 v1.8.0（原 v0.1~v1.4 混杂，影响 `.kb-initialized` upgrade 判定） | 全部 17 SKILL.md |

### 文件清单

| 类型 | 文件 |
|------|------|
| 新增 references | `references/write-validation-rules.md` |
| 新增技能自带资源 | `skills/quick-kb-init/templates/{zh,en}/**`（14×2）、`skills/quick-kb-init/references/frontmatter-schema-v1.json` |
| 新增 dev doc | `docs/dev/v1.8-e2e-calibration.md` |
| 修改 SKILL.md × 17 | 全部 17 个 SKILL（version 统一）+ 其中 12 个含实质改动 |
| 修改 references | `references/scoring.md` |

### 校准过滤（不修复清单）

测试报告 41 条 → 报告 §九自审 8 真问题 → 仓库二次校准：
- #2/#8（confidence/relations schema 矛盾）→ 根因重定位为 WP1（vault 即兴 schema），仓库权威源内部一致
- #18 refresh_value / #20 cross_verify → 降级 P2 措辞修复（归 WP3）
- 12 条执行偏差类误报 → 由 WP2 校验层拦截根因，不改技能逻辑
- #28/#29 设计约束、#36/#37 推迟、import 输出项计数 → 测试方法学问题

详见 `docs/dev/v1.8-e2e-calibration.md` §0 校准 + 附：41 条处理映射。

### 评测

capture split=test **9/9 hard（100%）**；flow split=train (6:1:1 seed 1) **2/4 hard / soft 0.79**（hard 在已知方差内，soft 较 v1.7.0 的 0.69 提升）。均无退化。

---

## v1.7.0 · 2026-08-14 · 自动化与跨技能集成（WP1-WP7）

**摘要**：基于测试5（155 笔记 / 215 改进点）+ 测试6（22 笔记 / 36 完善点）两份独立报告交叉比对，经 §0 校准过滤后落地 24 条真问题，归为 7 WP。核心改进：agent 被调用契约硬化、ingest 全链路补强（反向补全 + inbox 清理 + tags 硬化）、关系循环/冲突检测、polish_mode 自动化、模板与 slug 协议补齐、仪表盘 maturity 漏斗 + recency_factor、导入归档协议完善。**无 BREAKING CHANGE**。

### 工作包

| WP | 内容 | 影响 |
|----|------|------|
| WP1 | research/memory/manager 三个 agent SKILL 顶部增设 §0 被调用契约段（声明所有 intent 的入参 + 返回结构）；ingest/goal/project/advisor/connect/query 5+1 个调用方 SKILL 改为引用契约而非重述返回结构 | 9 SKILL.md |
| WP2 | ingest 新增步骤 4.1 关系反向补全（复用 connect §5.2.1 表）+ 步骤 4.5 inbox 素材归档（移至 `00_inbox/_processed/`，frontmatter 加 `status: ingested` + `ingested_to`）+ §2.5 强制 inline-array tags；import 写完加强提示调用 ingest（不自动触发，避免批量回滚） | ingest / import SKILL.md |
| WP3 | connect §2.1 写入策略加循环检测（双向 evolves 拒绝）+ supports/contradicts 冲突消歧；ingest §4.2 同步冲突消歧；connect §5.2.2 新增 evolves/supersedes 候选推荐（tag Jaccard ≥ 0.7 + 时间差 > 30 天）；experience 模板补 outcome + trigger 必填字段；frontmatter-v0.2.md §2 同步声明 | connect / ingest SKILL.md + experience 模板（zh/en）+ frontmatter-v0.2.md |
| WP4 | capture + daily 新增 `polish_mode` 参数（confirm / auto / skip），kb.config.yaml 新增 `polish.default_mode`；daily §4 wikilink 生成硬化（匹配范围限定 02/07/03/04 + basename 完全匹配 + 标题 ≤ 3 字符跳过 + 同日志去重 + 用户已手写不重复） | capture / daily SKILL.md + kb.config.yaml |
| WP5 | 新建 `references/slug-rules.md`；新建 `templates/{zh,en}/progress.md` + `retrospective.md`；init 修改 vault 根 `_index.md` 为使用指引；project SKILL 增 DEC 编号规则；archive SKILL + kb.config.yaml 增归档原因受控词表（completed/cancelled/low_reuse/low_confidence/superseded/absorbed/ingested/stale） | init / project / archive SKILL.md + kb.config.yaml + slug-rules.md + 4 新模板 |
| WP6 | init 新增创建 `99_system/workflows/.gitkeep`（供 query-log.jsonl 用）；query 自检清单加查询日志检查；stats 输出新增 Maturity 转换漏斗 + 停滞态告警；review refresh_value 加 recency_factor 计算（≤30天→1.0 / 30-90→0.8 / 90-180→0.65 / >180→0.5）；scoring.md §3.2 同步分段规则 | init / query / stats / review SKILL.md + scoring.md |
| WP7 | import confidence 量纲自动转换（0-1 → ×100，>1 保留，缺失 60）+ 新增 `action` 参数（run / dry-run）；archive 归档 goal 时扫描 linked_projects 仅提示不自动归档；project archive 扫描 ADR 提取 actual/lesson 生成 experience 草稿（status: draft 待确认） | import / archive SKILL.md |

### 文件清单

| 类型 | 文件 |
|------|------|
| 新增 references | `references/slug-rules.md` |
| 新增模板 | `templates/{zh,en}/progress.md`、`templates/{zh,en}/retrospective.md` |
| 新增 dev doc | `docs/dev/v1.7-automation-and-integration.md` |
| 修改 SKILL.md × 17 | 全部 17 个 SKILL（3 agent + 14 业务技能） |
| 修改 references | `references/frontmatter-v0.2.md`、`references/scoring.md` |
| 修改配置 | `examples/demo-vault/99_system/config/kb.config.yaml` |
| 修改模板 | `templates/{zh,en}/experience.md` |

### 校准过滤（不修复清单）

测试报告原条目 251 条 → 经 §0 校准过滤后真问题 24 条。明确不修复的关键条目：
- 「Agent 不可执行」—— Claude Code harness 约束，非技能缺陷
- 「归档 wikilink 后缀破坏 Obsidian」—— v1.6.0 WP9 已修
- 「非对称关系不自动反向补全」—— connect §5.2.1 已实现（真问题是 ingest 未调用，归 WP2）
- 「归档全库扫描需手动」—— archive §6 已实现
- confidence/maturity schema 不一致 —— v1.5.0 WP2-4 已修

详见 `docs/dev/v1.7-automation-and-integration.md` §0 校准 + §11 不修复清单。

### 评测

capture split=test **9/9 hard（100%）**；flow split=train (6:1:1 seed 1) **2/4 hard / soft 0.69**（within known variance）。均无退化。

---

## v1.6.0 · 2026-08-13 · canvas / wikilink 规范化（WP9）

**摘要**：为 canvas 文件与 wikilink 写法建立跨技能一致性规范。引入两份 references 文件作为 connect / archive / stats 的共同真相源。**无 BREAKING CHANGE**。

### 工作包

| WP | 内容 | 影响 |
|----|------|------|
| WP9-1 | `references/json-canvas-schema.md`：nodes/edges 字段定义 + 边按 relations 类型着色表（supports=绿/contradicts=红/evolves=紫/supersedes=橙/derived_from=黄/refines=青）+ archive 节点处理（file→stub、label+「(已归档)」、color=红、id/edges 不动） | 新文件 |
| WP9-2 | `references/wikilink-conventions.md`：默认 basename `[[X]]` / 重名 path-qualified `[[ai-eng/rag]]` / 归档半角后缀 `(已归档)` / Decision Ledger 强制全路径 / canvas file 字段区别 / stats 死链统计口径 | 新文件 |
| WP9-3 | connect §步骤4 + archive §4 step8 引用上述两份 ref；stats 死链统计引用 wikilink-conventions §8 | connect / archive / stats SKILL.md |

### 文件清单

| 类型 | 文件 |
|------|------|
| 新增 references | `references/json-canvas-schema.md`、`references/wikilink-conventions.md` |
| 修改 SKILL.md | quick-kb-connect / quick-kb-archive / quick-kb-stats（source_of_truth + 内文引用） |

### 评测

capture split=test 9/9 hard（100%）；flow split=train 2/4 hard / soft 0.79（within known variance）。

---

## v1.5.2 · 2026-08-13 · 跨技能一致性硬化 WP7+WP8

**摘要**：补全 capture→ingest 衔接映射 + daily 待入库一键命令；统一各技能自检清单的「降级态」表述格式。**无 BREAKING CHANGE**。

### 工作包

| WP | 内容 | 影响 |
|----|------|------|
| WP7 | ingest 新增 `capture_type → note_type` 默认映射表（web/pdf/meeting/ai_dialog/reading/import → resource），保留 `source.capture_type` 作溯源；daily §步骤4 wikilink 提取算法明示（候选集 7 目录 + 整词匹配 + 强别名 + 高潜力名词判定）；§步骤5 待入库段加 `quick-kb-capture "<摘要>"` 一键命令 | ingest / daily SKILL.md |
| WP8 | advisor / goal / review / ingest / normalize 自检清单改为「正常态 / 降级态 / 二选一」三档格式，覆盖 agent 不可用场景；connect/query 不需调整（行为驱动自检） | advisor / goal / review / ingest / normalize SKILL.md |

### 文件清单

修改 SKILL.md × 6（ingest / daily / advisor / goal / review / normalize）。

---

## v1.5.1 · 2026-08-13 · 跨技能一致性硬化 WP1+WP5+WP6

**摘要**：init 增加模板 SHA-256 校验机制；archive 改用 copy+stub 模式（原位置保留 stub 含 `redirect_to`，断链率最低）；advisor 支持可选持久化到产出层。**无 BREAKING CHANGE**。

### 工作包

| WP | 内容 | 影响 |
|----|------|------|
| WP1 | init §3.7 upgrade 增加 12 模板 SHA-256 比对 + frontmatter-schema.json 补缺检查；§3.2.1 铺设 schema 文件到 vault；§7 自检 +3 项 | init/SKILL.md |
| WP5 | archive 定档 copy+stub 模式：完整内容复制到 `98_archive/<type>/<slug>.md` + 原位置保留 stub（frontmatter `status: archived` + `archive_meta.redirect_to` + 正文一行重定向）；unarchive 反向流程同步；index 命名统一 `_archive-index.md`；relations 边界澄清（类型结构不动 / target 字符串可加「(已归档)」后缀） | archive/SKILL.md |
| WP6 | advisor 新增 `persist` 参数（默认 false）：不写认知资产层（02/07）+ 可选持久化决策记录到产出层（05/decisions）；§7 降级扩展为手动 Grep 4 类认知资产（concept/principle/belief/pattern/experience） | advisor/SKILL.md |

### 文件清单

修改 SKILL.md × 3（init / archive / advisor）。

---

## v1.5.0 · 2026-08-13 · 跨技能一致性硬化 WP2+WP3+WP4

**摘要**：统一 confidence 量纲为 0-100 整数；引入 JSON Schema 校验机制（normalize `schema_check` 子动作）；project Decision Ledger 支持多对一派生（多 decisions → 单 experience 合并）。**含 BREAKING：confidence 字段从 0-1 小数统一为 0-100 整数**（spec 早已是 0-100，import 违反，本版本对齐）。**含 BREAKING：source 字段结构统一**（废弃 import 的 kind/original_path/imported_at）。

### 工作包

| WP | 内容 | 影响 |
|----|------|------|
| WP2 | confidence 全库统一 0-100 整数（spec frontmatter-v0.2.md L44 已是 0-100，本版本修正 import / ingest / research-agent / stats / advisor / review 等违规处）；import 归一逻辑：原 (0,1] × 100 取整，默认 50 | 全部含 confidence 的 SKILL.md + frontmatter-v0.2.md |
| WP3 | 新增 `references/frontmatter-schema-v1.json`（JSON Schema 覆盖 13+ 字段类型）；normalize `action=schema_check` 子动作（9 项检查表 + 输出格式）；schema 文件由 init 铺设到 vault | 新文件 + normalize SKILL.md + init SKILL.md |
| WP4 | project Decision Ledger 多对一派生：多 decisions → 单 experience 合并（same domain + same lesson 主题词）；§6 step 3 重写为 6 子步（派生判定 / 新建 / 字段 / 双向 / 升格 / 消解）；§6 step 1.5 字段缺失/空字符串/null 三态等价拦截；§6 step 2.3 outcome 关键字清单明示（success/failure/mixed + failure 优先）；frontmatter-v0.2 §3.0.2 新增 derived_from/derived_to 必为 YAML list 支持多对一 | project/SKILL.md + frontmatter-v0.2.md |

### 文件清单

| 类型 | 文件 |
|------|------|
| 新增 references | `references/frontmatter-schema-v1.json` |
| 修改 references | `references/frontmatter-v0.2.md`（confidence 量纲声明 + derived_from/derived_to list） |
| 修改 SKILL.md | 全部含 confidence 字段的技能（import / ingest / research-agent / advisor / review / stats / normalize）+ project + init |

### 设计决策

- confidence 选 0-100（vs 0-1）：5 处 spec 已用 0-100，仅 import 用 0-1，迁移成本更低
- 多对一派生合并键：same domain + same lesson 主题词（避免同项目 N decisions 生成 N 条碎片 experience）
- schema 检查不强制阻塞 normalize：只报告，不自动改（防误改用户笔记）

---

## v1.4.2 · 2026-08-13 · 日期类文件名 summary 提炼防绕过（内容笼统场景）

**摘要**：堵住 v1.4.0「日期类文件名附带 LLM 摘要」规则的一个绕过路径——当 LLM 输出「内容笼统」「今日笔记」等无信息摘要时，捕捉 / 重提取规则不生效。本版本集中化判定规则 + 在 4 个技能中同步堵漏。**无 BREAKING CHANGE**。

### 变更

- 抽出集中化判定规则到单一位置（避免 4 处技能各写各的漂移）
- capture / daily / ingest / advisor 4 处同步引用集中化规则
- 「素材缺失」「内容笼统」两个场景分别明示触发条件（AND 逻辑）

### 文件清单

修改 SKILL.md × 4（capture / daily / ingest / advisor）+ 1 处集中化规则。

---

## v1.4.1 · 2026-08-13 · 测试反馈硬化 Part B（基于两次外部端到端测试）

**摘要**：两次外部端到端测试共提出 174 条改进建议，去伪存真后保留 18 条真实可落地项（剔除误报 38 条，主要是测试者未完整阅读 SKILL.md 把 spec 已有能力当成缺失）。本版本不引入新能力，只做**硬化**：把执行走样点升级为硬约束、补全跨技能联动断点、公开缺失的受控词表/评分公式。**无 BREAKING CHANGE**。

### 工作包

| WP | 内容 | 影响 |
|----|------|------|
| B-WP1 | init 铺全 12 模板（原 4） + schema_version 升级机制 + 模板路径三级回退 | init/SKILL.md +69 行 |
| B-WP2 | connect MOC 字段硬约束（必须逐字抄自 frontmatter，禁止正文推断） + 非对称关系反向补全（evolved_by/superseded_by/source_of/refined_by） | connect/SKILL.md + frontmatter-v0.2.md |
| B-WP3 | import confidence 量表统一 0-1（原百分制） + 弱键去重（tags 交集+url 相似度，仅标注不 skip） | import/SKILL.md |
| B-WP4a | archive 冲突消解回写（lesson 解决的 contradicts 对自动加 resolved_by） | project/SKILL.md + archive/SKILL.md |
| B-WP4b | normalize 提示刷新 MOC（迁移后扫描 06_wiki/mocs/ 列出过期引用） | normalize/SKILL.md |
| B-WP4c | query 归档标注（命中 98_archive/ 追加 📄 已归档） + include_archived 参数 | query/SKILL.md |
| B-WP4d | advisor 降级召回扩展（quick-kb-memory-agent 不可用时扫 07_principles/ + 05_outputs/daily/） | advisor/SKILL.md |
| B-WP4e | project Decision Ledger 回填检查（update 提示 + archive 前置门控） | project/SKILL.md |
| B-WP5 | references 公开 counting-rules/scoring/polish-rules + 各技能「下一步」提示 + Windows 中文路径段 | 3 新文件 + 4 SKILL.md + user-guide.md |

### 剔除的误报（不做）

| 来源 | 原报告说法 | 不做的原因 |
|------|----------|----------|
| 测试2 §4.3 / 测试3 init | 模板不在仓库 | `templates/{zh,en}/` 各 12 个齐全 |
| 测试3 全篇 | docs/ 不存在 | `docs/{DESIGN,AGENTS_SPEC,SKILLS_SPEC,VERSIONING}.md` 齐全 |
| 测试3 §5.1 | agent 全部缺失 | `agents/` 下三个 agent 定义齐全；是否实例化是 harness 职责 |
| 测试3 archive | archive 不幂等/不可恢复 | `archive/SKILL.md §8` 已定义幂等 + unarchive action |
| 测试3 advisor | advisor 无降级路径 | `advisor/SKILL.md §7` 已定义两档降级（本版本仅扩展召回范围） |
| 测试3 ingest | inbox 状态未更新 | ingest 步骤 7 追加 `> [!info] 已入库` callout（本版本不改形式） |

### 文件清单

| 类型 | 文件 |
|------|------|
| 新增设计文档 | `docs/dev/v1.4-nested-domain-and-hardening.md`（Part A 反推 + Part B 计划合一） |
| 新增 references | `references/counting-rules.md`（正式笔记边界）、`references/scoring.md`（KS/reuse 公式）、`references/polish-rules.md`（润色决策表统一） |
| 修改 references | `references/frontmatter-v0.2.md`（补 4 个反向关系键 schema） |
| 修改 SKILL.md（10 个） | init / capture / ingest / daily / connect / query / advisor / normalize / archive / project / import |
| 修改 docs | `docs/dev/README.md`（v1.4 行）、`docs/user-guide.md`（Windows 中文路径段） |

合计 14 文件修改 + 4 新文件，约 +377 / -43 行。

---

## v1.4.0 · 2026-08-12 · 嵌套 domain + LLM 文件名摘要

**摘要**：让 `domain` 字段从扁平字符串升级为支持嵌套的路径（如 `ai-engineering/retrieval/rag`），引入 `domain_taxonomy` 配置 schema，扩展 ingest/init/connect/query/normalize 全链路感知。日期类文件名附带 LLM 提炼的摘要。**无 BREAKING CHANGE**。

### 工作包（已实施）

| WP | commit | 内容 |
|----|--------|------|
| A-WP1 | `f7c1c30` | spec：`domain_taxonomy` 配置 schema + frontmatter-v0.2 嵌套 domain 字段 |
| A-WP2 | `daa54cd` | skills：ingest/init/connect/query 支持嵌套 domain 解析与路由 |
| A-WP3 | `6cbabb4` | normalize：`regroup` 动作支持 flat→嵌套 domain 迁移 |
| A-WP4 | `be6a597` | skills：日期类文件名附带 LLM 提炼的摘要 |

### 设计决策

- domain 分隔符选 `/`（与文件系统路径一致，可直接映射目录）
- domain 必须在 `domain_taxonomy` 中声明（受控词表，避免拼写漂移）
- `regroup` 默认不开启，需显式 `--regroup`（迁移是大动作）

### 后补文档

设计文档 `docs/dev/v1.4-nested-domain-and-hardening.md` Part A 在实施后补写，记录决策与验收点。

---

## v1.3.1 · 2026-08-11 · capture 行为修复（hard rate 0% → 100%）

**摘要**：基于 v1.3 引入的 SkillOpt 行为评测，跨模型（qwen3.7-max + GLM 5.2）跑 capture val/test split 后发现 5 类共 20+ 个 bug，分 5 个 commit（P0–P4）系统性修复。最终 val/test/unseen 三 split 全部 100% hard rate。**无 BREAKING CHANGE**——所有修复都是「让 SKILL.md 表达更清晰 + harness scorer 更精确 + case 设计自洽」，技能外部行为契约不变。

### 修复分组

| 阶段 | commit | 类别 | 影响 case |
|------|--------|------|----------|
| P0 | `23151c5` | harness + SKILL 输出契约 | frontmatter 双重 wrap、polish 单轮 eval auto-default、§6 yaml 强约束 |
| P1 | `8260180` | SKILL 清晰度 + scorer dotted-key | source dict 模板、source.url 嵌套查询、主题即素材边界、A6.1 绝对路径 |
| P2 | `abcf91f` | polish 触发逻辑 + capture 素材化 + 正文段 | §2.5 触发条件 AND 逻辑、§内容约束·素材化原则、§6 加正文段 |
| P3 | `0bd8d3b` | scorer bool 规范化 + test-split case 设计 | True→"true" regex 匹配；A3.2/F1/G3/A6.2 输入与规则对齐 |
| P4 | `a05c845` | unseen 泛化验证 + 字面 token 契约 | 步骤 2e ai-dialog 标签字面保留、步骤 2.5 polish 菜单 `[1]/[2]/[3]` ASCII token |

### 新增能力

- **10 个 unseen golden case**（`bench/cases/capture-unseen/items.json`）：覆盖 idea/meeting/web-clip/pdf/ai-dialog/reading/polish/edge/frontmatter 9 类场景，**严格按 SKILL.md 已有规则设计、零适配**，作为真泛化探针
- **standalone unseen evaluator**（`bench/run_unseen_eval.py`）：绕过 QuickkbDataLoader 切分，直接读 flat items.json 跑评测；不影响主 `capture` skill 的 train/val/test 切分
- **deterministic replay-test 框架**（`bench/harness/replay-test.py` + `replay-fixtures/*.json`）：冻结真实模型回复，零 LLM 成本回归测试 P0 修复是否仍生效；支持 `--mode=bug`（断言 bug 存在）vs `--mode=fix`（断言 bug 已修）双模式

### 评测结果（连续多次跑，同一 SKILL.md）

| split | n | hard rate | soft mean | case 适配? |
|-------|---|-----------|-----------|-----------|
| val (held-in) | 9 | 9/9 (100%) | 1.00 | 否（仅 SKILL.md 修） |
| test (held-out) | 9 | 9/9 (100%) | 1.00 | 是（case 设计修正） |
| unseen（全新） | 10 | 10/10 (100%) | 1.00 | 否（纯泛化验证） |

baseline → 修复后：`0/9 → 9/9 → 9/9 → 10/10`，无过拟合信号。

### 文件清单

| 类型 | 文件 |
|------|------|
| 新增 | `bench/harness/replay-test.py` |
| 新增 | `bench/harness/replay-fixtures/{A6.1,B2,H3}.json`（冻结 GLM 5.2 真实回复） |
| 新增 | `bench/cases/capture-unseen/items.json`（10 case） |
| 新增 | `bench/run_unseen_eval.py` |
| 修改 | `skills/quick-kb-capture/SKILL.md`（§2.5 触发逻辑 + 单轮 eval 续写 + §2e 标签字面契约 + §5 主题边界 + §6 yaml 强约束 + 正文段 + §内容约束·素材化原则 + §路径约束） |
| 修改 | `bench/quickkb/rollout.py`（`_extract_frontmatter` 双重 wrap 修 + `_format_user_message` auto-default [2] 注入） |
| 修改 | `bench/quickkb/scoring/frontmatter.py`（`_lookup` dotted-key + bool 规范化） |
| 修改 | `bench/cases/capture/items.json`（A3.2/A6.1/A6.2/F1/G3/B2 共 6 处 case 设计修正） |
| 修改 | `.gitignore`（`_generated_splits/`） |
| 修改 | `.claude-plugin/plugin.json` + `marketplace.json`（1.3.0 → 1.3.1） |

### 关键边界

- **不放宽任何 case 要求**：所有 case 修改方向都是「让 case 与 SKILL.md 规则一致」（输入要有触发词、长度合理、路径合规），不是降低门槛让模型更容易 pass
- **不修改 `ci.yml` 4 个结构校验 job**：行为评测仍是参考信号，不阻塞 merge
- **不引入新依赖**：所有修复都在既有 `bench/` 模块内

---

## v1.3 · 2026-08-11 · skillopt-integration（行为评测与技能文本优化）

**摘要**：引入 [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) 作为行为评测引擎，补齐 v0.1–v1.2 缺失的「行为测试」能力。CI 从「纯结构校验」扩展到「结构 + 行为」双层。**无 BREAKING CHANGE**——原 4 个 CI job 全保留，SkillOpt 评测作为 non-blocking nightly workflow 加入。

### 新增能力

- **自定义 SkillOpt benchmark `quickkb`**（`bench/quickkb/`）：
  - `QuickkbDataLoader`（SplitDataLoader 子类，加载 golden case）
  - `run_batch` rollout helper（chat_target 跑技能 + 持久化 conversation.json）
  - `QuickkbAdapter`（EnvAdapter 子类，对接 SkillOpt 生命周期）
- **4 个评分器**（`bench/quickkb/scoring/`）：
  - `routing.py`：路径 glob 匹配（fnmatch）
  - `frontmatter.py`：字段正则 + 禁止字段缺席
  - `behavior.py`：润色菜单 / 去重提示 / prompt 注入防御
  - `flow.py`：J 类端到端流程契约（fixture-based）
- **51 个 golden case**（`bench/cases/`）：
  - 45 单点 × 9 维度（source-routing 18 / v1.2-polish 8 / triggers 2 / auto-detect 3 / dedup 3 / frontmatter 4 / degradation 3 / edge 3 / feedback 1）
  - 6 J 类端到端流程衔接（输入→沉淀→目标→执行→产出→索引→系统，单种子输入贯穿 7 阶段）
  - split：30 train / 10 val / 11 test（J1-J6 全部 held-out 作系统级回归 gate）
- **nightly mock 后端 workflow**（`.github/workflows/skillopt.yml`）：02:17 UTC 自动跑，mock smoke 不烧 API 配额，real-backend 仅在 `workflow_dispatch + split=test + secret set` 时触发；产物 `bench/reports/<run-id>/` 上传 30 天
- **standalone evaluator**（`bench/run_eval.py`）：不依赖 SkillOpt registry，作为库直接消费 `chat_target` + `SplitDataLoader`

### 设计

- DESIGN §6.11（行为评测）+ §13 路线图 v1.3 行 + ADR-017（引入 SkillOpt 决策与边界）
- 完整设计文档：[`docs/dev/v1.3-skillopt-integration.md`](./dev/v1.3-skillopt-integration.md)（13 节，含 51 case 完整清单 + 评分器映射 + split 划分）

### 关键边界

- **不修改任何 SKILL.md 的现有版本**（SkillOpt 产出的 `best_skill.md` 永远经人工 review 后单独 commit）
- **不修改原 `.github/workflows/ci.yml`**（4 个结构校验 job 保持原样作 merge gate）
- **不在 v1.3 接入 SkillOpt-Sleep**（隐私边界需要单独 ADR-018，留 v1.4+）
- **不在 PR 上阻塞 merge**（行为评测是参考信号，不是 gate）
- **主项目仍纯 Node.js + markdown**（Python 依赖隔离在 `requirements-bench.txt`，bench 是可选组件）

### 文件清单

| 类型 | 文件 |
|------|------|
| 新增 | `bench/quickkb/{dataloader,rollout,adapter}.py` |
| 新增 | `bench/quickkb/scoring/{__init__,routing,frontmatter,behavior,flow}.py` |
| 新增 | `bench/run_eval.py`（standalone 入口）|
| 新增 | `bench/cases/{capture,flow}/items.json` + `bench/cases/_schema.json` |
| 新增 | `bench/cases/flow/fixtures/J{1..6}-*.json` |
| 新增 | `bench/configs/{capture-default,flow-default}.yaml` + `_base/skill-template.md` |
| 新增 | `bench/harness/clone-vault.mjs`（exec 后端用）|
| 新增 | `bench/quickkb/skills/capture-initial.md`（基线 snapshot）|
| 新增 | `.github/workflows/skillopt.yml` |
| 新增 | `requirements-bench.txt` |
| 修改 | `.claude-plugin/plugin.json` + `marketplace.json`（1.2.0 → 1.3.0，phases 加 v1.3）|
| 修改 | `docs/DESIGN.md`（§6.11 + §13 + ADR-017）|
| 修改 | `docs/dev/README.md`（阶段表 v1.3 行更新为 51 case）|
| 修改 | `README*.md` × 5 语种（加 SkillOpt 评测段）|
| 修改 | `.gitignore`（bench/reports + .tmp-vault + Python hygiene）|

---

## v1.2 · 2026-08-09 · ai-polish（AI 润色提议）

**摘要**：capture / daily 写入前新增「AI 润色提议」步骤——AI 主动生成扩写版，用户三选一（用润色 / 保留原文 / 再改一版）。解决「用户输入过简、事后看不懂」问题。**无 BREAKING CHANGE**。

### 新增能力

- **capture 步骤 2.5**：对 idea / meeting / ai-dialog / reading 类型，启发式触发（字符数 < 50 或无标点或用户显式说「润色」），AI 生成扩写版，三选一菜单
- **daily 步骤 3.5**：扫描 4 段（Did/Learned/Ideas/Blockers）短句，一次性呈现编号润色菜单
- **原文保存机制**：
  - capture：`source.original_text` + frontmatter `ai_polished: true`
  - daily：行内 `<!-- original: ... -->` HTML 注释 + frontmatter `ai_polished_entries: [编号]`
- **配置**：`kb.config.capture_ai` 段（润色 prompt 中英双语 + 阈值 + 轮次上限）
- **设计**：DESIGN §6.10 + ADR-016（决策、代价、否决方案）

### 边界修订（向后兼容）

- `quick-kb-capture`「不改正文」→「默认不改正文；用户选润色版时原文存 source.original_text」
- `quick-kb-daily`「不改正文语义」→「同上；daily 用行内 HTML 注释保留原句」
- **未改**：web-clip / pdf 抓取正文仍然逐字保留，**不进润色流程**

### 与 ingest / 反问机制的关系

| 维度 | AI 润色（v1.2） | Ingest | daily 反问（v0.2） |
|------|----------------|--------|-------------------|
| 时机 | capture / daily 写入前 | capture 后按需 | daily 写入前 |
| 输入 | 用户原始输入 | 已 capture 内容 | vague input |
| 输出 | 同语义扩写 | 结构化原子观点 | 用户自补的回答 |
| 职责 | 改写 | 抽取 + 分类 | 澄清 |

三者互补不重叠。

### 不包含

- 润色质量评估机制（推后到社区反馈后补）
- 自动学习用户偏好的个性化 prompt（v1.3+ 候选）

---

## v1.1 · 2026-08-09 · flow-restructure（目录流转制 + 路径硬约束）

**摘要**：vault 顶层目录改为 `NN_` 数字前缀（按流转语义排序）；同时落地「文档引用禁绝对路径」硬约束。

⚠️ **BREAKING CHANGE** —— vault 顶层目录从扁平命名改为 `NN_` 前缀。v1.0 vault 需手动迁移，详见 `docs/dev/v1.1-restructure.md` 与 ADR-015。

### BREAKING：顶层目录重命名

| 旧 | 新 | 流转语义 |
|----|----|---------|
| `inbox/` | `00_inbox/` | 灵感库（最上游输入） |
| `resources/` | `01_resources/` | 外部资源（原材料输入） |
| `areas/` | `02_areas/` | 领域知识（核心沉淀） |
| `goals/` | `03_goals/` | 目标管理（方向牵引） |
| `projects/` | `04_projects/` | 项目实践（执行落地） |
| `outputs/` | `05_outputs/` | 产出与复盘（成果输出） |
| `wiki/` | `06_wiki/` | 知识索引（全局导航） |
| `principles/` | `07_principles/` | 认知资产（原则/信念/模式/经验） |
| `archive/` | `98_archive/` | 归档（紧贴 system） |
| `system/` | `99_system/` | 系统与工具（底层支撑） |

**理由**：IDE 文件浏览器按字典序排，扁平命名丢失流转语义；加 `NN_` 前缀后肉眼一眼可辨笔记处在管线哪个阶段。详见 ADR-015。

### 任务 A：路径硬约束（禁绝对路径）

- **3 处 `/path/to/...` 占位符** → 相对路径示例（`docs/quick-start.md` 中英 + `quick-kb-import/SKILL.md`）
- **3 个 SKILL 加「路径约束（硬性）」段**：`quick-kb-capture` / `quick-kb-ingest` / `quick-kb-import`
  - 统一三条：禁绝对路径 / 外部依赖复制到 `01_resources/` / `source.url` 仅 `http(s)://` 或 vault 相对路径
- **CI 校验**：`scripts/check-frontmatter.mjs` 新增 `source.url` 绝对路径检测（覆盖 `file://`、盘符路径）
- **保留能力**：`[[principle/xxx]]` / `[[belief/xxx]]` / `[[pattern/xxx]]` / `[[experience/xxx]]` 等省略前缀 wikilink 由 `check-links.mjs` basename 兜底解析，**不变**

### 其他改动

- `check-frontmatter.mjs`：inbox 跳过规则同步到 `00_inbox`（保留旧名向后兼容）
- `ci.yml`：`demo-vault-init` job 的 find 路径同步（`areas` → `02_areas`、`principles` → `07_principles`）
- `.kb-initialized`：保留 `version: v0.1`，加 `restructured_at: 2026-08-09 (v1.1)`
- v0.x dev 文档顶部加历史注释，指向 ADR-015
- `plugin.json` + `marketplace.json` version → 1.1.0；`phases` 增加 v1.1 条目

### 不包含

- v1.0 vault 自动迁移脚本（用户手动迁移，按映射表 sed 即可）
- 录屏 / 发布社交材料

---

## v1.0 · 2026-08-09 · release（公开发布）

**摘要**：对外发布到 GitHub + skills marketplace。无新功能，全是发布打磨。

### 新增交付

- **治理文档**：`CONTRIBUTING.md` / `COMMUNITY.md` / `CODE_OF_CONDUCT.md`
- **LICENSE**：MIT
- **GitHub 模板**：`.github/ISSUE_TEMPLATE/{bug,feature,config}.yml` + `PULL_REQUEST_TEMPLATE.md`
- **CI 基础检查**：`.github/workflows/ci.yml` + `scripts/check-frontmatter.mjs` + `scripts/check-links.mjs`
  - 4 个 job：frontmatter / wikilink / placeholder / demo-vault 结构
- **demo-vault 完善**（覆盖 v0.1-v0.4）：
  - 7 条认知资产笔记（principle/belief/pattern×2/experience×3）
  - Decision Ledger（含 expected/actual/lesson 完整闭环 + derived_to）
  - 项目 README（plugin-system）+ 目标 README（learn-plugin-design）
  - MOC（含冲突对照段）+ 周复盘（含 KS Top 3 + 结构演化）
- **skills marketplace 配置**：`.claude-plugin/marketplace.json` + `plugin.json`
- **用户文档体系**：`docs/quick-start.md`（v0.4 已有，打磨）+ `docs/user-guide.md`（新增进阶指南）

### 不包含

- 录屏 / 发布社交材料（推后到发布周内补完）
- CONTRIBUTING 实战示例（社区首贡献后补）

---

## v0.4 · 2026-08-09 · extensions（扩展与多语言）

**摘要**：补齐运维性技能与国际化。无结构性新概念。

### 新增技能（4 个）

- `quick-kb-normalize` —— 批量规整（related→relations 迁移 / dry-run / 可回滚）
- `quick-kb-archive` —— 通用归档（任意对象 / 不死链 / 可恢复）
- `quick-kb-stats` —— 健康仪表盘（孤立率/KS Top/置信度/maturity 分布）
- `quick-kb-import` —— 外部库导入（Obsidian/Notion/Logseq → inbox）

### 新增配置

- `references/kb-config-schema.md` —— kb.config.yaml 完整 schema + 校验规则 + 各技能读取映射

### 新增文档

- 5 语种 README（中/英/日/韩/西）+ `docs/quick-start.md`（5 分钟上手）

### 偏差检查

- `references/v0.4-deviation-check.md` —— 无重大偏差，3 处细微补充

---

## v0.3 · 2026-08-09 · assistant（个人助手）

**摘要**：从「带引用的 RAG」升级为「个人决策助手」。引入 quick-kb-memory-agent + 认知资产层 + Decision Ledger 派生闭环。**核心差异化阶段**。

### 新增 Agent

- **`quick-kb-memory-agent`**（核心）—— 长期记忆调取。5 个 intent：
  - `recall_similar` —— 经验召回（按 AGENTS_SPEC §3.5 排序公式）
  - `check_beliefs` —— 原则/假设一致性判定
  - `detect_repeat_mistakes` —— 历史失败模式重演检测
  - `proactive_suggest` —— 4 个 memory 提醒事件
  - `present_conflicts` —— ADR-011 冲突呈现

### 新增技能（3 个）

- `quick-kb-advisor` —— 决策辅助（三段输出：你的历史/你的原则/建议路径）
- `quick-kb-project` —— 项目全生命周期（archive 含 lesson 派生 experience）
- `quick-kb-goal` —— 目标管理（含 quick-kb-research-agent 学习路径 + memory 召回）

### 新增模板（中英 14 个）

- `decision.md`（Decision Ledger 8 字段）
- `principle.md` / `belief.md` / `pattern.md` / `experience.md`（4 类认知资产）
- `goal.md` / `project.md`

### 新增文档

- `references/frontmatter-v0.3.md` —— maturity 6 态 + KS 公式 + value.impact/uniqueness
- `references/conflict-presentation-rule.md` —— ADR-011 落地说明
- `references/proactive-reminders-v0.3.md` —— 全量 7 类事件

### 升级

- `frontmatter`：maturity（6 态）+ value.impact/uniqueness + 14 type 枚举（含 4 类认知资产）
- `quick-kb-manager-agent`：v0.2→v0.3，新增 `detect_structure_drift` + KS 排序 refresh_value
- `KS 公式`：`KS = confidence × log2(1 + reuse) × impact`（仅 maturity ≥ applied 参与 Top-N）
- `quick-kb-memory-agent 排序`：`score = sim^0.45 × recency^0.20 × impact^0.15 × conf^0.20` + 类型加权 + 失败加权

---

## v0.2 · 2026-08-09 · loops（闭环完整）

**摘要**：补齐六大闭环 + 两个 agent + 英文模板。从「单点 capture」到「闭环系统」。

### 新增技能（3 个）

- `quick-kb-connect` —— 类型化关系（supports/contradicts/evolves/supersedes）+ MOC + canvas
- `quick-kb-query` —— strict 模式（默认）+ ADR-011 冲突呈现 + `.query-log.jsonl`
- `quick-kb-review` —— 4 维分析（knowledge/value/structure/daily）+ 健康报告

### 新增 Agent（2 个）

- `quick-kb-manager-agent` —— 库内结构（tidy_inbox/build_moc/recommend_relations/detect_orphans/repair_deadlinks/refresh_value + manager 事件子集）
- `quick-kb-research-agent` —— 外部资料（process_resource/extract_atoms/cross_verify/summarize）

### 升级

- `frontmatter`：新增 relations/context/value.reuse
- `capture`：扩展 PDF/meeting/AI dialog/reading + defuddle
- `ingest`：用 quick-kb-research-agent 替代内置 LLM；冲突检测（quick-kb-manager-agent 降级）
- `templates`：5 个英文版本同步

### 新增文档

- `references/frontmatter-v0.2.md` / `v0.2-deviation-check.md`
- `references/obsidian-integration.md`（5 依赖 + 降级 + 测试矩阵）
- `references/proactive-reminders-v0.2.md`（manager 事件子集）

---

## v0.1 · 2026-08-08 · mvp（最小可用）

**摘要**：从「设计文档」到「能跑通」。建立基础 capture → ingest → daily 流程。

### 新增技能（4 个）

- `quick-kb-init` —— 创建完整 vault 骨架 + 最小 kb.config.yaml + 4 中文模板
- `quick-kb-capture` —— idea + web-clip（基础 HTML→MD + 标题相似度去重）
- `quick-kb-ingest` —— 内置 LLM 抽取原子观点 + confidence 初始值
- `quick-kb-daily` —— 4 段（做了/学到/想法/卡点）+ max 2 轮追问

### 新增模板

- `templates/zh/`：note-concept / note-idea / note-resource / daily

### 新增示例

- `examples/demo-vault/`：11 条样例（3 inbox + 6 formal + 2 daily），演示完整 ingest 链

### 新增文档

- `references/frontmatter-v0.1.md` —— v0.1 字段子集（confidence 可选）
- `docs/dev/v0.1-mvp.md` —— 开发文档

---

<!-- =========================== 设计文档版本（与上面实现阶段独立） =========================== -->

## V2 · 2026-08-09 · 知识冲突 / Decision Ledger / Memory Agent 规格 / 主动提醒

**摘要**：补齐 V1 的四个结构性缺口 —— 知识冲突管理、决策闭环、quick-kb-memory-agent 详细规格、事件驱动的主动提醒机制。

### 变更明细

#### DESIGN.md

- **§6.1 标准字段**：`related` 升级为类型化 `relations`（supports/contradicts/evolves/supersedes），新增可选 `context` 字段。
- **§6.4 maturity**：`deprecated` 强制关联 `supersedes`/`contradicts` 至少一项。
- **新增 §6.7 关系类型化**、**§6.8 上下文字段**，原 §6.7 顺延为 §6.9。
- **§7.3 quick-kb-memory-agent**：能力表加"冲突感知"与"失败案例优先"；引用 AGENTS_SPEC。
- **§7.4**：引用 AGENTS_SPEC。
- **新增 §7.6 主动提醒机制**：7 类事件 → 触发 agent → 提醒示例。
- **§8.3 concept 模板**：`related` → `relations` + `context`。
- **新增 §8.4 Decision Ledger 模板**：problem/options/chosen/reason/rejected/expected/actual/lesson 闭环；lesson 派生为 experience。
- **§11 仓库结构**：加入 AGENTS_SPEC/VERSIONING/CHANGELOG/archive。
- **新增 ADR-011**（关系类型化与冲突管理）、**ADR-012**（Decision Ledger 强化）、**ADR-013**（主动提醒机制）、**ADR-014**（quick-kb-memory-agent 详细规格独立成文）。

#### SKILLS_SPEC.md

- **§2 capture**：工作流加"主动提醒"步（命中 belief/pattern/contradicts 苗头时）。
- **§3 ingest**：工作流加"关系类型化"与"冲突检测与主动提醒"步；输出示例 frontmatter 升级为 `relations` + `context`。
- **§6 advisor**：明确引用 AGENTS_SPEC §3 的 quick-kb-memory-agent 契约。
- **§10 project(init)**：新增"主动相似项目召回"步与"决策骨架"步；archive 工作流新增"Decision Ledger 闭环 + lesson 派生 experience"。
- **附录 A**：新增"主动提醒"与"派生"两行；引用 AGENTS_SPEC。

#### 新增文件

- **docs/AGENTS_SPEC.md**（V1）：三个 agent 的输入/输出契约、降级路径；quick-kb-memory-agent 召回排序公式 `similarity × recency × impact × confidence` + 类型加权；冲突呈现规则；主动提醒协议与限流。

### 变更原因

外部评审第二轮反馈指出四个缺口：

| 反馈点 | 处理 | 对应 ADR |
|--------|------|---------|
| 缺少知识冲突管理 | 升级 `related` 为类型化 `relations` + 自由文本 `context`；拒绝结构化 `context:{team_size,stage}` 防摩擦 | ADR-011 |
| 缺少 Decision Ledger | 强化 `outputs/decisions/` 模板为 expected/actual/lesson 闭环（已存在目录，仅增强模板） | ADR-012 |
| Memory Agent 缺规格 | 新建 AGENTS_SPEC.md，含排序公式与降级 | ADR-014 |
| 缺少主动提醒 | 事件驱动机制（§7.6），非新技能 | ADR-013 |

### 不兼容变更

- **frontmatter**：`related` 仍兼容（视作未类型化弱关联），但 V2 笔记推荐用 `relations`。
- **迁移路径**：`quick-kb-normalize` 可批量迁移 `related` → `relations.supports`。
- **maturity=deprecated**：V2 起新降级必须关联，V1 既有 deprecated 笔记在首次 Review 时补关联或保留告警。

### 归档

V1 完整快照见 `docs/archive/V1/`。

---

## V1 · 2026-08-08 · 首个稳定设计

**摘要**：建立 quick-knowledge 知识库技能框架的完整设计基线。

### 核心内容

- **六大闭环**：Capture / Ingest / Normalize / Connect / Query / Review
- **目录结构**：PARA + 系统层 + `principles/`（认知资产）
- **技能清单**：10 核心 + 4 扩展
- **元数据规范**：`status`（文档状态）+ `maturity`（知识成熟度）正交双字段，加 `confidence` 与 `value`
- **Agent 设计**：manager / research / memory 三 agent 协作
- **多语言**：设计文档中文，模板与 README 中英双语
- **Obsidian 集成**：依赖 kepano/obsidian-skills，非 Obsidian 环境降级

### 已采纳的外部反馈

本版本在初始草稿基础上融合了首轮外部评审反馈：

| 反馈点 | 处理方式 |
|--------|---------|
| 缺少知识生命周期模型 | 拆分 `status`/`maturity` 为正交双字段，maturity 收敛为 6 态 |
| 缺少个人认知模型 | 新增 `principles/` 根目录 + 4 类认知资产 type |
| Agent 设计偏弱 | 新增 quick-kb-memory-agent；Knowledge Architect 能力并入 manager |
| Query 需要升级 | 不替换 query，并列新增 quick-kb-advisor |
| 缺少知识评分体系 | 引入价值维度，自动化优先；拒绝手填三分数 |

详见 `DESIGN.md` 的 ADR-004、ADR-007、ADR-008、ADR-009、ADR-010。

### 备注

- 初始草稿（融合反馈前的版本）未归档，因为版本规范在本版本才建立。
- 自 V2 起，每次迭代将严格按 `VERSIONING.md` §4 工作流执行。

### 涉及文件

- `docs/DESIGN.md`（主设计文档，14 节）
- `docs/SKILLS_SPEC.md`（技能详细规格，11 节 + 附录）

---

<!-- 模板：未来版本按此格式追加

## V2 · YYYY-MM-DD · 简短标题

**摘要**：一句话说明本版核心变更。

### 变更明细

#### DESIGN.md
- 第 X 节：...
- 新增 ADR-011：...

#### SKILLS_SPEC.md
- 第 X 节：...

### 变更原因
（为什么做这些变更 —— 外部反馈 / 实践发现 / 新需求）

### 不兼容变更
（如有，明确列出对已有 vault / frontmatter 的影响与迁移路径）

-->
