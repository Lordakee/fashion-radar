# opencode Stage 264 Plan Rereview Prompt

You are rereviewing the revised Fashion Radar Stage 264 plan in read-only mode. Do not edit files.

## Context

The first opencode plan review found:

- C1: circular import risk from `readiness.py` importing `templates.py` while `templates.py` imports readiness.
- I1: `row-one preview` could not compute readiness because `write_row_one_site_files()` returns `RowOneRenderResult`, not `RowOneEdition`.
- I2: the CLI test snippet referenced nonexistent `_write_empty_cli_project` and `runner` helpers.

The plan has been revised to:

- add `fashion_radar.row_one.utils` for shared `safe_external_url`, `isoformat_z`, and `utc_datetime` helpers;
- make `readiness.py`, `templates.py`, and `render.py` import shared helpers from `row_one.utils`;
- extend internal `RowOneRenderResult` with `edition: RowOneEdition`;
- compute preview readiness from `result.edition`;
- reuse the existing `_write_minimal_config` and inline `CliRunner().invoke(...)` pattern in CLI tests;
- specify `_render_status_metric` markup and package-archive fixture updates.

## Files To Review

- `docs/superpowers/specs/2026-07-02-stage-264-row-one-daily-readiness-preview-design.md`
- `docs/superpowers/plans/2026-07-02-stage-264-row-one-daily-readiness-preview-plan.md`
- `docs/reviews/opencode-stage-264-plan-review.md`
- Existing reference implementation under `src/fashion_radar/row_one/`, `src/fashion_radar/cli.py`, `scripts/check_first_run_smoke.py`, `scripts/check_package_archives.py`, and `tests/test_row_one*.py`.

## Review Questions

1. Did the revision fully resolve C1, I1, and I2?
2. Are there any remaining Critical or Important blockers before implementation?
3. Does the revised plan preserve the project boundaries and `row-one-app/v1` contract?
4. Are the proposed TDD steps executable against the current codebase?

## Output Format

Return one coherent review body with:

- Critical
- Important
- Minor
- Positive checks
- Verdict

Do not include command logs, tool chatter, or duplicated verdicts.
