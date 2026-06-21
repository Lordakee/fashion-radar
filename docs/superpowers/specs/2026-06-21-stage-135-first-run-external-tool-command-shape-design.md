# Stage 135 First-Run External Tool Command Shape Design

## Objective

Harden first-run smoke validation for external/community tool workflow command
shapes so command drift is caught by exact shell-argv comparison instead of
loose substring checks.

## Problem

The external/community tool readiness path is intentionally local and
print-oriented, but its generated workflow payloads still need stable command
contracts. `scripts/check_first_run_smoke.py` already validates adapter registry
recommended commands with `shlex.split()` and exact token checks. However,
`validate_external_tool_workflow()` and `validate_external_tool_readiness()`
still validate several step commands by checking whether required substrings
appear somewhere in the command string.

That means these malformed commands can pass smoke validation today:

- an external-tool workflow readiness command with extra flags after the pinned
  `--format table`;
- an external-tool readiness workflow command with `--format json` instead of
  `--format table`;
- an external-tool readiness dry-run import command with the wrong local input
  format or missing expected positional/flag values, as long as `--data-dir`,
  `--imported-at`, and `--dry-run` appear.

This weakens the first-run smoke gate around the user-controlled
external/community tool handoff path.

## Scope

In scope:

- Add focused negative tests for command-shape drift in:
  - `validate_external_tool_workflow()` readiness step;
  - `validate_external_tool_readiness()` workflow step;
  - `validate_external_tool_readiness()` dry-run import step.
- Add a small stdlib-only helper that parses a command with `shlex.split()`
  and compares the full argv list to the expected Fashion Radar command.
- Replace the existing substring checks for currently inspected external-tool
  workflow/readiness commands with exact argv checks.
- Keep exact command expectations derived from the payload's own
  `directory`, `config_dir`, `data_dir`, `as_of`, `input_format`, `pattern`,
  and `source_name` values so temporary first-run paths remain valid.

Out of scope:

- No CLI runtime behavior changes.
- No docs wording changes.
- No package/archive checker changes.
- No dependency changes.
- No `uv.lock` changes.
- No new connectors, scraping, browser automation, platform APIs, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance/audit product behavior.
- No execution of generated external/community commands.
- No PATH lookup behavior changes.
- No import, SQLite, file-read, or artifact creation behavior changes.

## Architecture

1. Add a helper near `expected_external_tool_command()`:

   - `validate_expected_external_tool_command(command_name, label, command,
     *parts)`
   - Parse `command` with `shlex.split(str(command))`.
   - On `ValueError`, raise `SmokeError` saying the command is not
     shell-parseable.
   - Compare parsed argv to `["fashion-radar", *parts]` with `assert_equal()`.

2. In `validate_external_tool_workflow()`:

   - Read the already validated payload values into local strings:
     `adapter_id`, `directory`, `config_dir`, `data_dir`, `as_of`,
     `input_format`, `pattern`, and `source_name`.
   - Replace substring checks for the registry, readiness, template, and lint
     steps with `validate_expected_external_tool_command()`.
   - Preserve existing step index, object-shape, effect, boundary, and
     step-name checks.

3. In `validate_external_tool_readiness()`:

   - Read the already validated payload values into local strings:
     `adapter_id`, `directory`, `config_dir`, `data_dir`, `as_of`,
     `input_format`, `pattern`, and `source_name`.
   - Replace substring checks for the workflow step and dry-run import step
     with exact argv checks.
   - Preserve existing checks, step effects, boundary assertions, and local
     read-only behavior.

4. Tests mutate existing static payload builders only. They do not execute
   generated commands, touch external tools, inspect directories, or import
   rows.

## Expected Behavior

After implementation:

- Existing valid first-run smoke payloads still pass.
- An external-tool workflow readiness command with a trailing `--verbose` flag
  fails with a `readiness command` smoke error.
- An external-tool readiness workflow command with `--format json` fails with a
  `workflow command` smoke error.
- An external-tool readiness dry-run import command with `--format csv` fails
  with a `dry-run command` smoke error.
- Real first-run smoke still accepts payloads containing temporary absolute
  `directory`, `config_dir`, and `data_dir` paths because expected argv values
  are derived from the payload.

## Risks

- Hardcoding `exports`, `configs`, or `data` inside the validator would break
  real first-run smoke runs that use temporary directories. The implementation
  must derive path arguments from the payload fields.
- Comparing command strings directly would overfit shell quoting. The helper
  must compare parsed argv lists so `'*.json'` and equivalent shell quoting
  remain acceptable.
- This stage should not broaden into all workflow step commands. It hardens
  only the command checks already present in these two validators, plus the
  readiness dry-run command that is currently checked by substring.

## Verification

Focused verification:

```bash
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
