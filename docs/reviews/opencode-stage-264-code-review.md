# opencode Stage 264 Code Review

## Critical

None.

## Important

None.

## Minor

- The retained `templates._safe_external_url()` wrapper is now a thin alias to
  `row_one.utils.safe_external_url()`. This is acceptable because existing
  callers still import the private template helper, but a future cleanup could
  move those callers directly to `row_one.utils`.
- The status strip is covered by HTML string assertions and first-run smoke, not
  browser screenshots. This is acceptable for this local static-site stage.
- `row-one preview --dry-run-serve-url` is tested for the default local URL
  message only. A future focused test could also cover wildcard/LAN host output.
- `edition_date` remains a date-only display value in readiness while
  `row-one-app/v1` keeps its date-time string. This is documented in the Stage
  264 design and does not change the app contract.

## Positive checks

- The implementation matches the revised Stage 264 plan: shared ROW ONE utility
  helpers, derived readiness, homepage status strip, preview CLI, first-run
  smoke coverage, package guardrails, and docs are all present.
- Circular imports are avoided: `templates.py` imports readiness, readiness
  imports `models.py` and `utils.py`, and `render.py` imports shared utility
  helpers without importing readiness.
- `RowOneRenderResult.edition` is an internal dataclass addition with one
  construction site in `render_row_one_site()`; `write_row_one_site_files()`
  returns it unchanged, so existing call signatures remain stable.
- `row-one build` and `row-one preview` share
  `_write_row_one_site_from_cli_options()`, keeping build behavior aligned.
- The Latest Edition status strip escapes dynamic text through `_esc()` and
  preserves bilingual `data-lang` spans.
- First-run smoke remains local-first and writes ROW ONE preview artifacts only
  under the temporary smoke reports directory.
- Package archive checks now require `docs/row-one.md`,
  `schemas/row-one-app.schema.json`, and all ROW ONE source files including
  `readiness.py` and `utils.py`.
- The `row-one-app/v1` JSON contract shape is unchanged; app contract tests
  continue to validate the generated payload.

## Verification reviewed

- `git diff --check`
- `uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_row_one*.py tests/test_package_archives.py`
- `uv --no-config run --frozen ruff format --check src/fashion_radar/row_one src/fashion_radar/cli.py scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_row_one*.py tests/test_package_archives.py`
- `uv --no-config run --frozen pytest tests/test_row_one_readiness.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_app_contract.py tests/test_package_archives.py -q` passed with 140 tests.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`

## Verdict

Approved for release. No Critical or Important issues were found.
