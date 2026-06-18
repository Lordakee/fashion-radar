# Stage 98 Candidate Discovery Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for the candidate discovery
source-expansion boundary.

**Architecture:** Create one pytest module that reads
`docs/candidate-discovery.md`, extracts the `## Boundaries` section, normalizes
whitespace/case, and asserts stable phrases. Keep this stage docs-test-only and
avoid runtime, CLI, schema, dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-98-candidate-discovery-docs-boundary-design.md`
  records the Stage 98 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-98-candidate-discovery-docs-boundary-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-98-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-98-plan-review.md` records the local plan
  review.
- Create: `tests/test_candidate_discovery_docs.py` contains the standalone docs
  drift guard.
- Create: `docs/reviews/opencode-stage-98-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-98-code-review.md` records the local code
  review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-98-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 98 Plan Review Prompt

Review the Stage 98 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/candidate-discovery.md`, scoped only
to the `## Boundaries` section, so candidate discovery remains documented as a
local review aid with no collectors, no new source types, no external inference,
and no background network reads.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-98-candidate-discovery-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-98-candidate-discovery-docs-boundary-plan.md`
- `docs/candidate-discovery.md`

## Planned Test

The implementation will add `tests/test_candidate_discovery_docs.py` with one
docs-only test that extracts `## Boundaries` and asserts:

- `candidate discovery adds no collectors`
- `no new source types`
- `no external inference calls`
- `no background network reads`
- `configured sources and imported local signals`
- `observed phrases that need review`

## Scope Constraints

Allowed changes:

- `tests/test_candidate_discovery_docs.py`
- Stage 98 review artifacts

Disallowed changes:

- `docs/candidate-discovery.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime candidate discovery tests
- data-retention, dashboard, architecture, source-pack, entity-pack, or
  imported-candidate behavior

## Review Questions

1. Does the plan protect a real candidate-discovery docs boundary without
   changing product behavior?
2. Are the planned phrases present in `docs/candidate-discovery.md` and scoped
   narrowly enough to `## Boundaries`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially data
   retention, dashboard, architecture/source boundaries, entity packs,
   entity-pack quality, and imported/community candidate workflows?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-98-plan-review-prompt.md)" > docs/reviews/opencode-stage-98-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-98-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_candidate_discovery_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DISCOVERY_DOC = ROOT / "docs" / "candidate-discovery.md"


def _read_candidate_discovery_doc() -> str:
    return CANDIDATE_DISCOVERY_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_candidate_discovery_docs_keep_no_source_expansion_boundary() -> None:
    boundaries = _section(_read_candidate_discovery_doc(), "Boundaries")
    normalized = _normalized(boundaries)

    for phrase in (
        "candidate discovery adds no collectors",
        "no new source types",
        "no external inference calls",
        "no background network reads",
        "configured sources and imported local signals",
        "observed phrases that need review",
    ):
        assert phrase in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py -q
```

Expected: pass.

- [ ] Run adjacent candidate tests:

```bash
uv --no-config run --frozen pytest tests/test_candidate_extraction.py tests/test_candidate_scoring.py tests/test_candidate_discovery_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_candidate_discovery_docs.py
uv --no-config run --frozen ruff format --check tests/test_candidate_discovery_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-98-code-review-prompt.md` with this
      review request:

```markdown
# Stage 98 Code Review Prompt

Review the Stage 98 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 98 adds `tests/test_candidate_discovery_docs.py`, a standalone docs drift
guard for the `## Boundaries` section in `docs/candidate-discovery.md`. It
asserts that candidate discovery adds no collectors, no new source types, no
external inference calls, and no background network reads, and that outputs
remain observed phrases from configured sources and imported local signals that
need review.

## Files To Review

- `tests/test_candidate_discovery_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-98-candidate-discovery-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-98-candidate-discovery-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-98-plan-review-prompt.md`
- `docs/reviews/opencode-stage-98-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_candidate_discovery_docs.py`
- Stage 98 review artifacts

Disallowed changes:

- `docs/candidate-discovery.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime candidate discovery tests
- data-retention, dashboard, architecture/source-boundary, source-pack,
  entity-pack, entity-pack-quality, or imported/community candidate behavior

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py -q
uv --no-config run --frozen pytest tests/test_candidate_extraction.py tests/test_candidate_scoring.py tests/test_candidate_discovery_docs.py -q
uv --no-config run --frozen ruff check tests/test_candidate_discovery_docs.py
uv --no-config run --frozen ruff format --check tests/test_candidate_discovery_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 98 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the candidate
   discovery `## Boundaries` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   candidate discovery tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-98-code-review-prompt.md)" > docs/reviews/opencode-stage-98-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-98-code-review.md`.
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

- [ ] Stage only Stage 98 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard candidate discovery docs boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.

## Self-Review Checklist

- [ ] No placeholders or incomplete steps.
- [ ] Test scope is one Markdown section only.
- [ ] No runtime code, docs source text, dependency, schema, CI, or lockfile
      changes.
- [ ] Verification includes focused, adjacent, full, staged, and secret-scan
      checks.
