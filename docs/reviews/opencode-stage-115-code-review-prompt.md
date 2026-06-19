# Stage 115 Code Review Prompt

You are reviewing the Stage 115 code changes in `/home/ubuntu/fashion-radar`.

Goal:

Add a new `xpoz_mcp` external-tool adapter metadata target for sanitized XPOZ
MCP / XPOZ Social Data API exports.

Design and plan:

- `docs/superpowers/specs/2026-06-19-stage-115-xpoz-adapter-metadata-design.md`
- `docs/superpowers/plans/2026-06-19-stage-115-xpoz-adapter-metadata-plan.md`
- Final plan rereview: `docs/reviews/opencode-stage-115-plan-rereview.md`

Changed runtime/docs/test files:

- `src/fashion_radar/external_tool_adapters.py`
- `src/fashion_radar/external_tool_readiness.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_external_tool_adapters.py`
- `tests/test_external_tool_readiness.py`
- `tests/test_external_tool_templates.py`
- `tests/test_external_tool_contract_parity.py`
- `tests/test_cli.py`
- `tests/test_first_run_smoke.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/cli-reference.md`
- `docs/first-run.md`

Expected behavior:

- Registry order is:
  `rednote_mcp`, `xiaohongshu_crawler`, `instaloader`, `tiktok_api`,
  `yt_dlp`, `x_search_export`, `xpoz_mcp`, `generic_community_export`.
- `xpoz_mcp` metadata:
  - display/source name: `XPOZ MCP Export`
  - platform label: `community`
  - format/pattern: `json` / `*.json`
  - upstream examples: `XPOZ MCP`, `XPOZ Social Data API`
  - description: sanitized XPOZ MCP / Social Data API exports created outside
    Fashion Radar.
- Readiness for `xpoz_mcp` uses `command=None` and reports
  `not_applicable`; Fashion Radar does not run XPOZ, MCP servers, APIs, or
  platform tools.
- Unfiltered external-tool template output now has 16 items.
- README, CLI reference, first-run docs, test fixtures, and smoke script are
  aligned with eight adapters.

Verification already run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_external_tool_adapters.py \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_templates.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli.py::test_external_tool_adapters_command_prints_json \
  tests/test_cli.py::test_external_tool_template_command_prints_all_adapters_when_unfiltered \
  tests/test_first_run_smoke.py \
  tests/test_cli_docs.py -q
# 174 passed

env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_workflow.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_external_tool_templates.py \
  tests/test_external_tool_adapters.py \
  tests/test_cli_docs.py \
  tests/test_first_run_smoke.py -q
# 181 passed

uv --no-config run --frozen fashion-radar external-tool-adapters --adapter xpoz_mcp --format json
uv --no-config run --frozen fashion-radar external-tool-template --adapter xpoz_mcp --format json
uv --no-config run --frozen fashion-radar external-tool-readiness --adapter xpoz_mcp --format json
uv --no-config run --frozen fashion-radar external-tool-workflow --adapter xpoz_mcp --format json

uv --no-config run --frozen ruff check \
  src/fashion_radar/external_tool_adapters.py \
  src/fashion_radar/external_tool_readiness.py \
  tests/test_external_tool_adapters.py \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_templates.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli.py \
  tests/test_first_run_smoke.py \
  scripts/check_first_run_smoke.py \
  tests/test_cli_docs.py
# All checks passed

uv --no-config run --frozen ruff format --check \
  src/fashion_radar/external_tool_adapters.py \
  src/fashion_radar/external_tool_readiness.py \
  tests/test_external_tool_adapters.py \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_templates.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli.py \
  tests/test_first_run_smoke.py \
  scripts/check_first_run_smoke.py \
  tests/test_cli_docs.py
# 10 files already formatted

git diff --check
```

Please review the current uncommitted diff and report findings ordered by
severity:

- Critical: must fix before commit.
- Important: should fix before release gate or commit.
- Minor: optional cleanup.

Focus on correctness and drift risks. Do not request scraper, connector, MCP
execution, API client, schema, dependency, lockfile, compliance/audit/legal
review, dashboard, importer, scoring, or report changes.

If there are no Critical/Important findings, say that explicitly.
