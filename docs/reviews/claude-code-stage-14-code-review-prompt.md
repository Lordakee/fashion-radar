# Claude Code Stage 14 Code Review Prompt

You are reviewing the Stage 14 implementation for Fashion Radar. Run this as a
read-only code and documentation review. Do not edit files, do not commit, do
not call the network, do not run collectors, do not create directories, do not
open SQLite, and do not execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-14-code-review-prompt.md
```

## Goal

Stage 14 adds an optional static fashion entity watchlist pack for broader local
matching coverage using the existing `entities.yaml` schema and matcher.

This is not a product-facing compliance review, audit workflow, safety workflow,
policy checklist, approval UI, source-acquisition guide, platform connector,
scraper, crawler, browser automation flow, social monitoring system, ranking, or
current-hotness detector.

Review files under `docs/reviews/` and staged plan/spec files under
`docs/superpowers/` are process metadata for the staged workflow. They are not
product/runtime behavior, package functionality, compliance/audit/safety
features, or user-facing approval workflows.

## Plan Review Status

The Stage 14 plan went through several read-only Claude Code reviews. The final
approved review is:

- `docs/reviews/claude-code-stage-14-plan-rereview-7.md`

It returned `Approved for Stage 14 implementation` with no Critical or
Important findings.

## Files Changed

Created:

- `configs/entity-packs/fashion-watchlist.example.yaml`
- `docs/entity-packs.md`
- `tests/test_entity_packs.py`
- `docs/superpowers/specs/2026-06-12-stage-14-entity-watchlist-pack-design.md`
- `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`
- `docs/reviews/claude-code-stage-14-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-14-plan-review.md`
- `docs/reviews/claude-code-stage-14-plan-rereview.md`
- `docs/reviews/claude-code-stage-14-plan-rereview-2.md`
- `docs/reviews/claude-code-stage-14-plan-rereview-3.md`
- `docs/reviews/claude-code-stage-14-plan-rereview-4.md`
- `docs/reviews/claude-code-stage-14-plan-rereview-5.md`
- `docs/reviews/claude-code-stage-14-plan-rereview-6.md`
- `docs/reviews/claude-code-stage-14-plan-rereview-7.md`
- `docs/reviews/claude-code-stage-14-code-review-prompt.md`

Modified:

- `README.md`
- `CHANGELOG.md`
- `.gitignore`
- `docs/architecture.md`
- `docs/source-boundaries.md`

No production Python module, collector, source model, DB schema, dashboard,
report renderer, scoring logic, dependency declaration, lockfile, source pack,
or packaged init template was changed.

## Implemented Behavior

- Added `configs/entity-packs/fashion-watchlist.example.yaml`, a complete
  optional `EntityConfig` file users can copy to `configs/entities.yaml`.
- Kept the default small starter config and packaged init template unchanged.
- Added tests proving:
  - the pack loads through `load_entity_config()`;
  - it has a broader type mix;
  - expected watchlist examples are present;
  - products reference existing parent brands;
  - single-word/common aliases have existing matcher guardrails;
  - generic `The Row`, `Coach`, `Margaux`, and `Arcadie` mentions are rejected;
  - parent-brand/fashion-context mentions are accepted;
  - entity-pack docs do not introduce a `fashion-radar collect` workflow.
- Added docs that frame the pack as a static local seed watchlist, not a
  ranking, current-hotness claim, source-acquisition guide, or monitoring
  system.
- Added root `.gitignore` coverage for `.codegraph/` after code review found
  the directory-level ignore missing.

## Explicit Out Of Scope

Please check that Stage 14 did not add or document:

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

## Verification Already Run

Focused RED:

```text
.venv/bin/python -m pytest tests/test_entity_packs.py -q
9 failed as expected because entity pack/docs did not exist; 1 default config
stability test passed.
```

Focused GREEN:

```text
.venv/bin/python -m pytest tests/test_entity_packs.py -q
10 passed in 0.36s
```

Full implementation verification:

```text
git diff --check
passed

.venv/bin/python -m pytest -q
293 passed in 6.75s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
74 files already formatted

codegraph status
Index is up to date
```

Post-review `.gitignore` fix:

```text
.gitignore now contains .codegraph/
git check-ignore -v .codegraph/codegraph.db .codegraph/daemon.log confirms root
ignore coverage for generated CodeGraph files.
```

Wording guards:

```text
rg -n "platform-wide|market-wide|verified demand|top social trend|real-time social monitoring|scraper|crawler|Playwright|Selenium|cookie|session|token|proxy|CAPTCHA|fingerprint|source-acquisition|hot-list|ranking" docs/entity-packs.md README.md docs/architecture.md docs/source-boundaries.md CHANGELOG.md configs/entity-packs/fashion-watchlist.example.yaml
```

Observed matches were negative boundary wording or existing boundary language,
including "not a hot-list", "ranking semantics" exclusions,
source-acquisition exclusions, and existing README/source-boundaries artifact
or trend-boundary text. No positive platform-wide, market-wide, verified-demand,
top-social-trend, source-acquisition, or ranking claim was added.

Targeted entity-pack acquisition guard:

```text
rg -n "collect|source setup|source acquisition|platform ingestion|community ingestion|scraping|crawler" docs/entity-packs.md
```

Observed one negative boundary match:

```text
source setup, collection workflows, platform or community ingestion, scraping,
```

The docs do not contain `fashion-radar collect`.

## Review Questions

Please focus on:

1. Whether the implementation matches the final approved Stage 14 design and
   plan.
2. Whether the optional pack is a valid `EntityConfig` and the default starter
   remains unchanged.
3. Whether tests cover real matcher behavior without assuming universal
   `context_terms` gating for every multi-word category/trend alias.
4. Whether docs keep workflow commands scoped to already-produced signals and
   avoid source acquisition, platform/community ingestion, `collect` workflow
   instructions, scraping, monitoring, or ranking claims.
5. Whether any production runtime code, dependency, lockfile, DB schema,
   collector, report, dashboard, scoring, source-pack, or packaged-template
   change was accidentally introduced.
6. Whether generated files, tokens, cookies, local SQLite DBs, build artifacts,
   `.codegraph`, `.venv`, or account/session artifacts are at risk of being
   committed.

## Response Format

Start with one of:

- `Approved for Stage 14 release handoff`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before release handoff.
- `Important:` issues that should be fixed before release handoff.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
