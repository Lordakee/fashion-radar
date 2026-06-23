# Stage 171 Community Handoff Check Count Label Grammar Design

## Objective

Fix singular count-label wording in the human-readable
`community-handoff-check-dir` summary lines.

## Current Gap

`render_community_handoff_directory_check_table(...)` already uses
`format_count_label(...)` for error counts, but several adjacent summary
phrases still hard-code plural labels:

```text
Lint: 1 files, 1/1 import-ready rows, 1 error
Candidate preview: 1 candidates from 1 rows
Import dry-run: 1/1 valid files, 1 rows, 1 error
```

The structured result is correct. JSON output is correct. The remaining issue
is presentation-only grammar in the text table.

## Scope

In scope:

- Tighten the existing renderer-level singular count-label test for
  `render_community_handoff_directory_check_table(...)`.
- Singularize only these human-readable labels:
  - Lint line: `file` / `files`.
  - Lint line: `import-ready row` / `import-ready rows`.
  - Candidate preview line: `candidate` / `candidates`.
  - Candidate preview line: `row` / `rows`.
  - Import dry-run line: `valid file` / `valid files`.
  - Import dry-run line: `row` / `rows`.
- Preserve the Stage 167 singular error-count assertions.

Out of scope:

- No changes to `check_community_handoff_directory(...)`.
- No changes to `lint_community_signal_directory(...)`.
- No changes to `preview_community_candidate_directory(...)`.
- No changes to `dry_run_manual_signal_directory(...)`.
- No changes to structured models, JSON output, CLI options, command flow,
  checks, strict-mode behavior, warnings, finding messages, or exit codes.
- No changes to historical stage design/plan/review artifacts that quote the
  old output as prior context.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Architecture

Modify one renderer:

```text
src/fashion_radar/community_handoff_check.py
```

The module already imports `format_count_label(...)`, so the implementation only
changes string composition inside
`render_community_handoff_directory_check_table(...)`.

Use `format_count_label(...)` directly for standalone count labels:

```python
format_count_label(count, "candidate", "candidates")
format_count_label(count, "row", "rows")
```

Use `format_count_label(...)` with a compound singular/plural label where the
existing phrase contains the adjective:

```python
format_count_label(row_count, "import-ready row", "import-ready rows")
format_count_label(file_count, "valid file", "valid files")
```

The slash prefix remains unchanged:

```text
1/1 import-ready row
1/1 valid file
```

Modify one test module:

```text
tests/test_community_handoff_check.py
```

Extend the existing
`test_render_community_handoff_directory_check_table_uses_singular_error_label`
test. It already builds a valid real result and uses `model_copy(...)` to force
synthetic one-error renderer state. Expand the same synthetic renderer state to
force one file, one total row, one import-ready row, one candidate, and one
dry-run row, then assert exact lines:

```text
Lint: 1 file, 1/1 import-ready row, 1 error
Candidate preview: 1 candidate from 1 row
Import dry-run: 1/1 valid file, 1 row, 1 error
```

## Tech Stack

- Python standard library.
- Existing Pydantic models and `model_copy(...)`.
- Existing helper `fashion_radar.lint_formatting.format_count_label`.
- Pytest.
- Markdown docs.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Tighten the renderer test to expect the exact singular Lint, Candidate
   preview, and Import dry-run lines.
2. Run the focused test and confirm it fails on hard-coded plural labels.
3. Update `render_community_handoff_directory_check_table(...)` to use
   `format_count_label(...)` for the in-scope labels.
4. Re-run focused tests and checks.
5. Run opencode code review, full release gate, opencode release review,
   commit, and push.

## Expected Behavior

With one count:

```text
Lint: 1 file, 1/1 import-ready row, 1 error
Candidate preview: 1 candidate from 1 row
Import dry-run: 1/1 valid file, 1 row, 1 error
```

With non-one counts, plural wording stays natural:

```text
Lint: 2 files, 2/2 import-ready rows, 0 errors
Candidate preview: 2 candidates from 2 rows
Import dry-run: 2/2 valid files, 2 rows, 0 errors
```

When candidate preview is unavailable, the existing output remains unchanged:

```text
Candidate preview: unavailable
```

## Risks

- Over-expanding into structured models or check logic would create unnecessary
  churn. Keep this stage inside the renderer.
- The synthetic `model_copy(...)` fixture will be internally inconsistent
  because counts are forced after building a valid real result. That is
  acceptable for a renderer-only grammar test and follows the Stage 167
  pattern.
- Old stage plan/spec/review files contain historical examples of prior output.
  They should remain unchanged unless they are active public docs.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q
uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q
uv --no-config run --frozen pytest tests/test_cli.py::test_community_handoff_check_dir_table_output_is_summary_only -q
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
