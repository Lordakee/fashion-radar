# Stage 87 Roadmap Boundary Test Scope Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Require the external tool import roadmap no-upstream/no-platform
boundary phrases inside the roadmap section itself, without changing docs or
runtime behavior.

**Architecture:** This is a test-only docs drift hardening. The test already
extracts `roadmap`; Stage 87 reuses that extracted section for boundary
assertions instead of scanning the whole document.

**Tech Stack:** pytest docs drift tests, Markdown docs, uv, Ruff.

---

## File Map

- Modify `tests/test_cli_docs.py`.
- Add Stage 87 review artifacts under `docs/reviews/`.

Do not modify docs content, `src/`, schemas, lint/import behavior, adapter
command behavior, dependency manifests, `uv.lock`, CI workflows, `AGENTS.md`,
or `docs/REVIEW_PROTOCOL.md`.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-87-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-87-plan-review-prompt.md)" > docs/reviews/opencode-stage-87-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Narrow The Roadmap Boundary Assertion Scope

- [ ] In `tests/test_cli_docs.py`, update
  `test_community_signal_import_docs_have_external_tool_import_roadmap`.
- [ ] Remove the full-document normalized text line:

```python
normalized = _normalized_doc_text(COMMUNITY_SIGNAL_IMPORT_DOC).casefold()
```

- [ ] Immediately after the existing `roadmap = ...` extraction, add:

```python
normalized_roadmap = _normalized_text(roadmap).casefold()
```

- [ ] In the final boundary phrase loop, change:

```python
assert term in normalized
```

to:

```python
assert term in normalized_roadmap
```

## Task 3: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_import_docs_have_external_tool_import_roadmap -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

- [ ] Create `docs/reviews/opencode-stage-87-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-87-code-review-prompt.md)" > docs/reviews/opencode-stage-87-code-review.md
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

- [ ] Stage only Stage 87 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Scope roadmap boundary docs test"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
