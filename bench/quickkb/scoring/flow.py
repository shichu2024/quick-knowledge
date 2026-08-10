"""Flow scorer — fixture-based contract checks for J-class (end-to-end).

Each J case has:
- ``flow_upstream_file``: path to a fixture file representing the upstream
  skill's output (e.g. capture's note that ingest must consume)
- ``flow_downstream_check``: dict of assertions to run against the downstream
  skill's product

Implementation strategy: MVP loads upstream fixture, asks the downstream
skill to act on it, then asserts the downstream product has the expected
fields. Does NOT run the full 7-stage pipeline (too expensive for MVP);
each transition is verified independently.
"""
from __future__ import annotations

import json
from pathlib import Path


def score(
    downstream_product_fm: dict,
    downstream_product_content: str,
    downstream_check: dict,
) -> tuple[float, float]:
    """Assert the downstream skill's product contains required contract fields.

    Parameters
    ----------
    downstream_product_fm : dict
        Parsed frontmatter of the file the downstream skill wrote.
    downstream_product_content : str
        Body text of the downstream skill's product.
    downstream_check : dict
        Map of field-name → regex (or list of substrings for content).
        Special key ``"_content_contains"`` is a list of required body substrings.

    Returns
    -------
    (hard, soft)
    """
    signals: list[float] = []
    content_lc = (downstream_product_content or "").lower()

    for key, spec in (downstream_check or {}).items():
        if key == "_content_contains":
            for kw in spec:
                signals.append(1.0 if kw.lower() in content_lc else 0.0)
            continue

        # Frontmatter field regex
        actual = downstream_product_fm.get(key)
        if actual is None:
            signals.append(0.0)
            continue
        import re
        try:
            ok = bool(re.match(str(spec), str(actual)))
        except re.error:
            ok = str(actual) == str(spec)
        signals.append(1.0 if ok else 0.0)

    if not signals:
        return (1.0, 1.0)
    hard = 1.0 if all(s >= 1.0 for s in signals) else 0.0
    soft = sum(signals) / len(signals)
    return (hard, soft)


def load_upstream_fixture(fixture_path: str) -> dict:
    """Load a JSON fixture describing the upstream skill's product.

    Fixture schema:
        {
          "vault_state": { "<path>": "<content>" },
          "upstream_note_path": "00_inbox/ideas/xxx.md",
          "upstream_note_fm": { ... }
        }
    """
    p = Path(fixture_path)
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as f:
        return json.load(f)
