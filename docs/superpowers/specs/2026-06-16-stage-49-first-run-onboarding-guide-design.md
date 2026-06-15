# Stage 49 First-Run Onboarding Guide Design

## Goal

Stage 49 makes the GitHub first-run experience explicit and copy-pasteable for
new users by splitting the current Quickstart into clear paths:

- verify a source checkout without writing repo-local runtime output;
- verify an installed wheel before release;
- run the manual repo-local sample flow to create inspectable reports;
- open the optional dashboard against that sample output;
- reset local sample artifacts when needed.

## Problem

Stages 47 and 48 added deterministic first-run smokes for source checkouts and
installed wheels. The README now documents both smokes plus the manual sample
flow, but the paths are close together and can read like one long sequence. A
new GitHub user can reasonably miss which path produces visible output for the
dashboard, which path is CI/release confidence only, and why automated smokes
should not modify repo-local `data/` or `reports/`.

The release checklist also documents the first-run smokes, but it does not use
the same strong boundary wording as README around browser/account/platform
automation and external services.

## Scope

- Add `docs/first-run.md` as the canonical first-run guide.
- Update README Quickstart to link the guide and present a small chooser.
- Keep README's manual sample and smoke commands, but clarify expected outputs,
  temporary runtime behavior, dashboard next step, and reset guidance.
- Add a small CLI reference note connecting repo-local path flags to the
  first-run guide.
- Add release checklist wording so source-checkout and installed-wheel smokes
  have the same stated boundaries.
- Add documentation drift tests for the new guide, exact smoke commands, setup
  path flags, expected report paths, dashboard command, reset guidance, and
  smoke boundaries.

## Non-Goals

- No runtime code, CLI behavior, database schema, matching, scoring, reporting,
  dashboard behavior, source config, entity config, dependency, or lockfile
  changes.
- No scraping, crawling, browser automation, account login, cookie/session
  handling, proxy support, CAPTCHA handling, platform connector work, hidden
  source access, source acquisition, live social platform search, scheduler
  changes, monitor/watch behavior, or external service integration.
- No compliance-review feature.
- No broad docs reorganization or new docs index beyond adding the new guide to
  README's documentation list.
- No GitHub Actions behavior change. CI already runs the source-checkout and
  installed-wheel first-run smokes.

## Technical Approach

- Keep `docs/first-run.md` as user-facing documentation only.
- Reuse existing exact smoke commands:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

```bash
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

- Document that both automated smokes:
  - use checked-in sample files;
  - create temporary config, data, report, and export directories;
  - verify temporary `fashion-radar-2026-06-13.md` and
    `fashion-radar-2026-06-13.json` report artifacts;
  - print `First-run sample smoke passed.`;
  - should not create files under repo `data/` or `reports/`;
  - do not run `collect`, `run`, `dashboard`, scheduler/monitoring commands,
    scraping/crawling, browser automation, account login, cookies/sessions,
    source/platform connectors, platform automation, or external services.
- Document that the manual repo-local sample flow is the path for visible
  output and dashboard inspection. It writes:
  - `configs/sources.yaml`;
  - `configs/entities.yaml`;
  - `configs/scoring.yaml`;
  - `data/fashion-radar.sqlite`;
  - `reports/fashion-radar-2026-06-13.md`;
  - `reports/fashion-radar-2026-06-13.json`.
- Document reset guidance with explicit repo-local generated paths and a warning
  that reset deletes local experiment state. Keep `data/README.md` and
  `reports/README.md`.
- Extend `tests/test_cli_docs.py` only. Reuse the existing markdown command
  parsing helpers and avoid duplicating the runtime smoke.

## Expected User-Visible Behavior

New GitHub users can choose the right first-run path without reading the whole
README:

- "I want to verify this checkout" -> source first-run smoke.
- "I want to inspect sample output" -> manual repo-local sample flow.
- "I want to view the sample dashboard" -> dashboard extra after manual sample.
- "I want to verify a release package" -> installed-wheel smoke.
- "I want to start over" -> reset generated repo-local sample artifacts.

## Verification

Focused:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
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
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```
