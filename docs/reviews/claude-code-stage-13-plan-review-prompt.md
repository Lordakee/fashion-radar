# Claude Code Stage 13 Plan Review Prompt

You are reviewing the Stage 13 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, do not create directories, do not open SQLite, and do not
execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-13-plan-review-prompt.md
```

## Goal

Stage 13 should prepare Fashion Radar for external community/social tools that
the user will provide later by defining a sanitized local CSV/JSON import
contract. It should reuse the existing `fashion-radar import-signals` command
and add examples, a strict JSON schema document, tests, and docs.

This is not a product-facing compliance review, audit workflow, safety
workflow, policy checklist, or approval UI.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-13-community-signal-import-design.md`
- `docs/superpowers/plans/2026-06-12-stage-13-community-signal-import-plan.md`

## Proposed Architecture

- Keep the existing Stage 9 importer as the only runtime import path.
- Do not change collectors, source models, database schema, reports, dashboard,
  scoring, source packs, or dependencies.
- Add repository examples:
  - `examples/community-signals.example.csv`
  - `examples/community-signals.example.json`
- Add a static strict JSON schema:
  - `schemas/community-signals.schema.json`
- Add tests that load the examples through `load_manual_signal_rows()` and run
  `import-signals --dry-run` on them.
- Add documentation:
  - `docs/community-signal-import.md`
  - links from README/manual import/source boundaries/architecture/changelog.

## Tech Stack

- Python 3.11+
- Existing Typer CLI
- Existing Pydantic manual importer
- Standard library `json`
- Static JSON Schema document
- pytest
- ruff
- uv

## Explicit Out Of Scope

The plan must not add or document:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, Discord,
  Telegram, WeChat, or other platform connectors
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or platform search
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxies, proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining platform exports from social platforms or
  communities
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile URLs, images, videos, media downloading, reposting, or archive
  redistribution
- Google News RSS or any new source type
- complete source coverage, platform-wide coverage, community-wide coverage,
  market-wide trend proof, verified demand outside the configured source set,
  real-time social monitoring, or top social trends
- LLM scoring, embeddings, vector databases, image recognition, paid service
  requirements, or sentiment analysis
- DB migrations, persistent adapter tables, source-health changes, collector
  changes, dashboard changes, report semantics changes, or network calls
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature

## Review Questions

Please focus on:

1. Whether Stage 13 is the right next step for the user's future community-tool
   handoff without implementing platform collection.
2. Whether reusing `import-signals` is better than adding a new connector or
   `--profile community` option at this stage.
3. Whether static examples plus a JSON schema provide enough contract clarity
   for external tools to target.
4. Whether the schema should be strict (`additionalProperties: false`) while the
   runtime importer keeps Stage 9's backward-compatible unknown-field ignore.
5. Whether the proposed examples and tests are useful and sufficiently bounded.
6. Whether dry-run tests and installed-wheel smoke cover the no-artifact
   boundary.
7. Whether the documentation plan avoids source-acquisition instructions and
   avoids platform-wide or market-wide claims.
8. Whether any code change is actually required for this stage.
9. Whether the verification list is sufficient for GitHub upload.

## Response Format

Start with one of:

- `Approved for Stage 13 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
