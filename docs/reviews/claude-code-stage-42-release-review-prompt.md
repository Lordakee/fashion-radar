# Claude Code Stage 42 Release Review Prompt

You are reviewing the Stage 42 CLI docs drift guards implementation for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Add pytest guards that keep Stage 41 CLI docs and upload checklist coverage in
sync with the actual public Typer command surface.

## Implementation Summary

- Added `tests/test_cli_docs.py`.
- The new tests derive public command names from `typer.main.get_command(app)`
  and filter hidden Click/Typer commands.
- The new tests verify:
  - `docs/cli-reference.md` lists every current public command and shared path
    environment variable.
  - `docs/github-upload-checklist.md` installed-wheel help loop matches the
    current public command set.
  - README links `docs/cli-reference.md` and no longer links the historical
    Stage 31 release gate as current docs.
  - Selected repo-local Markdown command examples keep required path flags
    together for `match`, `report`, `run`, `candidates`, `trends`, and
    `clean-old-data`.
- Adjusted `docs/cli-reference.md` command-name formatting from
  `` `command ARG` `` to `` `command` ARG `` so command names can be checked
  precisely without changing meaning.
- Kept the change test-focused. No runtime behavior, source acquisition,
  scraping/crawling/platform automation, schedulers, watchers, monitors,
  external services, dependencies, lockfiles, or CI workflow behavior changed.

## Files To Review

- `tests/test_cli_docs.py`
- `docs/cli-reference.md`
- `docs/superpowers/specs/2026-06-15-stage-42-cli-docs-drift-guards-design.md`
- `docs/superpowers/plans/2026-06-15-stage-42-cli-docs-drift-guards-plan.md`
- `docs/reviews/claude-code-stage-42-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-42-plan-review.md`
- `docs/reviews/claude-code-stage-42-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-42-plan-rereview.md`

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py tests/test_entity_packs.py tests/test_scheduling.py -q
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py::test_cli_help tests/test_cli.py::test_dashboard_command_help_lists_config_dir -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

All commands above exited successfully.

## Review Questions

1. Does `tests/test_cli_docs.py` correctly guard the current public CLI docs
   surface without hard-coding the command list?
2. Does it filter hidden commands and include `clean-old-data --data-dir` as
   required by the approved plan?
3. Are the Markdown parsers scoped tightly enough to useful docs drift checks
   without becoming a general-purpose shell parser?
4. Does the change remain test-focused and avoid runtime/source-acquisition/
   scraping/platform-automation behavior?
5. Is this acceptable to commit and push after the saved release review result
   is populated?

## Required Output

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if this implementation is acceptable to commit and push, include
this exact phrase:

```text
APPROVED FOR STAGE 42 COMMIT AND PUSH
```
