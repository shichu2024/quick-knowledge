<!--
Template: belief (English · v0.3)
Purpose: Personal hypothesis / judgment, not yet fully verified. No domain. Stored in 07_principles/beliefs/.
Source of truth: references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§6.4
-->
---
title: {{hypothesis in one sentence}}
type: belief
created: {{date}}
updated: {{date}}
tags:
  - belief/{{topic}}
status: active
maturity: captured             # belief usually captured / understood; promote to principle or pattern after verification
confidence: 40                 # unverified, lower confidence
relations:
  supports: []                 # supporting evidence
  contradicts: []              # counter-evidence
  evolves: []                  # if verified → principle/pattern
  supersedes: []
context: {{applicable situation}}
value:
  reuse: 0
  impact: 3
  uniqueness: 3
---

# {{hypothesis in one sentence}}

## Statement

{{state your hypothesis clearly · usually contains "I believe / I tend to"}}

## Why I think so

{{intuition source · experience fragments · observed phenomena}}

## Verification

- [ ] {{how to verify this hypothesis · quantifiable}}
- [ ] {{counterexample search: under what conditions it does not hold}}

## Current evidence

### Supporting
- [[experience/pattern/resource]]

### Opposing
- [[experience/pattern/resource]] (if any → establish contradicts)

## Open questions

- [ ] ...

## Promotion path

- Verified & abstractable → promote to [[relevant principle]] or [[relevant pattern]] (maturity → validated/applied)
- Refuted → demote to `maturity: deprecated` + establish contradicts

