# Stage 36 Report And Dashboard Quality Design

## Goal

Close the highest product-completion gaps found in the read-only audit without
adding source connectors, scraping, platform automation, or schema migrations.

## Scope

In scope:

- Enforce a deterministic report-safe snippet cap on every
  `RepresentativeItem.summary` used by entity and candidate reports.
- Expose entity heat score components in JSON and Markdown reports.
- Add a local recent-signals dashboard query and Daily Brief table.
- Expand dashboard entity mention tabs to all configured `EntityType` values:
  brand, designer, celebrity, product, category, and trend.
- Update focused tests and dashboard docs.
- Add Stage 36 plan/review artifacts.

Out of scope:

- Runtime source collection changes.
- Social connectors, platform automation, scraping, crawling, login/cookie
  flows, proxy pools, CAPTCHA bypass, source acquisition, source ranking, demand
  proof, watchers, or schedulers.
- Database schema changes.
- Manual signal `platform` persistence. That requires a schema migration and is
  deferred to a separate Stage 37 plan.
- Dependency or `uv.lock` changes.

## Design

### Report-Safe Snippets

Use `src/fashion_radar/models/report.py` as the single boundary for report
snippets. Add:

- `REPORT_SNIPPET_MAX_CHARS = 500`
- `report_safe_snippet(value: str | None) -> str | None`
- a `RepresentativeItem.summary` field validator that collapses whitespace,
  trims leading/trailing space, and truncates longer text to a maximum of 500
  characters with ASCII `...`.

This covers entity reports, candidate reports, CLI JSON/Markdown report output,
daily report files, and dashboard rows that reuse the helper.

### Score Components

`EntityHeatMetric` already computes:

- `weighted_mention_component`
- `growth_component`
- `source_diversity_component`
- `high_weight_component`

Add those fields to `EntityReport`, populate them in `_entity_report()`, and
render them in Markdown under each entity. This makes the README/dashboard claim
about transparent score components true.

### Dashboard Recent Signals

Add `recent_signals(data_dir: Path, limit: int = 20)` in
`src/fashion_radar/dashboard/queries.py`. It reads from local SQLite only,
returns public/local review fields, sorts by `collected_at desc, id desc`, and
caps summaries with `report_safe_snippet()`.

Render those rows in the Daily Brief tab under the existing metrics. Missing
databases return an empty list without creating files.

### Dashboard Entity Tabs

Drive mention tabs from `EntityType` instead of hard-coded brand/product/
celebrity tabs. Keep the existing mention-count query and tab style, but cover
all entity types.

## Verification

Focused verification:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py -q
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py
```

Release verification:

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
