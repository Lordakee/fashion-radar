# Claude Code Stage 43 Release Review Prompt

You are reviewing Stage 43 before commit and push.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a read-only release/code/docs review; do not edit files.
- Treat Critical and Important findings as blockers.

## User Rule Change

The user canceled the temporary opencode/GLM 5.2 review rule and asked to return
review work to local Claude Code.

## Expected Scope

- Active docs should restore Claude Code with `--effort max` as the plan and
  code/release review authority.
- `AGENTS.md` and `docs/REVIEW_PROTOCOL.md` should no longer require active
  opencode or GLM 5.2 review authority.
- `docs/github-upload-checklist.md` should remain aligned with Claude Code final
  review instructions.
- `tests/test_review_protocol_docs.py` should guard only active workflow docs,
  not historical audit records.
- Historical `docs/reviews/opencode-stage-40-*` records and old staged specs/plans
  should remain untouched.
- No runtime, source acquisition, scraping/crawling/platform automation, package,
  lockfile, CI, database, dashboard, or generated-data behavior should change.

## Review Inputs

- Base commit: `fe72e76f60a9d6bac7c7d2537994b449eec87eda`
- Inspect the working tree diff for:
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `tests/test_review_protocol_docs.py`
  - `docs/superpowers/specs/2026-06-15-stage-43-claude-review-protocol-restore-design.md`
  - `docs/superpowers/plans/2026-06-15-stage-43-claude-review-protocol-restore-plan.md`
  - `docs/reviews/claude-code-stage-43-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-43-plan-review.md`
  - `docs/reviews/claude-code-stage-43-plan-rereview-prompt.md`
  - `docs/reviews/claude-code-stage-43-plan-rereview.md`

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_review_protocol_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_review_protocol_docs.py
if rg -n "local opencode|opencode run|zhipuai-coding-plan/glm-5.2|GLM 5.2|docs/reviews/opencode-stage-N" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md; then echo "FAIL: active opencode authority terms remain"; exit 1; else echo "No active opencode authority terms found"; fi
rg -n "Claude Code|claude --effort max|claude-code-stage-N" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_review_protocol_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_review_protocol_docs.py
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Observed results:

- New guard red-green was verified: it failed before the docs edits and passed
  after `AGENTS.md` and `docs/REVIEW_PROTOCOL.md` were restored.
- Focused test: `2 passed`.
- Combined docs tests: `6 passed`.
- Ruff check and format check passed.
- No active opencode authority terms were found in the active workflow docs.
- Public lockfile stayed unchanged.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if Stage 43 is acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 43 COMMIT AND PUSH
```
