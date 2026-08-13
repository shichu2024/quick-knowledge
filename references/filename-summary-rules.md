---
version: v1.4.2
updated: 2026-08-13
phase: v1.4
applies_to: quick-kb-daily §1 / quick-kb-project §5 (progress) / quick-kb-goal §5 (progress) / quick-kb-review §4（以及任何生成 `<date-token>-<summary>.md` 文件名的技能）
source_of_truth:
  - skills/quick-kb-daily/SKILL.md §步骤 1
  - skills/quick-kb-project/SKILL.md §5 工作流 · update
  - skills/quick-kb-goal/SKILL.md §5 工作流 · progress
  - skills/quick-kb-review/SKILL.md §步骤 4
  - docs/dev/v1.4-docs.md B-WP6
---

# 日期类文件名 summary 提炼规则 · Filename Summary Rules

> 本文件是 **所有生成 `<date-token>-<summary>.md` 文件名的技能的统一决策表**。多个技能的判定逻辑完全一致，抽到此处集中维护，避免副本漂移。
>
> 解决问题：v1.4 引入「日期 + summary」命名后，模型大量以「内容笼统 / 主题分散 / 不可提炼」等**语义借口**退化为纯日期，违反 v1.4 设计意图。本规则用**机械字符判定**取代语义判定，杜绝绕过。

---

## 1. 适用范围

| 技能 | 文件名模式 | 触发场景 |
|------|-----------|---------|
| `quick-kb-daily` | `YYYY-MM-DD-<summary>.md` | 创建日志文件（§步骤 1） |
| `quick-kb-project` | `progress/YYYY-MM-DD-<summary>.md` | 追加项目进展（§5 update） |
| `quick-kb-goal` | `progress/YYYY-MM-DD-<summary>.md` | 追加目标进展（§5 progress） |
| `quick-kb-review` | `<date-token>-<summary>.md` | 创建周期报告（§步骤 4，date-token 形态随 period 而异） |

> 同日/同周期已有旧文件（任何形式）→ **编辑既有文件，不重新提炼 summary，不改名**（文件名稳定性硬约束，避免 wikilink 断）。本规则仅约束**新建**时的 summary 提炼决策。

---

## 2. summary 提炼决策表（逐步走，不许用单一条件宽放）

### Step 1 · 先查「强制纯日期」清单

命中以下**任一**条件 → **退化为纯日期**（`YYYY-MM-DD.md` 或对应 `<date-token>.md`），**禁止**提炼 summary：

| # | 强制纯日期条件 | 判定规则 |
|---|--------------|---------|
| 1 | content 完全为空 | `content` 为 null / 空字符串 / 仅空白字符 |
| 2 | 解析后实质条目全空 | 4 段（daily）/ 进展字段（progress）/ 报告维度（review）全部为空 |
| 3 | 实质字符数 < 5 | 去掉元描述后剩 < 5 字符（如「ok」/「无」/「没事」/「休息」/「今天」/「-」） |
| 4 | 仅含纯元描述且无事件 / 领域关键词 | 输入字面是「今天没什么」「就这些」「完毕」「没特别要记」「日常」之一，且不含任何具体名词 |

### Step 2 · 未命中 → **必须**提炼 summary

Step 1 全部未命中 → **强制**从 content 提炼 2-5 词 kebab-case 作为 summary：

- 限 30 字符内
- 从最有实质内容的段落 / 字段抽取核心名词 + 动作
- 多个候选 → 取第一个出现的实质内容
- 内容跨领域 / 主题分散 → **取首个主题**（不允许多主题作为退化为纯日期的借口）

---

## 3. 禁止语义绕过（硬约束）

Step 1-2 是**机械字符判定**。**严禁**用以下语义理由退化为纯日期：

- 「内容笼统 / 表达 vague / 不够具体」
- 「主题分散 / 跨多个领域 / 难以归纳」
- 「信息不足 / 内容太短」
- 「会议型日志无可提炼主题」
- 「用户表达模糊，无法判断核心」

> 这些恰恰是用户原始表达——**summary 反映原始表达即可**，不需要美化。例如「开了一天的会」→ summary 可以是 `meeting-marathon` / `meetings-only-day`，**不允**许以「会议型日志不可提炼」为由退化为纯日期。
>
> 「内容真的为空」通过 Step 1 条件 1-3 判定，**绝不**作为语义借口。Step 1 命中纯日期 + frontmatter 可加 `partial: true` 或 `status: draft`，二者可并存。

---

## 4. 错误绕过反例（模型常见的偷懒模式，必须避免）

### 4.1 daily 场景

| 输入 | 错误行为（纯日期） | 正确行为（带 summary） | 错误借口 |
|------|------------------|---------------------|---------|
| 「今天搞了一下午 RAG 调参」 | `2026-08-13.md` | `2026-08-13-rag-tuning.md` | ❌ 「调参太笼统」 |
| 「写了几行代码，修了个登录 bug」 | `2026-08-13.md` | `2026-08-13-login-bugfix.md` | ❌ 「bug 描述不具体」 |
| 「今天开了一天的会，重点是 RAG 评审」 | `2026-08-13.md` | `2026-08-13-rag-review-meetings.md` 或 `meeting-day.md` | ❌ 「会议型日志不可提炼」 |
| 「学了很多关于 mcp 的东西」 | `2026-08-13.md` | `2026-08-13-mcp-learning.md` | ❌ 「学了很多不具体」 |
| 「没什么特别的，就是日常开发」 | `2026-08-13.md` | `2026-08-13-routine-dev.md` 或 `daily-grind.md` | ❌ 「日常太笼统」 |
| 「」 / 「ok」 / 「没事」 | `2026-08-13.md` | `2026-08-13.md` | ✓ Step 1 条件 3 命中，纯日期正确 |

