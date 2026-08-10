"""QuickkbDataLoader — loads golden cases from bench/cases/<skill>/.

Each skill has its own items.json (JSON array of case dicts). The loader
also handles J-class flow cases (bench/cases/flow/items.json).

Schema:
    bench/cases/<skill>/items.json   # e.g. capture, flow
    bench/cases/_schema.json         # JSON Schema for self-documentation

SkillOpt's SplitDataLoader base auto-splits train/val/test given a
single items.json (split_mode="ratio" + split_ratio="3:1:1").
"""
from __future__ import annotations

import json
from pathlib import Path

from skillopt.datasets.base import SplitDataLoader


class QuickkbDataLoader(SplitDataLoader):
    """Load golden cases for a quick-knowledge skill.

    Parameters
    ----------
    skill : str
        Skill slug, e.g. ``"capture"`` or ``"flow"``. Maps to
        ``bench/cases/<skill>/items.json``.
    """

    def __init__(
        self,
        skill: str = "capture",
        cases_root: str = "bench/cases",
        **kwargs,
    ) -> None:
        self.skill = skill
        self.cases_root = cases_root
        # Resolve data_path to the skill's items.json; SplitDataLoader.setup()
        # with split_mode="ratio" will auto-materialize train/val/test dirs.
        data_path = str(Path(cases_root) / skill / "items.json")
        super().__init__(
            data_path=data_path,
            split_mode="ratio",
            split_ratio=kwargs.pop("split_ratio", "3:1:1"),
            split_seed=kwargs.pop("split_seed", 42),
            **kwargs,
        )

    def load_split_items(self, split_path: str) -> list[dict]:
        """Load items from one split directory.

        The base class writes ``items.json`` into each split dir during
        ratio materialization. We just read it back as a JSON array and
        normalize each case to ensure required keys exist.
        """
        path = Path(split_path)
        json_files = sorted(path.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"No .json file in {split_path}")
        # Skip split_manifest.json if it's the only JSON (shouldn't happen
        # for materialized splits, but defensive).
        items_file = next(
            (f for f in json_files if f.name != "split_manifest.json"),
            json_files[0],
        )
        with items_file.open(encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            raise ValueError(f"Expected JSON array in {items_file}")
        return [_normalize_case(item, self.skill) for item in raw]


def _normalize_case(raw: dict, skill: str) -> dict:
    """Ensure each case has the minimal required keys.

    Adds defaults for optional fields so rollout / scoring never KeyError.
    """
    item = dict(raw)
    item.setdefault("id", f"unnamed-{abs(hash(json.dumps(raw, sort_keys=True, ensure_ascii=False)))}")
    item.setdefault("dimension", "unknown")
    item.setdefault("source_type", "idea")
    item.setdefault("input", "")
    item.setdefault("user_choice", None)
    item.setdefault("category", skill)
    item.setdefault("references", [])
    item.setdefault("notes", "")

    expected = item.get("expected") or {}
    expected.setdefault("should_trigger_capture", True)
    expected.setdefault("path_glob", "")
    expected.setdefault("frontmatter", {})
    expected.setdefault("frontmatter_forbidden", [])
    expected.setdefault("content_contains", [])
    expected.setdefault("content_excludes", [])
    expected.setdefault("should_trigger_polish", False)
    expected.setdefault("feedback_contains", [])
    expected.setdefault("flow_upstream_file", "")   # J-class
    expected.setdefault("flow_downstream_check", {})  # J-class
    item["expected"] = expected
    return item
