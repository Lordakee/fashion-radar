# Stage 68 Code Review Prompt

You are reviewing the current uncommitted Stage 68 workspace in `/home/ubuntu/fashion-radar`.

Use model-level rigor. Do not edit files. Review for correctness, regression risk, and missing tests.

## Stage Goal

Add the existing `external-tool-readiness` command to every `external-tool-adapters` registry entry's `recommended_commands` list.

## Required Semantics

- `external-tool-adapters` remains `print_only`.
- `external-tool-adapters` must not call `external-tool-readiness`.
- `external-tool-adapters` must not inspect PATH, inspect directories, open SQLite, read handoff files, validate files, import rows, execute generated commands, or perform source/platform acquisition.
- The new recommended command must appear immediately after `community-signal-profile`.
- The new command must include:
  - `fashion-radar external-tool-readiness`
  - `--adapter <adapter_id>`
  - `--directory <directory>`
  - `--config-dir <config_dir>`
  - `--data-dir <data_dir>`
  - `--as-of <as_of>`
  - `--input-format <format>`
  - `--pattern <pattern>`
  - `--source-name <source_name>`
  - `--format table`
- The command should use the existing shell-quoting helper behavior for paths, patterns, and source names.
- `external-tool-template` table/model guidance may inherit the adapter command list, including readiness.
- `external-tool-template` JSON/CSV handoff output must remain rows-only and must not include readiness command guidance.
- `external-tool-readiness` and `external-tool-workflow` behavior should remain unchanged by this stage.

## Files In Scope

- `src/fashion_radar/external_tool_adapters.py`
- `tests/test_external_tool_adapters.py`
- `tests/test_external_tool_templates.py`
- `tests/test_cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`
- Stage 68 plan/review artifacts under `docs/superpowers/` and `docs/reviews/`

## Verification Already Run

- `uv --no-config run --frozen pytest tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q -k "external_tool_adapters or external_tool_template or run_first_run_flow"`
  - `36 passed, 377 deselected`
- `uv --no-config run --frozen pytest tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_external_tool_readiness.py tests/test_external_tool_workflow.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q`
  - `440 passed`
- `uv --no-config run --frozen ruff check src/fashion_radar/external_tool_adapters.py tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py`
  - passed
- `uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_adapters.py tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py`
  - passed
- `uv --no-config run --frozen python scripts/check_release_hygiene.py`
  - passed
- `git diff --check`
  - passed
- `uv --no-config run --frozen pytest`
  - `1099 passed`

## Review Output Format

Return:

1. Findings, ordered by severity.
2. For each finding, include file path, line number, severity (`Critical`, `Important`, or `Minor`), and concrete impact.
3. If no Critical/Important issues exist, state that explicitly.
4. Mention any residual risk or test gap.

Do not paste large diffs or long logs.
