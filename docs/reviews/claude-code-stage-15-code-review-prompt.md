# Claude Code Stage 15 Code Review Prompt

You are reviewing the Stage 15 implementation for Fashion Radar. Run this as a
read-only code and documentation review. Do not edit files, do not commit, do
not call the network, do not run collectors, do not create directories, do not
open SQLite, and do not execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-15-code-review-prompt.md
```

## Goal

Stage 15 adds `fashion-radar entity-pack-lint`, a pure local diagnostics command
for entity YAML files and optional entity packs. It should help users understand
local watchlist quality and current matcher consequences without changing
matching, scoring, collection, reports, dashboard, schema, dependencies, or
source acquisition behavior.

## Approved Plan And Reviews

Please use these as the implementation contract:

- `docs/superpowers/specs/2026-06-12-stage-15-entity-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md`
- `docs/reviews/claude-code-stage-15-plan-review.md`
- `docs/reviews/claude-code-stage-15-plan-rereview.md`

## Files To Review

Implementation:

- `src/fashion_radar/entity_packs.py`
- `src/fashion_radar/cli.py`

Tests:

- `tests/test_entity_pack_lint.py`
- `tests/test_entity_packs.py`
- `tests/test_cli.py`

Docs:

- `docs/entity-pack-quality.md`
- `docs/entity-packs.md`
- `README.md`
- `docs/architecture.md`
- `CHANGELOG.md`

Process records:

- `docs/reviews/claude-code-stage-15-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-15-plan-review.md`
- `docs/reviews/claude-code-stage-15-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-15-plan-rereview.md`
- `docs/reviews/claude-code-stage-15-code-review-prompt.md`

## Implementation Summary

- Added `src/fashion_radar/entity_packs.py` with:
  - `EntityPackFindingSeverity`
  - `EntityPackFinding`
  - `EntityPackLintResult`
  - `lint_entity_pack(path)`
  - `render_entity_pack_lint_table(result)`
  - local matcher-gate classification helpers
- Added `fashion-radar entity-pack-lint PATH --format table|json --strict`.
- Added focused module tests for invalid config, empty packs, aliases, normalized
  keys, tags/category tags, product parent-brand precision, context-term
  behavior, safe aliases, raw YAML defaults, JSON shape, and table rendering.
- Added CLI tests for help, table, JSON, strict mode, invalid configs, and no
  config/data/report/SQLite/workflow artifacts.
- Added docs for command usage, output, severity meanings, finding codes,
  matcher-rule notes, tuning guidance, and limits.

## Matcher Contract To Verify

Please pay close attention to current matcher branch order:

- product entities with `parent_brand` use parent-brand aliases or product
  `context_terms`; this branch ignores `safe_single_word`;
- non-product single-word aliases or aliases in `UNSAFE_COMMON_ALIASES` require
  context unless accepted first by effective `safe_single_word` plus reason;
- effective safe non-product aliases bypass context;
- ordinary multi-word aliases are accepted without context even when the entity
  defines `context_terms`;
- `context_terms_no_effect` should be emitted only when an entity has
  `context_terms` and none of its aliases consult context under those rules.

## Explicit Out Of Scope

The implementation must not add or document:

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

## Verification Already Run

Fresh commands run before this review:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
codegraph status
```

Observed results:

- `pytest`: 322 passed
- `ruff check .`: all checks passed
- `ruff format --check .`: 76 files already formatted
- `git diff --check`: exit 0
- `codegraph status`: index up to date

Two read-only Codex subagent reviews found no Critical or Important issues. One
Minor test-strengthening suggestion was applied before the full verification
above.

## Review Questions

Please focus on:

1. Correctness of entity-pack lint findings and severities.
2. Exact alignment with matcher semantics.
3. Whether schema validation is reused instead of duplicated.
4. Whether raw YAML omitted-default diagnostics are deterministic.
5. CLI output format, exit behavior, and read-only/no-artifact behavior.
6. Test coverage for the new module and CLI.
7. Documentation accuracy and boundary wording.
8. Any hidden dependency, packaging, import, or release risk.

## Response Format

Start with one of:

- `Approved for Stage 15 upload`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before upload.
- `Important:` issues that should be fixed before upload.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
