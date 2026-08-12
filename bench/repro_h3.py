"""One-off repro: run rollout on a single case by id.

Usage:
    TARGET_BACKEND=claude_chat ... python bench/repro_h3.py H3-edge-prompt-injection
"""
from __future__ import annotations

import datetime
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from bench.quickkb.dataloader import QuickkbDataLoader
from bench.quickkb.rollout import _rollout_one


def main(case_id: str) -> int:
    skill = "capture"
    skill_file = _REPO_ROOT / "skills/quick-kb-capture/SKILL.md"
    skill_content = skill_file.read_text(encoding="utf-8")

    loader = QuickkbDataLoader(
        skill=skill,
        cases_root=str(_REPO_ROOT / "bench/cases"),
        split_ratio="3:1:1",
        split_seed=42,
        limit=0,
    )
    loader.setup({"out_root": str(_REPO_ROOT), "env": f"quickkb_{skill}"})

    # Search all splits for the requested id
    target = None
    for split in ("train", "val", "test"):
        for item in loader.get_split_items(split):
            if str(item.get("id")) == case_id:
                target = item
                break
        if target:
            break
    if not target:
        print(f"[!] case {case_id!r} not found in any split")
        return 1

    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = _REPO_ROOT / "bench/reports" / f"repro-{case_id}-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    pred_dir = run_dir / "predictions"
    pred_dir.mkdir(exist_ok=True)

    result = _rollout_one(
        item=target,
        skill_content=skill_content,
        prediction_dir=pred_dir,
        max_completion_tokens=4096,
    )

    print("=" * 60)
    print(f"  REPRO  ·  case={case_id}  dim={result['task_type']}")
    print("=" * 60)
    print(f"hard = {result['hard']}")
    print(f"soft = {result['soft']:.2f}")
    print(f"path = {result['parsed_path'] or '(none)'}")
    print(f"fm   = {result['parsed_frontmatter']}")
    print()
    print("--- assistant reply (first 1200 chars) ---")
    print(result["predicted_answer"][:1200])
    print()
    print(f"[*] artifacts → {run_dir}")
    return 0 if result["hard"] >= 1.0 else 2


if __name__ == "__main__":
    case_id = sys.argv[1] if len(sys.argv) > 1 else "H3-edge-prompt-injection"
    sys.exit(main(case_id))
