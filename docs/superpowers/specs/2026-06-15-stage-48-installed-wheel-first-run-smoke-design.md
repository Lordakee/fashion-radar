# Stage 48 Installed-Wheel First-Run Smoke Design

## Goal

Stage 48 adds an installed-wheel mode to the deterministic first-run smoke so
the release gate proves the packaged CLI can execute the same local sample flow
that the source checkout can execute.

## Problem

Stage 47 added `scripts/check_first_run_smoke.py`, but it intentionally prepends
`repo_root/src` to `PYTHONPATH`. That is correct for source-checkout validation,
but it does not prove an installed wheel can run the full first-run sample path.

The current CI installed-wheel step validates top-level help, module help,
`init`, `doctor`, packaged template access, and dashboard imports. It does not
prove that the built wheel can:

- import checked-in sample signals through the installed CLI;
- match and report from an installed package;
- load packaged report templates during report generation;
- run candidate/trend JSON commands from the installed package;
- execute the directory community handoff dry-run path from the installed
  package.

## Scope

Add a source-checkout script mode that runs the existing first-run smoke flow
using an installed Python executable without adding the checkout `src/` path to
`PYTHONPATH`.

## Non-Goals

- No scraping, crawling, browser automation, account login, cookie/session
  management, proxy support, CAPTCHA handling, platform connector work, or
  hidden source access.
- No live `collect`, RSS, GDELT, dashboard server launch, scheduler, monitor,
  or external service calls.
- No package publishing or release tagging.
- No dependency, lockfile, database schema, scoring, matching, report template,
  source config, or entity config behavior change.
- No compliance-review feature. The smoke remains a local release-confidence
  check.

## Technical Approach

- Extend `scripts/check_first_run_smoke.py` with an `--installed` flag.
- Keep the same `SmokeContext` and deterministic command sequence.
- Add a `source_checkout` boolean to the command environment behavior:
  - default/source mode prepends `repo_root/src` to `PYTHONPATH`;
  - installed mode must not prepend `repo_root/src`, and must remove any
    inherited `repo_root/src` entry from `PYTHONPATH` before running commands.
- Add an installed-mode import-origin preflight using the target Python. The
  preflight imports `fashion_radar`, resolves `fashion_radar.__file__`, and
  fails if that path is inside `repo_root/src`.
- Keep `cwd=repo_root` so checked-in examples remain available by path.
- Keep all runtime config/data/reports/exports in `tempfile.TemporaryDirectory`.
- Keep the default repo `data/` and `reports/` hash guard active in both modes.
- Update CI's build/install step to run:
  `"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed`
- Update the upload checklist and README automated smoke wording to document
  both source-checkout and installed-wheel forms.

## Expected User-Visible Behavior

Source checkout:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Installed wheel after a local build/install:

```bash
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Both commands should print:

```text
First-run sample smoke passed.
```

## Verification

Focused:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Installed wheel:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Release:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```
