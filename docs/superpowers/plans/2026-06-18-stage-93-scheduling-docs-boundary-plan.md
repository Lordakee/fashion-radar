# Stage 93 Scheduling Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for `docs/scheduling.md` local,
serial, print-only, and manual-review boundaries without changing docs content
or runtime scheduling behavior.

**Architecture:** This is a test-only docs guard. A new test module reads the
scheduling Markdown file directly, normalizes whitespace/case, and asserts
stable boundary phrases from the current scheduling guide.

**Tech Stack:** pytest, pathlib Markdown reads, uv, Ruff.

---

## File Map

- Create `tests/test_scheduling_docs.py`.
- Add Stage 93 review artifacts under `docs/reviews/`.

Do not modify `docs/scheduling.md`, `src/`, schemas, dependency manifests,
`uv.lock`, CI workflows, `tests/test_cli_docs.py`, or runtime scheduling tests.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-93-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-93-plan-review-prompt.md)" > docs/reviews/opencode-stage-93-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Scheduling Docs Test

- [ ] Create `tests/test_scheduling_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEDULING_DOC = ROOT / "docs" / "scheduling.md"


def _read_scheduling_doc() -> str:
    return SCHEDULING_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_scheduling_docs_keep_local_serial_run_boundary() -> None:
    normalized = _normalized(_read_scheduling_doc())

    for phrase in (
        "does not run a background daemon",
        "run the existing serial command",
        "`run` executes `collect -> match -> report` in one local process",
        "do not schedule overlapping runs against the same sqlite database",
        "if a previous run is still active, wait for it to finish",
    ):
        assert phrase in normalized


def test_scheduling_docs_keep_local_digest_handoff_boundary() -> None:
    normalized = _normalized(_read_scheduling_doc())

    for phrase in (
        "write local files such as `latest.md`, `latest.json`, and `report-index.json`",
        "do not send email, call webhooks, open a browser, or install a notification daemon",
        "local `.eml` handoff file",
        "you review yourself",
    ):
        assert phrase in normalized


def test_scheduling_docs_keep_schedule_example_print_only_boundary() -> None:
    examples_section = _section(_read_scheduling_doc(), "Generate Examples")
    normalized = _normalized(examples_section)

    for phrase in (
        "use `schedule-example` to print snippets",
        "does not install anything",
    ):
        assert phrase in normalized
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_scheduling_docs.py -q
uv --no-config run --frozen pytest tests/test_scheduling.py tests/test_scheduling_docs.py -q
uv --no-config run --frozen ruff check tests/test_scheduling_docs.py
uv --no-config run --frozen ruff format --check tests/test_scheduling_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-93-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-93-code-review-prompt.md)" > docs/reviews/opencode-stage-93-code-review.md
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

- [ ] Stage only Stage 93 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard scheduling docs boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
