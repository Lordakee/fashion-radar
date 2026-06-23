# Stage 170 Community Signal Directory File Row Grammar Design

## Objective

Fix singular row-count wording in the human-readable per-file lines rendered by
`community-signal-lint-dir`.

## Current Gap

`render_community_signal_directory_lint_table(...)` currently renders each file
line with a fixed plural row-count label:

```text
- exports/b.csv: 1 rows, 0 import-ready, 1 error, 3 warnings, 2 info
```

The structured lint result is correct, and finding-count grammar is already
handled by `format_finding_counts(...)`. The remaining issue is presentation-only
row-count grammar in the per-file line.

## Scope

In scope:

- Add or tighten a renderer-level RED test that expects a per-file line to use
  `1 row`.
- Update the per-file renderer line to use `format_count_label(...)` for
  `file.row_count`.
- Update the user-facing example in `docs/community-signal-quality.md` from
  `1 rows` to `1 row`.

Out of scope:

- No changes to `lint_community_signal_directory(...)`.
- No changes to `lint_community_signal_file(...)`.
- No changes to structured models, JSON output, CLI command flow, field counts,
  source counts, platform counts, finding ordering, finding messages, or
  finding-count grammar.
- No changes to top-level summary lines such as `Rows: ... total, ...
  import-ready`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

## Architecture

Modify one renderer:

```text
src/fashion_radar/community_signals.py
```

Import `format_count_label` alongside the existing `format_finding_counts`
helper and use it only for `file.row_count` in the per-file directory lint line:

```python
f"{format_count_label(file.row_count, 'row', 'rows')}, "
```

Modify one test module:

```text
tests/test_community_signal_lint.py
```

Tighten the existing singular finding-count renderer test so it also asserts the
full per-file prefix includes `1 row, 0 import-ready`.

Modify one doc:

```text
docs/community-signal-quality.md
```

Update the example table output to match the renderer.

## Tech Stack

- Python standard library.
- Existing Pydantic models.
- Existing helper `fashion_radar.lint_formatting.format_count_label`.
- Existing helper `fashion_radar.lint_formatting.format_finding_counts`.
- Pytest.
- Markdown docs.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Tighten the renderer test to expect `1 row`.
2. Run the focused test and confirm it fails with `1 rows`.
3. Update the renderer to use `format_count_label(...)` for the per-file
   row-count phrase.
4. Update the doc example.
5. Re-run focused tests and checks.
6. Run opencode code review, full release gate, opencode release review,
   commit, and push.

## Expected Behavior

With one row:

```text
- exports/b.csv: 1 row, 0 import-ready, 1 error, 3 warnings, 2 info
```

With non-one counts, plural wording stays unchanged:

```text
- exports/a.csv: 2 rows, 2 import-ready, 0 errors, 0 warnings, 0 info
```

The top-level summary remains unchanged:

```text
Rows: 3 total, 2 import-ready
```

## Risks

- Over-expanding into valid-row-count grammar or summary-line grammar would
  cause broader human-output churn. Keep this stage to the per-file `row_count`
  label and the matching doc example.
- The existing singular finding-count test already has a synthetic
  `row_count=1` fixture, so tightening it is lower risk than adding a new
  malformed CSV fixture.
- Importing `format_count_label` should not create cycles. `lint_formatting.py`
  is a leaf helper module already imported by `community_signals.py` for
  `format_finding_counts`.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts -q
uv --no-config run --frozen pytest tests/test_community_signal_lint.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q
uv --no-config run --frozen ruff check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py
uv --no-config run --frozen ruff format --check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py
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
