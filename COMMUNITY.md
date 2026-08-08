# 社区技能索引 · COMMUNITY

> 本文档定义 quick-knowledge 社区贡献技能的索引规则。
>
> 参考 [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 的社区蒸馏模式。

---

## 1. 核心技能 vs 社区技能

| 类型 | 位置 | 维护方 | 索引 |
|------|------|--------|------|
| **核心技能** | 本仓库 `skills/` | 项目 maintainer | 本仓库 README |
| **社区技能** | 独立仓库 / fork | 社区贡献者 | 本文件 + topic 索引 |

核心技能覆盖六大闭环 + 三个 agent。社区技能扩展特定 domain / runtime / 工作流。

---

## 2. 社区技能提交流程

1. 在你的 GitHub 仓库实现技能（遵循 [SKILLS_SPEC.md](./docs/SKILLS_SPEC.md) 格式）
2. 测试通过后向本仓库提 PR 修改 `COMMUNITY.md`
3. PR 描述含：
   - 技能名 / 仓库链接
   - 解决的问题（属于哪个闭环 / domain）
   - 测试用例
4. Maintainer 评审：
   - 是否与核心技能重叠
   - 是否符合 SKILLS_SPEC 格式
   - 是否有清晰降级路径
5. 合并后纳入下方索引

---

## 3. 索引分类

### 3.1 Domain 扩展

特定领域（如法律、医学、学术研究）的捕获/ingest 模板与规则。

<!-- 提交示例：
- [quick-kb-law](https://github.com/<user>/quick-kb-law) —— 法律文书捕获与法条关联
-->

### 3.2 Runtime 适配

为非主流 runtime 提供的兼容层。

<!-- 提交示例：
- [quick-kb-aider-bridge](https://github.com/<user>/quick-kb-aider-bridge) —— Aider 集成
-->

### 3.3 工作流扩展

基于核心技能的复合工作流。

<!-- 提交示例：
- [quick-kb-research-deep](https://github.com/<user>/quick-kb-research-deep) —— 深度研究流水线（capture + 多轮 ingest + advisor）
-->

### 3.4 模板扩展

特定语言 / 文化 / 学科的模板。

<!-- 提交示例：
- [quick-kb-templates-ja-law](https://github.com/<user>/quick-kb-templates-ja-law) —— 日本法律文书模板
-->

---

## 4. 命名约定

社区技能仓库建议命名：`quick-kb-<topic>` 或 `quick-kb-<runtime>-<topic>`。

避免与核心技能重名（`quick-kb-*` 中已有 14 个核心技能）。

---

## 5. 质量门槛

纳入索引的社区技能必须：

- [ ] README 含安装方式与示例
- [ ] 至少 3 个测试用例（或 dry-run 示例）
- [ ] 明确的降级路径（核心依赖不可用时的行为）
- [ ] 与核心技能的兼容性说明
- [ ] LICENSE（推荐 MIT）

---

## 6. 索引维护

- 每季度 review 索引中的链接可达性
- 失效仓库移到 `archive/` 段
- 高活跃社区技能可提案升级为核心技能（走 [CONTRIBUTING.md](./CONTRIBUTING.md) 流程）
