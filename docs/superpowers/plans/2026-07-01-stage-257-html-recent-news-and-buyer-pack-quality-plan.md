# Stage 257 Plan: HTML Recent News Windowing And Buyer Pack Quality

## Objective

Fix obvious quality and correctness gaps left by the current uncommitted work:

- Make the generated HTML report's `Latest Collected News` section deterministic,
  report-window scoped, and covered by focused tests.
- Keep the new `buyer-brands` optional entity pack only if it is lintable,
  discoverable, package-checked, and covered by minimal regression tests.

This stage closes a report-quality gap in the existing `collect -> match ->
report` pipeline. It does not add new collection sources, social-platform
connectors, scraping, browser automation, demand proof, ranking semantics, or
platform coverage verification.

## Architecture

- Keep `render_html_report()` as a pure renderer that accepts already-selected
  recent item dictionaries.
- Keep `write_daily_report_files()` responsible for assembling report artifacts
  from local SQLite state.
- Scope recent HTML items to the same dated report context as the daily report:
  `as_of - scoring.current_window_days < collected_at <= as_of`.
- Continue returning only Markdown and JSON paths from `write_daily_report_files`
  for API compatibility in this node, but document and test that the companion
  HTML artifact is written to the existing date-derived path.
- Treat `configs/entity-packs/buyer-brands.example.yaml` as an optional local
  matching template, parallel to the existing fashion watchlist pack.

## Technical Stack

- Python 3.12 project managed by `uv`.
- SQLAlchemy Core for local SQLite reads.
- Existing Pydantic models and YAML entity-pack loading/linting.
- Existing HTML renderer helpers for escaping and URL safety.
- Pytest for regression tests.
- Ruff for lint/format checks.
- Review gate: local Claude Code with `--effort max`; opencode GLM 5.2 max for
  plan revision per `docs/REVIEW_PROTOCOL.md`.

## Implementation Method

1. Add focused report-renderer tests for `render_html_report(...,
   recent_items=...)`:
   - Shows the `Latest Collected News` section.
   - Escapes title/source/summary.
   - Escapes query-string `&` in links.
   - Drops unsafe `javascript:` links.
   - Truncates long recent summaries before the tail marker.
2. Add workflow integration coverage for `write_daily_report_files()`:
   - Writes the date-derived HTML artifact.
   - Includes recent local DB items in descending `collected_at` order.
   - Excludes items newer than `as_of`.
   - Excludes items outside `scoring.current_window_days`.
   - Does not leak long-summary tail markers in HTML.
3. Fix `write_daily_report_files()` recent-item selection to apply the same
   report-window bounds:
   - Compute `window_start = as_of_utc - timedelta(days=scoring.current_window_days)`.
   - Select `items_table.c.collected_at` along with source, URL, title, and
     summary.
   - Filter with `items_table.c.collected_at > window_start` and
     `items_table.c.collected_at <= as_of_utc`.
   - Keep descending `collected_at` order and the 50-item cap.
4. Keep and harden `buyer-brands.example.yaml`:
   - Add minimal tests that load/lint it and assert representative buyer brands,
     Chinese designer brands, and trend entries exist.
   - Ensure guarded aliases are used for broad/common names.
   - Mention the pack in entity-pack docs using the existing optional local
     configuration-template framing, while preserving current boundary phrases
     and the `fashion-radar collect` doc guard.
   - Add `configs/entity-packs/buyer-brands.example.yaml` to package/archive
     expectations and confirm the real sdist contains it.
5. Run focused verification:
   - `uv --no-config run --frozen pytest tests/test_reports.py tests/test_workflows.py tests/test_entity_packs.py tests/test_entity_pack_lint.py tests/test_entity_packs_docs.py tests/test_package_archives.py -q`
   - `uv --no-config run --frozen ruff check ...`
   - `uv --no-config run --frozen ruff format --check ...`
   - `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
6. Request Claude Code review of the new code and docs. Fix critical and
   important findings before commit.

## Scope Out

- No connector/source acquisition changes.
- No social-platform scraping/API/browser behavior.
- No scheduling changes.
- No compliance-review product feature.
- No `uv.lock` or dependency changes.
- No public API return-shape change for `write_daily_report_files()` in this
  node.