### 4.2 project / goal progress 场景

| 输入 | 错误行为 | 正确行为 | 错误借口 |
|------|---------|---------|---------|
| 「今天实现了登录流程」 | `progress/2026-08-13.md` | `progress/2026-08-13-auth-impl.md` | ❌ 「实现细节太简单」 |
| 「卡在向量库选型上」 | `progress/2026-08-13.md` | `progress/2026-08-13-vector-db-blocker.md` | ❌ 「卡点描述太短」 |
| 「完成 milestone 2」 | `progress/2026-08-13.md` | `progress/2026-08-13-m2-done.md` | ❌ 「里程碑完成不是主题」 |

### 4.3 review 场景

| 报告内容 | 错误行为 | 正确行为 | 错误借口 |
|---------|---------|---------|---------|
| 主线是 RAG 评估调试 | `2026-W32.md` | `2026-W32-rag-eval.md` | ❌ 「周报维度多」 |
| 季度稳定化为主 | `2026-Q3.md` | `2026-Q3-stabilization.md` | ❌ 「季度主题分散」 |

---

## 5. summary 提炼执行规则

### 5.1 词性组合

推荐组合：`<核心名词>-<动作/修饰>` 或 `<核心名词>-<次主题>`

| 模式 | 示例 |
|------|------|
| 名词-动名词 | `rag-tuning` / `auth-impl` / `mcp-learning` |
| 名词-名词 | `vector-db-blocker` / `rag-review-meetings` |
| 形容词-名词 | `routine-dev` / `daily-grind` / `meeting-marathon` |
| 缩写 | `m2-done`（milestone 2 done）/ `api-stabilization` |

### 5.2 多主题处理

- 内容含多个主题 → **取首个**（按 content 出现顺序）
- 多主题并重 → 用最宽泛的概括词（如「日常」→ `routine-dev`，**不要**退化纯日期）
- 在 diff log / 报告中可标 `needs_review: true` 提示用户人工调整（仅 review 技能）

### 5.3 字符约束

- 2-5 个词（kebab-case 连接）
- 总长度 ≤ 30 字符
- 仅 ASCII（中文输入也要提炼为英文 summary，便于 wikilink 与跨工具兼容）

---

## 6. 单轮 eval / 自动化场景

自动化调用（如 bench / CI）创建文件时：

1. **必须**按 Step 1-2 判定，**不允**许因「自动化场景」直接退化为纯日期
2. 文件路径反馈中**必须**含 summary 段（除非 Step 1 命中）
3. 反馈输出格式对齐各技能的 `✓ 路径行` 契约（路径行字面包含完整文件名）

---

## 7. 降级路径

| 场景 | 降级行为 |
|------|---------|
| LLM 不可用（无法提炼） | 用 fallback 启发式：取 content 首个实词 + 核心动词（如「RAG 调参」→ `rag-tuning`） |
| content 仅含中文 | 翻译为 ASCII kebab-case（「RAG 调参」→ `rag-tuning`，「登录 bug 修复」→ `login-bugfix`） |
| 实在抽不出关键词（罕见） | 用日期相关的最低信息（如 `daily-log` / `progress-note`），**不退化为纯日期** |
| summary 候选超 30 字符 | 截断到 30 字符内（保前 2 个词） |

> **永远不退化为纯日期**，除非 Step 1 命中。即使是降级路径，也要给出最低信息量的 summary（如 `daily-log`）。

---

## 8. 不变量

- **机械字符判定优先**：Step 1 是硬性条件检查，**不参**入语义判断
- **summary 提炼不可跳过**：只要 content 非空（Step 1 未命中），文件名**必须**含 summary 段
- **文件名稳定性**：同日/同周期已有任何形式的旧文件 → 编辑不改名（详见各技能 §加载/创建逻辑）
- **summary 永远 ASCII kebab-case**：即使 content 是中文，summary 也是 ASCII
- **长度上限 30 字符**：超出截断，不报错

---

## 9. 配置项

| 配置路径 | 默认值 | 说明 |
|---------|--------|------|
| `kb.config.filename_summary.enabled` | `true` | 全局开关；关闭时所有日期文件退为纯日期（仅用于排查） |
| `kb.config.filename_summary.min_chars` | 5 | Step 1 条件 3 的阈值 |
| `kb.config.filename_summary.max_length` | 30 | summary 字符上限 |
| `kb.config.filename_summary.lang` | `ascii` | summary 语言（v1.4 仅支持 ascii） |

---

## 10. 自检清单（执行后）

- [ ] 新建文件路径含 summary 段（除非 Step 1 命中纯日期）
- [ ] summary 是 2-5 词 ASCII kebab-case，≤ 30 字符
- [ ] 未用「内容笼统 / 主题分散 / 信息不足」等语义借口退化为纯日期
- [ ] 同日/同周期已有旧文件时，编辑不改名
- [ ] summary 反映 content 首个实质主题（多主题时取首个）
- [ ] 反馈输出路径行字面含完整文件名（含 summary）

---

## 11. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.4.2 | 2026-08-13 | 初始版本，从 daily §步骤 1 + project/goal progress + review §步骤 4 抽取统一决策表；引入机械判定杜绝语义绕过 |
