# Stage 106 Source Boundaries Storage Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for source-boundary storage wording.

**Architecture:** Create one pytest module that reads `docs/source-boundaries.md`,
extracts the `## Storage Boundaries` section, normalizes whitespace/case, and
asserts conservative local storage-boundary phrases. Keep this stage
docs-test-only and avoid runtime, collectors, robots/fetching, storage schema,
source acquisition, connector, social/platform scraping, compliance, dependency,
and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-106-source-boundaries-storage-docs-design.md`
  records the Stage 106 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-106-source-boundaries-storage-docs-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-106-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-106-plan-review.md` records the local
  plan review.
- Create: `tests/test_source_boundaries_docs.py` contains the standalone docs
  drift guard.
- Create: `docs/reviews/opencode-stage-106-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-106-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-106-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 106 Plan Review Prompt

Review the Stage 106 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/source-boundaries.md`, scoped only
to the `## Storage Boundaries` section, so source-boundary storage guidance
remains explicit about conservative local storage, source metadata and local
provenance, avoiding full article text/media/comment redistribution by default,
preserving source attribution, and skipping known paywalled extraction unless
permitted metadata is provided.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-106-source-boundaries-storage-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-106-source-boundaries-storage-docs-plan.md`
- `docs/source-boundaries.md`

## Planned Test

The implementation will add `tests/test_source_boundaries_docs.py` with one
docs-only test that extracts `## Storage Boundaries` and asserts:

- `Default storage should be conservative:`
- `` Store source URLs, titles, publication timestamps, source names, optional local `platform` provenance labels for imported rows, short summaries, entity matches, tags, counts, and scores. ``
- `Avoid storing full article text by default.`
- `Avoid storing original images or videos.`
- `Avoid storing user comments as redistributable assets.`
- `Preserve source links so users can read original content on the source site.`
- `Display source attribution beside representative items.`
- `Add attribution footer to generated reports.`
- `Skip extraction for known paywalled domains unless the source itself provides permitted metadata.`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 106 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- collector, robots/fetching, storage schema, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime storage checks, robots/fetching behavior,
source collection, platform search, social monitoring, market rankings,
dashboard logic, report logic, schema migrations, connector behavior, or
compliance features.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` storage boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Storage Boundaries`?
3. Does the plan avoid overlap with robots/fetching behavior, output wording,
   README requirements, architecture source-boundary docs, package archive
   checks, and runtime collector/storage code?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-106-plan-review-prompt.md)" > docs/reviews/opencode-stage-106-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-106-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_source_boundaries_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BOUNDARIES_DOC = ROOT / "docs" / "source-boundaries.md"


def _read_source_boundaries_doc() -> str:
    return SOURCE_BOUNDARIES_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_source_boundaries_docs_keep_storage_boundary() -> None:
    storage_boundaries = _section(
        _read_source_boundaries_doc(),
        "Storage Boundaries",
    )
    normalized = _normalized(storage_boundaries)

    for phrase in (
        "Default storage should be conservative:",
        "Store source URLs, titles, publication timestamps, source names, "
        "optional local `platform` provenance labels for imported rows, short "
        "summaries, entity matches, tags, counts, and scores.",
        "Avoid storing full article text by default.",
        "Avoid storing original images or videos.",
        "Avoid storing user comments as redistributable assets.",
        "Preserve source links so users can read original content on the source site.",
        "Display source attribution beside representative items.",
        "Add attribution footer to generated reports.",
        "Skip extraction for known paywalled domains unless the source itself provides "
        "permitted metadata.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
```

Expected: pass.

- [ ] Run adjacent source-boundary docs/reference tests:

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_architecture_boundary_docs.py tests/test_cli_docs.py tests/test_package_archives.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-106-code-review-prompt.md` with this
      review request:

```markdown
# Stage 106 Code Review Prompt

Review the Stage 106 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 106 adds `tests/test_source_boundaries_docs.py`, a standalone docs drift
guard for the `## Storage Boundaries` section in `docs/source-boundaries.md`.
It asserts that source-boundary storage guidance keeps explicit wording about
conservative local storage, source metadata and local provenance, avoiding full
article text/media/comment redistribution by default, preserving source
attribution, and skipping known paywalled extraction unless permitted metadata is
provided.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-106-source-boundaries-storage-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-106-source-boundaries-storage-docs-plan.md`
- `docs/reviews/opencode-stage-106-plan-review-prompt.md`
- `docs/reviews/opencode-stage-106-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 106 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- collector, robots/fetching, storage schema, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_architecture_boundary_docs.py tests/test_cli_docs.py tests/test_package_archives.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 106 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-boundaries.md` `## Storage Boundaries` section?
3. Is the new standalone test independent from robots/fetching, output wording,
   README requirements, architecture source-boundary docs, package archive
   checks, and runtime collector/storage behavior?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-106-code-review-prompt.md)" > docs/reviews/opencode-stage-106-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-106-code-review.md`.
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

- [ ] Stage only Stage 106 files:

```bash
git add \
  docs/reviews/opencode-stage-106-code-review-prompt.md \
  docs/reviews/opencode-stage-106-code-review.md \
  docs/reviews/opencode-stage-106-plan-review-prompt.md \
  docs/reviews/opencode-stage-106-plan-review.md \
  docs/superpowers/plans/2026-06-18-stage-106-source-boundaries-storage-docs-plan.md \
  docs/superpowers/specs/2026-06-18-stage-106-source-boundaries-storage-docs-design.md \
  tests/test_source_boundaries_docs.py
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
git commit -m "Guard source storage boundary docs"
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
