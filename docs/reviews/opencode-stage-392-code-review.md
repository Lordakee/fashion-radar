# Stage 392 Code Review - OpenCode Fallback

## Review Context

- Reviewer: local OpenCode fallback after the primary Claude Code attempt timed out without review output
- Model: `zhipuai-coding-plan/glm-5.2`
- Variant: `max`
- Scope: current Stage 392 uncommitted implementation and tests

## Critical

None.

## Important

None.

## Minor

None.

## Verification

- **Gate ordering** (`src/fashion_radar/cli.py:1550-1600`): `collect_configured_sources` is followed by `evaluate_daily_content_acceptance`; rejection occurs before `match_stored_items`, `write_daily_report_files`, `_write_row_one_site_from_cli_options`, `prune_stale_daily_report_files`, and `clean_old_data`. This matches the Stage 392 plan.
- **`typer.Exit` handling** (`src/fashion_radar/cli.py:1601-1608`): `except typer.Exit: raise` re-raises the deliberate rejection exit before the `ConfigError` and generic handlers.
- **Collector status and freshness semantics** (`src/fashion_radar/row_one/daily_content_acceptance.py:42-50`): only `CollectorRunStatus.SUCCESS` is counted; items are considered only inside the success branch; freshness implements `0 <= as_of - published_at <= max_fresh_item_age`. Reasons are ordered with successful collectors before fresh items. The evaluator has no I/O.
- **Config/template parity**: `configs/scoring.example.yaml` and `src/fashion_radar/templates/configs/scoring.example.yaml` contain identical `daily_content_acceptance` defaults and comments.
- **Settings** (`src/fashion_radar/settings.py:139-157`): all three thresholds use `gt=0` and `extra="forbid"`; the settings are mounted on `ScoringConfig` with `default_factory`, leaving the scoring formula and version unchanged.
- **Override behavior** (`src/fashion_radar/cli.py:1564-1576`): a rejected refresh exits with status 1 without the flag; `--allow-unaccepted-content` emits a warning to stderr and continues only for that invocation.
- **Test coverage**: evaluator tests cover accepted, empty, failed, skipped, zero-item, stale-boundary, future-dated, ordering, success-only counting, input immutability, and frozen verdict behavior. CLI tests cover rejection, preservation of live site/report bytes, downstream call suppression, override warning, and exact call order. Configuration tests cover defaults and non-positive thresholds.

## Verdict

**APPROVED.**
