# Stage 138 External Tool Readiness Step Argv Design

## Objective

Make the first-run smoke checker reject command drift in every
`external-tool-readiness` payload step by comparing parsed shell argv lists
exactly.

## Problem

Stage 135 and Stage 137 hardened exact command-shape checks for selected
external/community tool smoke surfaces. `validate_external_tool_readiness()`
still exact-checks only these readiness step commands:

- `print_external_tool_workflow`
- `dry_run_directory_import`

The remaining readiness step commands can silently drift as long as the step
names, effects, and surrounding payload fields remain valid:

- `inspect_adapter_registry`
- `print_adapter_template_json`
- `print_signal_profile`
- `lint_export_directory`
- `review_handoff_readiness`

This is a first-run smoke validation gap only. The CLI runtime behavior and
printed readiness payload generation are not changing.

## Scope

In scope:

- Add RED tests proving the five currently unguarded readiness step commands
  accept command drift today.
- Reuse existing `validate_expected_external_tool_command()` and its
  `shlex.split()` exact argv comparison.
- Derive expected command arguments from the `external-tool-readiness` payload
  values already validated in `validate_external_tool_readiness()`:
  `adapter_id`, `directory`, `config_dir`, `data_dir`, `as_of`,
  `input_format`, `pattern`, and `source_name`.
- Keep existing workflow and dry-run command checks intact.
- Keep this as first-run smoke validation only.

Out of scope:

- No CLI runtime behavior changes.
- No generated command execution.
- No PATH lookup changes.
- No directory inspection.
- No handoff file reads.
- No import behavior changes.
- No SQLite behavior changes.
- No artifact creation.
- No dependency changes.
- No `uv.lock` changes.
- No docs copy changes outside Stage 138 plan/review artifacts.
- No connectors, scraping, browser automation, platform APIs, account/session/
  cookie/token behavior, media downloads, monitoring, scheduling, source
  acquisition, demand proof, ranking, coverage verification, or
  compliance/audit product behavior.

## Architecture

1. Keep `validate_expected_external_tool_command()` as the single exact-command
   checker. It already parses commands with `shlex.split()` and compares the
   complete argv list to `["fashion-radar", *parts]`.
2. Add one parametrized negative test under `tests/test_first_run_smoke.py`
   that mutates each currently unguarded readiness step command while leaving
   every other payload field valid.
3. In `validate_external_tool_readiness()`, add exact-command checks for the
   five currently unguarded steps using payload-derived values:
   - `external-tool-adapters --adapter <adapter_id> --directory <directory>
     --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of>
     --format table`
   - `external-tool-template --adapter <adapter_id> --directory <directory>
     --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of>
     --format json`
   - `community-signal-profile --format json`
   - `community-signal-lint-dir <directory> --input-format <input_format>
     --pattern <pattern> --source-name <source_name> --strict`
   - `community-handoff-check-dir <directory> --input-format <input_format>
     --pattern <pattern> --config-dir <config_dir> --as-of <as_of>
     --source-name <source_name> --strict`
4. Keep validation order aligned to `EXPECTED_EXTERNAL_TOOL_READINESS_STEPS`
   so error labels map directly to the payload step being checked.

## Expected Behavior

After implementation:

- `validate_external_tool_readiness()` accepts the current valid
  `external-tool-readiness` payload.
- Changing `inspect_adapter_registry` from table to JSON format fails with a
  `registry command` error.
- Changing `print_adapter_template_json` from JSON to table format fails with a
  `template command` error.
- Changing `print_signal_profile` to `--format table` fails with a
  `signal profile command` error.
- Removing `--strict` from `lint_export_directory` fails with a `lint command`
  error.
- Removing `--strict` from `review_handoff_readiness` fails with a
  `handoff readiness command` error.
- Existing workflow and dry-run command drift tests continue to pass.
- The first-run smoke script still only validates command strings in local JSON
  payloads and does not execute generated commands.

## Risks

- The validator will become stricter by design. Future intentional readiness
  command changes must update the smoke checker and tests together.
- Expected args must use payload-derived path/date/source values, not hardcoded
  `exports`, `configs`, or `data`, so first-run smoke tests with temporary
  directories remain valid.
- Repeating five explicit validation blocks is verbose, but it follows the
  current file style and keeps this stage validation-only.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness or external_tool_workflow or external_tool_adapters"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if [ -n "$(git config --get-all http.https://github.com/.extraheader || true)" ]; then echo 'Persistent GitHub auth header found' >&2; exit 1; fi
```
