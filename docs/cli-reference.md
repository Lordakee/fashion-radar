# CLI Reference

This is a compact map of the current public `fashion-radar` command surface.
Use `fashion-radar COMMAND --help` for full Typer help and defaults.

## Beginner Roadmap

The roadmap uses existing commands only and points to detail docs instead of
duplicating each command block.

Boundaries: does not add live collection; does not add platform automation;
does not add connectors.

| Phase | Existing Commands | Where To Read Next |
| --- | --- | --- |
| Setup | `init`, `migrate-db`, `doctor` | [first-run.md](first-run.md) |
| Local sample/import | `community-signal-lint`, `import-signals`, `import-signals-dir` | [first-run.md](first-run.md) |
| Match/report/review | `match`, `report`, `candidates`, `trends`, `imported-signals` | [first-run.md](first-run.md) |
| Dashboard | `dashboard` | [first-run.md](first-run.md) |
| Optional entity matching | `entity-pack-lint` | [entity-packs.md](entity-packs.md) |
| Cleanup | Reset The Repo-Local Sample | [first-run.md](first-run.md) |

## Shared Path Options

Most operational commands accept path options with dynamic defaults:

- `--config-dir`: reads config files, or `FASHION_RADAR_CONFIG_DIR`.
- `--data-dir`: reads/writes local SQLite state, or `FASHION_RADAR_DATA_DIR`.
- `--reports-dir`: writes or reads report artifacts, or
  `FASHION_RADAR_REPORTS_DIR`.

Without those flags or environment variables, paths resolve to
platform-specific user directories. For repo-local experiments, pass the same
paths through the whole sequence so every command reads and writes the same
checkout-local config, SQLite, and report locations. The first-run onboarding
guide in [first-run.md](first-run.md) uses this same path pattern.

```bash
AS_OF="2026-06-13T12:00:00Z"
fashion-radar collect --config-dir "$PWD/configs" --data-dir "$PWD/data"
fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$AS_OF"
```

With `--as-of "2026-06-13T12:00:00Z"` and `--reports-dir "$PWD/reports"`,
the report command writes `reports/fashion-radar-2026-06-13.md` and
`reports/fashion-radar-2026-06-13.json`.

`scripts/check_first_run_smoke.py` is a source-checkout and release-package
smoke helper used by README, CI, and the upload checklist. It is not a normal
public `fashion-radar` CLI command; run it with Python when you need the
deterministic first-run smoke. It is the deterministic sample-output gate: it
validates deterministic sample output content, not only command execution.

## Setup And Operations

- `init`: create local starter config, data, and report directories; supports
  `--config-dir`, `--data-dir`, and `--reports-dir`.
- `migrate-db`: initialize or upgrade the local SQLite schema; supports
  `--data-dir`.
- `doctor`: check local paths and required config files; supports
  `--config-dir`, `--data-dir`, and `--reports-dir`.
- `source-pack-lint` PATH: lint one source pack without collecting sources;
  supports `--format table|json` and `--strict`.
- `entity-pack-lint` PATH: lint one entity pack without matching or collecting;
  supports `--format table|json` and `--strict`.
- `collect`: collect configured public sources into local SQLite; supports
  `--config-dir`, `--data-dir`, and `--now`.
- `match`: match configured entities against stored items; supports
  `--config-dir` and `--data-dir`.
- `report`: generate Markdown and JSON reports; requires `--as-of` and supports
  `--config-dir`, `--data-dir`, `--reports-dir`, `--digest-latest`,
  `--digest-index`, `--digest-eml`, and `--digest-summary`.
- `run`: run `collect -> match -> report` serially; requires `--as-of` and
  supports the same path and digest options as `report`.
- `schedule-example`: print safe scheduling snippets without installing them.
  Run `fashion-radar schedule-example --help` for current mode, time, project,
  config, data, and reports options.

## Local Import And Community Handoff

