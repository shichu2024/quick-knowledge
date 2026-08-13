# quick-knowledge

> Personal Knowledge Base × AI Skill Framework — distill fragmented information into reusable personal assets with one set of skills.

[中文](./README.md) · [日本語](./README_JA.md) · [한국어](./README_KO.md) · [Español](./README_ES.md)

---

## What It Is

`quick-knowledge` is a set of knowledge base skills based on the [Agent Skills protocol](https://agentskills.io). In any compatible runtime (Claude Code / Codex / Cursor / OpenCode, etc.), complete **Capture → Ingest → Connect → Review** with a single sentence.

It solves three things:

| Pain Point | quick-knowledge's Approach |
|------------|----------------------------|
| **Rot** — notes pile up but never reviewed | Mandatory Review loop + confidence decay |
| **Islands** — notes can't be found, not interlinked | Connect loop + bidirectional links + MOC |
| **Friction** — categorizing, naming, templating exhausts users | No categorization at capture stage; AI handles Normalize |

---

## Example Session

```
You: "Grab this article https://example.com/rag-best-practices"
→ quick-kb-capture: HTML → Markdown, writes to 00_inbox/

You: "Ingest this one"
→ quick-kb-ingest: extracts atomic viewpoints, suggests concept tags + relations

You: "What do my notes say about RAG?"
→ quick-kb-query: answers from library notes, every claim cited with [[wikilink]]

You: "I'm designing a plugin system, how should I do it?"
→ quick-kb-advisor: recalls your historical experience/principles, gives 3-section advice

You: "Weekly review"
→ quick-kb-review: scans orphan notes, confidence decay, low-reuse high-occupancy list
```

---

## Installation

### Option 1 · Universal one-liner (Recommended, all runtimes)

```bash
npx skills add shichu2024/quick-knowledge
```

### Option 2 · Claude Code marketplace

Inside Claude Code:

```
/plugin marketplace add shichu2024/quick-knowledge
/plugin install quick-knowledge
```

### Option 3 · Manual Install (by runtime)

| Runtime | Install Path |
|---------|--------------|
| Claude Code | `~/.claude/skills/quick-knowledge/` |
| Codex CLI | `~/.codex/skills/quick-knowledge/` |
| Cursor | `~/.cursor/skills/quick-knowledge/` |
| OpenCode | `~/.opencode/skills/quick-knowledge/` |

Clone the repo and copy `skills/` into the corresponding directory (agents are bundled inside skills as `quick-kb-{manager,memory,research}-agent`).

### Initialize Vault

After installing, in any empty directory say:

```
Initialize my knowledge base
```

The skill generates the full directory skeleton + system templates + `kb.config.yaml` in the current directory. The vault location is entirely your choice, decoupled from the skill install path.

---

## Usage · 5-Minute Quickstart

1. **Initialize**: "Initialize my knowledge base"
2. **First capture**: "Grab https://example.com/article"
3. **First ingest**: "Ingest this inbox note"
4. **First query**: "What do my notes say about X?"
5. **First advisor** (v0.3+): "I want to do X, how?"

See [docs/quick-start.md](./docs/quick-start.md).

---

## How It Works

### Six Closed Loops

```
Capture   ──▶  Ingest   ──▶  Normalize  ──▶  Connect  ──▶  Query    ──▶  Review
                                                                      │
                                                                      ▼
                                                                   back to Capture
```

### Three Agents (non-overlapping input domains)

| Agent | Role | Input Domain |
|-------|------|--------------|
| **quick-kb-manager-agent** | Librarian · structure | Library structure (relations, orphans, dead links) |
| **quick-kb-research-agent** | Researcher · external | External materials (URL/PDF/long-form) |
| **quick-kb-memory-agent** | Long-term memory · core differentiator | Library cognitive assets (experience/pattern/principle/belief) |

### Frontmatter Orthogonal Fields (V2)

- `status` — document lifecycle (6 states)
- `maturity` — knowledge maturity (6 states)
- `confidence` — verification depth (0-100)
- `value` — value dimensions ({reuse, impact, uniqueness})
- `relations` — typed relations (supports / contradicts / evolves / supersedes)
- `context` — applicable context

### Knowledge Score

```
KS = confidence × log2(1 + reuse) × impact
```

---

## Repository Structure

```
quick-knowledge/
├── skills/             # 11 skills (v0.1-v0.4)
├── agents/             # 3 agents
├── templates/          # Bilingual templates (zh/en)
├── references/         # Field specs, deviation checks, config schema
├── examples/demo-vault/  # Sample vault
└── docs/               # Design docs, dev docs
```

---

## Roadmap

| Phase | Codename | Status | Highlights |
|-------|----------|--------|------------|
| v0.1 | mvp | ✅ Done | init/capture/ingest/daily + zh templates |
| v0.2 | loops | ✅ Done | connect/query/review + manager/quick-kb-research-agent + en templates |
| v0.3 | assistant | ✅ Done | quick-kb-memory-agent + advisor/project/goal + cognitive asset templates |
| v0.4 | extensions | ✅ Done | normalize/archive/stats/import + kb.config + multilingual README |
| v1.0 | release | ✅ Done | CONTRIBUTING/COMMUNITY/LICENSE + CI + demo-vault release |
| v1.1 | flow-restructure | ✅ Done | Top-level `NN_` prefix + absolute-path hard ban (⚠️ BREAKING) |
| v1.2 | ai-polish | ✅ Done | AI polish proposal for user-typed capture / daily entries (3-way choice) |
| v1.3 | skillopt-integration | ✅ Done | Behavior testing + skill-text optimization (SkillOpt × 51 golden cases × nightly mock workflow) |

See [docs/](./docs/).

---

## Behavior Testing (v1.3+)

v0.1–v1.2 CI was purely structural (frontmatter / wikilink / placeholder checks) — **it could not answer "did this SKILL.md edit regress capture behavior?"**. v1.3 introduces [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) as a behavior-testing engine to close that gap:

- Custom benchmark `bench/quickkb/` (dataloader + rollout + adapter + 4 scorers)
- 51 golden cases: 45 point cases × 9 dimensions + 6 J-class end-to-end flow transitions
- Nightly mock-backend workflow, **never blocks PR merge** (non-blocking signal)
- Never auto-deploys — SkillOpt's `best_skill.md` is human-reviewed before any commit

See [`docs/dev/v1.3-skillopt-integration.md`](./docs/dev/v1.3-skillopt-integration.md).

---

## Design Documentation

- [DESIGN.md](./docs/DESIGN.md) — full design (source of truth)
- [SKILLS_SPEC.md](./docs/SKILLS_SPEC.md) — skill specifications
- [AGENTS_SPEC.md](./docs/AGENTS_SPEC.md) — agent specifications (with ranking formula)
- [dev/](./docs/dev/) — per-phase dev docs

---

## Acknowledgements

- [Agent Skills Protocol](https://agentskills.io)
- [Obsidian](https://obsidian.md)
- [Zettelkasten](https://zettelkasten.de)
- [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)

---

## License

To be finalized at v1.0 release (proposed: MIT or Apache 2.0).
