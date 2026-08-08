<!--
Template: concept note (English · v0.2)
Purpose: Record a concept, principle, or mental model. Written to areas/<domain>/ after ingest.
Fill: Auto-filled by quick-kb-ingest (via research-agent); user may revise.
Source of truth: references/frontmatter-v0.2.md · docs/DESIGN.md §6/§8.3
-->
---
title: {{title}}                       # required
type: concept                          # required
created: {{date}}                      # required · YYYY-MM-DD
updated: {{date}}                      # required
tags:                                  # required · controlled, domain/topic form
  - {{domain}}/{{topic}}
status: active                         # required · inbox/draft/active/done/cancelled/archived
domain: {{domain}}                     # optional
confidence: 50                         # optional · 0-100 · single 40/multi 60+/primary 80+
relations:                             # required structure · typed relations (DESIGN §6.7)
  supports:
    - "[[{{related-concept}}]]"
  contradicts: []
  evolves: []
  supersedes: []
context: {{applicable context · free text · optional}}   # optional · DESIGN §6.8
value:
  reuse: 0
source:
  - note: "[[{{inbox-source-wikilink}}]]"
  # - url: https://...
---

# {{title}}

## Core Definition

{{One sentence: what this concept is}}

## Why It's Useful

{{What problem it solves}}

## Key Components

-

## Use Cases

-

## Example

{{Inline concrete example, easy to recall}}

## Related

- [[related concept]]

## To Verify

- [ ] {{Record any unconfirmed claims here; tracked by review}}
