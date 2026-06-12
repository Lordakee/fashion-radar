# Claude Code Stage 14 Plan Review Prompt

You are reviewing the Stage 14 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, do not create directories, do not open SQLite, and do not
execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-14-plan-review-prompt.md
```

## Goal

Stage 14 should add an optional static fashion entity watchlist pack for broader
local tracking coverage of designer brands, products, bags, shoes, categories,
designers, celebrities, and style terms. It should use the existing entity
config schema and matching system without runtime code changes.

This is not a product-facing compliance review, audit workflow, safety
workflow, policy checklist, approval UI, platform connector, scraper, crawler,
browser automation flow, social monitoring system, or current-hotness ranking.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-14-entity-watchlist-pack-design.md`
- `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`

## Proposed Architecture

- Add `configs/entity-packs/fashion-watchlist.example.yaml` as a complete
  optional `EntityConfig`.
- Do not change `configs/entities.example.yaml` or the packaged init template.
- Do not change runtime Python modules, collectors, source packs, DB schema,
  scoring, reports, dashboard, dependencies, or lockfile.
- Add focused tests that load the pack through `load_entity_config()`.
- Add docs for copying/editing/running the pack.

## Explicit Out Of Scope

The plan must not add or document:

- social/platform connectors, platform search, remote community ingestion, or
  automated social collection
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or source-acquisition
  workflows
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass
- official or unofficial social platform APIs
- instructions for obtaining platform/community exports
- current hotness claims, platform-wide claims, market-wide trend proof,
  verified demand outside the configured source set, real-time monitoring, or
  top social trend rankings
- Google News RSS or any new source type
- paid API requirements, LLM scoring, embeddings, vector databases, image
  recognition, or sentiment analysis
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, or scoring algorithm changes
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature

## Review Questions

Please focus on:

1. Whether an optional entity watchlist pack is the right next stage after the
   community import contract.
2. Whether keeping the default starter config unchanged is the right boundary.
3. Whether the proposed pack contents are useful without claiming current
   hotness or market-wide demand.
4. Whether aliases/context terms/parent brands are planned safely enough for the
   existing matcher.
5. Whether tests cover loading, type mix, parent-brand references, and broad
   alias context protection.
6. Whether docs avoid platform/source acquisition instructions and ranking
   claims.
7. Whether verification is sufficient for GitHub upload.

## Response Format

Start with one of:

- `Approved for Stage 14 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
