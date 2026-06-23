# Stage 181 Community Docs Adapter Catalog Parity Design

## Objective

Add docs/test-only parity coverage so the community signal import and quality
docs list the current external social/community tool adapter catalog.

## Background

The runtime adapter registry already exposes built-in metadata targets for
Rednote/Xiaohongshu, Instagram, TikTok, media metadata, X search exports, XPOZ
MCP exports, and generic community exports. README and the CLI reference already
show the exact `Known adapter ids` table. The community import and quality docs
describe the registry only at category level, so a user following those docs has
to jump elsewhere to see exact adapter ids such as `rednote_mcp`,
`instaloader`, `tiktok_api`, `x_search_export`, and `xpoz_mcp`.

This stage makes those community docs self-contained and guards them against
future registry drift by deriving expected table rows from
`build_external_tool_adapter_registry(...)`.

## Scope

In scope:

- Add a docs parity test in `tests/test_external_tool_contract_parity.py`.
- Add a compact `Known adapter ids` table to `docs/community-signal-import.md`.
- Add the same compact `Known adapter ids` table to
  `docs/community-signal-quality.md`.
- Reuse the existing README/CLI table semantics:
  - adapter id;
  - display/source name;
  - advisory platform label;
  - recommended input format;
  - recommended filename pattern.
- Preserve the advisory-only wording for `suggested_platform_labels`.
- Add Stage 181 plan/review artifacts.

Out of scope:

- Runtime adapter changes.
- CLI command changes.
- New connectors, source acquisition, scraping, browser automation, platform
  APIs, login/cookie/token behavior, monitoring, scheduling, demand proof,
  ranking, platform coverage verification, or compliance-review product
  features.
- Dependency, lockfile, source-pack, entity-pack, package archive, first-run
  smoke, or release hygiene behavior changes.

## Technical Approach

Add a helper in `tests/test_external_tool_contract_parity.py` that formats a
Markdown row from each adapter in the existing `registry` fixture:

```python
| `{adapter.id}` | {adapter.display_name} | `{adapter.platform_label}` | `{adapter.recommended_input_format}` | `{adapter.recommended_pattern}` |
```

The test should read both community docs, normalize whitespace, require
`Known adapter ids:`, require every registry-derived row, and require the
advisory label boundary phrases already used by README/CLI:

- `Display/source name column`
- `suggested_platform_labels`
- `advisory local provenance`
- `not a schema enum`
- `not a linter restriction`
- `not platform coverage`
- `not demand proof`

Then add the current adapter table and the two explanatory paragraphs to both
docs. The table rows should match current runtime registry values exactly:

| Adapter id | Display/source name | Platform label | Format | Pattern |
| --- | --- | --- | --- | --- |
| `rednote_mcp` | Rednote MCP Export | `rednote` | `json` | `*.json` |
| `xiaohongshu_crawler` | Xiaohongshu Crawler Export | `xiaohongshu` | `csv` | `*.csv` |
| `instaloader` | Instaloader Export | `instagram` | `json` | `*.json` |
| `tiktok_api` | TikTok-Api Export | `tiktok` | `json` | `*.json` |
| `yt_dlp` | yt-dlp Metadata Export | `media` | `json` | `*.json` |
| `x_search_export` | X Search Export | `x` | `csv` | `*.csv` |
| `xpoz_mcp` | XPOZ MCP Export | `community` | `json` | `*.json` |
| `generic_community_export` | Generic Community Export | `community` | `csv` | `*.csv` |

## Acceptance Criteria

- `tests/test_external_tool_contract_parity.py` has a focused test that fails
  when either community doc omits the registry table, omits a current adapter
  row, or omits the advisory platform-label boundary wording.
- `docs/community-signal-import.md` includes the current adapter table under
  `## External Tool Adapter Registry`.
- `docs/community-signal-quality.md` includes the current adapter table near
  the existing `external-tool-adapters` guidance.
- Focused external-tool contract parity tests pass.
- Focused docs link/boundary tests in `tests/test_cli_docs.py` still pass.
- Ruff check and format check pass for the touched test file.
- Full release gate remains clean before commit.
