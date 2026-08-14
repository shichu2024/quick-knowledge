<!--
Template: daily log (English · v1.2)
Purpose: Daily journal, written to 05_outputs/daily/YYYY/MM/YYYY-MM-DD.md by quick-kb-daily.
Features: AI asks follow-up questions when description is vague (max 2 rounds); auto-generates wikilinks for existing note titles;
         v1.2+ short entries in 4 sections can be AI-polished (user picks from 3 options; original kept as inline HTML comment).
Source of truth: references/frontmatter-v0.2.md · docs/DESIGN.md §6/§6.10/§8 · docs/SKILLS_SPEC.md §8
Note: daily is a doc-type note (no maturity); but still has relations/value structure.
-->
---
title: {{YYYY-MM-DD}} Log              # required
type: daily                            # required
created: {{date}}                      # required
updated: {{date}}                      # required
tags:                                  # required
  - daily
status: active                         # required
domain:                                # optional · daily usually has no domain
relations:
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
value:
  reuse: 0
# ai_polished_entries: [1, 2]          # v1.2+ · only written when step 3.5 has user-polished entries
---

# {{YYYY-MM-DD}}

## What I Did

- {{Meeting/coding/communication/... · one line each · AI will follow up if vague; v1.2+ short lines optionally polished}}
  <!-- original: {{user's original line · only present when polished}} -->

## What I Learned

- {{Today's new insight · link to concept notes [[...]]}}

## Ideas

- {{Inspiration/observation · capture will be suggested if worth recording}}

## Blockers

- {{Blocked/confused/to-resolve · link to project or goal}}

## To Capture

> AI detected the following may be worth capturing separately. Call quick-kb-capture?

- [ ] {{candidate idea 1}}
- [ ] {{candidate idea 2}}

---

<!-- Follow-up log (max 2 rounds):
     Q1: {{AI round 1 follow-up}}
     A1: {{user answer}}
     Q2: {{AI round 2 follow-up (if any)}}
     A2: {{user answer}}
-->

<!-- v1.2+ Polish log:
     Polished entries' original lines are preserved as inline <!-- original: ... --> comments
     right beneath each polished entry. frontmatter ai_polished_entries lists the cross-section
     sequential numbering of polished entries. See DESIGN §6.10 + ADR-016.
-->
