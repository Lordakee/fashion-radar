# Opencode Stage 60 Release Review

Reviewer: local `opencode`
Model: `zhipuai-coding-plan/glm-5.2`
Reasoning variant: `max`

## Verdict: APPROVED FOR STAGE 60 RELEASE

## Critical

None.

## Important

None.

## Minor

None material.

Observation only: the focused suite now reports 88 passed / 245 deselected and
the full suite now reports 975 passed. That is the expected +1 test delta from
`test_upload_checklist_installed_workflow_json_check_uses_installed_python`.

## Requirements Verification

- New step `review_imported_candidate_phrases` is added at `order=4` in
  `src/fashion_radar/imported_review_workflow.py` with
  `suggested_effect="read_only"`.
- The step command is exactly
  `fashion-radar imported-candidates --config-dir <cfg> --data-dir <data> --as-of <iso> [--source-name <src>]`.
- The final step remains `review_local_heat_movers` at `order=6`, and its
  command omits source filtering, so it never includes `--source-name`.
- The workflow builder remains print-only: it normalizes `as_of`, stringifies
  paths, and joins shell tokens. It does not load configs, open SQLite, inspect
  paths, call `query_imported_candidates`, run subprocesses, or create
  artifacts.

## Scope Check

Only `src/fashion_radar/imported_review_workflow.py` changes in `src/`. There is
no new CLI command, option, connector, scraper, platform API, schema migration,
dependency, report writer, dashboard writer, or scheduler.

## Docs Drift Check

README, architecture, CLI reference, community signal import/quality, manual
signal import, source boundaries, changelog, and GitHub upload checklist all
consistently describe a read-only `imported-candidates` step before the final
read-only `heat-movers` step, with explicit no demand proof / no platform
coverage verification language.

The added CLI reference note clarifying that `--current-days` and
`--baseline-days` apply to entity-delta review, not candidate review, is
accurate because the candidate command carries neither option.

## Release Hygiene Verification

Opencode independently re-ran:

- Focused suite: 88 passed, 245 deselected.
- Full suite: 975 passed.
- `ruff check .` and `ruff format --check .`: pass.
- `git diff --check`: clean.
- Mirror URL scan in `uv.lock`: no matches.
- `uv lock --check`: pass.
- `uv sync --locked --dev --check`: pass.
- `git diff --exit-code -- uv.lock pyproject.toml`: unchanged.
- `scripts/check_release_hygiene.py`: pass.
- `scripts/check_first_run_smoke.py`: pass, including `step_count == 6`,
  step 4 `review_imported_candidate_phrases`, final `review_local_heat_movers`,
  and no `--source-name` on the final heat command.

## Rationale

Stage 60 adds exactly one read-only `review_imported_candidate_phrases` step to
the print-only workflow in the prescribed position with the prescribed command
shape, keeps `review_local_heat_movers` last without `--source-name`, preserves
the builder's print-only contract, updates relevant docs without overclaiming,
and passes the lint, format, test, lockfile, hygiene, and smoke gates.
