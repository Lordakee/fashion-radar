# Claude Code Stage 16 Plan Rereview Prompt

You are rereviewing the Stage 16 plan for Fashion Radar after the first Claude
Code plan review returned `Not approved`. Run this as a read-only planning
review. Do not edit files, do not commit, do not call the network, do not run
collectors, do not create directories, do not open SQLite, and do not execute
platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-16-plan-rereview-prompt.md
```

## Prior Review Result

The first review asked for these fixes before implementation:

1. Add explicit `csv_extra_cells` test coverage and implementation plan.
2. Clarify that prohibited fields such as `author_handle` emit only
   `prohibited_field`, while unrelated extra fields emit `unknown_field`.
3. Align fallback `source_name` behavior with `load_manual_signal_rows()`, or
   test equivalence so the linter cannot drift from `import-signals`.
4. Make no-artifact CLI tests more explicit.
5. Separate optional release/upload steps from Stage 16 implementation
   acceptance.

## Plan And Design To Rereview

Please rereview:

- `docs/superpowers/specs/2026-06-12-stage-16-community-signal-file-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-12-stage-16-community-signal-file-diagnostics-plan.md`

## Goal

Stage 16 should add a local, read-only community signal file diagnostics command:

```bash
fashion-radar community-signal-lint PATH --input-format csv
fashion-radar community-signal-lint PATH --input-format json
fashion-radar community-signal-lint PATH --input-format csv --format json
fashion-radar community-signal-lint PATH --input-format csv --strict
fashion-radar community-signal-lint PATH --input-format csv --source-name "Community Tool Export"
```

The command should help external tools controlled by the user produce sanitized
local CSV/JSON files that fit the existing community signal import contract
before `import-signals --dry-run` or `import-signals` is used.

This is not a product-facing compliance review, audit workflow, safety workflow,
policy checklist, approval UI, platform connector, scraper, crawler, browser
automation flow, social monitoring system, source acquisition tool, or
current-hotness ranking.

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

## Rereview Questions

Please focus on whether the revised plan fully resolves the prior Important
findings:

1. `csv_extra_cells` has concrete failing tests and implementation guidance.
2. Prohibited fields are classified separately from unknown fields without
   double-reporting.
3. Fallback `source_name` behavior is aligned with `load_manual_signal_rows()`
   and covered by a drift test.
4. No-artifact CLI tests explicitly assert no config/data/reports directories,
   SQLite files, report/digest/latest/index/workflow artifacts, or default/env
   directory creation.
5. Release/upload checks are clearly post-acceptance and not mixed with
   implementation acceptance.

Also flag any remaining plan issue that should block implementation.

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
