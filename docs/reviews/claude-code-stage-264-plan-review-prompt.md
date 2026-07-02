# Claude Code Stage 264 Plan Review Prompt

You are the primary reviewer for Fashion Radar Stage 264. Review the proposed
plan in read-only mode. Do not edit files.

## Objective

Stage 264 adds ROW ONE Daily Readiness & Preview: a deterministic readiness
summary derived from the current `RowOneEdition`, a homepage Latest Edition
status strip, a `fashion-radar row-one preview` command, first-run smoke checks
for ROW ONE CLI discoverability, and package archive guardrails for ROW ONE
source/docs.

## Architecture

- Keep the existing local static-site generator architecture.
- Add `fashion_radar.row_one.readiness` as a derived summary layer.
- Render readiness into existing static HTML.
- Add a Typer `row-one preview` command that builds once and prints paths,
  counts, readiness, and an optional dry-run serve URL.
- Extend existing first-run smoke and package archive scripts.
- Do not change collection, matching, ranking, scoring, schedule semantics, or
  the strict `row-one-app/v1` JSON contract.

## Tech Stack

Python 3.11+, Typer, existing Pydantic ROW ONE models, static HTML/CSS/JS,
pytest, Ruff, existing first-run/package verification scripts.

## Files To Review

- `docs/superpowers/specs/2026-07-02-stage-264-row-one-daily-readiness-preview-design.md`
- `docs/superpowers/plans/2026-07-02-stage-264-row-one-daily-readiness-preview-plan.md`
- Existing reference files:
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `src/fashion_radar/row_one/render.py`
  - `src/fashion_radar/row_one/templates.py`
  - `src/fashion_radar/cli.py`
  - `scripts/check_first_run_smoke.py`
  - `scripts/check_package_archives.py`
  - `tests/test_row_one_render.py`
  - `tests/test_row_one_cli.py`
  - `tests/test_package_archives.py`

## Review Questions

1. Does the plan close a real product gap in the `collect -> match -> report ->
   ROW ONE` path?
2. Is the scope appropriate for Stage 264, or does it mix too many concerns?
3. Does the plan preserve project boundaries: no new scraping, platform APIs,
   account/session behavior, translation, LLM calls, image generation, remote
   deployment, demand proof, platform coverage verification, or compliance-review
   product feature?
4. Is adding `row-one preview` technically reasonable given the existing Typer
   CLI and workflow helpers?
5. Does the readiness helper risk changing the app JSON contract or existing
   HTML behavior unexpectedly?
6. Are the proposed tests strong enough and placed in the right files?
7. Are any planned steps likely to break release packaging, first-run smoke, or
   existing ROW ONE tests?

## Output Format

Return a concise review with sections:

- Critical
- Important
- Minor
- Positive checks
- Verdict

Call out exact files/plan sections when possible. If you find Critical or
Important issues, include the concrete fix required before implementation.
