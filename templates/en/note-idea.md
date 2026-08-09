<!--
Template: idea note (English · v0.2)
Purpose: Fragmented ideas, thoughts, materials to be digested. Written to 00_inbox/ideas/ by quick-kb-capture.
Note: Inbox raw materials follow DESIGN §6.9 minimal frontmatter (title + captured_at).
      suggested_tags are AI-prefilled hints, optional, decided at ingest.
Source of truth: references/frontmatter-v0.2.md §7 · docs/DESIGN.md §6.9
-->
---
title: {{short title}}                  # required
captured_at: {{YYYY-MM-DDTHH:MM}}      # required · ISO 8601 with time
capture_type: idea                     # idea | web-clip | pdf | meeting | ai-dialog | reading
source:                                # optional · if from a conversation/person/link
  # - url: https://...
  # - person: "{{who said it}}"
suggested_tags:                        # optional · AI-prefilled candidates; promoted to tags at ingest
  - {{domain}}/{{topic}}
---

# {{short title}}

{{Idea/insight/observation · one paragraph is fine, structure not required}}

## Context (optional)

- Trigger: {{when/where you thought of it}}
- Related project/goal: [[{{wikilink}}]]

## Possible Next Steps

- [ ] Worth expanding → call `quick-kb-ingest` to convert to a formal concept/resource
- [ ] Hold for later review
- [ ] Discard (confirmed no value, cleaned by review)
