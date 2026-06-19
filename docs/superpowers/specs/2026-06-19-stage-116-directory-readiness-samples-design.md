# Stage 116 Directory Readiness Samples Design

## Goal

Connect the checked-in community tool handoff directory examples to the
existing `external-tool-readiness` and `external-tool-workflow` preflight
guidance, for both CSV and JSON directory layouts.

## Reviewer Context

This design is for Claude Code / local opencode review before implementation.
Use local review with:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-116-plan-review-prompt.md)" > docs/reviews/opencode-stage-116-plan-review.md
```

## Background

Fashion Radar already supports user-controlled external community tools that
export sanitized local CSV or JSON rows. The project also has a checked-in
directory example at `examples/community-tool-handoff-directory.example/` with
separate `csv/` and `json/` directories.

The runtime already accepts the required directory, format, pattern, and source
name overrides in `build_external_tool_readiness(...)` and
`build_external_tool_workflow(...)`. This stage should not add any new runtime
feature. It should make the checked-in examples more useful by showing the
readiness/workflow preflight commands users should run before linting or
importing a directory export.

This prepares for future community/social tool exports provided by the user or
by other tools. Fashion Radar continues to ingest sanitized local files only.

## Decision

Use the existing `generic_community_export` adapter for both checked-in
directories:

- CSV example:
  `examples/community-tool-handoff-directory.example/csv`,
  `--input-format csv`, `--pattern "*.csv"`.
- JSON example:
  `examples/community-tool-handoff-directory.example/json`,
  `--input-format json`, `--pattern "*.json"`.
- Shared source name override:
  `--source-name "External Community Tool"`.

Document `external-tool-readiness` before `external-tool-workflow` for each
directory. Keep the commands as local guidance only; they print or read local
files and do not run upstream social tools, MCP servers, APIs, scrapers, or
browser automation.

## In Scope

- Add tests that prove the checked-in CSV and JSON example directories can be
  used with `build_external_tool_readiness(...)` and
  `build_external_tool_workflow(...)` overrides.
- Tighten CLI docs tests so the directory example README and import docs both
  include the concrete readiness/workflow commands for CSV and JSON.
- Update `examples/community-tool-handoff-directory.example/README.md` with a
  short optional preflight block.
- Update `docs/community-signal-import.md` so the directory example workflow
  starts with readiness/workflow preflight commands before lint/import dry-run.
- Add Stage 116 review artifacts.

## Out of Scope

- No runtime behavior changes.
- No connector, scraper, crawler, MCP server runner, API client, browser
  automation, account/session/cookie handling, platform search, scheduling, or
  monitoring.
- No compliance/audit/legal-review product feature.
- No schema changes.
- No dependency or lockfile changes.
- No new source acquisition, demand proof, ranking, or coverage verification.
- No changes to dashboard, scoring, collectors, source packs, entity packs, CI,
  or GitHub workflows.

## Expected User-Facing Behavior

After implementation, users can copy commands from the checked-in directory
example README or `docs/community-signal-import.md`:

```bash
uv run fashion-radar external-tool-readiness --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-workflow --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-readiness --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/json --input-format json --pattern "*.json" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-workflow --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/json --input-format json --pattern "*.json" --source-name "External Community Tool" --format table
```

The existing lint and dry-run import examples remain available.

## Acceptance Criteria

- The directory examples test suite proves readiness/workflow builders preserve:
  adapter id, display name, platform label, directory path, input format,
  pattern, source name, execution mode, and step count for both CSV and JSON.
- The same tests prove the generated readiness/workflow commands carry the
  checked-in directory override, format override, pattern override, and source
  name override.
- The JSON directory example proves `generic_community_export` can be used with
  a JSON override despite its default CSV recommendation.
- `tests/test_cli_docs.py` asserts both the example README and import docs
  include concrete `external-tool-readiness` and `external-tool-workflow`
  snippets for both directory layouts.
- Focused and adjacent tests pass.
- Full release gate passes.
- `uv.lock` and `pyproject.toml` remain unchanged.
