# Stage 14 Entity Watchlist Pack Design

## Goal

Add an optional fashion entity watchlist pack so users can start tracking a
broader set of designer brands, products, bags, shoes, categories, designers,
celebrities, and style terms without hand-writing a large `entities.yaml`.

The pack should improve local matching coverage for daily fashion research while
remaining honest: it is a starter configuration, not a claim that any included
brand or product is currently hot, market-wide, platform-wide, or verified
demand.

## Context

The default `configs/entities.example.yaml` is intentionally small. It includes
The Row, Miu Miu, Jonathan Anderson, Zendaya, The Row Margaux, Ballet Flats, and
Quiet Luxury. That is useful for smoke tests and the first run, but the user's
fashion research needs include broader designer brands and products such as
The Row-style designer brands, bags, and shoes.

The existing entity schema already supports this:

- entity types: `brand`, `designer`, `celebrity`, `product`, `category`,
  `trend`;
- aliases with `safe_single_word` reasons;
- `context_terms` for broad/common aliases;
- `parent_brand` for product matching;
- tags/category tags;
- `initial_weight`, `match_confidence`, and active windows.

Stage 14 should use that schema rather than adding code.

## Recommended Approach

Create a new optional entity pack:

```text
configs/entity-packs/fashion-watchlist.example.yaml
```

This pack should be a complete `EntityConfig` YAML file that users can copy to
`configs/entities.yaml`. It should include a conservative starter watchlist for:

- designer and contemporary brands;
- named bags and shoes;
- general product categories;
- designers/creative directors;
- celebrity style signals;
- style/aesthetic terms.

Add docs:

```text
docs/entity-packs.md
```

The docs should explain how to copy the pack, edit it, run `doctor` with the
same `--config-dir` that receives the copied pack, and then use existing
`match`, `report`, `candidates`, and `trends` commands with that config
directory after the user's existing configured-source or local-signal pipeline
has already produced signals.

Add tests that load the pack with `load_entity_config()` and assert the pack has
the expected structure, parent-brand references, existing matcher guardrails for
high-risk aliases, narrow category aliases, and unique aliases through the real
config validator.

## Non-Goals

Stage 14 does not implement or document:

- new collectors, platform connectors, platform search, or community ingestion;
- web scraping, crawler development, browser automation, account automation, or
  source-acquisition workflows;
- official or unofficial social platform APIs;
- instructions for obtaining platform/community exports;
- current hotness claims, platform-wide claims, market-wide trend proof,
  verified demand, real-time monitoring, or top social trend rankings;
- paid API requirements, LLM scoring, embeddings, vector databases, or image
  recognition;
- DB migrations, source-health changes, report semantics changes, dashboard
  changes, or scoring algorithm changes;
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, or policy checklist.

## Pack Boundary

The pack is static YAML. It does not call the network, fetch source pages,
collect platform data, or update itself. Users should treat it as a seed list
for local observation and edit it for their own research.

The pack should avoid overly broad aliases where possible. Existing matching
uses context gates for product aliases with `parent_brand`, single-word aliases,
and aliases listed as unsafe/common by the application. It does not treat
`context_terms` as a universal phrase-level disambiguation system for every
multi-word category or trend alias.

If a single-word or application-marked common alias is useful, it must either:

- use `safe_single_word: true` with a reason for distinctive proper names; or
- include `context_terms` so generic prose does not match.

Named products should use `parent_brand` where possible. Product aliases should
match when the parent brand appears or when narrow product context appears.
Other multi-word category and trend aliases should be kept narrow because Stage
14 does not change matcher semantics.

## Files

Create:

- `configs/entity-packs/fashion-watchlist.example.yaml`
- `docs/entity-packs.md`
- `tests/test_entity_packs.py`

Modify:

- `README.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`

Review prompt/output files under `docs/reviews/` and plan files under
`docs/superpowers/` are process artifacts for the staged workflow. They are not
product/runtime files and are not part of the entity-pack behavior.

## Testing

Focused tests should prove:

- the watchlist pack loads with `load_entity_config()`;
- the pack contains a broader mix of entity types;
- key expected examples are present, including `The Row`, `Khaite`, `Alaia`,
  `Loewe`, `Alaia Le Teckel`, `Miu Miu Arcadie`, `Mary Jane Shoes`, and
  `East-West Bags`;
- product `parent_brand` values reference real brand entities;
- product aliases, single-word aliases, and application-marked common aliases
  use existing matcher guardrails;
- multi-word category aliases are narrow enough for the existing matcher rather
  than relying on `context_terms` as universal disambiguation;
- the packaged starter config remains unchanged and still loads.

No test should call the network or run collectors.

## Documentation

Docs should explain:

- the pack is optional;
- users can copy it into `configs/entities.yaml`;
- the default small starter config remains suitable for first runs;
- the pack is a seed watchlist, not a ranking or hot-list;
- scores and trend deltas remain local observations from configured sources and
  imported local signals;
- users should edit aliases and context terms for their market, language, and
  coverage needs.
- entity packs do not add sources, source setup, source acquisition, collection
  workflows, platform/community ingestion, or scraping;

## Verification

Required implementation verification before Stage 14 code review:

- focused entity-pack tests;
- full `pytest -q`;
- `ruff check .`;
- `ruff format --check .`;
- `git diff --check`;
- CodeGraph status;
- Claude Code code review with `--effort max`.

Optional downstream release operations, not part of Stage 14 implementation or
acceptance:

- `uv lock --check --default-index https://pypi.org/simple`;
- `uv sync --locked --dev --check --default-index https://pypi.org/simple`;
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`;
- wheel/sdist build;
- installed-wheel smoke for existing CLI help and package import;
- secret/generated-artifact sanity checks.
