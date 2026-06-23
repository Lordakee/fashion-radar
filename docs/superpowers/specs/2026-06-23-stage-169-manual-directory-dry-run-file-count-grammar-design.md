# Stage 169 Manual Directory Dry-Run File Count Grammar Design

## Objective

Fix singular count wording in the human-readable per-file lines rendered by
`import-signals-dir --dry-run`.

## Current Gap

`render_manual_signal_directory_dry_run_table(...)` currently renders each file
line with fixed plural labels:

```text
- exports/a.csv: 1 rows, 1 errors
```

The structured dry-run result is correct. The issue is presentation-only and
appears only in the human-readable directory dry-run renderer.

## Scope

In scope:

- Add a renderer-level RED test that forces a per-file dry-run row count and
  error count to `1`.
- Update the per-file renderer line to show:

  ```text
  1 row, 1 error
  ```

- Reuse the existing `format_count_label(...)` helper.

Out of scope:

- No changes to `dry_run_manual_signal_directory(...)`.
- No changes to `load_manual_signal_rows(...)`.
- No changes to import semantics, SQLite writes, row validation, directory
  scanning, sorting, structured models, JSON output, CLI command flow, first-run
  smoke command shape, or readiness checks.
- No changes to summary lines such as `Files: ...`, `Rows: ...`, or
  `Errors: ...`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

## Architecture

Modify one renderer:

```text
src/fashion_radar/importers/manual_signals.py
```

Import `format_count_label` from `fashion_radar.lint_formatting` and use it
only in the per-file line emitted by
`render_manual_signal_directory_dry_run_table(...)`:

```python
f"{format_count_label(file.row_count, 'row', 'rows')}, "
f"{format_count_label(file.error_count, 'error', 'errors')}"
```

Modify one test module:

```text
tests/test_manual_signal_import.py
```

Add a renderer-level test that creates a valid dry-run result, then uses
Pydantic `model_copy(...)` to force the first file result to `error_count=1`
while preserving `row_count=1`. This avoids depending on malformed CSV internals
to manufacture exactly one row and one file error.

## Tech Stack

- Python standard library.
- Existing Pydantic models.
- Existing helper `fashion_radar.lint_formatting.format_count_label`.
- Pytest.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Add the focused RED renderer test.
2. Run the single test and confirm it fails with `1 rows, 1 errors`.
3. Update the renderer to use `format_count_label(...)` for the per-file row
   and error-count phrases.
4. Re-run the focused test and the full `test_manual_signal_import.py` module.
5. Run opencode code review, full release gate, opencode release review,
   commit, and push.

## Expected Behavior

With one row and one error in a per-file dry-run line:

```text
- exports/a.csv: 1 row, 1 error
```

Non-one counts stay plural:

```text
- exports/a.csv: 2 rows, 0 errors
```

The top-level summary remains unchanged:

```text
Files: 1 total, 1 valid
Rows: 1 import-ready
Errors: 1
```

## Risks

- Over-expanding into all table count nouns would cause broader human-output
  churn. Keep this stage to the per-file dry-run line.
- Creating invalid CSV to force exactly one row plus one file error would be
  brittle. Use `model_copy(...)` on a valid result for a renderer-only test.
- Importing a helper should not create cycles. `lint_formatting.py` is a leaf
  module and is already used by other renderers.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_manual_signal_import.py::test_render_manual_signal_directory_dry_run_table_uses_singular_file_count_labels -q
uv --no-config run --frozen pytest tests/test_manual_signal_import.py -q
uv --no-config run --frozen ruff check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py
uv --no-config run --frozen ruff format --check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```
