# Stage 166 Community Handoff Check Dir Smoke Exactness Design

## Objective

Tighten the first-run smoke validator for `community-handoff-check-dir` JSON
output so stable nested payload drift is caught earlier.

## Current Gap

`scripts/check_first_run_smoke.py` already validates the
`community-handoff-check-dir` top-level mode, paths, strict flag, aggregate
health counts, and a few nested counts under:

- `community_signal_lint`
- `candidate_preview`
- `import_dry_run`

The helper payload and the actual command output include additional first-run
contract fields that the validator currently does not pin:

- top-level `findings`
- `community_signal_lint.directory`
- `community_signal_lint.input_format`
- `community_signal_lint.pattern`
- `community_signal_lint.info_count`
- `community_signal_lint.field_counts`
- `community_signal_lint.source_name_counts`
- `community_signal_lint.platform_counts`
- `candidate_preview.input_format`
- `candidate_preview.as_of`
- `candidate_preview.current_window_start`
- `candidate_preview.baseline_window_start`
- `candidate_preview.current_days`
- `candidate_preview.baseline_days`
- `candidate_preview.source_name`
- `candidate_preview.file_count`
- `candidate_preview.limit`
- `candidate_preview.candidates`
- `import_dry_run.directory`
- `import_dry_run.input_format`
- `import_dry_run.pattern`
- `import_dry_run.source_name_counts`
- `import_dry_run.platform_counts`

If one of these fields drifts while the already-pinned counts stay stable, the
first-run smoke check can still pass. This stage closes that gap without
changing the product command.

This stage intentionally does not pin nested `files` list contents. The test
fixture currently uses empty lists while the real smoke run can include
deterministic per-file entries. Pinning those lists needs a separate fixture
alignment pass.

## Scope

In scope:

- Add RED tests showing the current validator misses top-level and nested
  `community-handoff-check-dir` detail drift.
- Add exact `assert_equal(...)` checks for the stable first-run expected values
  listed above.
- Keep all changes inside the first-run smoke script and its tests.

Out of scope:

- No exact assertions for nested `files` lists.
- No exact assertions for nested `findings` lists.
- No CLI product behavior changes.
- No JSON producer/model changes.
- No database, import, lint, candidate, workflow, dashboard, or report changes.
- No changes to command execution order.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.
- No historical review archive rewrites.

## Architecture

Modify one local release-check script:

```text
scripts/check_first_run_smoke.py
```

`validate_community_handoff_check_dir(...)` remains a pure local payload
validator. It will add `assert_equal(...)` calls for stable top-level,
community-signal-lint, candidate-preview, and import-dry-run fields. It will
reuse existing constants where possible:

- `DIR_PATTERN`
- `SOURCE_NAME`
- `EXPECTED_PLATFORM_COUNTS`
- `EXPECTED_SOURCE_COUNTS`
- `EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS`
- `EXPECTED_SAMPLE_ROWS`

Modify one test module:

```text
tests/test_first_run_smoke.py
```

Add focused drift tests against `community_handoff_check_dir_payload(...)`.
These tests mutate one field at a time and expect `SmokeError` labels from the
validator. This keeps the assertions local to the smoke validator and avoids
running the CLI.

## Tech Stack

- Python standard library.
- Existing first-run smoke script.
- Pytest.
- `uv --no-config run --frozen` for tests, lint, and scripted checks.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD for the validator hardening:

1. Add RED tests for unpinned top-level and nested stable detail drift.
2. Run the focused tests and confirm the new drift cases fail against the
   current validator.
3. Add the minimal `assert_equal(...)` checks to
   `validate_community_handoff_check_dir(...)`.
4. Re-run the focused tests and first-run smoke script.
5. Run opencode code review, full release gate, opencode release review,
   commit, and push.

## Expected Behavior

The validator should reject these first-run drift examples:

```text
community-handoff-check-dir findings expected [], got [...]
community-handoff-check-dir lint directory expected ..., got ...
community-handoff-check-dir lint input_format expected 'csv', got 'json'
community-handoff-check-dir lint field_counts expected {...}, got {...}
community-handoff-check-dir lint source_name_counts expected {...}, got {...}
community-handoff-check-dir lint platform_counts expected {...}, got {...}
community-handoff-check-dir candidate_preview source_name expected ..., got ...
community-handoff-check-dir candidate_preview as_of expected ..., got ...
community-handoff-check-dir candidate_preview file_count expected 1, got 2
community-handoff-check-dir candidate_preview limit expected 50, got 99
community-handoff-check-dir candidate_preview candidates expected [], got [...]
community-handoff-check-dir import dry-run directory expected ..., got ...
community-handoff-check-dir import dry-run source_name_counts expected {...}, got {...}
community-handoff-check-dir import dry-run platform_counts expected {...}, got {...}
```

The clean first-run payload should still pass unchanged.

## Risks

- Overly broad exactness could make the smoke check brittle. This stage pins
  only stable first-run contract fields already present in the fixture and
  command output.
- Accidentally changing product behavior would expand the stage. Keep edits out
  of `src/`.
- The expected directory can vary between tests and real smoke runs. Use the
  existing `expected_directory` argument for nested directory assertions.
- Nested `files` lists are deliberately left unpinned in this stage to avoid
  making the smoke check stricter than the fixture can prove.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir"
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
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
