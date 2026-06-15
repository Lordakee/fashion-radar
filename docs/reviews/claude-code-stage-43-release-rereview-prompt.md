# Claude Code Stage 43 Release Rereview Prompt

You are rereviewing Stage 43 before commit and push after the first release
review withheld approval.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a read-only release/code/docs rereview; do not edit files.
- Treat Critical and Important findings as blockers.

## Previous Release Review Findings

The first release review withheld approval because
`docs/reviews/claude-code-stage-43-release-review.md` appeared empty while the
review command was still writing to it.

It also raised a Minor finding that `docs/github-upload-checklist.md` used a
shorter Claude Code command than `AGENTS.md` and `docs/REVIEW_PROTOCOL.md`
because it omitted `--tools Read,Grep,Glob,LS,Bash`.

## Fixes Applied

- `docs/reviews/claude-code-stage-43-release-review.md` now contains the full
  first release review result and is no longer an empty artifact.
- `docs/github-upload-checklist.md` now uses the same Claude Code command form
  as `AGENTS.md` and `docs/REVIEW_PROTOCOL.md`.
- Stage 43 spec/plan were updated to reflect that active workflow command
  alignment is in scope when review exposes drift.

## Expected Scope

- Active docs restore Claude Code with `--effort max` as the plan and
  code/release review authority.
- Active workflow docs no longer require active opencode or GLM 5.2 review
  authority.
- `tests/test_review_protocol_docs.py` guards only active workflow docs, not
  historical audit records.
- Historical `docs/reviews/opencode-stage-40-*` records and old staged specs/plans
  remain untouched.
- No runtime, source acquisition, scraping/crawling/platform automation, package,
  lockfile, CI, database, dashboard, or generated-data behavior changed.

## Verification Already Rerun

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_review_protocol_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_review_protocol_docs.py
if rg -n "local opencode|opencode run|zhipuai-coding-plan/glm-5.2|GLM 5.2|docs/reviews/opencode-stage-N" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md; then echo "FAIL: active opencode authority terms remain"; exit 1; else echo "No active opencode authority terms found"; fi
rg -n "Claude Code|claude --effort max|claude-code-stage-N|--tools Read,Grep,Glob,LS,Bash" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
git diff --check
```

Observed results:

- Combined docs tests: `6 passed`.
- Ruff check and format check passed.
- No active opencode authority terms were found.
- Positive active-doc search found Claude Code, `--effort max`,
  `claude-code-stage-N`, and `--tools Read,Grep,Glob,LS,Bash` in the active
  workflow docs.
- Diff check passed.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if Stage 43 is acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 43 COMMIT AND PUSH
```
