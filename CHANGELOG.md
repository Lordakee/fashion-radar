# Changelog

All notable changes to Fashion Radar will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Python package foundation with Typer CLI.
- YAML source, entity, and scoring configuration.
- RSS/Atom, RSSHub-compatible, and GDELT collector support.
- SQLite persistence with schema versioning and migrations through schema v4.
- Deterministic entity matching with context gates for broad/common aliases.
- Transparent heat scoring with current/baseline windows, source weights,
  source diversity, growth, high-weight source bonuses, labels, and stable
  first-seen tracking.
- Markdown and JSON daily report generation.
- Optional local Streamlit dashboard.
- CodeGraph project setup for Claude Code/Codex navigation.
- Source-boundary, scoring, retention, dashboard, mirror, and GitHub-readiness
  documentation.
- CI for locked install, lint, format check, tests, wheel build, installed CLI
  smoke, packaged template smoke, and dashboard extra smoke.
- Safe `schedule-example` CLI output for cron, systemd user timers, and GitHub
  Actions.
- Public RSS/GDELT fashion source-pack example.
- Scheduling and source-pack documentation.
- Stage 8 candidate discovery documentation for observed phrases, review
  windows, CLI usage, report/dashboard behavior, and source boundaries.
- Manual signal import documentation for local user-provided CSV/JSON files,
  dry runs, follow-up review commands, and privacy/source boundaries.
- Report and dashboard wording for candidate signals from configured sources and
  imported local signals that need review.
- Read-only `trends` CLI command for local observed entity and candidate signal
  deltas between scoring snapshots.
- Dashboard Trend Deltas view using local SQLite state and forwarded
  `--config-dir` settings.
- Trend delta documentation covering local-only scope, baseline windows,
  read-only behavior, and source-coverage limits.
- Optional local digest packaging for generated daily reports, including latest
  report artifacts, a report index, a local `.eml` handoff file, and stdout
  summary output.
- Local read-only `source-pack-lint` command for source YAML quality diagnostics
  and documentation for expanded public-pack RSS/GDELT categories.

### Not Included In 0.1.0

- No default Google News RSS connector.
- No broad non-core platform connector in the default workflow.
- No paid external-service requirement for the core workflow.
- No account-based collection, access-control bypass, or private data
  collection.
