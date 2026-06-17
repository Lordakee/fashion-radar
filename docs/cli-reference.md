# CLI Reference

This is a compact map of the current public `fashion-radar` command surface.
Use `fashion-radar COMMAND --help` for full Typer help and defaults.

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
  ranking, and no coverage verification.
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

Print adapter registry examples:

```bash
fashion-radar external-tool-adapters --format table
fashion-radar external-tool-adapters --format json
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
- `imported-candidates`: review imported candidate phrases. Requires `--as-of`;
  supports `--config-dir`, `--data-dir`, `--source-name`, `--limit`, and
  `--format`.
- `imported-candidate-evidence`: review retained rows behind one candidate
  phrase. Requires `--as-of` and `--phrase`; supports `--config-dir`,
  `--data-dir`, `--source-name`, `--limit`, and `--format`.
- `imported-review-workflow`: print a post-import review checklist without
  executing commands. Requires `--as-of`; supports `--config-dir`, `--data-dir`,
  `--source-name`, `--lookback-days`, `--current-days`, `--baseline-days`, and
  `--format`. The printed sequence includes a read-only imported-candidates
  step for candidate phrase review and still ends with the final read-only
  heat-movers step for local observed heat movement from configured sources and
  imported local signals; those review outputs need review and provide no
  demand proof and no platform coverage verification. The `--current-days` and
  `--baseline-days` options apply to the entity-delta review command, not to
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
