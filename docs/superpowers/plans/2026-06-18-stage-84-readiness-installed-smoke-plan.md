# Stage 84 Readiness Installed Smoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the upload checklist installed-wheel smoke include the
`external-tool-readiness --adapter instaloader --format table` command it
already claims to cover, and pin exact table/JSON installed-path commands in
docs tests.

**Architecture:** This is docs/test-only. The upload checklist owns the
installed-wheel smoke script; `tests/test_cli_docs.py` owns drift coverage for
that script. No runtime command behavior changes.

**Tech Stack:** Markdown docs, pytest docs drift tests, Ruff, uv.

---

## File Map

- Modify `docs/github-upload-checklist.md`.
- Modify `tests/test_cli_docs.py`.
- Add Stage 84 spec/plan/review artifacts under `docs/superpowers/` and
  `docs/reviews/`.
- Do not modify `src/`, dependency manifests, `uv.lock`, CI workflows,
  `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md`.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-84-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-84-plan-review-prompt.md)" > docs/reviews/opencode-stage-84-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Installed-Wheel Readiness Table Smoke

- [ ] In `docs/github-upload-checklist.md`, find the installed-wheel smoke
  readiness block:

```bash
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --help
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format json
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter rednote_mcp --format json
```

- [ ] Insert the table smoke command immediately after the help command and
  before the JSON command:

```bash
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format table
```

- [ ] Keep the existing JSON `instaloader` and `rednote_mcp` commands.

## Task 3: Tighten Docs Drift Test

- [ ] In `tests/test_cli_docs.py`, update
  `test_external_tool_readiness_upload_checklist_help_loop_and_smoke`.
- [ ] Replace the single exact JSON `instaloader` assertion with a loop that
  pins both exact installed-path commands:

```python
for format_name in ("table", "json"):
    assert (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-readiness '
        f"--adapter instaloader --format {format_name}"
    ) in checklist
```

- [ ] Preserve the existing assertions for:
  - `external-tool-readiness` in `_upload_checklist_help_loop_commands()`
  - `"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --help`
  - `"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter rednote_mcp`
  - `scripts/check_first_run_smoke.py`

## Task 4: Focused Verification

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_upload_checklist_help_loop_and_smoke -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_are_linked_and_bounded -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check -- docs/github-upload-checklist.md tests/test_cli_docs.py
```

## Task 5: Code Review And Full Verification

- [ ] Create `docs/reviews/opencode-stage-84-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-84-code-review-prompt.md)" > docs/reviews/opencode-stage-84-code-review.md
```

- [ ] Fix Critical or Important findings.
- [ ] Run full verification:

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

`env -u ALL_PROXY -u all_proxy` avoids the current local SOCKS proxy inherited
by `httpx` tests; it does not change project dependencies or behavior.

## Task 6: Commit And Publish

- [ ] Stage only Stage 84 files:

```bash
git add -- \
  docs/github-upload-checklist.md \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-18-stage-84-readiness-installed-smoke-design.md \
  docs/superpowers/plans/2026-06-18-stage-84-readiness-installed-smoke-plan.md \
  docs/reviews/opencode-stage-84-plan-review-prompt.md \
  docs/reviews/opencode-stage-84-plan-review.md \
  docs/reviews/opencode-stage-84-code-review-prompt.md \
  docs/reviews/opencode-stage-84-code-review.md
```

- [ ] Confirm `uv.lock` is not staged.
- [ ] Run staged release hygiene, whitespace check, and secret scan.
- [ ] Commit with message `Add readiness installed smoke coverage`.
- [ ] Push safely without persisting credentials.
- [ ] Verify local/remote `main` alignment, GitHub Actions success, clean
  worktree, mirror-free `uv.lock`, and no token/extraheader in git config.
