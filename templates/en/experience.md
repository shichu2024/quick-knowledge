<!--
Template: experience (English · v0.3)
Purpose: Concrete historical event / lesson. No domain. Stored in 07_principles/experiences/.
Key: usually auto-derived by quick-kb-project (on archive) from the Decision Ledger lesson field.
Source of truth: references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§6.4/§8.4
-->
---
title: {{event in one sentence · includes time/project}}
type: experience
created: {{date}}              # usually event date or project archive date
updated: {{date}}
tags:
  - experience/{{topic}}
  - {{secondary-tag}}          # e.g. lesson/security, lesson/performance
status: active
maturity: applied              # experience already applied (or applied→teachable)
confidence: 80                 # firsthand experience usually high confidence
relations:
  supports: []                 # principle/pattern supported by this experience
  contradicts: []              # conflicts with other experience (different context)
  evolves: []
  supersedes: []
context: {{event background: team size, stage, tech stack, constraints}}
value:
  reuse: 0                     # experience reuse usually higher (recalled by quick-kb-memory-agent)
  impact: 4                    # failure lessons usually higher impact
  uniqueness: 4
source:
  - note: "[[{{source Decision Ledger}}]]"   # derived from which decision
derived_from: "[[{{source Decision Ledger}}]]"  # v0.3 derivation relation field
# no domain (cognitive assets are cross-cutting)
event_date: {{event date}}     # optional · distinguish from created
outcome: {{positive/negative/neutral + brief result}}  # v1.7 WP3-D: required, for detect_repeat_mistakes
trigger: {{trigger situation}}                             # v1.7 WP3-D: required, for detect_repeat_mistakes (e.g. "high-pressure deploy", "short delivery cycle")
---

# {{event in one sentence}}

## Background

{{context of the event · team, stage, constraints}}

## Timeline

{{timeline · key decision points · turning points}}

## Outcome

{{result description · failure/success/mixed}}

## Lesson

> Derived from [[{{source Decision Ledger}}]] lesson field

{{one-sentence reusable lesson · the core of this note}}

## Abstractable principle/pattern

- Candidate principle: {{can it be promoted?}}
- Candidate pattern: {{can it be abstracted?}}
- → On promotion, establish wikilink and mark relations.evolves

## Applicable scope

{{context detail · when it does not apply}}

## Related experiences

- [[related experience]] (for comparison)

## To track

- [ ] Reuse this lesson next time in a similar scenario?

