# Claude Code Stage 38 Release Review Prompt

You are reviewing the Stage 38 local schema maintenance implementation for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release review before commit and push.
- Do not edit files.
- Treat Critical and Important findings as blockers.

## Approved Plan

Stage 38 plan review was approved in:

- `docs/reviews/claude-code-stage-38-plan-review.md`

Required approval phrase present:

```text
APPROVED FOR STAGE 38 LOCAL SCHEMA MAINTENANCE
```

## Goal

Add explicit local SQLite schema maintenance:

- `fashion-radar migrate-db --data-dir ...` initializes or upgrades the local
  SQLite schema via the existing schema initializer.
- `fashion-radar doctor` reports database schema status read-only and does not
  create or migrate SQLite.
- Read-only schema verifiers keep future schemas distinct from old/missing
  schemas and do not imply `migrate-db` can downgrade newer databases.
- No source connectors, scraping, crawling, browser automation,
  login/cookie/account/proxy/CAPTCHA flows, schedulers, watchers, external
  platform API integrations, or dependency changes.

## Files Changed

- `CHANGELOG.md`
- `README.md`
- `docs/architecture.md`
- `docs/reviews/claude-code-stage-38-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-38-plan-review.md`
- `docs/reviews/claude-code-stage-38-release-review-prompt.md`
- `docs/reviews/claude-code-stage-38-release-review.md`
- `docs/superpowers/plans/2026-06-14-stage-38-local-schema-maintenance-plan.md`
- `docs/superpowers/specs/2026-06-14-stage-38-local-schema-maintenance-design.md`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/db/schema_messages.py`
- `src/fashion_radar/imported_signals.py`
- `src/fashion_radar/trends.py`
- `tests/test_cli.py`
- `tests/test_stage1_hardening.py`

## Implementation Notes

- New `src/fashion_radar/db/schema_messages.py` centralizes migrate/future/invalid
  schema guidance.
- `migrate-db` uses `default_database_path(data_dir)`,
  `create_sqlite_engine()`, and `initialize_schema(engine)`, then reports the
  read-only inspected status.
- `doctor` validates configs first, then inspects the database with
  `create_readonly_sqlite_engine()` only.
- `doctor` treats missing DB as OK, current schema as OK, old/future/invalid as
  exit 1.
- `doctor` validates current-version table and column completeness.
- Read-only trend, imported-signal, and candidate schema verifiers read
  `schema_metadata.version` first when possible so future schemas do not get
  missing-table or migrate hints.
- Candidate read-only DB opening now reuses the quoted read-only engine helper.

## TDD / Verification Evidence

RED evidence:

- Before implementation, `UV_NO_CONFIG=1 uv run pytest tests/test_cli.py -q -k
  "migrate_db"` failed 5 tests because `migrate-db` did not exist.
- Before doctor implementation, `UV_NO_CONFIG=1 uv run pytest tests/test_cli.py
  tests/test_stage1_hardening.py -q -k "doctor"` failed 15 tests because
  doctor did not report schema status.
- Before read-only verifier changes, `UV_NO_CONFIG=1 uv run pytest
  tests/test_cli.py -q -k "future_schema_before_missing_table_validation or
  incompatible_database_without_schema_mutation"` failed 6 tests due to
  missing future-priority handling and missing migrate hints.

GREEN evidence:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py -q -k "migrate_db"
# 5 passed, 189 deselected

UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_stage1_hardening.py -q -k "doctor"
# 19 passed, 199 deselected

UV_NO_CONFIG=1 uv run pytest tests/test_cli.py -q -k "future_schema_before_missing_table_validation or incompatible_database_without_schema_mutation"
# 7 passed, 205 deselected

UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_stage1_hardening.py -q -k "doctor or migrate_db or invalid_schema or future_schema_before_missing_table_validation or incompatible_database_without_schema_mutation"
# 35 passed, 187 deselected

UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_imported_signals.py tests/test_imported_candidates.py tests/test_imported_candidate_evidence.py tests/test_imported_entity_deltas.py -q
# 263 passed
```

Release verification:

```bash
UV_NO_CONFIG=1 uv lock --check
# resolved cleanly

UV_NO_CONFIG=1 uv sync --locked --dev
# checked 36 packages

UV_NO_CONFIG=1 uv sync --locked --dev --check
# would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
# would make no changes

UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
# 606 passed

UV_NO_CONFIG=1 uv run ruff check .
# All checks passed

UV_NO_CONFIG=1 uv run ruff format --check .
# 93 files already formatted

git diff --check
# exit 0

git diff --cached --check
# exit 0

git diff --quiet -- uv.lock
# exit 0
```

Boundary checks:

- `git diff --name-only` lists only Stage 38 docs/source/tests plus the new
  schema message helper.
- `git diff -U0 -- pyproject.toml uv.lock requirements.txt setup.py setup.cfg`
  is empty.
- Diff-scoped scan for scraping/crawling/browser automation/login/cookie/CAPTCHA
  and platform/API connector terms only matched newly added documentation saying
  `migrate-db` does not monitor, watch, schedule, or touch external platforms.
- `git remote -v` shows token-free `https://github.com/Lordakee/fashion-radar.git`.
- `git config --get-all http.https://github.com/.extraheader || true` produced
  no output.
- `uv.lock` is unchanged.

## Review Focus

Please verify:

- `migrate-db` is local-only and does not call collection/import/matching/scoring
  reporting/dashboard/digest/source/platform paths.
- `doctor` remains read-only and does not create DB files or run migrations.
- Missing/current/old/future/invalid schema states are correctly classified.
- Future schemas are reported before compatibility checks in all modified
  read-only verifiers and do not include a `migrate-db` hint.
- Shared message helpers do not create misleading downgrade/repair guidance.
- Tests adequately cover the behavior and hardening boundaries.
- No dependency, lockfile, external platform, scraping/crawling, token, generated
  data, or generated report changes were introduced.

## Next Phase Plan

If approved:

1. Stage only Stage 38 files.
2. Commit with message `Add local database schema maintenance`.
3. Push with a one-shot HTTP extraheader only; do not persist the GitHub token.
4. Confirm GitHub Actions succeeds for the pushed commit.
5. Write the node Handoff Summary with repo status, verified commands, GitHub
   Actions result, uncommitted files, and next step.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the implementation is acceptable to commit and push, include
this exact phrase:

```text
APPROVED FOR STAGE 38 COMMIT AND PUSH
```
