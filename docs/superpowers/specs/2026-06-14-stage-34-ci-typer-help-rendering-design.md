# Stage 34 CI Typer Help Rendering Design

## Goal

Fix the remaining GitHub Actions pytest failure after Stage 33.

## Root Cause

Stage 33 fixed the fresh-runner lockfile/install order. The next CI run
`27482498492` advanced through lockfile check, install, lint, and format, then
failed in the pytest step.

The failures are CLI help assertions such as:

```text
assert "--config-dir" in result.output
```

Under `GITHUB_ACTIONS=true`, Typer's `rich_utils` sets `FORCE_TERMINAL=True`.
That causes Rich ANSI styling to split option text across escape sequences, for
example `--config-dir` is rendered as styled fragments rather than a contiguous
raw substring. The application help content is present, but raw substring tests
cannot match it.

Local reproduction:

```bash
CI=true GITHUB_ACTIONS=true uv run pytest tests/test_cli.py::test_dashboard_command_help_lists_config_dir -q
```

This fails. Setting Typer's documented/internal terminal override passes:

```bash
CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest tests/test_cli.py -q
```

Result:

```text
189 passed
```

## Scope

Stage 34 is a CI/docs hygiene fix.

In scope:

- Set `_TYPER_FORCE_DISABLE_TERMINAL=1` for the GitHub Actions pytest step.
- Document the CI rendering reason in Stage 34 artifacts and changelog.
- Verify local reproduction with `CI=true GITHUB_ACTIONS=true`.
- Confirm GitHub Actions passes after push.

Out of scope:

- Runtime CLI behavior changes.
- Test expectation rewrites.
- Dependency or `uv.lock` changes.
- Source connectors, scraping, crawling, browser automation, login/cookie
  flows, watchers, schedulers, source acquisition, source ranking, demand proof,
  or platform coverage verification.

## Design

Only the CI test step should get the Typer override:

```yaml
      - name: Tests
        env:
          _TYPER_FORCE_DISABLE_TERMINAL: "1"
        run: uv run pytest
```

This keeps production CLI behavior untouched while making test output stable in
GitHub Actions.

## Verification

Required checks:

```bash
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest tests/test_cli.py -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
```

After push, poll the GitHub Actions run for the new commit. If it fails, return
to systematic debugging with job logs.
