# Stage 82 Mirror Lockfile Recovery Plan

> Use local opencode for plan and code review with
> `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

## Goal

Document the safe recovery path for a local mirror-rewritten `uv.lock`, add a
docs drift test for that guidance, and restore the working tree lockfile to the
public mirror-free version.

## File Map

- Modify `docs/dependency-mirrors.md`.
- Modify `tests/test_cli_docs.py`.
- Add Stage 82 spec/plan/review artifacts.
- Restore `uv.lock` from `HEAD`; do not stage it if restoration leaves no diff.
- Do not modify `src/`, dependency manifests, `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md`, or CI.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-82-plan-review-prompt.md`.
- [ ] Run local opencode plan review.
- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Recovery Docs And Tests

- [ ] Add a `## Recover A Mirror-Rewritten Lockfile` section to
  `docs/dependency-mirrors.md` after `## Project Practice` as a peer `##`
  section. Keep the existing `## Project Practice` mirror scan; this section is
  additive recovery guidance for when a local mirror rewrite already happened.
- [ ] Include the exact heading `## Recover A Mirror-Rewritten Lockfile`.
- [ ] Pin the exact boundary phrase
  `If `uv.lock` was already rewritten locally with mirror URLs, do not commit it.`
- [ ] Include commands for `git restore -- uv.lock`, `UV_NO_CONFIG=1 uv lock
  --check`, mirror-marker `rg` scan, and `git diff --quiet -- uv.lock`.
- [ ] Add a short note that the `! rg ...` verification passes only when no
  mirror markers are found.
- [ ] Add a docs drift test in `tests/test_cli_docs.py` that pins the section,
  these commands, and boundary wording:

```python
"Recover A Mirror-Rewritten Lockfile"
"If `uv.lock` was already rewritten locally with mirror URLs, do not commit it."
"git restore -- uv.lock"
"UV_NO_CONFIG=1 uv lock --check"
"git diff --quiet -- uv.lock"
"rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock"
"frozen mirror install commands"
"do not regenerate or commit `uv.lock` from a mirror-backed lock operation"
```

## Task 3: Restore Local Lockfile

- [ ] Run `git restore uv.lock`.
- [ ] Confirm `git diff --quiet -- uv.lock`.
- [ ] Run `UV_NO_CONFIG=1 uv lock --check`.
- [ ] Run mirror-marker scan on `uv.lock`; the scan must find nothing.

## Task 4: Review And Verification

- [ ] Run focused docs tests.
- [ ] Run `tests/test_cli_docs.py`.
- [ ] Run `ruff check` and `ruff format --check` for `tests/test_cli_docs.py`.
- [ ] Run `git diff --check` for changed files.
- [ ] Create and run Stage 82 opencode code review.
- [ ] Fix Critical or Important findings.
- [ ] Run full verification:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --quiet -- uv.lock
```

## Task 5: Commit And Publish

- [ ] Stage only Stage 82 files:

```bash
git add -- \
  docs/dependency-mirrors.md \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-18-stage-82-mirror-lockfile-recovery-design.md \
  docs/superpowers/plans/2026-06-18-stage-82-mirror-lockfile-recovery-plan.md \
  docs/reviews/opencode-stage-82-plan-review-prompt.md \
  docs/reviews/opencode-stage-82-plan-review.md \
  docs/reviews/opencode-stage-82-code-review-prompt.md \
  docs/reviews/opencode-stage-82-code-review.md
```

- [ ] Confirm `uv.lock` is not staged.
- [ ] Run staged release hygiene, `git diff --cached --check`, and
  high-confidence secret scan.
- [ ] Commit with message `Document mirror lockfile recovery`.
- [ ] Push safely without persisting credentials.
- [ ] Verify local/remote `main` alignment and GitHub Actions success.