External tool import uses existing local commands only. For a user-controlled external export directory
that already contains a sanitized CSV/JSON local file handoff, use
[community-signal-import.md](community-signal-import.md) and follow:
`external-tool-adapters -> external-tool-readiness -> external-tool-workflow ->
community-signal-lint-dir -> community-candidates-dir ->
community-handoff-check-dir -> import-signals-dir -> imported-review-workflow`.
This route does not run upstream tools, does not search platforms, does not
scrape, does not call platform APIs, and does not add connectors.

- `import-signals` PATH: import one local CSV or JSON signal file. The
  `--format csv|json` flag selects the input format. Supports `--data-dir`,
  `--source-name`, `--imported-at`, and `--dry-run`.
- `import-signals-dir` DIRECTORY: validate or import direct-child files from
  one local directory. Requires `--format csv|json` and `--pattern`. Supports
  `--data-dir`, `--imported-at`, `--dry-run`, `--output-format table|json`, and
  `--source-name`.
- `community-signal-profile`: print the local producer contract for external
  user-controlled tools that write sanitized community signal CSV/JSON handoff
  files; supports `--format table|json`.
- `external-tool-adapters`: print the external social/community tool adapter
  registry as a local producer-discovery registry for user-controlled
  external/community tools that need sanitized CSV/JSON local file handoff
  targets. Supports `--adapter`, `--directory`, `--config-dir`, `--data-dir`,
  `--as-of`, and `--format table|json`. It is local and print-only: it does
  not run adapters, inspect directories, read handoff files, validate files,
  import rows, open SQLite, or create artifacts. It is not platform collection
  and has no connectors, no scraping, no browser automation, no platform APIs,
  no monitoring, no scheduling, no source acquisition, no demand proof, no
  ranking, and no coverage verification. Each adapter command list includes
  `external-tool-readiness` as an optional local read-only preflight command,
  while `external-tool-adapters` itself remains print-only and does not run
  readiness or perform PATH lookup.

  Known adapter ids:

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

  The Display/source name column reflects the current registry `display_name`
  and `suggested_source_name` values, which are identical for these adapters.

  The Platform label column reflects `suggested_platform_labels` as advisory local
  provenance label guidance for the optional handoff `platform` field. These
  labels are local provenance suggestions only: they are not a schema enum, not a
  linter restriction, not platform coverage, and not demand proof.
- `external-tool-template`: print local adapter-specific template rows for
  user-controlled external/community tools that need sanitized CSV/JSON local
  file handoff examples. Supports `--adapter`, `--directory`, `--config-dir`,
  `--data-dir`, `--as-of`, and `--format table|json|csv`. It is local and
  print-only: JSON and CSV output contain importable community handoff rows
  only, table output may include metadata and copyable commands, and the
  command does not write files, run adapters, inspect directories, read
  handoff files, validate files, import rows, open SQLite, or create artifacts.
  It is not platform collection and has no connectors, no scraping, no browser
  automation, no platform APIs, no monitoring, no scheduling, no source
  acquisition, no demand proof, no ranking, and no coverage verification. The
  JSON/CSV handoff rows remain importable row output only, while table/model
  guidance can include the same adapter recommended command list.
- `external-tool-workflow`: print workflow metadata for user-controlled
  external/community tools that need a producer-facing wrapper around existing
  local commands before writing sanitized CSV/JSON local file handoff rows.
  Supports `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`,
  `--input-format csv|json`, `--pattern`, `--source-name`, and
  `--format table|json`. It is local and print-only: JSON output is
  workflow metadata, not importable handoff rows, table output may include
  metadata and copyable commands, and the printed steps include
  `check_external_tool_readiness`, an optional preflight command that points to
  `external-tool-readiness` for local command availability guidance before
  sanitized handoff rows are prepared. The command does not run generated
  commands, adapters, or upstream tools, inspect directories, read handoff
  files, validate rows, import rows, open SQLite, or create artifacts. It is
  not platform collection and has no connectors, no scraping, no browser
  automation, no platform APIs, no monitoring, no scheduling, no source
  acquisition, no demand proof, no ranking, and no coverage verification.
