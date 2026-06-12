# Stage 13 Community Signal Import Contract Design

## Goal

Prepare Fashion Radar to accept sanitized community and social-tool outputs from
external tools as local CSV/JSON imports. The stage should give the user a clear
contract that other tools can target, plus checked examples that prove the
existing `import-signals` command can validate those files.

The implementation must stay local-first and free-first. It should not add any
new collector, platform connector, browser automation, account automation,
unofficial API, or source-acquisition workflow.

## Context

Stage 9 added `fashion-radar import-signals` for local user-provided CSV/JSON
files. It already validates the fields needed for external community-tool
handoff:

- `url`
- `title`
- `published_at`
- optional `summary`
- optional `source_name`
- optional `platform`
- optional `source_weight`
- optional `collected_at`

It also ignores unknown CSV/JSON fields before storage, stores rows as
`manual_import`, and does not persist platform labels, author handles, raw
comments, account IDs, media, or account data.

Stage 13 should therefore avoid duplicating the importer. The correct next step
is to define a stable external-tool contract around the existing importer.

## Recommended Approach

Add a repository-level community signal import contract:

- `docs/community-signal-import.md` explains how external tools should output
  sanitized rows.
- `examples/community-signals.example.csv` shows the CSV form accepted by
  `import-signals`.
- `examples/community-signals.example.json` shows the JSON object form accepted
  by `import-signals`.
- `schemas/community-signals.schema.json` documents the strict JSON contract for
  tools that can validate their output before handoff.
- Tests load the examples through the existing `load_manual_signal_rows()`
  parser and check that the schema excludes private/raw fields.

This keeps Fashion Radar ready for the user's future community/social tools
without adding platform-specific acquisition logic to this repository.

## Non-Goals

Stage 13 does not implement or document:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, Discord,
  Telegram, WeChat, or other platform connectors.
- Web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or platform search.
- Login cookies, account/session files, browser profiles, tokens, credentials,
  proxies, proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass.
- Official or unofficial social platform APIs.
- Instructions for obtaining platform exports from social platforms or
  communities.
- Raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile URLs, images, videos, media downloading, reposting, or archive
  redistribution.
- Google News RSS or any new source type.
- Complete source coverage, platform-wide coverage, community-wide coverage,
  market-wide trend proof, verified demand outside the configured source set,
  real-time social monitoring, or top social trends.
- LLM scoring, embeddings, vector databases, image recognition, paid service
  requirements, or sentiment analysis.
- DB migrations, persistent adapter tables, source-health changes, collector
  changes, dashboard changes, report semantics changes, or network calls.
- A product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Contract

External tools should output one item per observed signal. The item should be
small, reviewable, and link back to the source or a stable reference page.

Required fields:

- `url`: source URL or stable reference URL for the observed item.
- `title`: short observed text, headline, or normalized signal phrase.
- `published_at`: ISO 8601-compatible publication or observation timestamp.

Optional fields:

- `summary`: short sanitized note. This is the right place for an editorial note
  such as "seen in a stylist newsletter roundup" or "bag silhouette mentioned in
  a community digest."
- `source_name`: display name for the external tool or local export.
- `platform`: short provenance label supplied by the user or external tool. This
  is not stored as platform coverage and does not imply complete visibility.
- `source_weight`: numeric local score weight in `(0, 5]`.
- `collected_at`: ISO 8601-compatible timestamp for when the external tool
  produced the row.

The strict JSON schema should accept either:

```json
[
  {
    "url": "https://example.com/community/a",
    "title": "East-west tote interest",
    "published_at": "2026-06-12T08:00:00Z"
  }
]
```

or:

```json
{
  "items": [
    {
      "url": "https://example.com/community/a",
      "title": "East-west tote interest",
      "published_at": "2026-06-12T08:00:00Z"
    }
  ]
}
```

The schema should reject additional JSON properties so external tools do not
accidentally output private or raw fields. The runtime importer still ignores
unknown keys for backwards compatibility with Stage 9 manual imports; Stage 13
does not change that importer behavior.

CSV producers should follow the same allowed field set even though JSON Schema
cannot validate CSV files. The repository CSV example is the recommended CSV
handoff template. Unknown CSV columns may be ignored by the existing manual
importer for backwards compatibility, but external community tools should not
emit unknown, raw, private, media, account, cookie, session, or token fields.

## Data Flow

```text
External community/social tool
  -> writes sanitized CSV/JSON file locally
  -> optional external validation against schemas/community-signals.schema.json
  -> fashion-radar import-signals --dry-run
  -> fashion-radar import-signals
  -> existing manual_import item storage
  -> existing match/report/candidates/trends/dashboard workflows
```

Fashion Radar reads only the local file passed to `import-signals`. It does not
fetch the URL, call platform APIs, log in, download media, or inspect account
state.

## Files

Create:

- `docs/community-signal-import.md`
- `examples/community-signals.example.csv`
- `examples/community-signals.example.json`
- `schemas/community-signals.schema.json`
- `tests/test_community_signal_import_contract.py`

Modify:

- `README.md`
- `docs/manual-signal-import.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `CHANGELOG.md`

## Testing

Focused tests should prove:

- CSV example rows load through `load_manual_signal_rows()`.
- JSON example rows load through `load_manual_signal_rows()`.
- Both example formats use the same allowed public contract fields.
- The JSON schema is valid JSON, documents the required fields, bounds
  `source_weight` to `(0, 5]`, and excludes private/raw fields such as
  `author_handle`, `raw_comment`, `account_id`, `follower_count`, `image_url`,
  and `video_url`.
- The existing `import-signals --dry-run` command validates the examples without
  creating config/data/report directories, SQLite files, or workflow artifacts.

No test should call the network or use platform tooling.

## Documentation

Documentation should explain:

- This is a local handoff contract for outputs from tools the user controls.
- External tools should output sanitized rows only.
- The examples can be copied as templates.
- `import-signals --dry-run` is the first check before importing.
- After import, users can run `match`, `report`, `candidates`, and `trends`.
- Platform/community labels are provenance only.
- Results remain local observed signals from configured sources and imported
  local files, not market-wide or platform-wide truth.

The docs should not instruct users how to acquire platform exports, bypass
platform controls, automate accounts, or scrape platforms.

## Verification

Required verification before Stage 13 code review:

- Focused example/schema/import tests.
- Full `pytest -q`.
- `ruff check .`.
- `ruff format --check .`.
- `git diff --check`.
- `uv lock --check --default-index https://pypi.org/simple`.
- `uv sync --locked --dev --check --default-index https://pypi.org/simple`.
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`.
- Wheel/sdist build.
- Installed-wheel smoke for `import-signals --help` and dry-run validation of
  copied community examples.
- CodeGraph status.
- Claude Code code review with `--effort max`.
