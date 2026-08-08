# 贡献指南 · CONTRIBUTING

感谢你对 quick-knowledge 的兴趣！本文档说明如何参与贡献。

[English](#english) · [中文](#中文)

---

## English

### Ways to Contribute

- **Report bugs** — open an issue with the bug template
- **Suggest features** — open an issue with the feature template; please check the design doc first ([DESIGN.md](./docs/DESIGN.md)) to see if it fits the project's direction
- **Improve docs** — typos, clarity, missing sections
- **Add templates** — new language variants or new note types (must be approved via design discussion first)
- **Add skills** — see "Adding New Skills" below

### Adding New Skills

1. Read [`docs/SKILLS_SPEC.md`](./docs/SKILLS_SPEC.md) for the skill format
2. Read [`docs/DESIGN.md`](./docs/DESIGN.md) to ensure the skill fits the six closed loops
3. Open a feature issue first to discuss scope
4. Create `skills/<skill-name>/SKILL.md` following the convention:
   - YAML frontmatter with `name`, `description`, `version`, `phase`, `source_of_truth`
   - Trigger words (zh + en)
   - Input/output contract
   - Workflow
   - Idempotency guarantee
   - Degradation paths
   - Self-check list
   - Deviation notes (vs design doc)
5. Add the skill to the relevant dev phase doc
6. Run CI checks locally (frontmatter / wikilinks)

### Adding New Templates

1. Follow existing template structure (`templates/zh/`, `templates/en/`)
2. Frontmatter must align with [`references/frontmatter-v0.3.md`](./references/frontmatter-v0.3.md)
3. Provide both `zh/` and `en/` versions
4. Update `docs/DESIGN.md §8.1` template list

### Pull Request Process

1. Fork → feature branch (`feat-<topic>` or `fix-<topic>`)
2. Ensure CI passes (frontmatter validation, link check)
3. PR description follows the template
4. At least one maintainer review required
5. Squash-merge to `master`

### Code Style

- Markdown files end with a newline
- YAML frontmatter uses 2-space indent
- Filenames: kebab-case
- No emojis in code/docs unless explicitly requested

### Commit Message

Conventional commits: `<type>: <description>` (types: feat / fix / refactor / docs / test / chore / perf / ci)

---

## 中文

### 贡献方式

- **报 bug** —— 用 bug 模板开 issue
- **提特性** —— 用 feature 模板开 issue；请先看设计文档([DESIGN.md](./docs/DESIGN.md))是否契合方向
- **改文档** —— 错别字、清晰度、补缺
- **加模板** —— 新语言或新 type（需先经设计讨论）
- **加技能** —— 见下

### 加新技能

1. 阅读 [`docs/SKILLS_SPEC.md`](./docs/SKILLS_SPEC.md) 了解技能格式
2. 阅读 [`docs/DESIGN.md`](./docs/DESIGN.md) 确认技能落在六大闭环内
3. 先开 issue 讨论范围
4. 在 `skills/<skill-name>/SKILL.md` 按约定创建：
   - YAML frontmatter（name / description / version / phase / source_of_truth）
   - 触发词（中英）
   - 输入输出契约
   - 工作流
   - 幂等保证
   - 降级路径
   - 自检清单
   - 与设计文档的偏差说明
5. 在对应阶段开发文档登记
6. 本地跑 CI 检查（frontmatter / wikilinks）

### 加新模板

1. 遵循既有结构（`templates/zh/`、`templates/en/`）
2. frontmatter 对齐 [`references/frontmatter-v0.3.md`](./references/frontmatter-v0.3.md)
3. 中英两版都要
4. 更新 `docs/DESIGN.md §8.1` 模板清单

### PR 流程

1. Fork → 特性分支
2. CI 通过（frontmatter 校验 / 链接检查）
3. PR 描述按模板
4. 至少一位 maintainer review
5. Squash-merge 到 `master`

### 风格

- Markdown 末尾换行
- YAML frontmatter 2 空格缩进
- 文件名 kebab-case
- 不用 emoji（除非显式要求）

### Commit 信息

约定式提交：`<type>: <description>`（type：feat / fix / refactor / docs / test / chore / perf / ci）
