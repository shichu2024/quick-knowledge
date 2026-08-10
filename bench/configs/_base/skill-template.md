<!-- bench/configs/_base/skill-template.md -->
<!--
  Baseline SKILL.md template used by SkillOpt mock rollouts when the real
  skills/quick-kb-capture/SKILL.md is not yet wired into the harness.

  This is a deliberately MINIMAL spec: just enough to produce valid (if
  low-scoring) output so the eval pipeline can be smoke-tested end-to-end
  without depending on production SKILL.md.

  The pinned production baseline for optimization diffs lives at:
    bench/quickkb/skills/capture-initial.md
-->

# quick-kb-capture (baseline template)

Capture user input into the quick-knowledge vault.

## Triggers
- 记一下 / 记录 / save this / capture this

## Behavior
1. Detect source type from input (idea / meeting / ai-dialog / reading / web-clip / pdf).
2. Write a new markdown file to the matching inbox directory:
   - idea → `00_inbox/ideas/YYYYMMDD-HHMM-<slug>.md`
   - meeting → `00_inbox/meetings/...`
   - ai-dialog → `00_inbox/ai-dialogs/...`
   - reading → `00_inbox/reading-notes/...`
   - web-clip → `00_inbox/clips/...`
3. frontmatter must include: `title`, `captured_at`, `capture_type`.
4. Reply with a one-line confirmation + suggest next step `quick-kb-ingest`.
