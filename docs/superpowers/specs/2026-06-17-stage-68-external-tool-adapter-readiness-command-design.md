# Stage 68 External Tool Adapter Readiness Command Design

## Goal

Add the existing `external-tool-readiness` command to each
`external-tool-adapters` registry entry's `recommended_commands` list.

Stage 67 added the readiness preflight to `external-tool-workflow`. This stage
makes the adapter registry entry point equally discoverable: a user who starts
with `external-tool-adapters --format json` can see the local readiness command
before the broader workflow, lint, dry-run, import, and review commands.

## Scope

In scope:

- Insert one `external-tool-readiness` command into `_recommended_commands` in
  `src/fashion_radar/external_tool_adapters.py`.
- Place it after `community-signal-profile` and before
  `community-handoff-manifest`.
- Pass through the resolved adapter id, directory, config/data dirs, as-of,
  input format, pattern, source name, and `--format table`.
- Keep `external-tool-adapters` itself `execution_mode="print_only"` because it
  only prints command strings and does not run readiness or perform PATH lookup.
- Update adapter registry tests, CLI tests, smoke validators/fixtures, docs
  drift tests, AGENTS boundary text, CHANGELOG, and public docs where needed.

Out of scope:

- No new public CLI command.
- No changes to `external-tool-readiness` behavior.
- No changes to `external-tool-workflow` step order.
- No changes to `external-tool-template` JSON/CSV handoff-row output.
- `external-tool-template` table/model guidance may inherit the adapter
  registry's `external-tool-readiness` command through its existing
  `recommended_commands=[*adapter.recommended_commands]` copy.
- No running readiness, adapters, upstream tools, or generated commands.
- No connector, scraping, browser automation, platform API, account/session/
  cookie/token, proxy, media download, monitoring, scheduling, source
  acquisition, demand proof, ranking, platform coverage verification, or
  compliance-review product feature.
- No reading handoff files or directories.
- No importing rows, opening SQLite, writing config/data/report/dashboard/
  workflow/handoff artifacts, matching, scoring, or report generation.

## Data Contract

No top-level `ExternalToolAdapterRegistry` keys change.

Adapter `recommended_commands` will contain 9 commands instead of 8:

1. `community-signal-profile`
2. `external-tool-readiness`
3. `community-handoff-manifest`
4. `community-handoff-workflow`
5. `community-signal-lint-dir`
6. `community-handoff-check-dir`
7. `import-signals-dir --dry-run`
8. `import-signals-dir`
9. `imported-review-workflow`

The readiness command is:

```text
fashion-radar external-tool-readiness --adapter <adapter_id> --directory <directory> --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of> --input-format <format> --pattern <pattern> --source-name <source_name> --format table
```

## Builder Semantics

`build_external_tool_adapter_registry(...)` continues to:

- Resolve the community signal profile.
- Build adapter metadata for the existing seven adapter ids.
- Use adapter-specific input format, pattern, platform label, and source name.
- Normalize `as_of`.
- Never inspect supplied paths.
- Never execute generated commands.

The `_adapter(...)` helper must pass `adapter_id` to `_recommended_commands(...)`
so the readiness command can include `--adapter <adapter_id>`.

## Rendering

Table and JSON rendering remain unchanged except that each adapter's command
list includes the additional readiness command.

`external-tool-adapters` remains print-only. The printed readiness command is
local read-only only when the user manually runs it.

## Tests

Update focused tests:

- `tests/test_external_tool_adapters.py`
  - command prefix list includes `external-tool-readiness` at index 1;
  - readiness command includes adapter, directory, config/data dirs, as-of,
    input-format, pattern, source-name, and `--format table`;
  - dry-run/non-dry-run command indexes shift by one;
  - path quoting assertions still pass.
- `tests/test_external_tool_templates.py`
  - template `recommended_commands` includes `external-tool-readiness`;
  - rendered JSON/CSV handoff rows remain unchanged and do not gain metadata.

Update CLI tests:

- `tests/test_cli.py`
  - `external-tool-adapters --format json` includes the readiness command in
    the first adapter command list.

Update smoke:

- `scripts/check_first_run_smoke.py`
  - `validate_external_tool_adapters` asserts the first adapter's
    `recommended_commands` include `external-tool-readiness`.
- `tests/test_first_run_smoke.py`
  - fixture payload for external adapters includes representative
    `recommended_commands` if needed by the validator.

Update docs drift:

- Docs describing `external-tool-adapters` should mention that the recommended
  command list includes the local read-only `external-tool-readiness` preflight
  command while the registry itself remains print-only.

## Risks

The main risk is overstating adapter readiness as a gate. Wording must keep it
as optional local command availability guidance, not approval, authorization,
source acquisition, demand proof, ranking, or coverage verification.

The second risk is stable command-order churn. Tests intentionally lock the
command order, so update all order-sensitive coverage together:

- `tests/test_external_tool_adapters.py::test_instaloader_adapter_has_expected_mapping_and_commands`
- `tests/test_external_tool_adapters.py::test_registry_quotes_paths_pattern_and_source_names`
- `tests/test_external_tool_templates.py` checks that distinguish template
  recommended command guidance from JSON/CSV handoff-row output
- `tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths`
- `tests/test_first_run_smoke.py::external_tool_adapters_payload`
- `scripts/check_first_run_smoke.py::validate_external_tool_adapters`
- the first-run flow command that invokes `external-tool-adapters --format json`
