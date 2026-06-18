# Stage 105 Trend Deltas What Is Compared Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for trend-delta comparison wording.

**Architecture:** Create one pytest module that reads `docs/trend-deltas.md`,
extracts the `## What Is Compared` section, normalizes whitespace/case, and
asserts local observed comparison-boundary phrases. Keep this stage
docs-test-only and avoid runtime, scoring, candidate discovery, dashboard,
source acquisition, connector, social/platform scraping, compliance, dependency,
and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-105-trend-deltas-what-compared-docs-design.md`
  records the Stage 105 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-105-trend-deltas-what-compared-docs-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-105-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-105-plan-review.md` records the local
  plan review.
- Create: `tests/test_trend_deltas_docs.py` contains the standalone docs drift
  guard.
- Create: `docs/reviews/opencode-stage-105-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-105-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-105-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 105 Plan Review Prompt

Review the Stage 105 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/trend-deltas.md`, scoped only to the
`## What Is Compared` section, so trend-delta comparison guidance remains
explicit about local heat scoring reuse, candidate discovery snapshot reuse,
configured candidate-discovery thresholds, current-window mention fields,
separate internal baseline-window fields, and local observed review statuses
rather than market-wide rankings.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-105-trend-deltas-what-compared-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-105-trend-deltas-what-compared-docs-plan.md`
- `docs/trend-deltas.md`

## Planned Test

The implementation will add `tests/test_trend_deltas_docs.py` with one
docs-only test that extracts `## What Is Compared` and asserts:

- `Entity deltas reuse the same local heat scoring used by reports.`
- `Candidate deltas reuse candidate discovery snapshots.`
- `configured `candidate_discovery` settings`
- `not a complete raw phrase inventory.`
- `` `current_mentions` is the current comparison snapshot's current-window mention count. ``
- `` `baseline_mentions` is the baseline comparison snapshot's current-window mention count. ``
- `` Scoring's internal baseline-window counts are exposed only as `current_internal_baseline_mentions` and `baseline_internal_baseline_mentions`. ``
- `` Existing signals are labeled `rising` or `cooling` only when score and mention movement agree. ``
- `` Mixed-direction movement is `stable`. ``
- `These statuses are local observed signals for review, not market-wide rankings.`

## Scope Constraints

Allowed changes:

- `tests/test_trend_deltas_docs.py`
- Stage 105 review artifacts

Disallowed changes:

- `docs/trend-deltas.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- scoring, candidate discovery, heat movers, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime scoring checks, source collection,
platform search, social monitoring, market rankings, dashboard logic, report
logic, schema migrations, connector behavior, or compliance features.

## Review Questions

1. Does the plan protect a real `docs/trend-deltas.md` comparison boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/trend-deltas.md` and scoped narrowly
   enough to `## What Is Compared`?
3. Does the plan avoid overlap with CLI usage examples, manual signals,
   dashboard behavior, scoring implementation, and candidate discovery logic?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-105-plan-review-prompt.md)" > docs/reviews/opencode-stage-105-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-105-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_trend_deltas_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREND_DELTAS_DOC = ROOT / "docs" / "trend-deltas.md"


def _read_trend_deltas_doc() -> str:
    return TREND_DELTAS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_trend_deltas_docs_keep_what_is_compared_boundary() -> None:
    what_is_compared = _section(_read_trend_deltas_doc(), "What Is Compared")
    normalized = _normalized(what_is_compared)

    for phrase in (
        "Entity deltas reuse the same local heat scoring used by reports.",
        "Candidate deltas reuse candidate discovery snapshots.",
        "configured `candidate_discovery` settings",
        "not a complete raw phrase inventory.",
        "`current_mentions` is the current comparison snapshot's current-window "
        "mention count.",
        "`baseline_mentions` is the baseline comparison snapshot's current-window "
        "mention count.",
        "Scoring's internal baseline-window counts are exposed only as "
        "`current_internal_baseline_mentions` and "
        "`baseline_internal_baseline_mentions`.",
        "Existing signals are labeled `rising` or `cooling` only when score and "
        "mention movement agree.",
        "Mixed-direction movement is `stable`.",
        "These statuses are local observed signals for review, not market-wide "
        "rankings.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_trend_deltas_docs.py -q
```

Expected: pass.

- [ ] Run adjacent trend-delta docs reference tests:

```bash
uv --no-config run --frozen pytest tests/test_trend_deltas_docs.py tests/test_cli_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_trend_deltas_docs.py
uv --no-config run --frozen ruff format --check tests/test_trend_deltas_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-105-code-review-prompt.md` with this
      review request:

```markdown
# Stage 105 Code Review Prompt

Review the Stage 105 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 105 adds `tests/test_trend_deltas_docs.py`, a standalone docs drift guard
for the `## What Is Compared` section in `docs/trend-deltas.md`. It asserts that
trend-delta comparison guidance keeps explicit wording about entity deltas
reusing local heat scoring, candidate deltas reusing candidate discovery
snapshots and configured thresholds, mention fields comparing current-window
counts across snapshots, internal baseline-window counts remaining separate,
and statuses being local observed review signals rather than market-wide
rankings.

## Files To Review

- `tests/test_trend_deltas_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-105-trend-deltas-what-compared-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-105-trend-deltas-what-compared-docs-plan.md`
- `docs/reviews/opencode-stage-105-plan-review-prompt.md`
- `docs/reviews/opencode-stage-105-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_trend_deltas_docs.py`
- Stage 105 review artifacts

Disallowed changes:

- `docs/trend-deltas.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- scoring, candidate discovery, heat movers, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_trend_deltas_docs.py -q
uv --no-config run --frozen pytest tests/test_trend_deltas_docs.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_trend_deltas_docs.py
uv --no-config run --frozen ruff format --check tests/test_trend_deltas_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 105 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/trend-deltas.md` `## What Is Compared` section?
3. Is the new standalone test independent from CLI usage, manual signal,
   dashboard, scoring implementation, and candidate discovery runtime behavior?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-105-code-review-prompt.md)" > docs/reviews/opencode-stage-105-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-105-code-review.md`.
- [ ] Fix any Critical or Important findings before Task 4.

## Task 4: Full Verification, Commit, Push

- [ ] Run full verification:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] Stage only Stage 105 files:

```bash
git add \
  docs/reviews/opencode-stage-105-code-review-prompt.md \
  docs/reviews/opencode-stage-105-code-review.md \
  docs/reviews/opencode-stage-105-plan-review-prompt.md \
  docs/reviews/opencode-stage-105-plan-review.md \
  docs/superpowers/plans/2026-06-18-stage-105-trend-deltas-what-compared-docs-plan.md \
  docs/superpowers/specs/2026-06-18-stage-105-trend-deltas-what-compared-docs-design.md \
  tests/test_trend_deltas_docs.py
```

- [ ] Run staged checks:

```bash
if git diff --cached --name-only | rg -x 'uv.lock'; then exit 1; fi
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit:

```bash
git commit -m "Guard trend delta comparison docs"
```

- [ ] Push using a temporary git extraheader only; do not persist credentials in
      remote URLs or git config.
- [ ] Verify `git config --get-all http.https://github.com/.extraheader || true`
      is empty and `git remote -v` contains no token.
- [ ] Verify the GitHub Actions run for the pushed commit completes with
      `success`.

## Task 5: Handoff Summary

- [ ] Write a concise Handoff Summary with:
  - repo status
  - commit SHA and CI URL
  - verified commands
  - uncommitted files
  - next step candidates
