# Stage 94 Dashboard Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for `docs/dashboard.md` local
inspection, read-only trend, and local-security boundaries without changing docs
content or runtime dashboard behavior.

**Architecture:** This is a test-only docs guard. A new test module reads the
dashboard Markdown file directly, normalizes whitespace/case, and asserts stable
boundary phrases from the current dashboard guide.

**Tech Stack:** pytest, pathlib Markdown reads, uv, Ruff.

---

## File Map

- Create `tests/test_dashboard_docs.py`.
- Add Stage 94 review artifacts under `docs/reviews/`.

Do not modify `docs/dashboard.md`, `src/`, schemas, dependency manifests,
`uv.lock`, CI workflows, `tests/test_cli_docs.py`, or runtime dashboard tests.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-94-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-94-plan-review-prompt.md)" > docs/reviews/opencode-stage-94-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Dashboard Docs Test

- [ ] Create `tests/test_dashboard_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DOC = ROOT / "docs" / "dashboard.md"


def _read_dashboard_doc() -> str:
    return DASHBOARD_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_dashboard_docs_keep_local_inspection_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "optional streamlit app for inspecting local fashion radar state",
        "reads local sqlite/report state",
        "does not collect sources",
        "does not run entity matching",
        "does not generate reports",
        "does not make network requests on import or refresh",
    ):
        assert phrase in normalized


def test_dashboard_docs_keep_trend_readonly_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "computes the trend deltas tab from existing local sqlite state",
        "not from external services",
        "trend reads verify schema read-only",
        "do not initialize, migrate, or write trend tables",
    ):
        assert phrase in normalized


def test_dashboard_docs_keep_local_security_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "defaults to `127.0.0.1:8501`",
        "has no authentication layer",
        "intended for local use",
        "do not bind `--host 0.0.0.0`",
        "no scraping, no browser automation, no platform apis",
        "no account or cookie work",
    ):
        assert phrase in normalized
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_dashboard_docs.py -q
uv --no-config run --frozen pytest tests/test_dashboard.py tests/test_dashboard_docs.py -q
uv --no-config run --frozen ruff check tests/test_dashboard_docs.py
uv --no-config run --frozen ruff format --check tests/test_dashboard_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-94-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-94-code-review-prompt.md)" > docs/reviews/opencode-stage-94-code-review.md
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

- [ ] Stage only Stage 94 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard dashboard docs boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
