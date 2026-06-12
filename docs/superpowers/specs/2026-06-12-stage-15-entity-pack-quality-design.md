# Stage 15 Entity Pack Quality Diagnostics Design

## Goal

Add a local, read-only diagnostics command for entity YAML files and optional
entity packs. The command should help users maintain brand, designer, celebrity,
product, category, and trend watchlists before using them with existing local
matching, reporting, candidate, and trend-delta workflows.

Stage 15 improves pack quality visibility. It does not add source collection,
social monitoring, scraping, platform search, source acquisition, current-hotness
rankings, or market-wide demand claims.

## Context

Stage 14 added an optional static entity watchlist pack:

```text
configs/entity-packs/fashion-watchlist.example.yaml
```

That pack is useful, but entity YAML can be subtle:

- entity names are display labels, while the matcher checks aliases;
- product aliases with `parent_brand` are accepted only when the parent brand or
  product context is present;
- single-word aliases and aliases in `UNSAFE_COMMON_ALIASES` require context
  unless marked safe with a reason;
- ordinary multi-word aliases are accepted without context, even when
  `context_terms` are present;
- tags, category tags, weights, confidence, and parent fields are local
  interpretation and scoring inputs that are easy to omit while editing YAML.

Stage 12 already established a fitting pattern with `source-pack-lint`: read one
local YAML file, validate it through the canonical schema loader, emit stable
structured findings, render table or JSON output, and avoid collection, network,
database, report, or default-directory side effects.

## Recommended Approach

Create a sibling diagnostics module:

```text
src/fashion_radar/entity_packs.py
```

It should expose:

```python
class EntityPackFindingSeverity(StrEnum): ...
class EntityPackFinding(BaseModel): ...
class EntityPackLintResult(BaseModel): ...

def lint_entity_pack(path: Path) -> EntityPackLintResult: ...
def render_entity_pack_lint_table(result: EntityPackLintResult) -> list[str]: ...
```

The linter should call `load_entity_config(path)` for canonical schema
validation. Loader failures become one `invalid_config` error finding. Advisory
rules should not duplicate or weaken schema validation in `settings.py`.

Raw YAML should be read before typed validation so the command can detect
omitted fields such as `initial_weight` and `match_confidence`, matching the
source-pack linter pattern.

Add a flat Typer command:

```bash
fashion-radar entity-pack-lint PATH
fashion-radar entity-pack-lint PATH --format json
fashion-radar entity-pack-lint PATH --strict
```

Command behavior:

- default output is table;
- JSON output uses Pydantic `model_dump_json(indent=2)`;
- errors always exit non-zero;
- warnings exit non-zero only with `--strict`;
- output is printed before exit handling;
- the command has no `--config-dir`, `--data-dir`, or `--reports-dir`;
- the command does not open SQLite, run match/scoring/report workflows, collect
  sources, or create artifacts.

## Diagnostics

The first Stage 15 rule set should stay local and deterministic.

Errors:

- `invalid_config`: YAML cannot be read, parsed, or loaded through
  `load_entity_config()`.
- `empty_entity_pack`: the file contains no entities.
- `entity_without_aliases`: an entity has no aliases and cannot match text.
- `name_normalizes_empty`: an entity name normalizes to an empty matcher key.
- `alias_normalizes_empty`: an alias normalizes to an empty matcher key.

Warnings:

- `missing_tags`: a brand, designer, celebrity, or trend has no `tags`.
- `missing_category_tags`: a product or category has no `category_tags`.
- `product_missing_parent_brand`: a product does not define `parent_brand`.
- `product_missing_context_terms`: a product with `parent_brand` has no
  `context_terms`, so aliases that appear without the parent brand will be
  rejected.
- `parent_brand_on_non_product`: `parent_brand` is present on a non-product; the
  current matcher only treats it specially for product entities.
- `product_alias_matches_parent_brand`: a product alias normalizes to the parent
  brand name or one of the parent brand aliases, which can make product matches
  too broad.
- `parent_self_reference`: an entity's generic `parent` points to itself.
- `parent_cycle`: generic `parent` links form a cycle.
- `context_terms_no_effect`: an entity has `context_terms`, but none of its
  aliases consult those context terms under current matcher rules.
- `ungated_alias_with_context_terms`: an alias is ordinary multi-word text and
  will be accepted without context even though the entity defines
  `context_terms`.
- `self_context_term`: a context term normalizes to the same key as a gated alias
  on the same entity, letting the alias satisfy its own context gate.
- `safe_common_alias`: an alias marked safe normalizes to a value in
  `UNSAFE_COMMON_ALIASES`; context terms are usually safer for these phrases.
- `safe_alias_bypasses_context`: a non-product safe alias can bypass available
  context terms because safe aliases are accepted before context matching.
- `safe_alias_ignored_for_parent_product`: a product alias uses
  `safe_single_word`, but products with `parent_brand` still require parent
  brand or context.
- `blank_context_term`, `duplicate_context_term`,
  `context_term_normalizes_empty`, `blank_tag`, `duplicate_tag`,
  `blank_category_tag`, and `duplicate_category_tag`: local hygiene issues in
  metadata lists.

Info:

