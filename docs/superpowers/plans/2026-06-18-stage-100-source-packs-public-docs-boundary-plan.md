# Stage 100 Source Packs Public Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for the public source-pack starter
scope.

**Architecture:** Create one pytest module that reads `docs/source-packs.md`,
extracts the `## Public Fashion Pack` section, normalizes whitespace/case, and
asserts public-pack source-type and exclusion boundary phrases. Keep this stage
docs-test-only and avoid source YAML, runtime, CLI, schema, dependency, and CI
changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-100-source-packs-public-docs-boundary-design.md`
  records the Stage 100 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-100-source-packs-public-docs-boundary-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-100-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-100-plan-review.md` records the local
  plan review.
- Create: `tests/test_source_packs_docs.py` contains the standalone docs drift
  guard.
- Create: `docs/reviews/opencode-stage-100-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-100-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-100-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 100 Plan Review Prompt

Review the Stage 100 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/source-packs.md`, scoped only to the
`## Public Fashion Pack` section, so the starter pack remains documented as
using existing public source types and excluding unsupported acquisition
categories.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-100-source-packs-public-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-100-source-packs-public-docs-boundary-plan.md`
- `docs/source-packs.md`

## Planned Test

The implementation will add `tests/test_source_packs_docs.py` with one
docs-only test that extracts `## Public Fashion Pack` and asserts:

- `configs/source-packs/fashion-public.example.yaml`
- `it uses only existing v0.1.0 source types`
- `` `rss` ``
- `` `gdelt` ``
- `keeps the rss entries conservative`
- `bounded gdelt lanes`
- `inside the configured source set`
- `it does not include google news rss, google trends, account-based source access, browser automation, access-control bypasses, paywall bypass, or private data collection.`

## Scope Constraints

Allowed changes:

- `tests/test_source_packs_docs.py`
- Stage 100 review artifacts

Disallowed changes:

- `docs/source-packs.md`
- `configs/source-packs/`
- `docs/source-pack-quality.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source-pack tests
- data-retention, dashboard, architecture/source-boundary, entity-pack,
  entity-pack-quality, candidate-discovery, manual import, source-pack-quality,
  scheduling, or imported-candidate behavior

Do not expand this stage into source-pack lint quality, source availability,
article extraction, source acquisition, connector behavior, platform search,
social monitoring, compliance/audit/legal review, or runtime validation.

## Review Questions

1. Does the plan protect a real `docs/source-packs.md` public starter-pack
   boundary without changing product behavior?
2. Are the planned phrases present in `docs/source-packs.md` and scoped narrowly
   enough to `## Public Fashion Pack`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially
   Stage 92 source-pack quality and Stage 95 architecture/source boundaries?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-100-plan-review-prompt.md)" > docs/reviews/opencode-stage-100-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-100-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_source_packs_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKS_DOC = ROOT / "docs" / "source-packs.md"


def _read_source_packs_doc() -> str:
    return SOURCE_PACKS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_source_packs_docs_keep_public_pack_source_boundary() -> None:
    section = _section(_read_source_packs_doc(), "Public Fashion Pack")
    normalized = _normalized(section)

    for phrase in (
        "configs/source-packs/fashion-public.example.yaml",
        "it uses only existing v0.1.0 source types",
        "`rss`",
        "`gdelt`",
        "keeps the rss entries conservative",
        "bounded gdelt lanes",
        "inside the configured source set",
        "it does not include google news rss, google trends, "
        "account-based source access, browser automation, access-control bypasses, "
        "paywall bypass, or private data collection.",
    ):
        assert phrase in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q
```

Expected: pass.

- [ ] Run adjacent source-pack tests:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_packs_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_source_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_packs_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-100-code-review-prompt.md` with this
      review request:

```markdown
# Stage 100 Code Review Prompt

Review the Stage 100 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 100 adds `tests/test_source_packs_docs.py`, a standalone docs drift guard
for the `## Public Fashion Pack` section in `docs/source-packs.md`. It asserts
the starter pack path, existing v0.1.0 source types (`rss` and `gdelt`),
conservative RSS/bounded GDELT language, configured-source-set framing, and the
explicit exclusion of Google News RSS, Google Trends, account-based access,
browser automation, access-control bypasses, paywall bypass, and private data
collection.

## Files To Review

- `tests/test_source_packs_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-100-source-packs-public-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-100-source-packs-public-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-100-plan-review-prompt.md`
- `docs/reviews/opencode-stage-100-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_packs_docs.py`
- Stage 100 review artifacts

Disallowed changes:

- `docs/source-packs.md`
- `configs/source-packs/`
- `docs/source-pack-quality.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source-pack tests
- data-retention, dashboard, architecture/source-boundary, entity-pack,
  entity-pack-quality, candidate-discovery, manual import, source-pack-quality,
  scheduling, or imported-candidate behavior

Do not propose source-pack lint quality, source availability, article
extraction, source acquisition, connector behavior, platform search, social
monitoring, compliance/audit/legal review, or runtime validation changes.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_packs_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 100 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-packs.md` `## Public Fashion Pack` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   source-pack tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-100-code-review-prompt.md)" > docs/reviews/opencode-stage-100-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-100-code-review.md`.
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

- [ ] Stage only Stage 100 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard source packs public docs"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.

## Self-Review Checklist

- [ ] No placeholders or incomplete steps.
- [ ] Test scope is one Markdown section only.
- [ ] No source YAML, runtime code, docs source text, dependency, schema, CI, or
      lockfile changes.
- [ ] Verification includes focused, adjacent, full, staged, and secret-scan
      checks.