- `external-tool-readiness`: report external tool readiness and local command
  readiness for known free external/community tools such as Rednote MCP,
  Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, and X/search exports.
  Supports `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`,
  `--input-format csv|json`, `--pattern`, `--source-name`, and
  `--format table|json`. It is local read-only, not print-only, because it
  performs command availability only with local PATH lookup (`shutil.which`).
  It prints readiness guidance, mirror-friendly install hints, and Fashion
  Radar next-step handoff commands for user-controlled external/community tools
  producing sanitized CSV/JSON local file handoff rows. It does not install
  dependencies automatically, does not run adapters, does not run upstream
  tools, does not inspect directories, does not read handoff files, validate
  rows, import rows, open SQLite, or create artifacts. It is not platform
  collection and has no connectors, no scraping, no browser automation, no
  platform APIs, no account/session/cookie/token behavior, no monitoring, no
  scheduling, no source acquisition, no demand proof, no ranking, no coverage
  verification, and no compliance-review product feature.
- `community-signal-lint` PATH: lint one community signal handoff file. Requires
  `--input-format csv|json`; supports `--format table|json`, `--source-name`,
  and `--strict`.
- `community-signal-lint-dir` DIRECTORY: lint matching direct-child handoff
  files. Requires `--input-format csv|json` and `--pattern`; supports
  `--format table|json`, `--source-name`, and `--strict`.
- `community-candidates` PATH: preview candidate phrases from one community
  signal file. Requires `--as-of`; supports `--config-dir`, `--input-format`,
  `--source-name`, `--limit`, and `--format table|json`.
- `community-candidates-dir` DIRECTORY: preview candidate phrases from matching
  direct-child community files. Requires `--as-of`; supports `--config-dir`,
  `--input-format`, `--pattern`, `--source-name`, `--limit`, and
  `--format table|json`.
- `community-handoff-manifest` DIRECTORY: print a local producer manifest for a
  community handoff directory without reading it. Requires `--as-of`; supports
  `--config-dir`, `--data-dir`, `--input-format`, `--pattern`, `--source-name`,
  and `--format table|json`.
- `community-handoff-workflow` DIRECTORY: print a local handoff checklist
  without executing commands. Requires `--as-of`; supports `--config-dir`,
  `--data-dir`, `--input-format`, `--pattern`, `--source-name`, and
  `--format table|json`. The printed steps include
  `lint_handoff_directory`, `preview_candidate_phrases`,
  `review_handoff_readiness`, `dry_run_directory_import`,
  `import_directory_signals`, and `print_post_import_review`; the
  `review_handoff_readiness` step prints the `community-handoff-check-dir`
  local-only handoff readiness report before importing rows. The workflow does
  not execute commands, read directories, import rows, write artifacts, or add
  platform/source acquisition, scraping, crawling, login, scheduling,
  monitoring, platform API, media download, connector, demand proof, ranking,
  coverage verification, entity generation, compliance, policy, authorization,
  or safety-review features.
- `community-handoff-check-dir` DIRECTORY: print a local-only handoff readiness
  report for matched local regular files and local config without importing
  rows, opening SQLite, creating config/data/report/dashboard/digest artifacts,
  or adding fetch URLs/login/platform APIs/download media/browser automation/
  scrape/crawl/monitor/watch/schedule/connectors/source acquisition/demand
  proof/ranking/coverage verification/entity generation/compliance/policy/
  authorization/safety-review features. Requires `--as-of`; supports
  `--config-dir`, `--input-format`, `--pattern`, `--source-name`, `--limit`,
  `--strict`, and `--format table|json`.

For local/external tools that need machine-readable example discovery,
`fashion-radar community-signal-profile --format json` and
`fashion-radar community-handoff-manifest DIRECTORY --format json` include
`directory_example_paths` with these checked-in directory layout pointers:

