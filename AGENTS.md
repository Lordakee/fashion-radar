# Agent Instructions

Fashion Radar is a free-first, local-first open source project. Keep the core
workflow usable without paid APIs, login cookies, proxy pools, CAPTCHA bypass,
paywall bypass, or fragile full social-platform scraping.

## Review Gates

- Follow the staged review workflow in `docs/REVIEW_PROTOCOL.md`.
- Before starting a new stage, submit the objective, architecture, tech stack,
  implementation method, and plan to Claude Code for review.
- After completing a development node, run fresh verification and request
  Claude Code review of the new code before moving to the next stage.
- Fix critical and important review findings before continuing.

## Dependencies And Mirrors

- Prefer mirror-based installation commands for local dependency/software setup
  when useful for network speed.
- Keep public `uv.lock` free of mirror-bound URLs.
- Use `uv sync --frozen --dev` with `UV_DEFAULT_INDEX=...` for local mirror
  installs.
- Use `uv sync --locked --dev` and `uv lock --check` without mirror env vars for
  CI, verification, and committed lockfile checks.
- Do not commit virtual environments, package caches, build artifacts, cookies,
  tokens, or local account data.

## Scope Boundaries

- `v0.1.0` core sources are RSS/Atom and GDELT.
- Google News RSS is not part of `v0.1.0`.
- Social-platform connectors are future experimental opt-ins, not required for
  the core daily report.
- Reports must preserve source attribution and avoid republishing full articles.
