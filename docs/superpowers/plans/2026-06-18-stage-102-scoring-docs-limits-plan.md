# Stage 102 Scoring Docs Limits Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for scoring limit wording.

**Architecture:** Create one pytest module that reads `docs/scoring.md`,
extracts the `## Limits` section, normalizes whitespace/case, and asserts local
configured-source scoring boundary phrases. Keep this stage docs-test-only and
avoid runtime scoring, dashboard, CLI, schema, dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-102-scoring-docs-limits-design.md`
  records the Stage 102 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-102-scoring-docs-limits-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-102-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-102-plan-review.md` records the local
  plan review.
- Create: `tests/test_scoring_docs.py` contains the standalone docs drift guard.
- Create: `docs/reviews/opencode-stage-102-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-102-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-102-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 102 Plan Review Prompt

Review the Stage 102 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/scoring.md`, scoped only to the
`## Limits` section, so scoring docs remain documented as local configured
source/imported-signal boundaries rather than platform-wide, publication-time,
media-analysis, external-engagement, or market-wide claims.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-102-scoring-docs-limits-design.md`
- `docs/superpowers/plans/2026-06-18-stage-102-scoring-docs-limits-plan.md`
- `docs/scoring.md`

## Planned Test

The implementation will add `tests/test_scoring_docs.py` with one docs-only test
that extracts `## Limits` and asserts:

- `Scores only reflect configured sources and imported local signals.`
- `Candidate signals only reflect configured sources and imported local signals.`
- `Trend deltas only reflect configured sources and imported local signals.`
- `Candidate deltas are limited by configured candidate discovery thresholds.`
- `Counts use collected time, not necessarily publication time.`
- `Dashboard mention tabs show mention counts, while candidate signal views read the latest report JSON.`
- `There is no image/video or external engagement analysis in v0.1.0.`

## Scope Constraints

Allowed changes:

- `tests/test_scoring_docs.py`
- Stage 102 review artifacts

Disallowed changes:

- `docs/scoring.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime scoring, candidate discovery, trend delta, report, dashboard, or CLI
  tests
- first-run, source-pack, entity-pack, scheduling, dashboard, manual-import,
  candidate-discovery, community-signal, or project-brief docs guards

Do not expand this stage into scoring algorithm changes, generated data,
dashboard/report behavior, scheduling, source acquisition, connector behavior,
platform search, social monitoring, compliance/audit/legal review, or runtime
validation.

## Review Questions

1. Does the plan protect a real `docs/scoring.md` local configured-source
   scoring boundary without changing product behavior?
2. Are the planned phrases present in `docs/scoring.md` and scoped narrowly
   enough to `## Limits`?
3. Does the plan avoid overlap with recent docs-boundary stages and runtime
   scoring/trend tests?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-102-plan-review-prompt.md)" > docs/reviews/opencode-stage-102-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-102-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_scoring_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORING_DOC = ROOT / "docs" / "scoring.md"


def _read_scoring_doc() -> str:
    return SCORING_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_scoring_docs_keep_limits_boundary() -> None:
    limits = _section(_read_scoring_doc(), "Limits")
    normalized = _normalized(limits)

    for phrase in (
        "Scores only reflect configured sources and imported local signals.",
        "Candidate signals only reflect configured sources and imported local signals.",
        "Trend deltas only reflect configured sources and imported local signals.",
        "Candidate deltas are limited by configured candidate discovery thresholds.",
        "Counts use collected time, not necessarily publication time.",
        "Dashboard mention tabs show mention counts, while candidate signal views read "
        "the latest report JSON.",
        "There is no image/video or external engagement analysis in v0.1.0.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_scoring_docs.py -q
```

Expected: pass.

- [ ] Run adjacent scoring/trend tests:

```bash
uv --no-config run --frozen pytest tests/test_scoring.py tests/test_candidate_scoring.py tests/test_trends.py tests/test_scoring_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_scoring_docs.py
uv --no-config run --frozen ruff format --check tests/test_scoring_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-102-code-review-prompt.md` with this
      review request:

```markdown
# Stage 102 Code Review Prompt

Review the Stage 102 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 102 adds `tests/test_scoring_docs.py`, a standalone docs drift guard for
the `## Limits` section in `docs/scoring.md`. It asserts that scoring,
candidate signals, and trend deltas remain framed as configured-source and
imported-local-signal views; counts use collected time rather than necessarily
publication time; dashboard/candidate views have their documented data-source
boundary; and v0.1.0 does not include image/video or external engagement
analysis.

## Files To Review

- `tests/test_scoring_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-102-scoring-docs-limits-design.md`
- `docs/superpowers/plans/2026-06-18-stage-102-scoring-docs-limits-plan.md`
- `docs/reviews/opencode-stage-102-plan-review-prompt.md`
- `docs/reviews/opencode-stage-102-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_scoring_docs.py`
- Stage 102 review artifacts

Disallowed changes:

- `docs/scoring.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime scoring, candidate discovery, trend delta, report, dashboard, or CLI
  tests

Do not propose scoring algorithm changes, generated data, dashboard/report
behavior, scheduling, source acquisition, connector behavior, platform search,
social monitoring, compliance/audit/legal review, or runtime validation.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_scoring_docs.py -q
uv --no-config run --frozen pytest tests/test_scoring.py tests/test_candidate_scoring.py tests/test_trends.py tests/test_scoring_docs.py -q
uv --no-config run --frozen ruff check tests/test_scoring_docs.py
uv --no-config run --frozen ruff format --check tests/test_scoring_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 102 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/scoring.md` `## Limits` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   scoring/trend tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-102-code-review-prompt.md)" > docs/reviews/opencode-stage-102-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-102-code-review.md`.
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

- [ ] Stage only Stage 102 files:

```bash
git add \
  docs/reviews/opencode-stage-102-code-review-prompt.md \
  docs/reviews/opencode-stage-102-code-review.md \
  docs/reviews/opencode-stage-102-plan-review-prompt.md \
  docs/reviews/opencode-stage-102-plan-review.md \
  docs/superpowers/plans/2026-06-18-stage-102-scoring-docs-limits-plan.md \
  docs/superpowers/specs/2026-06-18-stage-102-scoring-docs-limits-design.md \
  tests/test_scoring_docs.py
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
git commit -m "Guard scoring docs limits"
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
