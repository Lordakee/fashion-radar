# Stage 91 Data Retention Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for `docs/data-retention.md`
cleanup and retention boundaries without changing docs content or runtime
cleanup behavior.

**Architecture:** This is a test-only docs guard. A new test module reads the
data-retention Markdown file directly and asserts stable cleanup-boundary
phrases that mirror existing workflow/CLI behavior tests.

**Tech Stack:** pytest, pathlib Markdown reads, uv, Ruff.

---

## File Map

- Create `tests/test_data_retention_docs.py`.
- Add Stage 91 review artifacts under `docs/reviews/`.

Do not modify `docs/data-retention.md`, `src/`, schemas, dependency manifests,
`uv.lock`, CI workflows, `tests/test_cli_docs.py`, or runtime cleanup tests.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-91-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-91-plan-review-prompt.md)" > docs/reviews/opencode-stage-91-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Data Retention Docs Test

- [ ] Create `tests/test_data_retention_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RETENTION_DOC = ROOT / "docs" / "data-retention.md"


def _read_data_retention_doc() -> str:
    return DATA_RETENTION_DOC.read_text(encoding="utf-8")


def test_data_retention_docs_pin_cleanup_boundaries() -> None:
    text = _read_data_retention_doc()

    for phrase in (
        "Use `clean-old-data` to prune old collected items",
        "as_of - retention_days",
        "Rows in `items` with `collected_at` older than that cutoff are pruned.",
        "explicitly deletes related `item_entities` rows before deleting",
        "does not rely on SQLite foreign-key cascade behavior",
        "`--dry-run` reports how many item and item/entity rows would be deleted without",
        "The cleanup command does not prune:",
        "`collector_runs`",
        "`source_health`",
        "`entity_first_seen`",
        "generated Markdown or JSON report files",
        "config files",
        "`entity_first_seen` is intentionally retained across item pruning",
        "Back up the SQLite database before aggressive cleanup",
    ):
        assert phrase in text
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_data_retention_docs.py -q
uv --no-config run --frozen pytest tests/test_workflows.py::test_clean_old_data_prunes_by_collected_at tests/test_cli.py::test_clean_old_data_command_prunes_old_items tests/test_data_retention_docs.py -q
uv --no-config run --frozen ruff check tests/test_data_retention_docs.py
uv --no-config run --frozen ruff format --check tests/test_data_retention_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-91-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-91-code-review-prompt.md)" > docs/reviews/opencode-stage-91-code-review.md
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

- [ ] Stage only Stage 91 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard data retention docs boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
