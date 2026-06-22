# Stage 158 First-Run Community Handoff Check JSON Design

## Objective

Make first-run smoke validate the JSON payload returned by the direct
`community-handoff-check-dir` execution added in Stage 157.

## Current Gap

Stage 157 made `run_first_run_flow()` execute:

```text
community-handoff-check-dir <exports_dir> ... --strict
```

That proves the command exits successfully, but the smoke discards stdout. It
does not assert the command reports `execution_mode = local_read_only`, `ok =
true`, `failed_check_count = 0`, or that the nested lint/candidate/import dry-run
summaries match the first-run sample directory.

## Scope

In scope:

- Run `community-handoff-check-dir` with `--format json` in first-run smoke.
- Add a small `validate_community_handoff_check_dir()` validator in
  `scripts/check_first_run_smoke.py`.
- Update deterministic first-run tests to expect `--format json` and provide a
  representative JSON payload.

Out of scope:

- No runtime CLI changes.
- No social platform connectors, scraping, browser automation, platform APIs,
  login/cookie/token behavior, monitoring, scheduling, source acquisition, or
  compliance-review feature work.
- No write-capable `import-signals-dir` directory import.
- No broad command ordering refactor.

## Architecture

`run_first_run_flow()` will wrap the existing direct `community-handoff-check-dir`
call in `validate_json_output(...)`, then call a focused validator:

```python
community_handoff_check_dir = validate_json_output(
    "community-handoff-check-dir",
    run_cli(..., "--strict", "--format", "json").stdout,
)
validate_community_handoff_check_dir(
    "community-handoff-check-dir",
    community_handoff_check_dir,
    expected_directory=str(context.exports_dir),
    expected_config_dir=str(context.config_dir),
)
```

The validator should assert only fields that are stable and relevant to the
first-run contract:

- top-level payload is a JSON object.
- `execution_mode` is `local_read_only`.
- `directory`, `config_dir`, `input_format`, `pattern`, `as_of`, `source_name`,
  `strict`, `limit`, `ok`, `failed_check_count`, and `warning_count` match the
  first-run sample expectations.
- `community_signal_lint.file_count`, `row_count`, `valid_row_count`,
  `error_count`, and `warning_count` match the copied single-file sample export.
- `candidate_preview.candidate_count` and `row_count` match the sample.
- `import_dry_run.file_count`, `valid_file_count`, `row_count`, and
  `error_count` match the sample.

The validator will not inspect full nested rows or candidate internals. Those are
covered by focused CLI and community handoff tests; first-run smoke should remain
a fast integration guard.

## Tech Stack

- Python standard library.
- Existing first-run smoke script.
- Existing pytest test module `tests/test_first_run_smoke.py`.
- Local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- `uv --no-config run --frozen` for verification.

## Implementation Method

Use test-first changes:

1. Add a test helper payload for `community-handoff-check-dir`.
2. Update `expected_first_run_flow_commands()` to require `--format json` on the
   direct handoff check.
3. Update deterministic fake stdout so the new command returns JSON.
4. Add focused validator tests covering acceptance and top-level/local-read-only
   rejection.
5. Run focused tests and confirm RED failures before implementation.
6. Implement the validator and wire it into `run_first_run_flow()`.
7. Run focused tests, full first-run module, real smoke script, code review, and
   release gate.

## Expected Behavior

The direct first-run handoff check command should become:

```text
community-handoff-check-dir <exports_dir> --config-dir <config_dir> --input-format csv --pattern <DIR_PATTERN> --as-of <AS_OF> --source-name <SOURCE_NAME> --strict --format json
```

The first-run smoke should fail if the command returns non-JSON output, a
non-`local_read_only` execution mode, a non-OK result, unexpected warnings, or
sample-count drift.

## Risks

- The JSON payload contains more fields than first-run needs. The validator
  should not overfit to every nested field because CLI unit tests already cover
  the complete schema shape.
- `as_of` is normalized by the CLI to `2026-06-13T12:00:00+00:00`; the validator
  should compare against that normalized value, matching existing first-run
  validators.
- The deterministic fake must return JSON for `community-handoff-check-dir`;
  otherwise `validate_json_output()` will correctly fail.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir or first_run_flow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```
