<!--
模板：idea 笔记（中文 · v0.1）
用途：碎片化灵感、想法、待消化的素材。由 quick-kb-capture 写入 00_inbox/ideas/。
说明：inbox 原始素材走 DESIGN §6.9 最小 frontmatter（title + captured_at），
      suggested_tags 是 AI 预标注的候选标签 hint，不强制，由 ingest 决定。
真相源：references/frontmatter-v0.1.md §3 · docs/DESIGN.md §6.9
-->
---
title: {{简短标题}}                    # required
captured_at: {{YYYY-MM-DDTHH:MM}}      # required · ISO 8601 含时间
capture_type: idea                     # idea | web-clip | pdf | meeting | ai-dialog | reading
source:                                # optional · 若来自对话/他人/链接
  # - url: https://...
  # - person: "{{谁说的}}"
suggested_tags:                        # optional · AI 预标注候选；ingest 时转正为 tags
  - {{domain}}/{{topic}}
---

# {{简短标题}}

{{想法/灵感/观察 · 一段话即可，不强求结构}}

## 背景（可选）

- 触发场景：{{何时何地想到的}}
- 关联项目/目标：[[{{wikilink}}]]

## 可能的下一步

- [ ] 值得展开 → 调用 `quick-kb-ingest` 转为正式 concept/resource
- [ ] 暂存，待后续判断
- [ ] 丢弃（确认无价值后由 review 清理）
