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
→ quick-kb-ingest: extracts atomic viewpoints, suggests concept tags + relations, writes to 02_areas/ (concept) or 01_resources/ (resource)

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

**Vault-wide language (v1.10.0)**: set the language at init time — English by default. All skills then use it for templates, AI-generated content, filenames, and reports:

```
Initialize my knowledge base in Chinese   # → Chinese vault (language: zh)
Initialize my knowledge base              # → English vault (language: en, default)
```

- The language declared in your message takes priority over the default; you can also switch later by editing the `language` field in `99_system/config/kb.config.yaml`
- Your raw input is always preserved verbatim — never translated; frontmatter field names/enums stay in English (machine-parsing layer)

---

## Usage · 5-Minute Quickstart

1. **Initialize**: "Initialize my knowledge base" (English vault by default; say it in Chinese for a Chinese vault)
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

- `status` — document lifecycle (10 states, incl. ingested/superseded and other archival/derived states)
- `maturity` — knowledge maturity (6 states: captured → … → teachable)
- `confidence` — verification depth (integer 0-100, unified scale library-wide)
- `value` — value dimensions ({reuse, impact, uniqueness, ks})
- `relations` — typed relations (4 forward keys: supports / contradicts / evolves / supersedes, plus inverse and derivation keys like derived_from / source_of / refines)
- `source` — provenance (object format: type / url / note / capture_type etc., linking back to the original inbox material)
- `context` — applicable context

### Knowledge Score

```
KS = confidence × log2(1 + reuse) × impact
```

---

## Repository Structure

```
quick-knowledge/
├── skills/             # 14 skills + 3 agent skills (17 total)
│   ├── quick-kb-init/            # init (self-contained templates + schema + fingerprint check)
│   ├── quick-kb-capture/         # capture (5 source types + AI polish proposal)
│   ├── quick-kb-ingest/          # ingest (atomic viewpoints + pre-write validation)
│   ├── quick-kb-daily/           # daily log
│   ├── quick-kb-connect/         # links + MOC + canvas
│   ├── quick-kb-query/           # fact QA (strict mandatory citations)
│   ├── quick-kb-review/          # periodic review + health check
│   ├── quick-kb-advisor/         # decision support (3-section)
│   ├── quick-kb-project/         # project lifecycle + Decision Ledger
│   ├── quick-kb-goal/            # goals + learning paths
│   ├── quick-kb-normalize/       # batch normalization (idempotent + rollbackable)
│   ├── quick-kb-archive/         # safe archive (copy + stub)
│   ├── quick-kb-stats/           # health dashboard
│   ├── quick-kb-import/          # external import (Obsidian/Notion/Logseq)
│   ├── quick-kb-manager-agent/   # librarian (9 capabilities)
│   ├── quick-kb-research-agent/  # researcher
│   └── quick-kb-memory-agent/    # long-term memory
├── templates/          # Bilingual templates (14 types × 2)
├── references/         # Field specs, wikilink/scoring/write-validation rules, deviation checks
├── bench/              # Behavior testing (SkillOpt × golden cases)
├── examples/demo-vault/  # Sample vault
└── docs/               # Design docs, dev docs, CHANGELOG
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
| v1.4 | nested-domain + hardening | ✅ Done | Nested domain_taxonomy + full template rollout (12→14) + schema validation |
| v1.5–v1.6 | consistency + conventions | ✅ Done | confidence 0-100 unification · JSON Schema validation · archive copy+stub · wikilink conventions · canvas spec |
| v1.7 | automation & integration | ✅ Done | Agent §0 contracts · polish_mode (3 levels) · near-dup/cycle detection · degradation observability |
| v1.8 | e2e-calibration | ✅ Done | Self-contained init resources (templates + schema + fingerprint) · pre-write validation layer · unified metrics |
| v1.8.1–v1.9.3 | test-calibration series | ✅ Done | 13 rounds of external test-report calibration: schema/vocabulary alignment · degradation threshold table · cold-start ranking · source format unified to object · structure-drift defense |
| v1.10.0 | vault-language | ✅ Done | Vault-wide language convention: init language param upgraded (default en) · drives templates / generated content / slugs / report language · verbatim-user-input exemption |

See [docs/](./docs/).

---

## Behavior Testing (v1.3+)

v0.1–v1.2 CI was purely structural (frontmatter / wikilink / placeholder checks) — **it could not answer "did this SKILL.md edit regress capture behavior?"**. v1.3 introduces [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) as a behavior-testing engine to close that gap:

- Custom benchmark `bench/quickkb/` (dataloader + rollout + adapter + 4 scorers)
- 51 golden cases: 45 point cases × 9 dimensions + 6 J-class end-to-end flow transitions
- Nightly mock-backend workflow, **never blocks PR merge** (non-blocking signal)
- Never auto-deploys — SkillOpt's `best_skill.md` is human-reviewed before any commit
- **Release regression**: capture / flow benches run before every release; results recorded in the "评测/Evaluation" section of each [CHANGELOG](./docs/CHANGELOG.md) entry

Since v1.8 there is also a **test-calibration loop**: external test reports (13+ rounds) are cross-checked claim-by-claim against the repository source of truth; only verified real defects are fixed while false claims are rejected with documented rationale — calibration conclusions, rejection lists, and methodology constraints are captured in the per-version calibration docs under [docs/dev/](./docs/dev/) and the CHANGELOG.

See [`docs/dev/v1.3-skillopt-integration.md`](./docs/dev/v1.3-skillopt-integration.md).

---

## Design Documentation

- [DESIGN.md](./docs/DESIGN.md) — full design (source of truth)
- [SKILLS_SPEC.md](./docs/SKILLS_SPEC.md) — skill specifications
- [AGENTS_SPEC.md](./docs/AGENTS_SPEC.md) — agent specifications (with ranking formula)
- [CHANGELOG.md](./docs/CHANGELOG.md) — version history (with per-release bench results)
- [dev/](./docs/dev/) — per-phase dev docs and calibration docs

---

## Acknowledgements

- [Agent Skills Protocol](https://agentskills.io)
- [Obsidian](https://obsidian.md)
- [Zettelkasten](https://zettelkasten.de)
- [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)

---

## License

[MIT](./LICENSE)
