# Claude Code Stage 330 Code Review Prompt

You are reviewing `/home/ubuntu/fashion-radar`.

Model/effort requirement from the user: use max reasoning effort.

## Stage 330 Goal

Add default SQLite data retention to `fashion-radar row-one refresh` so the daily
ROW ONE local fashion-news site does not keep old collected item rows
indefinitely.

The required behavior is:

- `row-one refresh` still performs collect -> match -> daily report -> ROW ONE
  latest-only site generation.
- After successful current report/site generation and stale dated report
  artifact pruning, it runs SQLite item retention by default.
- Default ROW ONE SQLite retention is 1 day.
- `--retention-days N` keeps a longer local item-history window.
- `--skip-data-retention` skips only SQLite item retention for that refresh.
- Retention deletes old `items` and related `item_entities`.
- Retention failure after successful refresh is a warning, not a failed refresh.
- Runtime/app contract must not drift: no `row-one-runtime/v2`, no runtime JSON
  `retention_days` / `skip_data_retention`, and no changed `refresh.command`.
- First-run smoke must not delete its own sample rows, so smoke refresh should
  explicitly use `--skip-data-retention`.
- Scheduling docs should distinguish ROW ONE refresh default retention from
  standalone/manual `clean-old-data`.

## Base

Base commit is `56047ec06ed83ee73e69472104a7dcce4792db80` (`origin/main`).
Review the current uncommitted working tree diff against that base.

## Changed Files Expected

- `src/fashion_radar/cli.py`
- `tests/test_row_one_cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `README.md`
- `docs/row-one.md`
- `docs/first-run.md`
- `docs/data-retention.md`
- `docs/cli-reference.md`
- `docs/scheduling.md`
- `tests/test_row_one_docs.py`
- `tests/test_data_retention_docs.py`
- `tests/test_scheduling_docs.py`
- Stage 330 plan/review artifacts under `docs/superpowers/` and `docs/reviews/`

## Review Focus

Please act as a code reviewer. Findings first, ordered by severity.

Look specifically for:

1. Critical or Important correctness bugs in `row-one refresh` retention order,
   exit behavior, and CLI flag behavior.
2. Whether the real SQLite integration test proves the old item and old
   `item_entities` row are deleted while the current item remains.
3. Whether the first-run smoke flow avoids default retention deleting sample
   data.
4. Whether docs and docs tests prevent stale claims, especially claims that ROW
   ONE leaves all SQLite cleanup entirely to `clean-old-data`.
5. Whether scheduling docs still reflect generated ROW ONE schedule behavior.
6. Any runtime/app contract drift.
7. Any missing focused verification before full release verification.

Do not propose adding compliance review functionality; the user explicitly does
not want that product behavior.

## Verification Already Run By Controller/Subagents

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k row_one_refresh`
  -> `5 passed, 67 deselected`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_data_retention_docs.py tests/test_cli_docs.py -q`
  -> `138 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one refresh --help | rg -- '--retention-days|--skip-data-retention|--no-skip-data-retention'`
  -> showed `--retention-days` and `--skip-data-retention`; no `--no-skip-data-retention`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_refresh_prunes_old_sqlite_items_after_successful_refresh tests/test_db.py::test_item_repository_prunes_old_items_and_match_rows_without_fk_cascade tests/test_workflows.py::test_clean_old_data_prunes_by_collected_at -q`
  -> `3 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py -q`
  -> `141 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_scheduling_docs.py tests/test_scheduling.py -q`
  -> `23 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_data_retention_docs.py tests/test_cli_docs.py tests/test_scheduling_docs.py tests/test_scheduling.py tests/test_row_one_app_contract.py -q`
  -> `374 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q`
  -> `176 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  -> `First-run sample smoke passed.`
- `git diff --check`
  -> clean

## Output Format

Return:

- Findings first. Use `Critical`, `Important`, `Medium`, `Minor`.
- Include file/line references.
- If no Critical/Important findings, say that clearly.
- Include any residual test gaps or release risks.
