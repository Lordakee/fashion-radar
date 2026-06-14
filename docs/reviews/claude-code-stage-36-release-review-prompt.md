# Claude Code Stage 36 Release Review Prompt

You are reviewing the completed Stage 36 report/dashboard quality changes for
the `fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release review only; do not edit files.
- Treat Critical and Important findings as blockers.
- Review tracked diffs and untracked Stage 36 plan/review artifacts.

## Goal

Make report output safer and more transparent, and make the local dashboard show
recent signals plus all entity-type mention tabs.

## Changed Files To Review

- `src/fashion_radar/models/report.py`
- `src/fashion_radar/reports.py`
- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_reports.py`
- `tests/test_workflows.py`
- `tests/test_dashboard.py`
- `docs/dashboard.md`
- `docs/superpowers/specs/2026-06-14-stage-36-report-dashboard-quality-design.md`
- `docs/superpowers/plans/2026-06-14-stage-36-report-dashboard-quality-plan.md`
- `docs/reviews/claude-code-stage-36-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-36-plan-review.md`
- `docs/reviews/claude-code-stage-36-release-review-prompt.md`

## Scope Boundaries

Stage 36 must remain local report/dashboard quality only:

- No dependency or `uv.lock` changes.
- No database schema or migration changes.
- No source connectors, scraping, crawling, browser automation, login/cookie
  flows, account automation, proxy pools, CAPTCHA bypass, source acquisition,
  source ranking, demand proof, watchers, schedulers, external platform API
  integrations, or social-platform functionality.
- No generated data/report/build artifacts.

## Implementation Summary

- Added `REPORT_SNIPPET_MAX_CHARS = 500` and `report_safe_snippet()` in
  `src/fashion_radar/models/report.py`.
- Added a `RepresentativeItem.summary` validator that collapses whitespace and
  caps report snippets with ASCII `...`.
- Added entity score component fields to `EntityReport`.
- Populated score components from `EntityHeatMetric` in `_entity_report()`.
- Rendered score components in Markdown entity sections.
- Added `recent_signals(data_dir, limit=20)` to dashboard queries. It checks for
  DB existence before creating an engine, returns only public/local review
  fields, orders by `collected_at desc, id desc`, limits rows, and caps summaries
  with `report_safe_snippet()`.
- Derived dashboard entity mention tabs from `EntityType`, covering brand,
  designer, celebrity, product, category, and trend.
- Added recent local signals to the Daily Brief dashboard tab.
- Updated dashboard docs to distinguish Daily Brief retained rows from Candidate
  Signals/report and entity-match requirements.

## TDD And Review Evidence

Report RED command:

```text
UV_NO_CONFIG=1 uv run pytest tests/test_reports.py tests/test_workflows.py -q -k "snippet or score_component or report_safe or caps_stored"
```

Observed RED result:

```text
ImportError: cannot import name 'REPORT_SNIPPET_MAX_CHARS'
```

Dashboard worker RED result:

```text
UV_NO_CONFIG=1 uv run pytest tests/test_dashboard.py -q -k "recent_signals or tab or dashboard_queries"
F..FF..
3 failed, 4 passed, 19 deselected
Expected failures: missing Designer Mentions tab and missing recent_signals.
```

Read-only diff reviewer result:

```text
Critical Findings: None.
Important Findings: None.
Minor Finding: docs/dashboard.md wording contradicted Daily Brief recent-signal behavior.
```

The docs wording was fixed after that finding.

## Verification Evidence

Fresh commands already run successfully:

```text
UV_NO_CONFIG=1 uv run pytest tests/test_reports.py tests/test_workflows.py -q
14 passed in 1.00s

UV_NO_CONFIG=1 uv run pytest tests/test_dashboard.py -q -k "recent_signals or tab or dashboard_queries"
7 passed, 19 deselected in 0.57s

UV_NO_CONFIG=1 uv run pytest tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py -q
40 passed in 1.36s

UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py
All checks passed!

UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_reports.py tests/test_workflows.py tests/test_dashboard.py
7 files already formatted

UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check

UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
578 passed in 14.18s

UV_NO_CONFIG=1 uv run ruff check .
All checks passed!

UV_NO_CONFIG=1 uv run ruff format --check .
92 files already formatted

git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
diff-scoped scope, source-acquisition/platform-automation, secret, and ASCII scans
```

## Review Focus

Please review:

- Whether snippet capping is applied at the correct report boundary and does not
  republish full RSS/manual summaries.
- Whether entity score components are exposed correctly in JSON and Markdown.
- Whether `recent_signals()` avoids creating missing data directories/DBs,
  returns only intended public/local review fields, and orders rows correctly.
- Whether dashboard tabs cover all `EntityType` values without breaking existing
  candidate/trend/source-health behavior.
- Whether docs accurately describe Daily Brief recent rows versus report and
  match requirements.
- Whether the diff stays inside the Stage 36 scope boundaries.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 36 COMMIT AND PUSH
```
