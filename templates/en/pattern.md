<!--
Template: pattern (English · v0.3)
Purpose: Reusable solution pattern abstracted from multiple practices. No domain. Stored in principles/patterns/.
Source of truth: references/frontmatter-v0.3.md · docs/DESIGN.md §6.2/§6.4
-->
---
title: {{pattern name}}
type: pattern
created: {{date}}
updated: {{date}}
tags:
  - pattern/{{topic}}
status: active
maturity: applied              # pattern usually ≥ applied (already applied multiple times)
confidence: 75
relations:
  supports: []                 # experiences supporting this pattern
  contradicts: []              # opposing pattern (anti-pattern or different context)
  evolves: []                  # evolved from earlier pattern
  supersedes: []               # replaces old pattern
context: {{applicable situation: problem type, constraints}}
value:
  reuse: 0                     # pattern usually has higher reuse
  impact: 4
  uniqueness: 3
---

# {{pattern name}}

## Problem

{{what kind of problem this pattern addresses · trigger conditions}}

## Description

{{structured description: roles, process, key decision points}}

## Key steps

1. {{step 1}}
2. {{step 2}}
3. {{step 3}}

## Applicable conditions

- {{condition 1 · must hold}}
- {{condition 2 · nice to have}}

## Anti-patterns (do not do this)

- {{counterexample 1 · leads to ...}}

## Applied cases

- [[project-1]] · {{application detail · outcome}}
- [[project-2]] · {{application detail}}

## Related patterns

- [[related pattern]] (composable / mutually exclusive)
- [[anti-pattern]] (if any → contradicts)

## To abstract further

- [ ] {{is there a more general abstraction layer?}}

