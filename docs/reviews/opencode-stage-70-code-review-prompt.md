# Stage 70 Code Review Prompt

You are reviewing the current uncommitted Stage 70 workspace in
`/home/ubuntu/fashion-radar`.

Do not edit files. Review for correctness, regression risk, missing tests, and
scope drift.

## Stage Goal

Harden tests and first-run smoke validation for the
`external-tool-readiness` command printed in external tool adapter
`recommended_commands`.

## Required Semantics

- No app runtime behavior should change.
- Adapter registry behavior and command output should not change.
- Adapter unit tests should explicitly assert readiness `--config-dir` and
  `--data-dir` values when those paths are explicitly supplied by the test.
- CLI adapter JSON tests should parse the readiness command with `shlex.split`
  and check stable flag/value mapping without hard-coding user config/data
  default paths.
- First-run smoke validation should parse the readiness command with
  `shlex.split`.
- First-run smoke validation should reject:
  - malformed shell quoting
  - missing required readiness flags
  - missing `--format`
  - non-table readiness output format
  - flag values that are missing or replaced by the next flag
- The stage must stay within local-first/free-first project boundaries and
  must not introduce connectors, scraping, browser automation, platform APIs,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance-review product behavior.

## Files In Scope

- `tests/test_external_tool_adapters.py`
- `tests/test_cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-17-stage-70-adapter-readiness-command-test-hardening-design.md`
- `docs/superpowers/plans/2026-06-17-stage-70-adapter-readiness-command-test-hardening-plan.md`
- `docs/reviews/opencode-stage-70-plan-review-prompt.md`
- `docs/reviews/opencode-stage-70-plan-review.md`
- `docs/reviews/opencode-stage-70-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-70-plan-rereview.md`

## Verification Already Run

- `uv --no-config run --frozen pytest tests/test_external_tool_adapters.py::test_instaloader_adapter_has_expected_mapping_and_commands -q`
  - passed before implementation: `1 passed`
  - passed after implementation: `1 passed`
- `uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths -q`
  - passed before implementation: `2 passed`
  - passed after implementation: `2 passed`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q`
  - failed before validator hardening on the new malformed quoting negative case
  - passed after validator hardening: `1 passed`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q`
  - `52 passed`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - passed
- `uv --no-config run --frozen ruff check tests/test_external_tool_adapters.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  - passed
- `uv --no-config run --frozen ruff format --check tests/test_external_tool_adapters.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  - passed after formatting `scripts/check_first_run_smoke.py`
- `uv --no-config run --frozen python scripts/check_release_hygiene.py`
  - passed
- `git diff --check`
  - passed
- `uv --no-config run --frozen pytest`
  - `1099 passed`

## Review Output Format

Return:

1. Findings ordered by severity.
2. For each finding, include file path, line number, severity (`Critical`,
   `Important`, or `Minor`), and concrete impact.
3. If no Critical/Important issues exist, state that explicitly.
4. Mention residual risk or test gaps.

Do not paste large diffs or long logs.
