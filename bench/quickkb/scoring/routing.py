"""Path routing scorer — was the file written to the right directory?

Used by dimension A (source-type routing) and partially D / E.
"""
from __future__ import annotations

import fnmatch


def score(actual_path: str, expected_glob: str) -> tuple[float, float]:
    """Compare actual written path against expected glob.

    Parameters
    ----------
    actual_path : str
        Path the skill actually wrote, relative to vault root
        (e.g. ``"00_inbox/ideas/20260810-1015-cache-bug.md"``).
        Empty string means "no file was written".
    expected_glob : str
        Expected path glob (e.g. ``"00_inbox/ideas/*.md"``).
        Empty string means "no file expected" (de-dup / no-trigger cases).

    Returns
    -------
    (hard, soft) : tuple[float, float]
        - Both empty → (1.0, 1.0) — correctly did nothing
        - Both match → (1.0, 1.0)
        - Mismatch → (0.0, partial credit based on directory hit)
    """
    actual = (actual_path or "").strip()
    expected = (expected_glob or "").strip()

    # Case: no file expected AND no file written → correct
    if not expected and not actual:
        return (1.0, 1.0)

    # Case: file expected but nothing written → fail
    if expected and not actual:
        return (0.0, 0.0)

    # Case: no file expected but file written → fail (false positive)
    if not expected and actual:
        return (0.0, 0.0)

    # Both non-empty: glob match
    if fnmatch.fnmatch(actual, expected):
        return (1.0, 1.0)

    # Partial credit: did the skill at least hit the right top-level dir?
    # E.g. wrote to 00_inbox/meetings/ when expected 00_inbox/ideas/
    actual_dir = "/".join(actual.split("/")[:2])
    expected_dir = "/".join(expected.split("/")[:2])
    if actual_dir == expected_dir and actual_dir:
        return (0.0, 0.5)
    return (0.0, 0.1)
