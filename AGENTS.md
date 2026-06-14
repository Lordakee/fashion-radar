# Agent Instructions

Fashion Radar is a free-first, local-first open source project. Keep the core
workflow usable without paid APIs, login cookies, proxy pools, CAPTCHA bypass,
paywall bypass, or fragile full social-platform scraping.

## Review Gates

- Follow the staged review workflow in `docs/REVIEW_PROTOCOL.md`.
- Before starting a new stage, submit the objective, architecture, tech stack,
  implementation method, and plan to local opencode with GLM 5.2 for review.
- After completing a development node, run fresh verification and request
  local opencode review of the new code before moving to the next stage.
- Fix critical and important review findings before continuing.

## Agent Runtime Settings

- When spawning Codex subagents for this project, set the subagent reasoning
  effort to `xhigh`.
- When invoking local opencode for plan or code review, use the GLM 5.2 model
  ID:

  ```bash
  opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
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
