"""quick-knowledge × SkillOpt benchmark adapter.

Implements the SkillOpt custom-benchmark contract (SplitDataLoader +
EnvAdapter + rollout helper + YAML config) so quick-knowledge's
natural-language SKILL.md files can be behaviorally evaluated.

Reference:
    https://github.com/microsoft/SkillOpt/blob/main/docs/guide/new-benchmark.md

Layout
------
quickkb/
├── dataloader.py        QuickkbDataLoader (SplitDataLoader subclass)
├── rollout.py           run_batch + _rollout_one (uses chat_target)
├── adapter.py           QuickkbAdapter (EnvAdapter subclass)
├── scoring/
│   ├── routing.py       path glob scoring
│   ├── frontmatter.py   required + forbidden field scoring
│   ├── behavior.py      model-reply assertions (polish / dedup / injection)
│   └── flow.py          J-class fixture-based contract scoring
├── skills/
│   └── capture-initial.md   pinned snapshot of skills/quick-kb-capture/SKILL.md
└── fixtures/            J-class pre-state files (capture/ingest/goal/...)
"""

__version__ = "0.1.0"
