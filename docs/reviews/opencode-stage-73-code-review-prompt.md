# Stage 73 Code Review Prompt

Review the Stage 73 implementation in `/home/ubuntu/fashion-radar`.

Use a code-review stance. Lead with Critical or Important findings if present,
then Minor notes. Focus on correctness, regression risk, test coverage, and
whether the implementation stays inside the intended static smoke-contract
scope. Do not propose adding scraping, connectors, browser automation, platform
APIs, login/cookie/session/token/proxy behavior, CAPTCHA handling, media
download, monitoring/scheduling, source acquisition, demand proof, ranking,
coverage verification, or compliance-review product behavior.

For this stage, the user explicitly directed local review through
`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`; this
stage-local review path does not change broader repository review protocol
documents.

## Goal

Extend first-run smoke validation of `external-tool-adapters --format json` so
the smoke path validates all seven adapter entries instead of only the first
`rednote_mcp` entry.

## Touched Files

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-18-stage-73-adapter-smoke-contract-design.md`
- `docs/superpowers/plans/2026-06-18-stage-73-adapter-smoke-contract-plan.md`
- `docs/reviews/opencode-stage-73-plan-review-prompt.md`
- `docs/reviews/opencode-stage-73-plan-review.md`
- `docs/reviews/opencode-stage-73-code-review-prompt.md`

## Implementation Summary

- Added a pinned `EXPECTED_EXTERNAL_TOOL_ADAPTERS` map to
  `scripts/check_first_run_smoke.py`.
- Refactored `validate_external_tool_adapters` to:
  - preserve the payload/object, contract version, execution mode, and
    non-empty adapter-list prelude checks;
  - require the exact seven adapter ids in registry order;
  - pin public metadata fields for every adapter;
  - validate every adapter's `recommended_commands` list;
  - shell-parse every recommended command;
  - require the exact nine `fashion-radar <command>` prefixes in order;
  - require exactly one `external-tool-readiness` command per adapter;
  - check each readiness command prefix, `--adapter`, `--directory`,
    `--input-format`, `--pattern`, `--source-name`, and `--format table`;
  - require non-empty `--config-dir`, `--data-dir`, and `--as-of` values.
- Expanded `tests/test_first_run_smoke.py::external_tool_adapters_payload` to a
  registry-like seven-adapter fixture.
- Added `shlex.join`-based test helpers so glob patterns and multi-word source
  names are shell-quoted consistently.
- Updated negative tests to cover later-adapter id drift, adapter reorder,
  metadata drift, missing command lists, command-prefix drift, duplicate
  readiness command count, and later-adapter readiness input-format drift.
- Kept runtime CLI, adapter registry code, platform collection, and first-run
  flow behavior unchanged.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_adapters"
uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Latest broad verification result: full pytest collected 1099 tests and all
passed.

## Review Questions

1. Does the implementation actually validate all seven adapters in first-run
   smoke, including later adapter drift?
2. Does the expanded fixture stay registry-like without importing runtime
   registry code into the smoke contract?
3. Are the public metadata and exact recommended command-prefix checks scoped
   appropriately to static smoke contract validation?
4. Did the implementation accidentally alter first-run command sequencing,
   runtime adapter behavior, or external platform behavior?
5. Are there any Critical or Important issues to fix before commit?
