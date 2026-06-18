# Stage 101 First Run Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for the first-run local sample
boundary.

**Architecture:** Create one pytest module that reads `docs/first-run.md`,
extracts the `## Boundary` section, normalizes whitespace/case, and asserts
first-run local-sample boundary phrases. Keep this stage docs-test-only and
avoid runtime first-run smoke, CLI, schema, dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-101-first-run-docs-boundary-design.md`
  records the Stage 101 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-101-first-run-docs-boundary-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-101-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-101-plan-review.md` records the local
  plan review.
- Create: `tests/test_first_run_docs.py` contains the standalone docs drift
  guard.
- Create: `docs/reviews/opencode-stage-101-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-101-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-101-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 101 Plan Review Prompt

Review the Stage 101 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/first-run.md`, scoped only to the
`## Boundary` section, so first-run docs remain documented as deterministic
local sample checks rather than live collection, platform automation, external
services, demand proof, platform coverage, or source ranking.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-101-first-run-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-101-first-run-docs-boundary-plan.md`
- `docs/first-run.md`

## Planned Test

The implementation will add `tests/test_first_run_docs.py` with one docs-only
test that extracts `## Boundary` and asserts:

- `first-run sample does not run live collection`
- `` automated smoke does not run `collect`, `run`, or `dashboard` ``
- `` should not create files under repo `data/` or `reports/` ``
- `does not perform browser automation, account login, cookies/sessions`
- `source/platform connectors, scraping, platform automation, monitoring`
- `scheduling, or external services`
- `candidate and trend outputs are local sample content checks from the checked-in example`
- `not proof of demand`
- `not platform coverage`
- `not source ranking`

## Scope Constraints

Allowed changes:

- `tests/test_first_run_docs.py`
- Stage 101 review artifacts

Disallowed changes:

- `docs/first-run.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime first-run smoke tests
- data-retention, dashboard, scheduling, architecture/source-boundary,
  source-pack, entity-pack, candidate-discovery, manual import, scoring, or
  imported-candidate behavior

Do not expand this stage into first-run smoke command changes, generated sample
data, dashboard/report behavior, scheduling, source acquisition, connector
behavior, platform search, social monitoring, compliance/audit/legal review, or
runtime validation.

## Review Questions

1. Does the plan protect a real `docs/first-run.md` local sample boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/first-run.md` and scoped narrowly
   enough to `## Boundary`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially
   dashboard, scheduling, candidate discovery, source-pack, and scoring
   boundaries?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-101-plan-review-prompt.md)" > docs/reviews/opencode-stage-101-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-101-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_first_run_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST_RUN_DOC = ROOT / "docs" / "first-run.md"


def _read_first_run_doc() -> str:
    return FIRST_RUN_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_first_run_docs_keep_local_sample_boundary() -> None:
    boundary = _section(_read_first_run_doc(), "Boundary")
    normalized = _normalized(boundary)

    for phrase in (
        "first-run sample does not run live collection",
        "automated smoke does not run `collect`, `run`, or `dashboard`",
        "should not create files under repo `data/` or `reports/`",
        "does not perform browser automation, account login, cookies/sessions",
        "source/platform connectors, scraping, platform automation, monitoring",
        "scheduling, or external services",
        "candidate and trend outputs are local sample content checks "
        "from the checked-in example",
        "not proof of demand",
        "not platform coverage",
        "not source ranking",
    ):
        assert phrase in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_first_run_docs.py -q
```

Expected: pass.

- [ ] Run adjacent first-run tests:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_first_run_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_first_run_docs.py
uv --no-config run --frozen ruff format --check tests/test_first_run_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-101-code-review-prompt.md` with this
      review request:

```markdown
# Stage 101 Code Review Prompt

Review the Stage 101 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 101 adds `tests/test_first_run_docs.py`, a standalone docs drift guard for
the `## Boundary` section in `docs/first-run.md`. It asserts that first-run
docs keep the sample framed as local, deterministic content checks that do not
run live collection, `collect`, `run`, or `dashboard`; do not create repo
`data/` or `reports/` files; do not perform browser/account/platform automation
or external services; and do not claim demand proof, platform coverage, or
source ranking.

## Files To Review

- `tests/test_first_run_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-101-first-run-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-101-first-run-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-101-plan-review-prompt.md`
- `docs/reviews/opencode-stage-101-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_first_run_docs.py`
- Stage 101 review artifacts

Disallowed changes:

- `docs/first-run.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime first-run smoke tests
- data-retention, dashboard, scheduling, architecture/source-boundary,
  source-pack, entity-pack, candidate-discovery, manual import, scoring, or
  imported-candidate behavior

Do not propose first-run smoke command changes, generated sample data,
dashboard/report behavior, scheduling, source acquisition, connector behavior,
platform search, social monitoring, compliance/audit/legal review, or runtime
validation.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_first_run_docs.py -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_first_run_docs.py -q
uv --no-config run --frozen ruff check tests/test_first_run_docs.py
uv --no-config run --frozen ruff format --check tests/test_first_run_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 101 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/first-run.md` `## Boundary` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   first-run smoke tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-101-code-review-prompt.md)" > docs/reviews/opencode-stage-101-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-101-code-review.md`.
- [ ] Fix any Critical or Important findings before Task 4.

## Task 4: Full Verification, Commit, Push

- [ ] Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] Stage only Stage 101 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard first run docs boundary"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.

## Self-Review Checklist

- [ ] No placeholders or incomplete steps.
- [ ] Test scope is one Markdown section only.
- [ ] No first-run docs source text, runtime code, scripts, examples, dependency,
      schema, CI, or lockfile changes.
- [ ] Verification includes focused, adjacent, full, staged, and secret-scan
      checks.
