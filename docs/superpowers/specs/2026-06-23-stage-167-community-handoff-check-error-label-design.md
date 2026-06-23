# Stage 167 Community Handoff Check Error Label Design

## Objective

Fix singular `1 error` wording in the human-readable
`community-handoff-check-dir` table for lint and import dry-run summaries.

## Current Gap

`render_community_handoff_directory_check_table(...)` currently renders fixed
plural error-count labels:

```text
Lint: 2 files, 1/2 import-ready rows, 1 errors
Import dry-run: 1/2 valid files, 2 rows, 1 errors
```

The structured counts are correct. The issue is presentation-only and appears
only in the human table renderer.

## Scope

In scope:

- Add a renderer-level RED test that forces both relevant nested error counts
  to `1` and expects `1 error`.
- Update the two `error_count` labels in
  `render_community_handoff_directory_check_table(...)`.
- Reuse the existing `format_count_label(...)` helper.

Out of scope:

- No changes to `check_community_handoff_directory(...)`.
- No model, JSON, CLI command flow, lint, dry-run, candidate preview,
  strict-mode, or readiness semantics changes.
- No changes to `files`, `rows`, or `candidates` wording.
- No changes to `manual_signals.py`; the per-file manual dry-run `1 errors`
  wording is a separate candidate stage.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

## Architecture

Modify one renderer:

```text
src/fashion_radar/community_handoff_check.py
```

Import `format_count_label` from `fashion_radar.lint_formatting` and use it for
the two error-count phrases:

```python
format_count_label(result.community_signal_lint.error_count, "error", "errors")
format_count_label(result.import_dry_run.error_count, "error", "errors")
```

Modify one test module:

```text
tests/test_community_handoff_check.py
```

Add a focused renderer test that creates a normal valid result and then uses
Pydantic `model_copy(...)` to set both nested error counts to `1`. This avoids
depending on malformed CSV internals to manufacture exactly one error.

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
2. Run the single test and confirm it fails with `1 errors`.
3. Update the renderer to use `format_count_label(...)` for the two error-count
   phrases.
4. Re-run the focused test and the full `test_community_handoff_check.py`
   module.
5. Run opencode code review, full release gate, opencode release review,
   commit, and push.

## Expected Behavior

With one lint error:

```text
Lint: 2 files, 2/2 import-ready rows, 1 error
```

With one import dry-run error:

```text
Import dry-run: 2/2 valid files, 2 rows, 1 error
```

Non-one counts stay plural, using the existing helper contract.

## Risks

- Over-expanding into all table count nouns would cause broader human-output
  churn. Keep this stage to the two `error_count` phrases.
- Creating invalid CSV to force a single error could be brittle. Use
  `model_copy(...)` on a valid result for a renderer-only test.
- Importing a helper should not create cycles. `lint_formatting.py` is a leaf
  module and is already used by multiple renderers.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q
uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q
uv --no-config run --frozen ruff check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py
uv --no-config run --frozen ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py
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
