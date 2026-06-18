# Stage 96 Entity Packs Docs Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for `docs/entity-packs.md` local
matching and optional local sample boundaries without changing docs content or
runtime entity-pack behavior.

**Architecture:** This is a test-only docs guard. A new test module reads the
entity-packs Markdown file directly, normalizes whitespace/case, and asserts
stable boundary phrases from the current entity-pack guide.

**Tech Stack:** pytest, pathlib Markdown reads, uv, Ruff.

---

## File Map

- Create `tests/test_entity_packs_docs.py`.
- Add Stage 96 review artifacts under `docs/reviews/`.

Do not modify `docs/entity-packs.md`, `configs/entity-packs/`, `src/`, schemas,
dependency manifests, `uv.lock`, CI workflows, `tests/test_cli_docs.py`, or
runtime entity-pack tests.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-96-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-96-plan-review-prompt.md)" > docs/reviews/opencode-stage-96-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Entity Packs Docs Test

- [ ] Create `tests/test_entity_packs_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTITY_PACKS_DOC = ROOT / "docs" / "entity-packs.md"


def _read_entity_packs_doc() -> str:
    return ENTITY_PACKS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_entity_packs_docs_keep_local_matching_boundary() -> None:
    normalized = _normalized(_read_entity_packs_doc())

    for phrase in (
        "optional local configuration templates",
        "without changing fashion radar's runtime behavior",
        "only changes local entity matching",
        "does not add sources",
        "does not add ingestion",
        "does not add live collection",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
    ):
        assert phrase in normalized


def test_entity_packs_docs_keep_optional_sample_boundary() -> None:
    normalized = _normalized(_read_entity_packs_doc())

    for phrase in (
        "optional local sample",
        "checked-in synthetic community-signal rows",
        "local sample rows are synthetic",
        "not a hot-list, not a ranking",
        "not demand proof",
        "not platform coverage verification",
        "local files only",
        "no fetching urls",
        "no platform data collection",
        "no connectors",
    ):
        assert phrase in normalized
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_entity_packs_docs.py -q
uv --no-config run --frozen pytest tests/test_entity_packs.py tests/test_entity_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_entity_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_entity_packs_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-96-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-96-code-review-prompt.md)" > docs/reviews/opencode-stage-96-code-review.md
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

- [ ] Stage only Stage 96 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Guard entity packs docs boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
