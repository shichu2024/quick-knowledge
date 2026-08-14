<!--
模板：goal 目标（中文 · v0.3）
用途：目标管理 + 学习路径。由 quick-kb-goal create 写入 03_goals/<slug>/goal.md。
真相源：references/frontmatter-v0.3.md · docs/DESIGN.md §6 · docs/SKILLS_SPEC.md §9
-->
---
title: {{目标名称}}
type: goal
created: {{date}}
updated: {{date}}
tags:
  - goal/{{slug}}
status: active                 # active → done（完成）/ cancelled（取消）
maturity: applied              # goal 仍属知识型，但可选；通常 applied
confidence: 70
deadline: {{YYYY-MM-DD}}       # 可选
domain: {{domain}}             # 可选 · 学 Rust 等学习目标通常有领域
relations:
  supports: []                 # 相关 concept 笔记支撑
  contradicts: []
  evolves: []
  supersedes: []
context: {{目标情境：为什么立这个目标}}
value:
  reuse: 0
  impact: 4
---

# {{目标名称}}

## 成功标准

- [ ] {{可验证的完成标准 1}}
- [ ] {{可验证的完成标准 2}}

## 学习路径

> 由 quick-kb-goal create 调 quick-kb-research-agent 生成；库内已有笔记优先关联

1. 基础概念（X 周） → [[已有 concept 1]] / [建议 Capture 缺口]
2. 进阶主题（X 周） → [[已有 concept 2]]
3. 实战项目（X 周）

## 里程碑

- [ ] M1：{{描述}} · 目标日期 {{YYYY-MM-DD}}
- [ ] M2：{{描述}} · 目标日期 {{YYYY-MM-DD}}
- [ ] M3：{{描述}} · 目标日期 {{YYYY-MM-DD}}

## 进度记录

> 进展写入 progress/YYYY-MM-DD.md（每次 quick-kb-goal progress 追加一条）

- [[progress/2026-XX-XX]]
- [[progress/2026-XX-XX]]

## 关联项目

- [[04_projects/{{project-slug}}/_readme|{{项目名}}]]

## 相关笔记

- [[concept 1]]
- [[concept 2]]
