# Claude Code Stage 16 Code Rereview Prompt

You are rereviewing Stage 16 after the first code review approved upload with
two Minor test-hardening suggestions. Run this as a read-only code review. Do
not edit files, do not commit, do not call the network, do not run collectors,
do not create directories, and do not execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-16-code-rereview-prompt.md
```

## Prior Review

The first code review returned `Approved for Stage 16 upload` with no Critical
or Important findings. It suggested two Minor improvements:

1. Add a focused test for JSON object top-level strictness with
   `{"items": [...], "extra": ...}`.
2. Add a dedicated CLI test proving warning-only files exit `0` without
   `--strict`.

## Changes Since Approval

Test-only hardening:

- `tests/test_community_signal_lint.py`
  - Added `test_json_object_with_extra_top_level_key_is_invalid_file_error`.
- `tests/test_cli.py`
  - Added `test_community_signal_lint_non_strict_exits_zero_on_warnings`.

No production code or docs were changed after the approved code review.

## Verification Already Run After These Test Changes

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
codegraph status
```

Observed results:

- `git diff --check`: passed.
- `pytest`: 344 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `codegraph status`: index up to date.

## Response Format

Start with one of:

- `Approved for Stage 16 upload`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before upload.
- `Important:` issues that should be fixed before upload.
- `Minor:` optional improvements.
