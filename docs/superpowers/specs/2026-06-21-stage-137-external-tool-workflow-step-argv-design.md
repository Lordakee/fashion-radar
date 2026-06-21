# Stage 137 External Tool Workflow Step Argv Design

## Objective

Make the first-run smoke checker reject command drift in every
`external-tool-workflow` payload step by comparing parsed shell argv lists
exactly.

## Problem

Stage 135 added exact `shlex.split()` argv checks for selected
external/community tool command shapes. In `validate_external_tool_workflow()`,
only these workflow step commands are currently exact-checked:

- `inspect_adapter_registry`
- `check_external_tool_readiness`
- `print_adapter_template_json`
- `lint_export_directory`

The remaining workflow step commands still pass if their `name`,
`suggested_effect`, and surrounding payload fields are correct, even when the
printed command silently changes important arguments. The unguarded steps are:

- `print_signal_profile`
- `print_handoff_manifest`
- `print_handoff_workflow`
- `preview_candidate_phrases`
- `review_handoff_readiness`
- `dry_run_directory_import`
- `import_directory_signals`
- `print_post_import_review`

This is a validation gap in the smoke checker only. The CLI runtime behavior is
not changing.

## Scope

In scope:

- Add RED tests proving each currently unguarded workflow step accepts command
  drift today.
- Reuse existing `validate_expected_external_tool_command()` and its
  `shlex.split()` exact argv comparison.
- Derive expected command arguments from the `external-tool-workflow` payload
  values already validated in `validate_external_tool_workflow()`:
  `directory`, `input_format`, `pattern`, `config_dir`, `data_dir`, `as_of`,
  and `source_name`.
- Keep existing registry, readiness, template, and lint command checks intact.
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
- No docs copy changes outside Stage 137 plan/review artifacts.
- No connectors, scraping, browser automation, platform APIs, account/session/
  cookie/token behavior, media downloads, monitoring, scheduling, source
  acquisition, demand proof, ranking, coverage verification, or
  compliance/audit product behavior.

## Architecture

1. Keep `validate_expected_external_tool_command()` as the single exact-command
   checker. It already parses commands with `shlex.split()` and compares the
   complete argv list to `["fashion-radar", *parts]`.
2. In tests, add one parametrized negative test under
   `tests/test_first_run_smoke.py` that mutates the command for each currently
   unguarded workflow step. Each mutation keeps the step name/effect and the
   rest of the payload valid so the test isolates command-shape drift.
3. In `validate_external_tool_workflow()`, add exact-command checks for the
   eight currently unguarded steps using payload-derived values:
   - `community-signal-profile --format json`
   - `community-handoff-manifest <directory> --input-format <input_format>
     --pattern <pattern> --config-dir <config_dir> --data-dir <data_dir>
     --as-of <as_of> --source-name <source_name> --format json`
   - `community-handoff-workflow <directory> --input-format <input_format>
     --pattern <pattern> --config-dir <config_dir> --data-dir <data_dir>
     --as-of <as_of> --source-name <source_name>`
   - `community-candidates-dir <directory> --input-format <input_format>
     --pattern <pattern> --config-dir <config_dir> --as-of <as_of>
     --source-name <source_name>`
   - `community-handoff-check-dir <directory> --input-format <input_format>
     --pattern <pattern> --config-dir <config_dir> --as-of <as_of>
     --source-name <source_name> --strict`
   - `import-signals-dir <directory> --format <input_format> --pattern
     <pattern> --source-name <source_name> --data-dir <data_dir>
     --imported-at <as_of> --dry-run`
   - `import-signals-dir <directory> --format <input_format> --pattern
     <pattern> --source-name <source_name> --data-dir <data_dir>
     --imported-at <as_of>`
   - `imported-review-workflow --config-dir <config_dir> --data-dir
     <data_dir> --as-of <as_of> --source-name <source_name>`
4. Keep validation order close to existing step order so error labels map
   directly to the payload step being checked.

## Expected Behavior

After implementation:

- `validate_external_tool_workflow()` accepts the current valid
  `external-tool-workflow` payload.
- Changing `print_signal_profile` to `--format table` fails with a
  `signal profile command` error.
- Changing handoff manifest/workflow/candidate/readiness commands to wrong or
  incomplete argv fails with labels for those steps.
- Removing `--dry-run` from `dry_run_directory_import` fails with a
  `dry-run command` error.
- Adding `--dry-run` to `import_directory_signals` fails with an
  `import command` error.
- Changing the post-import review source name fails with a
  `post-import review command` error.
- The first-run smoke script still only validates command strings in local JSON
  payloads and does not execute generated commands.

## Risks

- Repeating eight explicit validation blocks is verbose, but it follows the
  existing style and avoids introducing abstraction during a validation-only
  hardening stage.
- Exact argv checks are intentionally strict. Future intentional command
  changes must update the smoke checker and tests together.
- The expected args must use payload-derived path/date/source values, not
  hardcoded `exports`, `configs`, or `data`, so first-run smoke tests with
  temporary directories remain valid.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness or external_tool_adapters"
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
