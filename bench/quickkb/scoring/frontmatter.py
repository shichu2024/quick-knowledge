"""Frontmatter scorer — checks required fields present + forbidden absent.

Used by dimension F (frontmatter constraints) and partially A / B.
"""
from __future__ import annotations

import re


def score(
    actual_fm: dict,
    required_fields: dict | None = None,
    forbidden_fields: list[str] | None = None,
) -> tuple[float, float]:
    """Score frontmatter against required + forbidden specs.

    Parameters
    ----------
    actual_fm : dict
        Parsed frontmatter from the file the skill wrote.
    required_fields : dict
        Map of field-name → regex string. Each field must exist and match.
        E.g. ``{"capture_type": "^idea$", "title": ".*cache.*"}``.
    forbidden_fields : list[str]
        Field names that must NOT appear. Used to verify capture does not
        leak ingest-stage fields (maturity / status / relations / ...).

    Returns
    -------
    (hard, soft)
        hard = 1.0 iff all required present-and-matching AND no forbidden present
        soft = mean over (required matches) ∪ (forbidden absences)
    """
    required_fields = required_fields or {}
    forbidden_fields = forbidden_fields or []

    signals: list[float] = []

    # Required: present + regex match
    for name, pattern in required_fields.items():
        actual_value = actual_fm.get(name)
        if actual_value is None:
            signals.append(0.0)
            continue
        try:
            ok = bool(re.match(pattern, str(actual_value)))
        except re.error:
            ok = str(actual_value) == str(pattern)
        signals.append(1.0 if ok else 0.0)

    # Forbidden: absent
    for name in forbidden_fields:
        signals.append(1.0 if name not in actual_fm else 0.0)

    if not signals:
        return (1.0, 1.0)
    hard = 1.0 if all(s >= 1.0 for s in signals) else 0.0
    soft = sum(signals) / len(signals)
    return (hard, soft)


def parse_frontmatter_text(text: str) -> dict:
    """Parse a YAML frontmatter block from raw markdown text.

    Returns empty dict if no frontmatter found. Minimal YAML parser
    (handles flat key: value pairs only; nested via indent is captured
    as raw string under the parent key).
    """
    if not text:
        return {}
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return {}
    lines = stripped.splitlines()
    if len(lines) < 2:
        return {}
    # Find closing ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}
    fm_lines = lines[1:end_idx]
    out: dict = {}
    current_key: str | None = None
    current_list: list | None = None
    for line in fm_lines:
        if not line.strip():
            continue
        # List item under current key
        if line.lstrip().startswith("- ") and current_key is not None:
            value = line.lstrip()[2:].strip()
            if current_list is None:
                current_list = []
                out[current_key] = current_list
            current_list.append(_coerce(value))
            continue
        # key: value
        if ":" in line and not line.startswith(" "):
            # Close previous list
            current_key = None
            current_list = None
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Might be nested; capture as empty dict placeholder
                out[key] = {}
                current_key = key
                current_list = None
            else:
                out[key] = _coerce(value)
                current_key = key
                current_list = None
        elif line.startswith(" ") and current_key is not None:
            # Nested scalar (e.g. source.url: ...) → flatten with dot
            sub_key, _, sub_val = line.strip().partition(":")
            if isinstance(out.get(current_key), dict):
                out[current_key][sub_key.strip()] = _coerce(sub_val.strip())
    return out


def _coerce(value: str):
    """Coerce a YAML scalar string into Python type."""
    if not value:
        return ""
    if value.lower() in ("true", "yes"):
        return True
    if value.lower() in ("false", "no"):
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        # Inline list
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [s.strip().strip('"') for s in inner.split(",")]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
