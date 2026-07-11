# Agent Instructions

Fashion Radar is a free-first, local-first open source project. Keep the core
workflow usable without paid APIs, login cookies, proxy pools, CAPTCHA bypass,
or paywall bypass by default; opt-in social-platform collection (Phase 2-5:
Xiaohongshu, Instagram, X, YouTube) is use-at-your-own-risk and not enabled by
default.

## Review Gates

- Follow the staged review workflow in `docs/REVIEW_PROTOCOL.md`.
- Claude Code is the **primary reviewer** for plan, code, and release reviews.
- Before starting a new stage, submit the objective, architecture, tech stack,
  implementation method, and plan to local Claude Code for review.
- After Claude Code's review, local opencode revises the plan based on that
  review and its own judgment. local opencode is also the fallback reviewer when
  Claude Code is unavailable.
- After completing a development node, run fresh verification and request local
  Claude Code review of the new code before moving to the next stage.
- Record active plan, code, release, and rereview artifacts under
  `docs/reviews/claude-code-stage-N-...` and `docs/reviews/opencode-stage-N-...`.
- Before committing review artifacts, ensure each review record contains
  completed review output and no live-capture stubs, duplicated or truncated
  text, tool-status messages, or empty output.
- Fix critical and important review findings before continuing.

## Agent Runtime Settings

- When spawning Codex subagents for this project, set the subagent reasoning
  effort to `max`.
- Claude Code is the primary reviewer. Use `--effort max`, read-only plan mode,
  and no session persistence for plan, code, and release reviews:

  ```bash
  claude --effort max --permission-mode plan --no-session-persistence \
    --tools Read,Grep,Glob,LS,Bash \
    -p "review prompt..."
  ```

- When local opencode revises a plan after Claude Code's review, or acts as the
  fallback reviewer, use GLM 5.2 with the max variant:

  ```bash
  opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
    --dir /home/ubuntu/fashion-radar "review prompt..."
  ```

## Dependencies And Mirrors

- Prefer mirror-based installation commands for local dependency/software setup
  when useful for network speed.
- Keep public `uv.lock` free of mirror-bound URLs.
- Use `uv sync --frozen --dev` with `UV_DEFAULT_INDEX=...` for local mirror
  installs.
- For agent-run verification commands, prefer `uv --no-config run --frozen ...`
  so user-level mirror config cannot rewrite `uv.lock` during tests, lint, or
  scripted checks. Keep mirror-backed commands as frozen mirror install
  commands, not test or lockfile regeneration commands.
- Use `UV_NO_CONFIG=1 uv lock --check` for public lockfile validation so
  user-level uv mirror config cannot affect the public lockfile.
- Use `UV_NO_CONFIG=1 uv sync --locked --dev` for fresh CI/release installs,
  then `UV_NO_CONFIG=1 uv sync --locked --dev --check` after the project
  environment exists.
- Do not commit virtual environments, package caches, build artifacts, cookies,
  tokens, or local account data.

## Scope Boundaries

- `v0.1.0` core sources are RSS/Atom, RSSHub-compatible, GDELT, HTML seed-URL collection, and sitemap discovery.
- Google News RSS is not part of `v0.1.0`.
- Social-platform connectors are opt-in (Phase 2 adds Xiaohongshu), not enabled
  by default and not required for the core daily report.
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
  ranking, and no coverage verification. Each adapter command list includes
  `external-tool-readiness` as an optional local read-only preflight command,
  while `external-tool-adapters` itself remains print-only and does not run
  readiness or perform PATH lookup.
- Future external social/community template work must keep
  `external-tool-template` as a local, print-only command that prints
  adapter-specific template rows for user-controlled external/community tools
  that target sanitized CSV/JSON local file handoff. It is not platform
  collection and must have no connectors, no scraping, no browser automation,
  no platform APIs, no monitoring, no scheduling, no source acquisition, no
  demand proof, no ranking, and no coverage verification. JSON/CSV handoff
  rows must remain importable row output only, while table/model guidance can
  include the same adapter recommended command list.
- Future external social/community workflow work must keep
  `external-tool-workflow` as a local, print-only command that prints workflow
  metadata for user-controlled external/community tools that need a
  producer-facing wrapper around existing local commands before writing
  sanitized CSV/JSON local file handoff rows. JSON output is workflow metadata,
  not importable handoff rows. It may print `check_external_tool_readiness` as
  an optional preflight command pointing to the local read-only
  `external-tool-readiness` command, but it must not run that command. It must
  not inspect directories, read handoff files, import rows, open SQLite, or
  create artifacts. It is not platform
  collection and must have no connectors, no scraping, no browser automation,
  no platform APIs, no monitoring, no scheduling, no source acquisition, no
  demand proof, no ranking, and no coverage verification.
- Future `external-tool-readiness` external tool readiness work must stay
  distinct from the print-only external-tool trio: it may remain local
  read-only command availability only guidance using local PATH lookup,
  mirror-friendly install hints, and Fashion Radar handoff next steps for
  user-controlled
  external/community tools producing sanitized CSV/JSON local file handoff
  rows. It must not install dependencies, run adapters, run upstream tools,
  inspect directories, read handoff files, import rows, open/write SQLite, or
  create config/data/report/dashboard/workflow/handoff artifacts. It must have
  no connectors, no scraping, no browser automation, no platform APIs, no
  account/session/cookie/token behavior, no monitoring, no scheduling, no
  source acquisition, no demand proof, no ranking, no coverage verification,
  and no compliance-review product feature.
- Future community handoff readiness checks must keep
  `community-handoff-check-dir` as a local-only handoff readiness report for
  user-controlled community signal directories. It reads only matched local
  regular files and local config, does not import rows, uses no SQLite, creates
  no config/data/report/dashboard/digest artifacts, and has no fetch URLs/login/platform
  APIs/download media/browser automation/scrape/crawl/monitor/watch/schedule/connectors/source
  acquisition/demand proof/ranking/coverage verification/entity generation/compliance/policy/
  authorization/safety-review features.
- Future `imported-entity-evidence` work must keep the command local
  read-only, imported-only, and limited to privacy-safe retained local rows for
  one `manual_import` stored matched entity. The `review_imported_entity_evidence`
  workflow step must stay print-only. It must have no scraping, no browser
  automation, no platform APIs, and no account or cookie behavior.

## Heat Movers Boundary

`heat-movers` is local observed heat movement over one configured source set.
It compares configured sources and imported local signals, and the output needs
review. It provides no demand proof and no platform coverage verification.
