# Claude Code Stage 39 Release Review Prompt

You are reviewing the Stage 39 implementation for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release review; do not edit files.
- Treat Critical and Important findings as blockers.
- Review the staged diff with `git diff --cached`.

## Goal

Consolidate Stage 38 read-only SQLite schema inspection into one shared helper
while preserving existing CLI behavior.

## Implemented Scope

- Added `src/fashion_radar/db/schema_inspection.py`.
- Moved `create_readonly_sqlite_engine()` into
  `src/fashion_radar/db/engine.py`.
- Kept `fashion_radar.trends.create_readonly_sqlite_engine` available as an
  explicit import alias.
- Replaced duplicated read-only schema verification logic in:
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/imported_signals.py`
  - `src/fashion_radar/trends.py`
- Added shared helper coverage in `tests/test_schema_inspection.py`.
- Added CLI regression tests proving signed schema version strings still work
  for `doctor` and `candidates`.
- Added Stage 39 spec, plan, and Claude plan-review artifacts.

## Behavior That Must Be Preserved

- `doctor`, `migrate-db` status inspection, and candidate verification keep the
  Stage 38 signed schema parser behavior for strings like `+5` and `-1`.
- Imported-signal and trend verification keep the Stage 38 unsigned parser
  behavior and reject signed strings.
- Future schemas are reported before missing-table validation.
- Future-schema messages use the future-version hint and do not include a
  `migrate-db` hint.
- Old/missing-schema messages retain the explicit `migrate-db` hint where Stage
  38 had it.
- Missing columns, duplicate version rows, non-integer versions, missing
  `schema_metadata.version` column, and corrupt SQLite files remain invalid
  without implying `migrate-db` can fix them.
- `doctor` keeps its existing status formatting and missing-schema hint split.
- Imported-signal required columns remain the narrower compatibility set and do
  not require full current-schema columns.
- No source connectors, scraping, crawling, browser automation, login/cookie
  flows, account automation, proxy/CAPTCHA handling, source acquisition,
  schedulers, watchers, monitors, dependency changes, or schema version changes
  are introduced.

## Review Inputs

Primary files:

- `src/fashion_radar/db/schema_inspection.py`
- `src/fashion_radar/db/engine.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/imported_signals.py`
- `src/fashion_radar/trends.py`
- `tests/test_schema_inspection.py`
- `tests/test_cli.py`

Planning/review artifacts:

- `docs/superpowers/specs/2026-06-14-stage-39-shared-readonly-schema-inspection-design.md`
- `docs/superpowers/plans/2026-06-14-stage-39-shared-readonly-schema-inspection-plan.md`
- `docs/reviews/claude-code-stage-39-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-39-plan-review.md`
- `docs/reviews/claude-code-stage-39-release-review-prompt.md`

## Verification Already Run

TDD RED:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py -q
```

Observed before implementation: collection failed with
`ModuleNotFoundError: No module named 'fashion_radar.db.schema_inspection'`.

Focused GREEN and regression checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py -q
```

Observed: `19 passed`.

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py::test_doctor_accepts_signed_current_database_schema_string tests/test_cli.py::test_candidates_command_accepts_signed_current_database_schema_string -q
```

Observed: `2 passed`.

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py -q -k "schema or doctor or migrate_db or invalid_schema or future_schema_before_missing_table_validation or incompatible_database_without_schema_mutation"
```

Observed after the CLI signed regression tests were added:
`58 passed, 198 deselected`.

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py tests/test_trends.py -q -k "readonly or read_only or create_readonly_sqlite_engine or schema"
```

Observed: `9 passed, 25 deselected`.

Related test group:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_imported_signals.py tests/test_imported_candidates.py tests/test_imported_candidate_evidence.py tests/test_imported_entity_deltas.py tests/test_dashboard.py -q
```

Observed before the final two CLI signed regression tests were added:
`289 passed`.

Full release verification after final test additions:

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

Observed:

- `uv lock --check`: resolved with no lock update.
- `uv sync --locked --dev`: checked installed packages.
- `uv sync --locked --dev --check`: would make no changes.
- mirror check with `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple`:
  would make no changes.
- full pytest: `627 passed`.
- ruff check: `All checks passed!`
- ruff format check: `95 files already formatted`.
- diff checks: no whitespace errors.
- `uv.lock`: no diff.

Subagent reviews:

- Spec-compliance subagent: no Critical, Important, or Minor findings.
- Code-quality subagent: no Critical or Important findings. Minor findings:
  broad helper API surface, and lack of real CLI signed-parser integration
  tests. The CLI signed-parser integration tests were added. The public helper
  API surface was kept because it matches the approved Stage 39 design.

Boundary scans:

- No `pyproject.toml` or `uv.lock` changes.
- No diff-scoped source/test matches for token/secret material.
- No implementation of scraping, crawling, browser automation, platform
  automation, login/cookie/account/proxy/CAPTCHA, external platform API,
  scheduler, watcher, monitor, connector, or source-acquisition behavior.

## Proposed Next Stage

Stage 40 should be a small repository-readiness node:

- review README and contributor-facing docs against the current CLI surface;
- add a concise local verification/checklist document if it is missing;
- avoid dependency, connector, scraping, platform automation, scheduler, watcher,
  monitor, or source-acquisition work;
- preserve all current behavior unless documentation reveals a broken command
  example that needs a focused test-first fix.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if this implementation is acceptable to commit and push, include
this exact phrase:

```text
APPROVED FOR STAGE 39 COMMIT AND PUSH
```
