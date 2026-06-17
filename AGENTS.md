# Agent Instructions

Fashion Radar is a free-first, local-first open source project. Keep the core
workflow usable without paid APIs, login cookies, proxy pools, CAPTCHA bypass,
paywall bypass, or fragile full social-platform scraping.

## Review Gates

- Follow the staged review workflow in `docs/REVIEW_PROTOCOL.md`.
- Before starting a new stage, submit the objective, architecture, tech stack,
  implementation method, and plan to local Claude Code with `--effort max` for
  review.
- After completing a development node, run fresh verification and request
  local Claude Code review of the new code before moving to the next stage.
- Fix critical and important review findings before continuing.

## Agent Runtime Settings

- When spawning Codex subagents for this project, set the subagent reasoning
  effort to `xhigh`.
- When invoking local Claude Code for plan or code review, use `--effort max`
  and read-only plan mode:

  ```bash
  claude --effort max --permission-mode plan --no-session-persistence \
    --tools Read,Grep,Glob,LS,Bash \
    -p "review prompt..."
  ```

## Dependencies And Mirrors

- Prefer mirror-based installation commands for local dependency/software setup
  when useful for network speed.
- Keep public `uv.lock` free of mirror-bound URLs.
- Use `uv sync --frozen --dev` with `UV_DEFAULT_INDEX=...` for local mirror
  installs.
- Use `UV_NO_CONFIG=1 uv lock --check` for public lockfile validation so
  user-level uv mirror config cannot affect the public lockfile.
- Use `UV_NO_CONFIG=1 uv sync --locked --dev` for fresh CI/release installs,
  then `UV_NO_CONFIG=1 uv sync --locked --dev --check` after the project
  environment exists.
- Do not commit virtual environments, package caches, build artifacts, cookies,
  tokens, or local account data.

## Scope Boundaries

- `v0.1.0` core sources are RSS/Atom and GDELT.
- Google News RSS is not part of `v0.1.0`.
- Social-platform connectors are future experimental opt-ins, not required for
  the core daily report.
- Reports must preserve source attribution and avoid republishing full articles.
- Future external community tool handoff work must keep the external tool
  handoff template limited to sanitized CSV/JSON local file handoff for
  user-controlled external/community tools. This is not platform collection
  and does not add connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, source acquisition, demand proof, ranking, or
  coverage verification.
- Future external community tool export directory examples must stay sanitized
  CSV/JSON local directory samples for user-controlled external/community
  tools. They are not platform collection and do not add connectors, scraping,
  browser automation, platform APIs, monitoring, scheduling, source acquisition,
  demand proof, ranking, or coverage verification.
- Future external social/community tool adapter registry work must keep
  `external-tool-adapters` as a local, print-only local producer-discovery
  registry for user-controlled external/community tools that target sanitized
  CSV/JSON local file handoff. It is not platform collection and must have no
  connectors, no scraping, no browser automation, no platform APIs, no
  monitoring, no scheduling, no source acquisition, no demand proof, no
  ranking, and no coverage verification.
- Future external social/community template work must keep
  `external-tool-template` as a local, print-only command that prints
  adapter-specific template rows for user-controlled external/community tools
  that target sanitized CSV/JSON local file handoff. It is not platform
  collection and must have no connectors, no scraping, no browser automation,
  no platform APIs, no monitoring, no scheduling, no source acquisition, no
  demand proof, no ranking, and no coverage verification.
- Future external social/community workflow work must keep
  `external-tool-workflow` as a local, print-only command that prints workflow
  metadata for user-controlled external/community tools that need a
  producer-facing wrapper around existing local commands before writing
  sanitized CSV/JSON local file handoff rows. JSON output is workflow metadata,
  not importable handoff rows. It must not inspect directories, read handoff
  files, import rows, open SQLite, or create artifacts. It is not platform
  collection and must have no connectors, no scraping, no browser automation,
  no platform APIs, no monitoring, no scheduling, no source acquisition, no
  demand proof, no ranking, and no coverage verification.
- Future community handoff readiness checks must keep
  `community-handoff-check-dir` as a local-only handoff readiness report for
  user-controlled community signal directories. It reads only matched local
  regular files and local config, does not import rows, uses no SQLite, creates
  no config/data/report/dashboard/digest artifacts, and has no fetch URLs/login/platform
  APIs/download media/browser automation/scrape/crawl/monitor/watch/schedule/connectors/source
  acquisition/demand proof/ranking/coverage verification/entity generation/compliance/policy/
  authorization/safety-review features.

## Heat Movers Boundary

`heat-movers` is local observed heat movement over one configured source set.
It compares configured sources and imported local signals, and the output needs
review. It provides no demand proof and no platform coverage verification.
