# Claude Code Stage 15 Plan Review Prompt

You are reviewing the Stage 15 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, do not create directories, do not open SQLite, and do not
execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-15-plan-review-prompt.md
```

## Goal

Stage 15 should add a local, read-only entity-pack quality diagnostics command:

```bash
fashion-radar entity-pack-lint PATH
fashion-radar entity-pack-lint PATH --format json
fashion-radar entity-pack-lint PATH --strict
```

The command should help users maintain entity YAML and optional entity packs for
brands, designer brands, celebrities, designers, named products, bags, shoes,
categories, and trend terms. It should diagnose local YAML quality and current
matcher consequences before the existing local matching/reporting/candidate/trend
workflow uses those entities.

This is not a product-facing compliance review, audit workflow, safety workflow,
policy checklist, approval UI, platform connector, scraper, crawler, browser
automation flow, social monitoring system, source acquisition tool, or
current-hotness ranking.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-15-entity-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md`

## Proposed Architecture

- Add `src/fashion_radar/entity_packs.py` as a sibling of
  `src/fashion_radar/source_packs.py`.
- Do not extract a shared lint abstraction in Stage 15.
- Read raw YAML first for omitted-default diagnostics.
- Validate with the existing `load_entity_config()` canonical loader.
- Return one structured `invalid_config` error for schema/load failures.
- Emit deterministic local findings and summary counts.
- Add `fashion-radar entity-pack-lint PATH --format table|json --strict`.
- Add focused module tests, CLI tests, and docs.
- Do not change entity schema validation, matcher behavior, scoring, collectors,
  reports, dashboard, DB schema, dependencies, or lockfile.

## Important Matcher Contract

Please check the plan against current matcher semantics:

- product entities with `parent_brand` consult parent-brand aliases and
  `context_terms`;
- non-product aliases consult `context_terms` only when the alias is single-word
  or listed in `UNSAFE_COMMON_ALIASES`;
- `safe_single_word` can bypass context for non-product aliases that require
  context;
- `safe_single_word` is ignored by the product-with-`parent_brand` branch;
- ordinary multi-word aliases are accepted without context even when the entity
  defines `context_terms`.

The plan must not imply that `context_terms` universally gate every multi-word
alias.

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
- current hotness claims, platform-wide claims, social-wide claims, market-wide
  trend proof, verified demand outside configured local signals, real-time
  monitoring, or top social trend rankings;
- Google News RSS or any new source type;
- paid API requirements, LLM scoring, embeddings, vector databases, image
  recognition, sentiment analysis, or internet lookups;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, matcher behavior changes, or scoring algorithm
  changes;
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Review Questions

Please focus on:

1. Whether a read-only entity-pack linter is the right next stage after the
   optional entity watchlist pack.
2. Whether the module boundary should be a new `entity_packs.py` sibling rather
   than changes to `source_packs.py` or schema models.
3. Whether the proposed finding set is useful, deterministic, and not too
   intrusive for valid local configs.
4. Whether severities are appropriate, especially for product parent/context
   issues and multi-word aliases that are accepted without context.
5. Whether the plan correctly handles `context_terms`, `safe_single_word`,
   `UNSAFE_COMMON_ALIASES`, and product `parent_brand` behavior.
6. Whether CLI output, exit behavior, and read-only/no-artifact constraints are
   sufficiently specified.
7. Whether tests cover module behavior, CLI behavior, and docs boundaries.
8. Whether documentation wording avoids social/platform acquisition, ranking, or
   market-wide/current-hotness claims.
9. Whether verification is sufficient before GitHub upload.

## Response Format

Start with one of:

- `Approved for Stage 15 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
