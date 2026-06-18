# Stage 99 Manual Signal Import Privacy Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for the manual signal import privacy
boundary.

**Architecture:** Create one pytest module that reads
`docs/manual-signal-import.md`, extracts the `## Privacy Boundary` section,
normalizes whitespace/case, and asserts privacy-sensitive material boundary
phrases. Keep this stage docs-test-only and avoid runtime, CLI, schema,
dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-design.md`
  records the Stage 99 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-99-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-99-plan-review.md` records the local plan
  review.
- Create: `tests/test_manual_signal_import_docs.py` contains the standalone
  docs drift guard.
- Create: `docs/reviews/opencode-stage-99-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-99-code-review.md` records the local code
  review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-99-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 99 Plan Review Prompt

Review the Stage 99 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/manual-signal-import.md`, scoped only
to the `## Privacy Boundary` section, so manual import remains documented as
limited to conservative local metadata and away from private or sensitive
material.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-plan.md`
- `docs/manual-signal-import.md`

## Planned Test

The implementation will add `tests/test_manual_signal_import_docs.py` with one
docs-only test that extracts `## Privacy Boundary` and asserts:

- `do not import private comments`
- `account ids`
- `cookies`
- `author profiles`
- `follower lists`
- `images, videos`
- `private or sensitive material`
- `keep imported rows limited to conservative metadata`
- `allowed to process and review locally`

## Scope Constraints

Allowed changes:

- `tests/test_manual_signal_import_docs.py`
- Stage 99 review artifacts

Disallowed changes:

- `docs/manual-signal-import.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime manual import tests
- data-retention, dashboard, architecture/source-boundary, source-pack,
  entity-pack, entity-pack-quality, candidate-discovery, or imported-candidate
  behavior

Do not expand this stage into manual import workflow text, local input path
claims, connector/platform-collector claims, source-acquisition guide claims,
candidate review semantics, dashboard/report wording, privacy-compliance
features, audit/legal review, or runtime validation changes.

## Review Questions

1. Does the plan protect a real manual-signal-import privacy docs boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/manual-signal-import.md` and scoped
   narrowly enough to `## Privacy Boundary`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially
   architecture/source boundaries and candidate discovery?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-99-plan-review-prompt.md)" > docs/reviews/opencode-stage-99-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-99-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_manual_signal_import_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_SIGNAL_IMPORT_DOC = ROOT / "docs" / "manual-signal-import.md"


def _read_manual_signal_import_doc() -> str:
    return MANUAL_SIGNAL_IMPORT_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_manual_signal_import_docs_keep_privacy_boundary() -> None:
    privacy_boundary = _section(_read_manual_signal_import_doc(), "Privacy Boundary")
    normalized = _normalized(privacy_boundary)

    for phrase in (
        "do not import private comments",
        "account ids",
        "cookies",
        "author profiles",
        "follower lists",
        "images, videos",
        "private or sensitive material",
        "keep imported rows limited to conservative metadata",
        "allowed to process and review locally",
    ):
        assert phrase in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_manual_signal_import_docs.py -q
```

Expected: pass.

- [ ] Run adjacent manual import tests:

```bash
uv --no-config run --frozen pytest tests/test_manual_signal_import.py tests/test_manual_signal_import_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_manual_signal_import_docs.py
uv --no-config run --frozen ruff format --check tests/test_manual_signal_import_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-99-code-review-prompt.md` with this
      review request:

```markdown
# Stage 99 Code Review Prompt

Review the Stage 99 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 99 adds `tests/test_manual_signal_import_docs.py`, a standalone docs drift
guard for the `## Privacy Boundary` section in `docs/manual-signal-import.md`.
It asserts that manual import docs prohibit private comments, account IDs,
cookies, author profiles, follower lists, images/videos, and other private or
sensitive material, and keep imported rows limited to conservative metadata that
the user is allowed to process and review locally.

## Files To Review

- `tests/test_manual_signal_import_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-99-plan-review-prompt.md`
- `docs/reviews/opencode-stage-99-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_manual_signal_import_docs.py`
- Stage 99 review artifacts

Disallowed changes:

- `docs/manual-signal-import.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime manual import tests
- data-retention, dashboard, architecture/source-boundary, source-pack,
  entity-pack, entity-pack-quality, candidate-discovery, or imported-candidate
  behavior

Do not propose adding privacy-compliance, audit, legal-review, runtime
validation, connector, platform collector, source acquisition, candidate review,
or dashboard/report behavior.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_manual_signal_import_docs.py -q
uv --no-config run --frozen pytest tests/test_manual_signal_import.py tests/test_manual_signal_import_docs.py -q
uv --no-config run --frozen ruff check tests/test_manual_signal_import_docs.py
uv --no-config run --frozen ruff format --check tests/test_manual_signal_import_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 99 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the manual
   signal import `## Privacy Boundary` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   manual import tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-99-code-review-prompt.md)" > docs/reviews/opencode-stage-99-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-99-code-review.md`.
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

- [ ] Stage only Stage 99 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard manual signal import privacy docs"
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
