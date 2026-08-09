# 提交到 Claude Code 官方 plugin 目录 · Submission Checklist

> 本文档帮助维护者向 [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 提交 quick-knowledge。
> 这是进入 Claude Code `/plugin > Discover` 官方浏览列表的唯一推荐路径。

---

## 1. 提交入口

**官方 submission form**：<https://clau.de/plugin-directory-submission>

> ⚠️ 不接受直接 PR。Anthropic 通过此表单审核第三方 plugin。审核标准见官方仓库 README「External Plugins」段。

---

## 2. 提交前自检清单

提交前确认：

- [x] 仓库公开可克隆：<https://github.com/shichu2024/quick-knowledge>
- [x] `.claude-plugin/plugin.json` 就位（Claude Code plugin 入口）
- [x] `.claude-plugin/marketplace.json` 含 `$schema` + `plugins[]` 数组（Claude Code marketplace schema）
- [x] 至少 1 个 `SKILL.md` 存在（当前 14 个 skills）
- [x] `LICENSE` 文件存在（MIT）
- [x] `README.md` 含安装/使用说明
- [x] 通过基础 CI（frontmatter / wikilink / demo-vault 结构）
- [x] `npx skills add shichu2024/quick-knowledge` 在干净环境安装成功（已验证）
- [ ] `/plugin marketplace add shichu2024/quick-knowledge` 在 Claude Code 实测可用（待 maintainer 在 Claude Code 环境验证）
- [ ] 至少 1 个 runtime 实测可用（待 maintainer 在 Claude Code 验证）

---

## 3. Form 字段速查（建议答案）

| 表单字段 | 建议内容 |
|---------|---------|
| **Plugin name** | `quick-knowledge`（不可变 slug，与 marketplace.json `plugins[0].name` 一致） |
| **Display name** | quick-knowledge |
| **Description (short)** | Personal Knowledge Base × AI Skill Framework — distill fragmented information into reusable personal assets. |
| **Description (long)** | 14 skills + 3 agents (manager/research/memory). Six closed loops: Capture / Ingest / Normalize / Connect / Query / Review. Decision Ledger with lesson→experience derivation. Memory-agent with ranking formula makes it a personal advisor, not just RAG with citations. |
| **Category** | productivity（备选：knowledge-management，若无此类别则 productivity） |
| **Author / Maintainer** | shichu2024 — <你的联系邮箱> |
| **Source repository** | <https://github.com/shichu2024/quick-knowledge> |
| **Source path within repo** | `/`（plugin manifest 在仓库根的 `.claude-plugin/`） |
| **Homepage** | <https://github.com/shichu2024/quick-knowledge> |
| **License** | MIT |
| **Tags / Keywords** | knowledge-management, agent-skills, personal-knowledge-base, obsidian, zettelkasten, memory, decision-ledger |
| **Minimum Claude Code version** | ≥ 1.0（含 `/plugin marketplace` 命令的版本） |
| **Demo / Screenshot URL** | （发布周内补完录屏后填） |

---

## 4. Plugin 在 Claude Code 中的预期呈现

提交通过审核后，Claude Code 用户可：

```bash
# 路径 1：从官方目录浏览安装
/plugin                              # 打开 plugin UI
# → Discover 标签 → 搜索 "quick-knowledge" → Install

# 路径 2：直接用 plugin slug 安装
/plugin install quick-knowledge@claude-plugins-official

# 路径 3：把本仓库作为独立 marketplace 添加
/plugin marketplace add shichu2024/quick-knowledge
/plugin install quick-knowledge
```

---

## 5. 审核可能的反馈与应对

| 可能反馈 | 应对 |
|---------|------|
| Schema 不符 | 对照 [anthropics/claude-plugins-official/.claude-plugin/marketplace.json](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json) 调整 |
| 缺少 `source.sha` | 提交时锁定到 v1.0.0 tag 对应的 commit sha |
| 缺录屏 / 截图 | 发布周内补完 |
| Skill 触发词与现有 plugin 冲突 | 加 namespace 前缀（已用 `quick-kb-`，冲突风险低） |
| 安全审计（MCP/可执行代码） | 本 plugin 无 MCP、无可执行脚本（CI 用 Node 脚本仅在仓库内运行，不进入用户环境），需说明 |

---

## 6. 提交后跟进

- 提交 form 后， Anthropic 审核（无 SLA 承诺）
- 通过后，plugin 会出现在 `/plugin > Discover` 列表
- 失败会通过表单留下的联系方式反馈，按反馈调整后重新提交

---

## 7. 同时维护的其他发布渠道

| 渠道 | 状态 | 安装命令 |
|------|------|---------|
| **GitHub Release v1.0.0** | ✅ 已发布 | — |
| **`npx skills add` CLI** | ✅ 已验证 | `npx skills add shichu2024/quick-knowledge` |
| **Claude Code 自建 marketplace** | 🟡 schema 已就位，待用户实测 | `/plugin marketplace add shichu2024/quick-knowledge` |
| **Claude Code 官方目录** | ⏳ 待 maintainer 提交 form | 通过后：`/plugin install quick-knowledge@claude-plugins-official` |
| **第三方 registry（skillpm / ClawHub / Smithery）** | ⏳ 未提交 | （未来按需扩展） |

---

## 8. Maintainer 提交步骤摘要

1. 打开 <https://clau.de/plugin-directory-submission>
2. 按 §3 表单字段填表
3. 在 Claude Code 实测：`/plugin marketplace add shichu2024/quick-knowledge` → `/plugin install quick-knowledge` → 跑一遍 `quick-kb-init` 验证
4. 提交表单，等待 Anthropic 审核
5. 通过后在本文件 §7 更新渠道状态，commit 推送
