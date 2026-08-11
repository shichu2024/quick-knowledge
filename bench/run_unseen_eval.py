#!/usr/bin/env python3
"""bench/run_unseen_eval.py — Generalization probe on unseen cases.

Reads a flat items.json (no train/val/test split) and runs the current
SKILL.md against every case via SkillOpt chat_target. Used to verify
that P0/P1/P2/P3 fixes generalize beyond the held-in val and held-out
test splits.

Usage
-----
    TARGET_BACKEND=claude_chat \\
    OPTIMIZER_BACKEND=claude_chat \\
    TARGET_DEPLOYMENT=glm-5.2 \\
    CLAUDE_CLI_BIN=claude.cmd \\
    CLAUDE_CODE_GIT_BASH_PATH='D:\\Program Files\\Git\\bin\\bash.exe' \\
    python -m bench.run_unseen_eval \\
        --items bench/cases/capture-unseen/items.json

Differs from run_eval.py: bypasses QuickkbDataLoader (no ratio split)
so adding unseen cases here does not perturb the train/val/test
materialization for the main `capture` skill.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from bench.quickkb.dataloader import _normalize_case
from bench.quickkb.rollout import run_batch


_DEFAULT_SKILL_FILE = "skills/quick-kb-capture/SKILL.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run unseen-cases generalization probe.")
    p.add_argument(
        "--items",
        default="bench/cases/capture-unseen/items.json",
        help="Flat items.json (array of cases, no split).",
    )
    p.add_argument(
        "--skill-file",
        default=_DEFAULT_SKILL_FILE,
        help="Path to SKILL.md under test (default: current capture SKILL.md).",
    )
    p.add_argument(
        "--out-dir",
        default="bench/reports",
        help="Where to write report artifacts.",
    )
    p.add_argument(
        "--max-completion-tokens",
        type=int,
        default=2048,
    )
    return p.parse_args()


def load_cases(path: str) -> list[dict]:
    p = Path(path)
    if not p.is_absolute():
        p = _REPO_ROOT / p
    if not p.exists():
        raise FileNotFoundError(f"Items file not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"Expected JSON array in {p}")
    return [_normalize_case(item, "capture") for item in raw]


def load_skill(path: str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = _REPO_ROOT / path
    if not p.exists():
        raise FileNotFoundError(f"Skill file not found: {p}")
    return p.read_text(encoding="utf-8")


def main() -> int:
    args = parse_args()
    items = load_cases(args.items)
    skill_content = load_skill(args.skill_file)

    print(f"[*] items      = {args.items} ({len(items)} cases)")
    print(f"[*] skill_file = {args.skill_file}")
    print(f"[*] running rollouts ...")

    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(args.out_dir) / f"unseen-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    results = run_batch(
        items=items,
        skill_content=skill_content,
        out_root=str(run_dir),
        max_completion_tokens=args.max_completion_tokens,
    )

    by_dim: dict[str, list[dict]] = {}
    for r in results:
        by_dim.setdefault(r["task_type"], []).append(r)

    print()
    print("=" * 60)
    print(f"  UNSEEN REPORT  ·  {len(results)} cases")
    print("=" * 60)
    print(f"{'dimension':<30} {'n':>4} {'hard':>8} {'soft':>8}")
    print("-" * 60)
    total_hard_pass = 0
    total_n = 0
    for dim in sorted(by_dim.keys()):
        rows = by_dim[dim]
        n = len(rows)
        hard_pass = sum(1 for r in rows if r["hard"] >= 1.0)
        soft_mean = sum(r["soft"] for r in rows) / n if n else 0.0
        total_hard_pass += hard_pass
        total_n += n
        print(f"{dim:<30} {n:>4} {hard_pass:>8} {soft_mean:>8.2f}")
    print("-" * 60)
    overall_hard = total_hard_pass / total_n if total_n else 0.0
    overall_soft = sum(r["soft"] for r in results) / len(results) if results else 0.0
    print(f"{'TOTAL':<30} {total_n:>4} {total_hard_pass:>8} {overall_soft:>8.2f}")
    print(f"  hard rate = {overall_hard:.1%}")
    print()
    print(f"[*] artifacts -> {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
