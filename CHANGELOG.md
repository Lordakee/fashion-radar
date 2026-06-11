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

### Not Included In 0.1.0

- No default Google News RSS connector.
- No Instagram/TikTok/X/Xiaohongshu scraping.
- No paid API requirement for the core workflow.
- No login cookies, account/session files, proxy/account pools, CAPTCHA bypass,
  paywall bypass, or private data collection.
