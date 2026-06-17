# Stage 70 Code Rereview Prompt

You are rereviewing the current uncommitted Stage 70 workspace in
`/home/ubuntu/fashion-radar` after the first code review reported only Minor
test-coverage gaps.

Do not edit files.

## Prior Minor Findings

The first code review found that the validator already rejected these cases,
but the test file did not explicitly cover them:

- non-table `--format` values
- flag values replaced by the next flag
- trailing flags with no value

## Rereview Goal

Confirm the current changes now add explicit negative tests for those paths
while preserving all Stage 70 constraints:

- no app runtime behavior changes
- adapter registry behavior and command output unchanged
- CLI JSON tests use `shlex.split` without hard-coding user config/data default
  paths
- first-run smoke validation parses readiness commands with `shlex.split`
- malformed shell quoting, missing required flags, missing `--format`,
  non-table `--format`, values replaced by the next flag, and trailing flags
  with no value are rejected
- no connectors, scraping, browser automation, platform APIs, scheduling,
  source acquisition, demand proof, ranking, coverage verification, or
  compliance-review product behavior

## Verification Since Fixing Minors

- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q`
  - `1 passed`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q`
  - `52 passed`
- `uv --no-config run --frozen pytest tests/test_external_tool_adapters.py::test_instaloader_adapter_has_expected_mapping_and_commands tests/test_cli.py::test_external_tool_adapters_command_prints_json tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths -q`
  - `3 passed`

## Output Format

Return findings ordered by severity. Use `Critical`, `Important`, or `Minor`.
If there are no Critical/Important issues, state that explicitly. Keep the
review concise and include file/line references where relevant.
