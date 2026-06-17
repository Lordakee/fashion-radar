# Stage 67 External Tool Workflow Readiness Preflight Design

## Goal

Add the existing `external-tool-readiness` command as an early preflight step in
the print-only `external-tool-workflow` output.

Stage 66 made external tool readiness available, but the main external tool
handoff workflow still starts with adapter/template/profile guidance and does
not point users through the readiness check. This stage makes the recommended
external workflow more complete while keeping Fashion Radar local-first,
free-first, and non-connector.

## Scope

In scope:

- Add one new `external-tool-workflow` step named
  `check_external_tool_readiness`.
- Place the step after `inspect_adapter_registry` and before
  `print_adapter_template_json`.
- Print a copyable command:
  `fashion-radar external-tool-readiness --adapter ... --directory ... --config-dir ... --data-dir ... --as-of ... --input-format ... --pattern ... --source-name ... --format table`.
- Mark the new step `suggested_effect="read_only"` because running it performs
  local PATH lookup only.
- Keep `external-tool-workflow` itself `execution_mode="print_only"` because it
  only prints commands and does not run the readiness command.
- Increase workflow `step_count` from 11 to 12.
- Update stable workflow tests, CLI JSON tests, first-run smoke validators,
  deterministic smoke fixtures, docs, upload checklist snippets, AGENTS
  boundary text, CHANGELOG, and release hygiene docs as needed.

Out of scope:

- No new public CLI command.
- No changes to `external-tool-readiness` semantics.
- No changes to `external-tool-template` JSON/CSV output.
- No changes to the external tool adapter registry command list.
- No connector, scraping, browser automation, platform API, account/session/
  cookie/token, proxy, media download, monitoring, scheduling, source
  acquisition, demand proof, ranking, platform coverage verification, or
  compliance-review product feature.
- No running upstream tools or generated commands.
- No installing dependencies automatically.
- No reading handoff files or directories.
- No importing rows, opening SQLite, writing config/data/report/dashboard/
  workflow/handoff artifacts, matching, scoring, or report generation.

## User Flow

Example:

```bash
uv run fashion-radar external-tool-workflow \
  --adapter instaloader \
  --directory "$PWD/exports" \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --as-of 2026-06-13T12:00:00Z
```

The workflow will now show this early step:

```text
check_external_tool_readiness
fashion-radar external-tool-readiness --adapter instaloader ...
```

The user can manually run that readiness command if they want local command
availability guidance and mirror-friendly install hints before preparing
sanitized CSV/JSON handoff rows.

This is not a gate. Missing an upstream command is local availability guidance
only and is not proof that the user cannot create sanitized local handoff rows
another way.

## Data Contract

No top-level `ExternalToolWorkflow` keys change.

Stable workflow keys remain:

- `contract_version`
- `execution_mode`
- `adapter_id`
- `display_name`
- `platform_label`
- `directory`
- `input_format`
- `pattern`
- `as_of`
- `config_dir`
- `data_dir`
- `source_name`
- `step_count`
- `steps`
- `boundaries`

Step keys remain:

- `order`
- `name`
- `purpose`
- `command`
- `suggested_effect`

Workflow step names become:

1. `inspect_adapter_registry`
2. `check_external_tool_readiness`
3. `print_adapter_template_json`
4. `print_signal_profile`
5. `print_handoff_manifest`
6. `print_handoff_workflow`
7. `lint_export_directory`
8. `preview_candidate_phrases`
9. `review_handoff_readiness`
10. `dry_run_directory_import`
11. `import_directory_signals`
12. `print_post_import_review`

Suggested effects become:

1. `print_only`
2. `read_only`
3. `print_only`
4. `print_only`
5. `print_only`
6. `print_only`
7. `read_only`
8. `read_only`
9. `read_only`
10. `read_only`
11. `updates_local_imports`
12. `print_only`

## Builder Semantics

`build_external_tool_workflow(...)` continues to:

- Resolve adapter defaults from `build_external_tool_adapter_registry`.
- Normalize `as_of` with `parse_datetime_utc`.
- Use adapter defaults when `input_format`, `pattern`, or `source_name`
  overrides are omitted or blank.
- Never inspect `directory`, `config_dir`, or `data_dir`.
- Never execute generated commands.

The new step uses the same resolved values as the rest of the workflow:

- `adapter_id`
- `directory_text`
- `config_text`
- `data_text`
- `as_of_text`
- `input_format`
- `pattern`
- `source_name`

The command is quoted with the existing `_shell_command` helper, which uses
`shlex.join`.

## Rendering

Table and JSON rendering remain unchanged except for the additional step.

Table output still starts with:

```text
External tool handoff workflow.
Contract version: external-tool-workflow/v1
Execution mode: print_only
Commands were not executed.
```

The new line is a printed command only. `external-tool-workflow` itself must not
call the readiness builder or perform PATH lookup.

## Documentation

Update public docs to say `external-tool-workflow` now includes an early
`check_external_tool_readiness` step that points to `external-tool-readiness`
for optional local command availability guidance.

Docs must repeat the scope boundary:

- workflow remains local and print-only;
- the printed readiness command is local read-only when run manually;
- no platform collection, connectors, scraping, browser automation, platform
  APIs, account/session/cookie/token behavior, monitoring, scheduling, source
  acquisition, demand proof, ranking, coverage verification, or
  compliance-review product feature.

## Tests

Update focused tests:

- `tests/test_external_tool_workflow.py`
  - `step_count == 12`
  - step names include `check_external_tool_readiness` at position 2
  - suggested effects include `read_only` for that step
  - readiness command includes adapter, directory, config/data dirs, as-of,
    input-format, pattern, source-name, and `--format table`
  - path/pattern/source-name quoting remains stable
  - no top-level key changes

Update CLI tests:

- `tests/test_cli.py`
  - workflow JSON `step_count == 12`
  - command list contains `check_external_tool_readiness`
  - the new step is `read_only`
  - table output includes `external-tool-readiness`
  - no-artifact assertions continue to pass

Update smoke:

- `scripts/check_first_run_smoke.py`
  - `EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS` includes the new step
  - `validate_external_tool_workflow` expects 12 steps and the new effects list
  - validator asserts the readiness step command includes
    `fashion-radar external-tool-readiness`, `--adapter rednote_mcp`,
    `--input-format json`, `--pattern '*.json'`, `--source-name`, and
    `--format table`
- `tests/test_first_run_smoke.py`
  - deterministic external workflow payload includes the new step
  - command sequence expectations do not change, because the smoke does not
    execute generated workflow commands

Update docs drift:

- Existing `test_external_tool_workflow_docs_are_linked_and_bounded` and
  `test_external_tool_workflow_docs_include_examples_and_steps` should cover
  the new step name and boundary phrasing.

## Risks

The main risk is circular printed guidance: `external-tool-readiness` already
prints an `external-tool-workflow` next step, and the workflow will now print an
`external-tool-readiness` preflight step. This is acceptable because neither
command executes generated commands. Wording must frame the workflow step as an
optional preflight check, not as a recursive workflow requirement.

The second risk is stable contract churn. Workflow step count/order are tested
as public behavior. This stage intentionally changes the ordered steps and must
update all locked fixtures and validators together.

The third risk is overstating readiness. Do not describe the readiness step as
approval, compliance, authorization, source acquisition, demand proof, ranking,
coverage verification, or a guarantee that an upstream platform can be queried.
