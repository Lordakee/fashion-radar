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
paths through the whole sequence:

```bash
fashion-radar collect --config-dir "$PWD/configs" --data-dir "$PWD/data"
fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

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
- `community-handoff-workflow` DIRECTORY: print a local handoff checklist
  without executing commands. Requires `--as-of`; supports `--config-dir`,
  `--data-dir`, `--input-format`, `--pattern`, `--source-name`, and
  `--format table|json`.

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
  `--format`.

## Trends, Dashboard, And Cleanup

- `candidates`: print read-only candidate signals from collected and imported
  local rows. Requires `--as-of`; supports `--config-dir`, `--data-dir`,
  `--limit`, and `--format table|json`.
- `trends`: compare local observed signal deltas between two scoring snapshots.
  Requires `--as-of`; supports `--config-dir`, `--data-dir`,
  `--baseline-as-of`, `--limit`, `--format table|json`, and
  `--include-dropped`.
- `dashboard`: launch the optional local Streamlit dashboard. Supports
  `--config-dir`, `--data-dir`, `--reports-dir`, `--host`, and `--port`.
  Defaults to `127.0.0.1:8501`.
- `clean-old-data`: prune old collected items and matcher rows. Supports
  `--data-dir`, requires `--as-of`, and accepts `--retention-days` and
  `--dry-run`.
