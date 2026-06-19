# Stage 115 XPOZ Adapter Metadata Design

## Goal

Add an `xpoz_mcp` external-tool adapter metadata target so Fashion Radar can
print local handoff guidance for sanitized XPOZ MCP / XPOZ Social Data API
exports.

## Reviewer Context

This design is for Claude Code / local opencode review before implementation.
Use local review with:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-115-plan-review-prompt.md)" > docs/reviews/opencode-stage-115-plan-review.md
```

## Background

The user wants a GitHub-ready fashion radar tool that can later ingest social
signals from free or free-tier sources such as Xiaohongshu/Rednote,
Instagram, TikTok, X/Twitter, and community tools. The project already has a
local external-tool handoff contract:

- `external-tool-adapters` prints adapter metadata and copyable local commands.
- `external-tool-template` prints importable sanitized CSV/JSON sample rows.
- `external-tool-readiness` prints local read-only preflight guidance.
- `external-tool-workflow` prints the local handoff workflow.

XPOZ is a useful next target because its current public pages and GitHub
project present it as a social data API/MCP/SDK covering Twitter/X,
Instagram, TikTok, and Reddit. Fashion Radar should not call XPOZ, run MCP
servers, persist API keys, scrape platforms, or fetch remote data in this
stage. It should only expose the metadata target that lets a user-controlled
XPOZ export be converted to the existing sanitized community signal row shape.

## Decision

Add a new adapter with:

- `id`: `xpoz_mcp`
- `display_name`: `XPOZ MCP Export`
- `platform_label`: `community`
- `suggested_source_name`: `XPOZ MCP Export`
- `recommended_input_format`: `json`
- `recommended_pattern`: `*.json`
- `upstream_tool_examples`: `["XPOZ MCP", "XPOZ Social Data API"]`

Use `platform_label="community"` because the current platform labels are local
provenance suggestions, not a schema enum. XPOZ is multi-platform, and adding a
new `social` or `multi_platform_social` label would unnecessarily widen the
community signal profile in this stage.

`external-tool-readiness` should treat `xpoz_mcp` as `not_applicable` for
`upstream_command`, because this project should not depend on a specific XPOZ
CLI command or run a remote service. The install hint can point users to the
XPOZ MCP / Social Data API docs and remind them to export sanitized local JSON
rows.

## In Scope

- Add `xpoz_mcp` to `src/fashion_radar/external_tool_adapters.py`.
- Add a readiness mapping in `src/fashion_radar/external_tool_readiness.py`.
- Update adapter id/order expectations and collection counts in focused tests.
- Update first-run smoke pinned adapter fixtures and drift tests.
- Update adapter matrices in `README.md` and `docs/cli-reference.md`.
- Add or update tests that prove JSON/template/readiness/workflow parity for
  the new adapter.

## Out of Scope

- No scraper, crawler, connector, MCP server runner, API client, browser
  automation, account/session/cookie handling, platform search, scheduling, or
  monitoring.
- No compliance/audit/legal-review product feature.
- No schema changes.
- No dependency or lockfile changes.
- No persistence of external credentials.
- No changes to source packs, entity packs, scoring, dashboard, importer
  behavior, or report generation.

## Expected User-Facing Behavior

After implementation:

```bash
uv run fashion-radar external-tool-adapters --adapter xpoz_mcp --format json
uv run fashion-radar external-tool-template --adapter xpoz_mcp --format json
uv run fashion-radar external-tool-readiness --adapter xpoz_mcp --format json
uv run fashion-radar external-tool-workflow --adapter xpoz_mcp --format json
```

should all work locally and print metadata / importable sample rows / local
workflow guidance only.

Unfiltered adapter/template commands should include the new adapter, so the
registry count becomes 8 and the unfiltered template row count becomes 16.

## Acceptance Criteria

- `xpoz_mcp` is present in the registry in stable order after
  `x_search_export` and before `generic_community_export`.
- The adapter emits the standard nine recommended handoff commands.
- `external-tool-template --adapter xpoz_mcp --format json` prints importable
  community signal rows with `source_name="XPOZ MCP Export"` and
  `platform="community"`.
- `external-tool-readiness --adapter xpoz_mcp --format json` reports a
  `not_applicable` upstream command check and does not call `shutil.which`.
- First-run smoke fixture validation pins the new adapter details.
- README and CLI reference adapter matrices include `xpoz_mcp`.
- Full release gate remains green.
