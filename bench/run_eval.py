#!/usr/bin/env python3
"""bench/run_eval.py — Standalone SkillOpt-based evaluator for quick-knowledge.

Runs the current SKILL.md (or a candidate) against the golden-case suite,
prints a per-dimension report, and writes ``bench/reports/<run-id>/`` artifacts.

Usage
-----
    # Activate a SkillOpt backend first (see requirements-bench.txt + .env)
    python -m bench.run_eval --skill capture
    python -m bench.run_eval --skill capture --split test
    python -m bench.run_eval --skill flow          # J-class end-to-end
    python -m bench.run_eval --skill capture --skill-file path/to/candidate.md

This script does NOT register into SkillOpt's internal _ENV_REGISTRY;
it consumes SkillOpt as a library (chat_target, SplitDataLoader) directly.
This keeps us insulated from upstream registry changes.

Optional environment (set in .env):
    SKILLOPT_BACKEND      = openai_chat | openai_compatible | claude_chat | ...
    AZURE_OPENAI_*        = ...   (if backend=openai_chat)
    OPENAI_COMPATIBLE_*   = ...   (if backend=openai_compatible)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# Make `bench` importable when invoked as `python -m bench.run_eval`
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from bench.quickkb.dataloader import QuickkbDataLoader
from bench.quickkb.rollout import run_batch


_DEFAULT_SKILL_FILES = {
    "capture": "skills/quick-kb-capture/SKILL.md",
    "flow": "skills/quick-kb-capture/SKILL.md",  # J-class uses capture too for MVP
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Evaluate a quick-knowledge skill on golden cases via SkillOpt."
    )
    p.add_argument(
        "--skill",
        default="capture",
        choices=sorted(_DEFAULT_SKILL_FILES.keys()),
        help="Skill slug to evaluate (default: capture).",
    )
    p.add_argument(
        "--skill-file",
        default=None,
        help="Path to a candidate SKILL.md (default: pinned file under skills/).",
    )
    p.add_argument(
        "--split",
        default="val",
        choices=["train", "val", "test"],
        help="Dataset split to evaluate (default: val).",
    )
    p.add_argument(
        "--cases-root",
        default="bench/cases",
        help="Root directory of cases (default: bench/cases).",
    )
    p.add_argument(
        "--split-ratio",
        default="3:1:1",
        help="train:val:test ratio (default: 3:1:1).",
    )
    p.add_argument(
        "--split-seed",
        type=int,
        default=42,
    )
    p.add_argument(
        "--out-dir",
        default="bench/reports",
        help="Where to write report artifacts (default: bench/reports).",
    )
    p.add_argument(
        "--max-completion-tokens",
        type=int,
        default=4096,
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Cap cases per split (0 = no cap, debug with small N).",
    )
    return p.parse_args()


def load_skill(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")
    return p.read_text(encoding="utf-8")


def main() -> int:
    args = parse_args()
    skill_file = args.skill_file or _DEFAULT_SKILL_FILES[args.skill]
    skill_file_abs = str(_REPO_ROOT / skill_file) if not os.path.isabs(skill_file) else skill_file
    skill_content = load_skill(skill_file_abs)

    # Build dataloader + materialize splits
    loader = QuickkbDataLoader(
        skill=args.skill,
        cases_root=str(_REPO_ROOT / args.cases_root),
        split_ratio=args.split_ratio,
        split_seed=args.split_seed,
        limit=args.limit,
    )
    loader.setup({
        "out_root": str(_REPO_ROOT),
        "env": f"quickkb_{args.skill}",
    })

    items = loader.get_split_items(args.split)
    if not items:
        print(f"[!] split '{args.split}' has 0 items — nothing to evaluate.")
        return 1

    print(f"[*] skill      = {args.skill}")
    print(f"[*] skill_file = {skill_file_abs}")
    print(f"[*] split      = {args.split} ({len(items)} cases)")
    print(f"[*] running rollouts ...")

    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(args.out_dir) / f"{args.skill}-{args.split}-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    results = run_batch(
        items=items,
        skill_content=skill_content,
        out_root=str(run_dir),
        max_completion_tokens=args.max_completion_tokens,
    )

    # Per-dimension report
    by_dim: dict[str, list[dict]] = {}
    for r in results:
        by_dim.setdefault(r["task_type"], []).append(r)

    print()
    print("=" * 60)
    print(f"  REPORT  ·  skill={args.skill}  split={args.split}")
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
    print(f"[*] artifacts → {run_dir}")
    print(f"    - rollouts.json   (per-case raw result)")
    print(f"    - predictions/<id>/conversation.json  (trajectories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
