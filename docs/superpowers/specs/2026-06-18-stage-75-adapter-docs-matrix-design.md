# Stage 75 Adapter Docs Matrix Design

## Goal

Make the public external-tool adapter documentation explicitly list every
registered adapter id, display/source name, platform label, input format, and
filename pattern, then guard that matrix with exact docs tests.

## Context

Stages 72-74 hardened the runtime JSON contract, first-run smoke validation,
and smoke fixture parity for the seven external-tool adapters. The user-facing
documentation still describes adapter categories in prose, but it does not
provide a stable matrix of the exact adapter ids that users can pass to
`--adapter`.

That creates a discoverability gap: tests now guarantee the registry is stable,
but docs do not guarantee that a user can see all supported adapter ids without
running the CLI.

The first-run smoke docs also mention sample row, report, trend, and candidate
checks, but they do not mention that the automated first-run smoke now
validates the external-tool adapter registry JSON contract from
`external-tool-adapters --format json` across all seven adapters.

## Scope

In scope:

- Update `README.md`.
- Update `docs/cli-reference.md`.
- Update `docs/first-run.md`.
- Update `CHANGELOG.md`.
- Add a resolution note to `docs/reviews/opencode-stage-74-code-review.md`
  because its Minor finding about the Stage 74 plan-review artifact was fixed
  before the Stage 74 commit, but the review artifact still reads stale.
- Update `tests/test_cli_docs.py` with docs guards that require:
  - the same seven adapter matrix rows in both README and CLI reference;
  - the first-run smoke adapter-registry contract sentence in both README and
    first-run guide docs.

Out of scope:

- Runtime CLI behavior changes.
- Adapter registry code changes.
- Adding connectors, scraping, browser automation, platform APIs,
  login/cookie/session/token/proxy/CAPTCHA behavior, media downloads,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product behavior.

## Design

Add a small adapter matrix near the existing `external-tool-adapters`
documentation in both `README.md` and `docs/cli-reference.md`.

The matrix should list:

| Adapter id | Display/source name | Platform label | Format | Pattern |
| --- | --- | --- | --- | --- |
| `rednote_mcp` | Rednote MCP Export | `rednote` | `json` | `*.json` |
| `xiaohongshu_crawler` | Xiaohongshu Crawler Export | `xiaohongshu` | `csv` | `*.csv` |
| `instaloader` | Instaloader Export | `instagram` | `json` | `*.json` |
| `tiktok_api` | TikTok-Api Export | `tiktok` | `json` | `*.json` |
| `yt_dlp` | yt-dlp Metadata Export | `media` | `json` | `*.json` |
| `x_search_export` | X Search Export | `x` | `csv` | `*.csv` |
| `generic_community_export` | Generic Community Export | `community` | `csv` | `*.csv` |

Add a docs guard in `tests/test_cli_docs.py`:

- Define a stable `EXTERNAL_TOOL_ADAPTER_DOC_ROWS` tuple near the external-tool
  docs constants.
- In `test_external_tool_adapter_registry_docs_are_linked_and_bounded`, require
  each full Markdown row string to appear in both `README.md` and
  `docs/cli-reference.md`.

Full-row matching is intentional. Short tokens such as `x`, `csv`, `json`, and
`media` can appear elsewhere in docs, so individual substring assertions would
not prove that the matrix cells are present.

Add a sentence to the automated first-run smoke sections in `README.md` and
`docs/first-run.md`:

```text
The automated first-run smoke also validates the external-tool adapter registry JSON contract from `external-tool-adapters --format json` across all seven adapters.
```

Add a matching docs guard in `tests/test_cli_docs.py` for both docs.

Add a concise Stage 75 changelog entry under `[Unreleased]`, noting that the
change is documentation/test-only and adds no runtime adapter or
external-platform behavior.

Append a short correction note to `docs/reviews/opencode-stage-74-code-review.md`
stating that the M1 artifact issue was resolved before the Stage 74 commit and
publish.

## Test Strategy

- Run the focused docs tests after adding the guards and before docs updates to
  confirm the new assertions fail for missing docs.
- Run the focused docs tests after docs updates to confirm they pass.
- Run all CLI docs tests.
- Run ruff on `tests/test_cli_docs.py`.
- Run release hygiene, `git diff --check`, and full pytest before commit.

## Acceptance Criteria

- `README.md` and `docs/cli-reference.md` both show the complete adapter matrix.
- The docs guard fails if any full adapter matrix row disappears from README or
  CLI reference.
- `README.md` and `docs/first-run.md` both say the automated first-run smoke
  validates the external-tool adapter registry JSON contract from
  `external-tool-adapters --format json` across all seven adapters.
- `CHANGELOG.md` includes a Stage 75 docs entry.
- Stage 74 review artifact has a correction note for the stale M1 finding.
- Runtime/source files remain untouched.
