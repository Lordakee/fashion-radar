# Stage 92 Source-Pack Quality Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for
`docs/source-pack-quality.md` local/read-only and non-guarantee boundaries
without changing docs content or runtime source-pack lint behavior.

**Architecture:** This is a test-only docs guard. A new test module reads the
source-pack quality Markdown file directly, normalizes whitespace/case, and
asserts stable boundary phrases that mirror the documented command limits.

**Tech Stack:** pytest, pathlib Markdown reads, uv, Ruff.

---

## File Map

- Create `tests/test_source_pack_quality_docs.py`.
- Add Stage 92 review artifacts under `docs/reviews/`.

Do not modify `docs/source-pack-quality.md`, `src/`, schemas, dependency
manifests, `uv.lock`, CI workflows, `tests/test_cli_docs.py`, or runtime
source-pack lint tests.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-92-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-92-plan-review-prompt.md)" > docs/reviews/opencode-stage-92-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Source-Pack Quality Docs Test

- [ ] Create `tests/test_source_pack_quality_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACK_QUALITY_DOC = ROOT / "docs" / "source-pack-quality.md"


def _read_source_pack_quality_doc() -> str:
    return SOURCE_PACK_QUALITY_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_source_pack_quality_docs_keep_local_read_only_boundary() -> None:
    normalized = _normalized(_read_source_pack_quality_doc())

    for phrase in (
        "linting is local and read-only",
        "does not fetch sources",
        "check live feed availability",
        "collect source items",
        "open sqlite",
        "create config, data, report, or workflow artifacts",
        "not a compliance, audit, policy, or source-terms review workflow",
    ):
        assert phrase in normalized


def test_source_pack_quality_json_docs_keep_non_data_boundary() -> None:
    normalized = _normalized(_read_source_pack_quality_doc())

    for phrase in (
        "json output does not include fetched data, collected items",
        "database state, source contents, or account data",
    ):
        assert phrase in normalized


def test_source_pack_quality_docs_keep_availability_and_demand_boundaries() -> None:
    normalized = _normalized(_read_source_pack_quality_doc())

    for phrase in (
        "the lint command does not fetch article pages",
        "should not be described as proof of demand outside it",
        "checks the configured yaml file only",
        "does not know whether a feed is live today",
        "whether a gdelt query will return records",
        "local configuration quality signal, not as a source availability guarantee",
    ):
        assert phrase in normalized
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-92-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-92-code-review-prompt.md)" > docs/reviews/opencode-stage-92-code-review.md
```

- [ ] Fix Critical or Important findings before final verification.

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

- [ ] Stage only Stage 92 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard source pack quality docs boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
