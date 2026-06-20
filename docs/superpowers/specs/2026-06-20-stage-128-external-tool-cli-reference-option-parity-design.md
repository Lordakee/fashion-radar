# Stage 128 External Tool CLI Reference Option Parity Design

## Objective

Align `docs/cli-reference.md` with the actual public option sets for
`external-tool-workflow` and `external-tool-readiness`.

## Problem

The CLI already exposes a full local handoff option set for both commands:

- `--adapter`
- `--directory`
- `--config-dir`
- `--data-dir`
- `--as-of`
- `--input-format`
- `--pattern`
- `--source-name`
- `--format`

`docs/cli-reference.md` is stale:

- `external-tool-workflow` omits `--input-format`, `--pattern`, and
  `--source-name`.
- `external-tool-readiness` documents only `--adapter` and
  `--format table|json`, omitting the directory/config/data/as-of/input
  format/pattern/source-name options.

Existing CLI help tests already prove the runtime option surface is correct.
This stage should update the reference documentation and add a docs parity
guard.

## Scope

In scope:

- Add a helper/test in `tests/test_cli_docs.py` that extracts only the command
  bullet from `docs/cli-reference.md`.
- Assert both command bullets document the public options shown by Typer help.
- Update the two support sentences in `docs/cli-reference.md`.

Out of scope:

- No runtime CLI changes.
- No external adapter behavior changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.
- No dependency changes.
- No `uv.lock` changes.
- No upload checklist or README expansion in this stage.

## Architecture

This is a documentation parity guard:

1. A `_cli_reference_command_entry(command)` helper extracts the specific
   markdown bullet for a command from `docs/cli-reference.md`.
2. `test_cli_reference_external_tool_option_parity` compares expected option
   strings against that bullet and confirms each option name is present in
   Typer help.
3. The test stays scoped to `external-tool-workflow` and
   `external-tool-readiness` so other command sections do not create false
   positives.
4. The docs keep readiness wording accurate: readiness remains local read-only
   because it performs local PATH lookup; it does not read directories or
   validate handoff files.

## Expected Behavior

After implementation:

- `external-tool-workflow` documents `--adapter`, `--directory`,
  `--config-dir`, `--data-dir`, `--as-of`, `--input-format csv|json`,
  `--pattern`, `--source-name`, and `--format table|json`.
- `external-tool-readiness` documents the same public option set.
- The docs test fails if either CLI reference bullet omits an expected option.
- The docs test also fails if the option is not present in actual command help.

## Risks

- A whole-file search would be too weak because other command sections mention
  similar flags. The test must parse only the relevant bullet.
- Readiness option documentation must not imply readiness reads directories or
  validates files. These options feed readiness metadata and printed next-step
  commands; the command still only performs local command availability lookup.
- `--format` should remain `table|json` for these two commands. CSV applies to
  `external-tool-template`, not workflow/readiness.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_cli_reference_external_tool_option_parity -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -k "external_tool_option_parity or external_tool_workflow_docs_include_examples_and_steps or external_tool_readiness_upload_checklist_help_loop_and_smoke" -q
uv --no-config run --frozen pytest tests/test_cli.py -k "external_tool_workflow_help_lists_options or external_tool_readiness_help_lists_options or external_tool_workflow_command_applies_overrides or external_tool_readiness_command_applies_overrides" -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
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
```
