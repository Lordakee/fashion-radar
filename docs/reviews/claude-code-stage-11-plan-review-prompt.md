# Claude Code Stage 11 Plan Review Prompt

You are reviewing the Stage 11 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, and do not execute platform/social tooling.

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-11-plan-review-prompt.md
```

## Goal

Stage 11 should add optional local digest packaging for already-generated
Fashion Radar Markdown/JSON daily reports. The goal is to make scheduled daily
output easier to find and hand off locally, without adding delivery services or
new source collection.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-11-local-digest-design.md`
- `docs/superpowers/plans/2026-06-12-stage-11-local-digest-plan.md`

## Proposed Architecture

- Keep `reports.py` focused on report content rendering.
- Keep `workflows.write_daily_report_files()` focused on date-stamped
  Markdown/JSON generation.
- Add `src/fashion_radar/digests.py` as a local file-packaging module.
- Add explicit no-op-by-default digest flags to `fashion-radar report` and
  `fashion-radar run`.
- Generate only local artifacts:
  - `latest.md`
  - `latest.json`
  - `report-index.json`
  - `fashion-radar-YYYY-MM-DD.eml`
  - optional stdout summary
- Use strict date-stamped filename parsing for report-index generation.
- Use safe names that do not collide with dashboard `fashion-radar-*.json`
  discovery.
- Use temporary files and `Path.replace()` where practical.
- Never send email, open browsers, call webhooks, use notification services, or
  create background daemons.

## Tech Stack

- Python 3.11+
- dataclasses
- `enum.StrEnum`
- pathlib
- stdlib `email.message.EmailMessage`
- Typer
- pytest
- ruff
- uv

## Explicit Out Of Scope

The plan must not add or document:

- SMTP sending, Sendmail sending, webhooks, push services, desktop
  notifications, browser opening, or background daemons
- platform search or automated social collection
- crawlers, scrapers, browser automation, Playwright, Selenium, MCP platform
  scraping servers, or account automation
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining exports from Instagram, TikTok, X/Twitter,
  Xiaohongshu, or similar platforms
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile internals, images, videos, media downloading, or reposting
- claims of complete social listening, complete platform coverage, verified
  demand, market-wide trend proof, real-time social monitoring, or top social
  trends
- LLM scoring, embeddings, vector databases, image recognition, or paid service
  requirements
- database schema changes, new delivery tables, dashboard writes, or changes to
  default `report`/`run` behavior

## Review Questions

Please focus on:

1. Whether this stage genuinely improves daily usability without adding risky
   source collection or network delivery behavior.
2. Whether `digests.py` is the right module boundary instead of modifying
   `reports.py`.
3. Whether the CLI flags are no-op by default and understandable.
4. Whether artifact names avoid dashboard latest-report collisions.
5. Whether report-index generation based on strict filename pairs is safe and
   deterministic.
6. Whether `.eml` generation as a local file is acceptable and sufficiently
   bounded.
7. Whether tests cover copy, symlink, index, `.eml`, summary, missing files,
   malformed names, CLI wiring, and default-output stability.
8. Whether docs and wording avoid implying platform-wide or market-wide signal
   coverage.
9. Whether any plan step risks committing generated reports, local digest
   artifacts, credentials, cookies, or private data.
10. Whether any simpler architecture would better match the existing codebase.

## Response Format

Start with one of:

- `Approved for Stage 11 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
