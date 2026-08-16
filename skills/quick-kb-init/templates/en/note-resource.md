<!--
Template: resource note (English · v0.2)
Purpose: External resource summary (article, book, course, open-source project). Written to 01_resources/<category>/.
Difference: concept is "my understanding"; resource is "summary of others' work".
Source of truth: references/frontmatter-v0.2.md · docs/DESIGN.md §6/§8
-->
---
title: {{resource title}}               # required
type: resource                         # required
created: {{date}}                      # required
updated: {{date}}                      # required
tags:                                  # required
  - {{category}}/{{topic}}             #   category ∈ articles/books/courses/repos
status: active                         # required
domain: {{domain}}                     # optional
confidence: 40                         # optional · single-source default 40; raise after cross-verification
relations:
  supports: []                         #   which concepts this resource supports
  contradicts: []                      #   conflicts with other resources (same topic, different conclusion)
  evolves: []                          #   updated from earlier version
  supersedes: []                       #   replaces outdated resource
context: {{applicable context · optional}}
value:
  reuse: 0
source:                                # optional · strongly recommended · object format (v1.9.3, schema-aligned)
  url: {{original url}}
  author: "{{author/origin}}"
  published: {{publish date}}
  note: "[[{{inbox-source-wikilink}}]]"
---

# {{resource title}}

## One-line Summary

{{What this article/book/project is about}}

## Key Points

1. {{Point 1 · paraphrase in your own words, not a copy}}
2. {{Point 2}}
3. {{Point 3}}

## Why I Saved It

{{Relevance to my current project/goal/understanding}}

## Key Excerpt

> {{A sentence/passage worth revisiting}}

## Related Notes

- [[related concept]]
- [[related project/goal]]

## Action Items

- [ ] {{If the resource triggers concrete action, note it here}}
