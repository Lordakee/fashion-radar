# Claude Code Stage 34 Release Review Prompt

You are reviewing the completed Stage 34 CI Typer help rendering fix for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release/code review only; do not edit files.
- Treat Critical and Important findings as blockers for commit and push.

## Goal

Fix the GitHub Actions pytest failure caused by Typer/Rich forced terminal
rendering under `GITHUB_ACTIONS=true`, without changing runtime CLI behavior,
tests, dependencies, or `uv.lock`.

## Root Cause Evidence

GitHub Actions run `27482498492` for commit
`3a02785ae011f2209b7f817f78e7fcdad0d2884d` passed:

- Public lockfile check
- Install dependencies
- Lint
- Format check

It failed in `Tests` because Typer/Rich help output under `GITHUB_ACTIONS=true`
split option names with ANSI sequences. Local reproduction:

```bash
CI=true GITHUB_ACTIONS=true uv run pytest tests/test_cli.py::test_dashboard_command_help_lists_config_dir -q
```

The raw help output contains styled fragments such as
`-\x1b[...-config\x1b[...-dir` instead of contiguous `--config-dir`.

Typer's `rich_utils.py` sets `FORCE_TERMINAL=True` when `GITHUB_ACTIONS` is
present, and honors `_TYPER_FORCE_DISABLE_TERMINAL`.

## Approved Plan Evidence

- Stage 34 design:
  `docs/superpowers/specs/2026-06-14-stage-34-ci-typer-help-rendering-design.md`
- Stage 34 plan:
  `docs/superpowers/plans/2026-06-14-stage-34-ci-typer-help-rendering-plan.md`
- Stage 34 plan approval:
  `docs/reviews/claude-code-stage-34-plan-review.md`

The plan review contains:

```text
APPROVED FOR STAGE 34 CI TYPER HELP FIX
```

## Files To Review

- `.github/workflows/ci.yml`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-14-stage-34-ci-typer-help-rendering-design.md`
- `docs/superpowers/plans/2026-06-14-stage-34-ci-typer-help-rendering-plan.md`
- `docs/reviews/claude-code-stage-34-*.md`

## Review Checklist

Check that:

- The GitHub Actions `Tests` step sets `_TYPER_FORCE_DISABLE_TERMINAL: "1"`.
- The override is scoped to pytest and does not affect lint, format, build, or
  installed-wheel smoke.
- Runtime CLI code and tests are unchanged.
- Dependencies, `pyproject.toml`, and `uv.lock` are unchanged.
- Changelog accurately describes the CI-only test stabilization.
- There are no source connector, scraping, crawling, platform automation,
  watcher, scheduler, source acquisition, source ranking, demand proof, platform
  coverage verification, or social-platform functionality changes.
- There are no secrets or generated artifacts in the diff.

## Verification Evidence

The CI-specific reproduction with the Typer override exited `0`:

```bash
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest tests/test_cli.py -q
```

Result:

```text
189 passed
```

Full verification with user-level uv config disabled exited `0`:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Test result:

```text
572 passed
```

Diff-scoped boundary and secret scans returned no matches. Runtime/dependency
diff checks returned no files. `uv.lock` is clean after verification.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 34 COMMIT AND PUSH
```
