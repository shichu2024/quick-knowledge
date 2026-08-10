"""Behavior scorer — model-reply assertions that routing/frontmatter can't see.

Used by dimensions B (polish), C (triggers), E (dedup messages),
H (no-trigger / prompt-injection), I (feedback next-step).
"""
from __future__ import annotations


def score(
    model_reply: str,
    expected: dict,
) -> tuple[float, float]:
    """Assert key behavioral signals in the model's reply.

    Parameters
    ----------
    model_reply : str
        The full text the model produced (its "what I did" summary).
    expected : dict
        Subset of the case's ``expected`` block relevant to behavior:
        - ``should_trigger_polish``: bool — polish menu should appear
        - ``should_trigger_capture``: bool — capture should run at all
        - ``feedback_contains``: list[str] — keywords expected in feedback
        - ``content_excludes``: list[str] — forbidden substrings in written content
        - ``content_contains``: list[str] — required substrings in written content
        - ``flow_upstream_file`` / ``flow_downstream_check`` are handled by flow.py

    Returns
    -------
    (hard, soft)
    """
    reply = (model_reply or "").lower()
    signals: list[float] = []

    # Polish trigger assertion
    if "should_trigger_polish" in expected:
        want_polish = bool(expected["should_trigger_polish"])
        # Polish menu heuristic: contains "润色" + "[1]" + "[2]" + "[3]" OR
        # contains "polish" + "1" + "2" + "3"
        polish_markers = (
            ("润色" in reply or "polish" in reply)
            and "[1]" in reply
            and "[2]" in reply
            and "[3]" in reply
        )
        signals.append(1.0 if polish_markers == want_polish else 0.0)

    # Capture trigger assertion (when expected False, model should NOT have written a file)
    if "should_trigger_capture" in expected and not expected["should_trigger_capture"]:
        capture_markers = (
            "已采集" in reply
            or "captured" in reply
            or "00_inbox" in reply
            or "quick-kb-capture" in reply
        )
        signals.append(0.0 if capture_markers else 1.0)

    # Feedback keyword assertion
    for kw in expected.get("feedback_contains", []):
        signals.append(1.0 if kw.lower() in reply else 0.0)

    # Content excludes (check in reply too — model often echoes content)
    for kw in expected.get("content_excludes", []):
        signals.append(0.0 if kw.lower() in reply else 1.0)

    # Content contains (loose check in reply)
    for kw in expected.get("content_contains", []):
        signals.append(1.0 if kw.lower() in reply else 0.0)

    if not signals:
        return (1.0, 1.0)
    hard = 1.0 if all(s >= 1.0 for s in signals) else 0.0
    soft = sum(signals) / len(signals)
    return (hard, soft)
