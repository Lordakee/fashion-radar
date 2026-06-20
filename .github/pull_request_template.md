## Summary

-

## Linked Issue

-

## Change Type

- [ ] Bug fix
- [ ] Feature
- [ ] Docs
- [ ] Tests
- [ ] Refactor
- [ ] Packaging/CI
- [ ] Security

## Affected Areas

- [ ] CLI
- [ ] Config
- [ ] Collectors
- [ ] Matcher
- [ ] Scoring
- [ ] Reports
- [ ] Dashboard
- [ ] Docs
- [ ] Packaging

## Source-Boundary Impact

Describe any source, fetching, robots, attribution, storage, or platform-boundary
impact.

## User-Visible Behavior

Describe CLI/config/report/dashboard behavior changes.

## Boundary Checklist

- [ ] Keeps v0.1.0 core limited to RSS/GDELT unless explicitly documenting future opt-in work.
- [ ] Adds no social scraping, login cookies, account/proxy pools, CAPTCHA bypass, paywall bypass, or private data collection.
- [ ] Preserves source attribution and snippets/metadata-only report behavior.
- [ ] Does not commit secrets, cookies, session files, browser profiles, local DBs, generated reports, build artifacts, or private config.
- [ ] Keeps `uv.lock` free of mirror URLs.

## Verification

- [ ] `UV_NO_CONFIG=1 uv lock --check`
- [ ] `UV_NO_CONFIG=1 uv sync --locked --dev`
- [ ] `UV_NO_CONFIG=1 uv sync --locked --dev --check`
- [ ] `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- [ ] `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- [ ] `uv --no-config run --frozen ruff check .`
- [ ] `uv --no-config run --frozen ruff format --check .`
- [ ] `uv --no-config run --frozen pytest`
- [ ] If packaging/templates changed:
  - `tmp_build="$(mktemp -d)"`
  - `uv --no-config build --out-dir "$tmp_build"`
  - `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`
  - Installed-wheel smoke from `"$tmp_build"/*.whl` for `fashion-radar --help`, `init`, `doctor`, and `fashion_radar.templates/daily_report.md`.
- [ ] If dashboard/dependencies changed: install/resolve `dashboard` extra and import `fashion_radar.dashboard.app` plus `fashion_radar.dashboard.queries` without launching Streamlit.

## Docs

- [ ] README/docs updated where behavior changed.
- [ ] `CHANGELOG.md` updated for user-visible changes.
- [ ] Source-boundary/security docs updated for connector, dashboard, or data-handling changes.
