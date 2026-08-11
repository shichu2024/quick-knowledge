#!/usr/bin/env python3
"""bench/harness/replay-test.py — Deterministic regression test for harness scorers.

Replays frozen model replies (bench/harness/replay-fixtures/*.json) through
the scorer pipeline, asserting each bug still reproduces (or, after a fix,
no longer reproduces).

Two modes:
    --mode=bug       # assert bug PRESENT (documents the broken baseline)
    --mode=fix       # assert bug FIXED   (run after P0 patches land)

No LLM calls. No env vars. Deterministic.

Usage:
    python bench/harness/replay-test.py
    python bench/harness/replay-test.py --mode=fix
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Force UTF-8 stdout/stderr — Windows cp936 default breaks ✓ chars in messages
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench.quickkb.rollout import _extract_path, _extract_frontmatter, _format_user_message
from bench.quickkb.scoring.frontmatter import score as fm_score
from bench.quickkb.scoring.routing import score as r_score
from bench.quickkb.scoring.behavior import score as b_score

FIXTURES = REPO_ROOT / 'bench' / 'harness' / 'replay-fixtures'


def _load_cases() -> dict[str, dict]:
    cases = {}
    p = REPO_ROOT / 'bench' / 'cases' / 'capture' / 'items.json'
    for c in json.loads(p.read_text(encoding='utf-8')):
        cases[c['id']] = c
    return cases


def run(mode: str) -> int:
    cases = _load_cases()
    failures: list[str] = []

    print(f'=== replay-test (mode={mode}) ===')
    print()

    # ── P0-1: frontmatter 双重 --- 包裹 ─────────────────────────────
    print('[P0-1] frontmatter double-dash wrap (rollout.py:222)')
    fm_reply = '```yaml\n---\ntitle: test\ncapture_type: idea\n---\n```'
    fm = _extract_frontmatter(fm_reply)
    if mode == 'bug':
        if fm == {}:
            print('  BUG present: parsed_frontmatter = {} ✓')
        else:
            failures.append('P0-1 bug mode: expected empty dict (bug should still reproduce)')
    else:  # fix
        if fm.get('capture_type') == 'idea' and fm.get('title') == 'test':
            print(f'  FIXED: parsed_frontmatter = {fm} ✓')
        else:
            failures.append(f'P0-1 fix mode: parser still broken (got {fm})')
    print()

    # ── P0-2: polish case 单轮默认 [2] ──────────────────────────────
    print('[P0-2] polish-menu auto-default in single-turn eval')
    # Build a synthetic case that should_trigger_polish but has no user_choice
    polish_case = {
        'id': 'synthetic-polish-no-choice',
        'input': '记一下 cache 方案',
        'user_choice': None,
        'expected': {'should_trigger_polish': True, 'path_glob': '00_inbox/ideas/*.md'},
    }
    msg = _format_user_message(polish_case)
    if mode == 'bug':
        if '[simulated-user-choice]' not in msg:
            print(f'  BUG present: no auto-injection; msg={msg!r} ✓')
        else:
            failures.append('P0-2 bug mode: auto-injection should not exist yet')
    else:  # fix
        if '[simulated-user-choice] 2' in msg:
            print(f'  FIXED: auto-injected [2] default ✓')
            print(f'    msg = {msg!r}')
        else:
            failures.append(f'P0-2 fix mode: no auto-default [2] (got {msg!r})')
    print()

    # ── GLM-S1: SKILL.md 加 yaml 格式约束 ───────────────────────────
    print('[GLM-S1] SKILL.md explicit yaml output format spec')
    skill = (REPO_ROOT / 'skills' / 'quick-kb-capture' / 'SKILL.md').read_text(encoding='utf-8')
    has_yaml_directive = (
        '```yaml' in skill
        and ('机器解析' in skill or 'machine' in skill.lower() or '强约束' in skill)
    )
    if mode == 'bug':
        # Original SKILL.md only had yaml inside frontmatter template, no
        # explicit "output must be yaml-parseable" directive
        if not has_yaml_directive or '输出格式（强约束）' not in skill:
            print('  BUG present: SKILL.md lacks explicit yaml output directive ✓')
        else:
            failures.append('GLM-S1 bug mode: directive already exists')
    else:  # fix
        if '输出格式（强约束）' in skill and '机器解析' in skill:
            print('  FIXED: SKILL.md §6 has yaml output directive ✓')
        else:
            failures.append('GLM-S1 fix mode: directive missing')
    print()

    # ── F4: 模型输出纯文本 frontmatter (NOT fixed by P0; SKILL fix only) ──
    print('[F4] plain-text frontmatter (only fixed when SKILL.md update propagates)')
    f4_reply = (
        '已采集 web-clip：\n'
        '路径：00_inbox/clips/20260815-1430-example-article.md\n'
        '标题：Example Article\n'
        '候选标签：tech/example\n'
    )
    path = _extract_path(f4_reply)
    fm = _extract_frontmatter(f4_reply)
    case = cases['F4-fm-source-url-no-absolute']
    h_r, _ = r_score(path, case['expected']['path_glob'])
    h_f, _ = fm_score(fm, case['expected']['frontmatter'], [])
    print(f'  parsed_path = {path!r}  routing hard={h_r}')
    print(f'  parsed_frontmatter = {fm!r}  frontmatter hard={h_f}')
    # This remains a model-format issue — harness can't fix it without SKILL.md
    # We don't fail in either mode, just document
    print()

    # ── H3: prompt-injection over-defense (cross-model, NOT fixed by P0) ──
    print('[H3] prompt-injection over-defense (cross-model signal; needs SKILL §安全约束 update)')
    fx_path = FIXTURES / 'H3-edge-prompt-injection.json'
    if fx_path.exists():
        fx = json.loads(fx_path.read_text(encoding='utf-8'))
        path = _extract_path(fx['assistant'])
        print(f'  GLM 5.2 reply excerpt: {fx["assistant"][:80]}...')
        print(f'  parsed_path = {path!r}  (case expects 00_inbox/ideas/*.md)')
        if path == '':
            print('  SIGNAL confirmed: model refused to capture (over-defensive)')
        else:
            failures.append('H3: expected empty path (refusal)')
    else:
        print('  SKIP: fixture missing')
    print()

    # ── A6.x: absolute-path case design error (NOT fixed by P0; needs case edit) ──
    print('[A6.x] absolute-path case design error (needs case edit; P1 work)')
    case = cases['A6.1-pdf-file']
    print(f'  case input: {case["input"]!r}')
    print(f'  case expected.should_trigger_capture = {case["expected"]["should_trigger_capture"]}')
    print(f'  SKILL §路径约束 prohibits absolute paths')
    print('  → CASE ERROR documented; fix is to edit case, not harness')
    print()

    # ── Summary ─────────────────────────────────────────────────────
    print('=' * 60)
    if failures:
        print(f'FAIL ({len(failures)} issue):')
        for f in failures:
            print(f'  - {f}')
        return 1
    print(f'PASS (mode={mode}) — all P0 assertions verified')
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['bug', 'fix'], default='bug',
                   help='bug = assert bug present; fix = assert bug fixed')
    return run(p.parse_args().mode)


if __name__ == '__main__':
    sys.exit(main())
