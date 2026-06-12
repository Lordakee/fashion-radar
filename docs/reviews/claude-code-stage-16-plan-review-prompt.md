# Claude Code Stage 16 Plan Review Prompt

You are reviewing the Stage 16 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, do not create directories, do not open SQLite, and do not
execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-16-plan-review-prompt.md
```

## Goal

Stage 16 should add a local, read-only community signal file diagnostics command:

```bash
fashion-radar community-signal-lint PATH --input-format csv
fashion-radar community-signal-lint PATH --input-format json
fashion-radar community-signal-lint PATH --input-format csv --format json
fashion-radar community-signal-lint PATH --input-format csv --strict
```

The command should help external tools controlled by the user produce sanitized
local CSV/JSON files that fit the existing community signal import contract
before `import-signals --dry-run` or `import-signals` is used.

This is not a product-facing compliance review, audit workflow, safety workflow,
policy checklist, approval UI, platform connector, scraper, crawler, browser
automation flow, social monitoring system, source acquisition tool, or
current-hotness ranking.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-16-community-signal-file-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-12-stage-16-community-signal-file-diagnostics-plan.md`

## Proposed Architecture

- Add `src/fashion_radar/community_signals.py`.
- Read one local CSV/JSON file and check it against the community signal
  contract.
- Validate import readiness using the existing `ManualSignalRow` model.
- Detect unknown fields, excluded raw/private/account/media/session fields,
  duplicate URLs, missing provenance, omitted defaults, and date-order issues.
- Add `fashion-radar community-signal-lint PATH --input-format csv|json --format table|json --strict`.
- Add focused module tests, CLI tests, and docs.
- Do not change import storage behavior, entity matching, scoring, collectors,
  reports, dashboard, DB schema, dependencies, lockfile, or existing
  `import-signals` behavior.

## Explicit Out Of Scope

The plan must not add or document:

- social/platform connectors, platform search, remote community ingestion, or
  automated social collection;
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or source-acquisition
  workflows;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- official or unofficial social platform APIs;
- instructions for obtaining platform/community exports;
- raw comments, full post bodies, private messages, author handles, account IDs,
  follower lists, profile URLs, images, videos, media downloading, reposting, or
  archive redistribution;
- current hotness claims, platform-wide claims, social-wide claims,
  community-wide claims, market-wide trend proof, verified demand outside
  configured local signals, real-time monitoring, or top social trend rankings;
- Google News RSS or any new source type;
- paid API requirements, LLM scoring, embeddings, vector databases, image
  recognition, sentiment analysis, or internet lookups;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, matcher behavior changes, persistent adapter tables,
  or scoring algorithm changes;
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Review Questions

Please focus on:

1. Whether a read-only community signal file linter is the right next stage
   after the community import contract and entity-pack quality diagnostics.
2. Whether the module boundary should be a new `community_signals.py` diagnostics
   module rather than changes to import storage or database schema.
3. Whether using `ManualSignalRow` for import-readiness validation keeps behavior
   aligned with `import-signals`.
4. Whether the proposed finding severities are appropriate.
5. Whether `--input-format` plus output `--format` is a clear CLI shape.
6. Whether tests prove read-only/no-artifact behavior and strict exit behavior.
7. Whether docs avoid platform/source acquisition instructions and
   platform/community-wide claims.
8. Whether verification is sufficient before GitHub upload.

## Response Format

Start with one of:

- `Approved for Stage 16 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
