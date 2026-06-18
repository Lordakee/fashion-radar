# Stage 83 Upload Checklist Mirror Recovery Plan

> Use local opencode for plan and code review with
> `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

## Goal

Add a short GitHub upload checklist reminder that points to the mirror-lockfile
recovery path and add a docs drift test for that reminder.

## File Map

- Modify `docs/github-upload-checklist.md`.
- Modify `tests/test_cli_docs.py`.
- Add Stage 83 spec/plan/review artifacts.
- Do not modify `src/`, dependency manifests, `uv.lock`, `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, or `docs/dependency-mirrors.md` unless a scoped
  test exposes a real mismatch.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-83-plan-review-prompt.md`.
- [ ] Run local opencode plan review.
- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Checklist Reminder And Test

- [ ] Add a short reminder under the `Before Upload` section in
  `docs/github-upload-checklist.md`, immediately after the current
  mirror-marker `rg ... uv.lock` block and before `Historical boundary checks`.
- [ ] Keep the reminder to one or two sentences. It should be a pointer, not a
  duplicate command block.
- [ ] Point the reminder to
  `[Recover A Mirror-Rewritten Lockfile](dependency-mirrors.md#recover-a-mirror-rewritten-lockfile)`.
- [ ] Mention the `Recover A Mirror-Rewritten Lockfile` guidance by name.
- [ ] Add a docs drift test that uses whole-file substring presence and pins
  these exact strings without scoping to `## Before Upload`:

```python
"Recover A Mirror-Rewritten Lockfile"
"dependency-mirrors.md#recover-a-mirror-rewritten-lockfile"
"If `uv.lock` was changed by mirror-backed local operations before upload"
```

## Task 3: Focused Verification

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_upload_checklist_mentions_mirror_lockfile_recovery \
  -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check -- docs/github-upload-checklist.md tests/test_cli_docs.py
```

## Task 4: Code Review And Full Verification

- [ ] Create `docs/reviews/opencode-stage-83-code-review-prompt.md`.
- [ ] Run local opencode code review.
- [ ] Fix Critical or Important findings.
- [ ] Run full verification:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
```

## Task 5: Commit And Publish

- [ ] Stage only Stage 83 files:

```bash
git add -- \
  docs/github-upload-checklist.md \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-18-stage-83-upload-checklist-mirror-recovery-design.md \
  docs/superpowers/plans/2026-06-18-stage-83-upload-checklist-mirror-recovery-plan.md \
  docs/reviews/opencode-stage-83-plan-review-prompt.md \
  docs/reviews/opencode-stage-83-plan-review.md \
  docs/reviews/opencode-stage-83-code-review-prompt.md \
  docs/reviews/opencode-stage-83-code-review.md
```

- [ ] Confirm `uv.lock` is not staged.
- [ ] Run staged release hygiene and secret scan.
- [ ] Commit with message `Document upload checklist mirror recovery`.
- [ ] Push safely without persisting credentials.
- [ ] Verify local/remote `main` alignment and GitHub Actions success.
