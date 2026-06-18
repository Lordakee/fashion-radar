# Stage 90 Daily Digest Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for `docs/daily-digest.md` local
digest boundaries without changing digest behavior or docs content.

**Architecture:** This is a test-only docs guard. A new test module reads the
daily digest Markdown file directly and asserts stable boundary phrases for
local-only packaging, manual `.eml` review, and local observed source-set
limits.

**Tech Stack:** pytest, pathlib Markdown reads, uv, Ruff.

---

## File Map

- Create `tests/test_daily_digest_docs.py`.
- Add Stage 90 review artifacts under `docs/reviews/`.

Do not modify `docs/daily-digest.md`, `src/`, schemas, dependency manifests,
`uv.lock`, CI workflows, `tests/test_cli_docs.py`, `tests/test_digests.py`, or
review protocol docs/tests.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-90-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-90-plan-review-prompt.md)" > docs/reviews/opencode-stage-90-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Daily Digest Docs Tests

- [ ] Create `tests/test_daily_digest_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY_DIGEST_DOC = ROOT / "docs" / "daily-digest.md"


def _read_daily_digest_doc() -> str:
    return DAILY_DIGEST_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_daily_digest_docs_keep_local_file_only_boundary() -> None:
    normalized = _normalized(_read_daily_digest_doc())

    for phrase in (
        "reads only the markdown and json report files",
        "does not collect sources",
        "open sqlite",
        "send email",
        "call webhooks",
        "open a browser",
        "install a notification daemon",
        "generated locally inside the configured reports directory",
    ):
        assert phrase in normalized


def test_daily_digest_docs_keep_eml_manual_review_boundary() -> None:
    normalized = _normalized(_read_daily_digest_doc())

    for phrase in (
        "write a local `.eml` file for manual review",
        "has no `to`, `cc`, or `bcc` headers",
        "fashion radar never sends it",
        "review source attribution",
        "before sharing a report or `.eml` file",
    ):
        assert phrase in normalized


def test_daily_digest_docs_keep_review_boundary_section() -> None:
    text = _read_daily_digest_doc()
    review_boundary = text.split("## Review Boundary", 1)[1]
    normalized = _normalized(review_boundary)

    for phrase in (
        "local observed signals",
        "configured source set",
        "imported local signals",
        "review aids",
        "not claims about demand outside that source set",
    ):
        assert phrase in normalized
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_daily_digest_docs.py -q
uv --no-config run --frozen pytest tests/test_digests.py tests/test_daily_digest_docs.py -q
uv --no-config run --frozen ruff check tests/test_daily_digest_docs.py
uv --no-config run --frozen ruff format --check tests/test_daily_digest_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-90-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-90-code-review-prompt.md)" > docs/reviews/opencode-stage-90-code-review.md
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

- [ ] Stage only Stage 90 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard daily digest docs boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