- `safe_single_word_alias`: an effective safe single-word/common alias is
  present.
- `safe_single_word_no_effect`: `safe_single_word` is set on an alias that does
  not require context under current matcher rules.
- `implicit_initial_weight`: raw YAML omitted `initial_weight`, so the default
  scoring weight is used.
- `implicit_match_confidence`: raw YAML omitted `match_confidence`, so the
  default match confidence is used.

The diagnostics must describe matcher behavior precisely. `context_terms` are
not a universal phrase-level gate. They affect product aliases with
`parent_brand`, and they affect non-product single-word/common aliases only when
those aliases are not accepted first through an effective `safe_single_word`
reason. The product-with-`parent_brand` branch ignores `safe_single_word`.
Other multi-word aliases may match without context.

## Output Shape

JSON output should be stable and small enough for CI:

```json
{
  "path": "configs/entity-packs/fashion-watchlist.example.yaml",
  "entity_count": 27,
  "alias_count": 42,
  "type_counts": {
    "brand": 10,
    "category": 5,
    "celebrity": 2,
    "designer": 2,
    "product": 6,
    "trend": 3
  },
  "tag_counts": {
    "designer_brand": 8,
    "luxury": 4
  },
  "category_tag_counts": {
    "bag": 5,
    "shoes": 4
  },
  "accepted_without_context_aliases": 18,
  "context_gated_aliases": 5,
  "safe_aliases": 8,
  "product_parent_gated_aliases": 12,
  "findings": []
}
```

Table output should mirror `source-pack-lint`:

```text
Entity pack: configs/entity-packs/fashion-watchlist.example.yaml
Entities: 27 total
Aliases: 42 total
Types: brand=10, category=5, celebrity=2, designer=2, product=6, trend=3
Findings: 0 errors, 0 warnings, 0 info
No entity-pack quality findings.
```

When findings exist:

```text
Severity | Code | Entity | Alias | Field | Message
warning | missing_category_tags | Example Bag | n/a | category_tags | Product or category entity has no category tags.
```

## Files

Create:

- `src/fashion_radar/entity_packs.py`
- `tests/test_entity_pack_lint.py`
- `docs/entity-pack-quality.md`

Modify:

- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `README.md`
- `docs/entity-packs.md`
- `docs/architecture.md`
- `CHANGELOG.md`

Process artifacts:

- `docs/superpowers/specs/2026-06-12-stage-15-entity-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md`
- `docs/reviews/claude-code-stage-15-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-15-plan-review.md`
- `docs/reviews/claude-code-stage-15-code-review-prompt.md`
- `docs/reviews/claude-code-stage-15-code-review.md`

## Non-Goals

Stage 15 does not implement or document:

- social-platform connectors, platform search, automated community ingestion, or
  source acquisition;
- web scraping, crawler development, browser automation, account automation, or
  unofficial platform APIs;
- login cookies, session files, browser profiles, tokens, proxy pools,
  fingerprint evasion, CAPTCHA bypass, rate-limit bypass, access-control
  bypass, or paywall bypass;
- instructions for obtaining exports from social/community platforms;
- current-hotness claims, platform-wide claims, social-wide claims, market-wide
  demand proof, or real-time trend rankings;
- DB migrations, source-health changes, collector changes, scoring changes,
  report changes, dashboard changes, or matcher behavior changes;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Testing

Focused tests should prove:

- repository watchlist pack lints with no errors;
- invalid entity YAML returns `invalid_config`;
- an empty entity file returns `empty_entity_pack`;
- entities without aliases and empty-normalized names/aliases are errors;
- missing tags/category tags, product parent/context issues, parent hierarchy
  issues, safe-alias semantics, metadata-list hygiene, and implicit defaults
  emit deterministic findings;
- result JSON shape and table rendering are stable;
- CLI help, table output, JSON output, `--strict`, and invalid-config exit
  behavior match `source-pack-lint`;
- the CLI command is read-only and does not create config, data, reports,
  SQLite, workflow, digest, or collector artifacts.

No test should call the network, run collectors, invoke platform/social tooling,
or require external account data.

## Documentation

Add `docs/entity-pack-quality.md` with command examples, table/JSON output,
severity meanings, finding codes, why findings matter, tuning guidance for
aliases/context terms/parents/tags/weights, and limits.

Update `docs/entity-packs.md` and `README.md` to recommend linting a local pack
before copying or editing it. Documentation must keep the same boundary as
previous stages: entity-pack diagnostics are local YAML checks, not signal
collection, not platform monitoring, and not proof that a brand, bag, shoe, or
trend is currently hot outside the configured local source set.

## Verification

Required before Stage 15 code review:

- focused entity-pack lint tests;
- full `pytest -q`;
- `ruff check .`;
- `ruff format --check .`;
- `git diff --check`;
- CodeGraph status;
- Claude Code code review with `--effort max`.

Optional downstream release operations, not part of Stage 15 implementation
acceptance:

- `uv lock --check --default-index https://pypi.org/simple`;
- `uv sync --locked --dev --check --default-index https://pypi.org/simple`;
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`;
- package build;
- installed-wheel smoke checks;
- secret/generated-artifact sanity checks before GitHub upload.
