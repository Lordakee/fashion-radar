# Stage 95 Architecture Source Boundary Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for the `## Source Boundary`
section in `docs/architecture.md` without changing docs content or runtime
behavior.

**Architecture:** This is a test-only docs guard. A new test module reads the
architecture Markdown file directly, extracts the Source Boundary section,
normalizes whitespace/case, and asserts stable section-scoped boundary phrases.

**Tech Stack:** pytest, pathlib Markdown reads, uv, Ruff.

---

## File Map

- Create `tests/test_architecture_boundary_docs.py`.
- Add Stage 95 review artifacts under `docs/reviews/`.

Do not modify `docs/architecture.md`, `docs/source-boundaries.md`, `src/`,
schemas, dependency manifests, `uv.lock`, CI workflows, `tests/test_cli_docs.py`,
or runtime tests.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-95-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-95-plan-review-prompt.md)" > docs/reviews/opencode-stage-95-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Architecture Source Boundary Docs Test

- [ ] Create `tests/test_architecture_boundary_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_DOC = ROOT / "docs" / "architecture.md"


def _read_architecture_doc() -> str:
    return ARCHITECTURE_DOC.read_text(encoding="utf-8")


def _markdown_section(text: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    assert marker in f"\n{text}"
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_architecture_source_boundary_keeps_core_scope_and_local_import_limits() -> None:
    section = _markdown_section(_read_architecture_doc(), "## Source Boundary")
    normalized = _normalized(section)

    for phrase in (
        "the core collector set is rss, rsshub-compatible feeds, and gdelt",
        "manual signal import is a local input path",
        "user-provided csv/json files",
        "not a connector or platform collector",
        "non-core platform collection is not part of v0.1.0",
        "source-boundaries.md",
    ):
        assert phrase in normalized
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_architecture_boundary_docs.py -q
uv --no-config run --frozen ruff check tests/test_architecture_boundary_docs.py
uv --no-config run --frozen ruff format --check tests/test_architecture_boundary_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-95-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-95-code-review-prompt.md)" > docs/reviews/opencode-stage-95-code-review.md
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

- [ ] Stage only Stage 95 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard architecture source boundary docs"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