- `examples/community-tool-handoff-directory.example/README.md`
- `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
- `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
- `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
- `examples/community-tool-handoff-directory.example/json/community-tool-b.json`

For copyable `generic_community_export` CSV/JSON `external-tool-readiness` /
`external-tool-workflow` preflight examples against the checked-in directory
examples, see
[community-signal-import.md#external-tool-export-directory-examples](community-signal-import.md#external-tool-export-directory-examples).

Print adapter registry examples:

```bash
fashion-radar external-tool-adapters --format table
fashion-radar external-tool-adapters --format json
fashion-radar external-tool-template --adapter instaloader --format table
fashion-radar external-tool-template --adapter instaloader --format json
fashion-radar external-tool-template --adapter instaloader --format csv
fashion-radar external-tool-workflow --adapter instaloader --format table
fashion-radar external-tool-workflow --adapter instaloader --format json
fashion-radar external-tool-readiness --adapter instaloader --format table
fashion-radar external-tool-readiness --adapter instaloader --format json
```

## Imported Signal Review

These commands read existing local SQLite rows where `source_type` is
`manual_import`. Review commands use `--format table|json` where available.

- `imported-signals`: review retained imported rows. Requires `--as-of`;
  supports `--data-dir`, `--lookback-days`, `--limit`, `--source-name`,
  `--unmatched-only`, and `--format`.
- `imported-signals-summary`: summarize imported source labels; supports
  `--data-dir` and `--format`.
- `imported-entity-deltas`: compare imported entity counts across local
  collected-at windows. Requires `--as-of`; supports `--data-dir`,
  `--current-days`, `--baseline-days`, `--entity-type`, `--source-name`,
  `--limit`, and `--format`.
- `imported-entity-evidence`: local read-only imported-only
  `manual_import` evidence drilldown for one stored matched entity. Requires
  `--as-of`, `--entity-name`, and `--entity-type`; supports `--data-dir`,
  `--current-days`, `--baseline-days`, `--source-name`, `--limit`, and
  `--format`. JSON and table output are privacy-safe: review metadata plus
  `window`, `id`, `source_name`, `title`, `url`, `published_at`, and
  `collected_at` for retained local rows, omitting summaries, candidate
  contexts, match internals, import file paths, normalized keys, and platform
  labels. It does no scraping, no browser automation, no platform APIs, and no
  account or cookie work.
- `imported-candidates`: review imported candidate phrases. Requires `--as-of`;
  supports `--config-dir`, `--data-dir`, `--source-name`, `--limit`, and
  `--format`.
- `imported-candidate-evidence`: review retained rows behind one candidate
  phrase. Requires `--as-of` and `--phrase`; supports `--config-dir`,
  `--data-dir`, `--source-name`, `--limit`, and `--format`.
- `imported-review-workflow`: print a post-import review checklist without
  executing commands. Requires `--as-of`; supports `--config-dir`, `--data-dir`,
  `--source-name`, `--lookback-days`, `--current-days`, `--baseline-days`, and
  `--format`. The printed sequence includes `review_imported_entity_evidence`
  after entity deltas, then a read-only imported-candidates step for candidate
  phrase review, and still ends with the final read-only heat-movers step for
  local observed heat movement from configured sources and imported local
  signals; those review outputs need review and provide no demand proof and no
  platform coverage verification. The `--current-days` and `--baseline-days`
  options apply to the entity-delta and entity-evidence review commands, not to
  candidate phrase review.

## Trends, Dashboard, And Cleanup

- `candidates`: print read-only candidate signals from collected and imported
  local rows. Requires `--as-of`; supports `--config-dir`, `--data-dir`,
  `--limit`, and `--format table|json`.
- `trends`: compare local observed signal deltas between two scoring snapshots.
  Requires `--as-of`; supports `--config-dir`, `--data-dir`,
  `--baseline-as-of`, `--limit`, `--format table|json`, and
  `--include-dropped`.

### Heat Movers

- `heat-movers`: review local observed heat movement for one configured source
  set. It compares configured sources and imported local signals, and the
  output needs review, with no demand proof and no platform coverage
  verification. Requires `--config-dir`, `--data-dir`, and `--as-of`; supports
  `--baseline-as-of`, `--limit`, `--format table|json`, and
  `--include-cooling`.

- `dashboard`: launch the optional local Streamlit dashboard. Supports
  `--config-dir`, `--data-dir`, `--reports-dir`, `--host`, and `--port`.
  Defaults to `127.0.0.1:8501`.
- `clean-old-data`: prune old collected items and matcher rows. Supports
  `--data-dir`, requires `--as-of`, and accepts `--retention-days` and
  `--dry-run`.
