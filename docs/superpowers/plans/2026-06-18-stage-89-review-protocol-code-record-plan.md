# Stage 89 Review Protocol Code Record Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document and test review artifact names for implementation code
reviews and code rereviews in the active review protocol.

**Architecture:** This is a docs/test-only review-process clarification. The
protocol already requires code review during development; Stage 89 aligns the
record naming section and its drift test with that existing requirement.

**Tech Stack:** Markdown docs, pytest docs drift tests, uv, Ruff.

---

## File Map

- Modify `docs/REVIEW_PROTOCOL.md`.
- Modify `tests/test_review_protocol_docs.py`.
- Add Stage 89 review artifacts under `docs/reviews/`.

Do not modify `src/`, schemas, dependency manifests, `uv.lock`, CI workflows,
community signal/import/adapter behavior, product docs outside the review
protocol, `AGENTS.md`, or `docs/github-upload-checklist.md`.

## Carry-Forward Review Runner Drift

Stage 89 review artifacts intentionally use `opencode-stage-89-*` names because
the current user-directed review runner for this development thread is local
opencode. Do not rename opencode-generated artifacts to `claude-code-stage-89-*`.
This plan aligns the checked-in protocol's record naming section with its
existing Claude Code code-review requirement, but it does not resolve the
separate active-review-runner drift between current execution practice and the
checked-in Claude Code protocol.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-89-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-89-plan-review-prompt.md)" > docs/reviews/opencode-stage-89-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.
- [ ] If plan review requires a planning fix, create
  `docs/reviews/opencode-stage-89-plan-rereview-prompt.md` and save the result
  as `docs/reviews/opencode-stage-89-plan-rereview.md` before implementation.

## Task 2: Add Failing Review Protocol Test Assertions

- [ ] In `tests/test_review_protocol_docs.py`, add this helper after `_read`:

```python
def _section(text: str, heading: str) -> str:
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]
```

- [ ] In `test_active_review_protocol_documents_claude_code_gate`, set:

```python
naming_section = _section(protocol_text, "Review Record Naming")
```

immediately after `protocol_text = _read(REVIEW_PROTOCOL)`.

- [ ] Replace the two direct record-name assertions:

```python
assert "claude-code-stage-N-plan-review.md" in protocol_text
assert "claude-code-stage-N-release-review.md" in protocol_text
```

with:

```python
review_record_names = (
    "claude-code-stage-N-plan-review.md",
    "claude-code-stage-N-code-review.md",
    "claude-code-stage-N-release-review.md",
)
for record_name in review_record_names:
    assert record_name in naming_section

assert naming_section.index(review_record_names[0]) < naming_section.index(
    review_record_names[1]
) < naming_section.index(review_record_names[2])

rereview_record_names = (
    "claude-code-stage-N-plan-rereview.md",
    "claude-code-stage-N-code-rereview.md",
    "claude-code-stage-N-release-rereview.md",
)
for record_name in rereview_record_names:
    assert record_name in naming_section

assert naming_section.index(rereview_record_names[0]) < naming_section.index(
    rereview_record_names[1]
) < naming_section.index(rereview_record_names[2])
```

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py::test_active_review_protocol_documents_claude_code_gate -q
```

Expected: FAIL because `docs/REVIEW_PROTOCOL.md` does not yet list the
`code-review` and `code-rereview` names.

## Task 3: Document Code Review Record Names

- [ ] In `docs/REVIEW_PROTOCOL.md`, update the "During Development" code-review
  step from:

```markdown
2. Local Claude Code review of newly added code.
```

to:

```markdown
2. Local Claude Code review of newly added code
   (`docs/reviews/claude-code-stage-N-code-review.md`).
```

- [ ] In `docs/REVIEW_PROTOCOL.md`, update the normal review naming block from:

```text
docs/reviews/claude-code-stage-N-plan-review.md
docs/reviews/claude-code-stage-N-release-review.md
```

to:

```text
docs/reviews/claude-code-stage-N-plan-review.md
docs/reviews/claude-code-stage-N-code-review.md
docs/reviews/claude-code-stage-N-release-review.md
```

- [ ] Update the follow-up review naming block from:

```text
docs/reviews/claude-code-stage-N-plan-rereview.md
docs/reviews/claude-code-stage-N-release-rereview.md
```

to:

```text
docs/reviews/claude-code-stage-N-plan-rereview.md
docs/reviews/claude-code-stage-N-code-rereview.md
docs/reviews/claude-code-stage-N-release-rereview.md
```

## Task 4: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py::test_active_review_protocol_documents_claude_code_gate -q
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
uv --no-config run --frozen ruff check tests/test_review_protocol_docs.py
uv --no-config run --frozen ruff format --check tests/test_review_protocol_docs.py
git diff --check
```

- [ ] Create `docs/reviews/opencode-stage-89-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-89-code-review-prompt.md)" > docs/reviews/opencode-stage-89-code-review.md
```

- [ ] Fix Critical or Important findings before final verification.

## Task 5: Full Verification, Commit, Push

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

- [ ] Stage only Stage 89 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Document code review record names"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
