# Claude Code Stage 34 Plan Review Prompt

You are reviewing the Stage 34 CI Typer help rendering fix plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Fix the GitHub Actions pytest failure after Stage 33 without changing runtime
CLI behavior, tests, dependencies, or `uv.lock`.

## Root Cause Evidence

GitHub Actions run `27482498492` for commit
`3a02785ae011f2209b7f817f78e7fcdad0d2884d` passed:

- Public lockfile check
- Install dependencies
- Lint
- Format check

It failed in `Tests` because Typer/Rich help output under `GITHUB_ACTIONS=true`
splits option names with ANSI sequences. Example local reproduction:

```bash
CI=true GITHUB_ACTIONS=true uv run pytest tests/test_cli.py::test_dashboard_command_help_lists_config_dir -q
```

This fails because raw output contains styled fragments such as
`-\x1b[...-config\x1b[...-dir` instead of contiguous `--config-dir`.

Typer's `rich_utils.py` sets `FORCE_TERMINAL=True` when `GITHUB_ACTIONS` is
present, but it also honors `_TYPER_FORCE_DISABLE_TERMINAL`.

Local verification:

```bash
CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest tests/test_cli.py -q
```

Result:

```text
189 passed
```

## Proposed Technical Approach

- Add `_TYPER_FORCE_DISABLE_TERMINAL: "1"` only to the GitHub Actions pytest
  step.
- Do not modify runtime CLI behavior.
- Do not rewrite tests.
- Do not touch dependencies, `uv.lock`, runtime source code, source connectors,
  scraping/crawling/platform automation, watchers, schedulers, source
  acquisition, ranking, demand proof, platform coverage verification, or social
  platform functionality.
- After push, query the GitHub Actions result for the new commit and debug
  again if it still fails.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-34-ci-typer-help-rendering-design.md`
- `docs/superpowers/plans/2026-06-14-stage-34-ci-typer-help-rendering-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 34 CI TYPER HELP FIX
```
