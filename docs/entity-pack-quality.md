# Entity-Pack Quality

`fashion-radar entity-pack-lint` checks one local entity YAML or entity-pack YAML
file before using that YAML in existing matching workflows. It helps catch
watchlist issues that are easy to miss when editing brands, designer brands,
celebrities, designers, named bags, shoes, categories, and trend terms.

Linting is local and read-only. It does not match items, score entities, inspect
SQLite, collect sources, search social platforms, fetch pages, or create config,
data, report, digest, or workflow artifacts. It is not a hot-list, ranking,
platform-wide signal, market-wide proof, compliance review, audit workflow, or
legal review.

## Command Examples

Run the default table output:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
```

Print stable JSON for CI or scripts:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
```

Fail on warnings as well as errors:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --strict
```

Use `--strict` when an edited local pack should have no advisory warnings before
you rely on it in scheduled local workflows. Without `--strict`, warnings remain
visible but only errors fail the command.

## Table Output

Table output starts with a compact summary:

```text
Entity pack: configs/entity-packs/fashion-watchlist.example.yaml
Entities: 32 total
Aliases: 51 total
Types: brand=12, category=5, celebrity=2, designer=2, product=8, trend=3
Findings: 0 errors, 16 warnings, 71 info
```

The summary shows:

- `Entity pack`: the local file that was linted.
- `Entities`: total entity entries.
- `Aliases`: total aliases across all entities.
- `Types`: entity counts by configured entity type.
- `Findings`: counts by severity.

When findings exist, table output adds one row per finding:

```text
Severity | Code | Entity | Alias | Field | Message
warning | missing_category_tags | Example Bag | n/a | category_tags | Product or category entity has no category tags.
```

The row shows severity, stable code, entity name when available, alias when
available, field when available, and a short explanation.

## JSON Output

JSON output contains the same information in a stable shape. The example below
is an abbreviated representative excerpt from the checked-in starter watchlist
pack: scalar counts and count maps match current lint output, while `findings`
shows one representative finding, not the full findings list:

```json
{
  "path": "configs/entity-packs/fashion-watchlist.example.yaml",
  "entity_count": 32,
  "alias_count": 51,
  "type_counts": {
    "brand": 12,
    "category": 5,
    "celebrity": 2,
    "designer": 2,
    "product": 8,
    "trend": 3
  },
  "tag_counts": {
    "accessories": 2,
    "aesthetic": 3,
    "american_fashion": 1,
    "bags": 1,
    "celebrity_style": 2,
    "consumer_trend": 1,
    "contemporary_luxury": 2,
    "creative_director": 2,
    "designer_brand": 11,
    "emerging_label": 2,
    "footwear": 1,
    "luxury": 4,
    "lvmh": 1,
    "minimalism": 2,
    "new_york": 1,
    "prada_group": 1,
    "red_carpet": 1,
    "street_style": 1,
    "styling": 2
  },
  "category_tag_counts": {
    "bag": 7,
    "flats": 3,
    "handbag": 5,
    "mary_jane": 1,
    "mule": 1,
    "shoe": 2,
    "shoes": 4,
    "shoulder_bag": 1,
    "sneakers": 1,
    "top_handle": 1,
    "tote": 2
  },
  "accepted_without_context_aliases": 22,
  "context_gated_aliases": 4,
  "safe_aliases": 9,
  "product_parent_gated_aliases": 16,
  "findings": [
    {
      "severity": "warning",
      "code": "context_terms_no_effect",
      "message": "Entity has context_terms, but none of its aliases consult context under current matcher rules.",
      "entity_name": "Boat Shoes",
      "alias": null,
      "field": "context_terms"
    }
  ]
}
```

The matcher-gate counts are derived from current local matcher rules:

- `accepted_without_context_aliases`: ordinary multi-word aliases that match
  without context.
- `context_gated_aliases`: non-product single-word/common aliases that require
  context.
- `safe_aliases`: non-product single-word/common aliases accepted by
  `safe_single_word` plus a reason.
- `product_parent_gated_aliases`: product aliases with `parent_brand`, which
  require either the parent brand or product context.

## Severity Meanings

- `error`: the entity pack is structurally invalid or contains an entity that
  cannot match safely or meaningfully. Errors exit non-zero.
- `warning`: the pack can load, but an entity may be too broad, too ambiguous,
  under-classified, or surprising under current matcher rules. Warnings exit
  non-zero only with `--strict`.
- `info`: the pack has an explicit setting or omitted default worth reviewing.
  Informational findings do not fail the command.

## Finding Codes

- `invalid_config`: the YAML cannot be read, parsed, or loaded through the
  entity config schema.
- `empty_entity_pack`: the file contains no entities.
- `entity_without_aliases`: an entity has no aliases. Entity names are display
  labels; matching checks aliases.
- `name_normalizes_empty`: an entity name normalizes to an empty matcher key.
- `alias_normalizes_empty`: an alias normalizes to an empty matcher key.
- `missing_tags`: a brand, designer, celebrity, or trend has no `tags`.
- `missing_category_tags`: a product or category has no `category_tags`.
- `product_missing_parent_brand`: a product does not define `parent_brand`. This
  is a precision recommendation for named branded products, not a validity
  failure. Products without `parent_brand` still follow ordinary alias semantics.
- `product_missing_context_terms`: a product with `parent_brand` has no
  `context_terms`, so product aliases without the parent brand are rejected.
- `parent_brand_on_non_product`: `parent_brand` is present on a non-product; the
  matcher treats it specially only for product entities.
- `product_alias_matches_parent_brand`: a product alias normalizes to the parent
  brand name or one of its aliases, which can make product matching too broad.
- `parent_self_reference`: an entity's generic `parent` points to itself.
- `parent_cycle`: generic `parent` links form a cycle.
- `context_terms_no_effect`: an entity has `context_terms`, but none of its
  aliases consult context under current matcher rules.
- `ungated_alias_with_context_terms`: an ordinary multi-word alias is accepted
  without context even though the entity defines `context_terms`.
- `self_context_term`: a context term normalizes to the same key as a gated alias
  on the same entity.
- `safe_common_alias`: an alias marked safe normalizes to a value in
  `UNSAFE_COMMON_ALIASES`; context terms are usually safer for these phrases.
- `safe_alias_bypasses_context`: a safe non-product alias bypasses available
  `context_terms`.
- `safe_alias_ignored_for_parent_product`: `safe_single_word` is set on a product
  alias with `parent_brand`, but that matcher branch ignores the flag.
- `blank_context_term`: `context_terms` contains a blank value.
- `duplicate_context_term`: `context_terms` contains duplicate normalized
  values.
- `context_term_normalizes_empty`: a context term normalizes to an empty matcher
  key.
- `blank_tag`: `tags` contains a blank value.
- `duplicate_tag`: `tags` contains duplicate normalized values.
- `blank_category_tag`: `category_tags` contains a blank value.
- `duplicate_category_tag`: `category_tags` contains duplicate normalized
  values.
- `safe_single_word_alias`: an effective safe single-word/common alias is
  present.
- `safe_single_word_no_effect`: `safe_single_word` is set on an alias that does
  not require context.
- `implicit_initial_weight`: raw YAML omitted `initial_weight`, so scoring uses
  the default weight.
- `implicit_match_confidence`: raw YAML omitted `match_confidence`, so matching
  uses the default confidence.

## Why Findings Matter

Entity names do not match text unless they also appear as aliases. A display name
without aliases can look configured while never producing a match.

Product parent brands improve precision for named branded items. A product such
as a named bag or shoe can match when the parent brand appears or when product
context appears. Without a parent brand, the product follows ordinary alias
semantics, which may be fine for generic products but can be noisy for branded
items.

`context_terms` are not universal phrase-level gates. They matter for product
aliases with `parent_brand`, non-product single-word aliases, and aliases listed
as unsafe/common by the application. Other multi-word aliases can match without
context, so broad phrases should be narrowed or reviewed.

Safe aliases are explicit shortcuts. They are useful for distinctive brand or
person names, but they can also bypass context that a user expected to apply.
For product aliases with `parent_brand`, the safe flag is not consulted.

Tags and category tags do not change matching directly, but they help users
understand the shape of the local watchlist and review report/candidate results
by lane.

Weights and confidence affect local scoring and match filtering. Omitting them
uses defaults, which can be correct but should be visible when editing a larger
watchlist.

## Tuning Aliases, Context Terms, Parents, Tags, And Weights

Start with specific aliases. Prefer `Alaia Le Teckel` over `Teckel` unless the
short form is common in your retained local source set and has product context.

Use `parent_brand` for named branded products when the brand is present in the
same entity file. Add product `context_terms` for shorthand aliases that may
appear without the parent brand.

Use `safe_single_word` only when a single-word or application-marked common
alias is distinctive enough for your local source set. Always keep the reason
specific.

Review ordinary multi-word category and trend aliases such as `Mary Janes`,
`boat shoes`, or `office siren`. These can be useful in a retained fashion
corpus, but they are accepted without context by the current matcher.

Use `tags` for brands, designers, celebrities, and trends. Use `category_tags`
for products and categories. Tags should describe how you want to review the
local watchlist, such as `designer_brand`, `bags`, `footwear`, `red_carpet`,
`aesthetic`, or `runway`.

Keep `initial_weight` conservative until you have observed a few local reports.
Weights are local scoring inputs, not confidence in external demand.

## Limits

`entity-pack-lint` checks one local YAML file. It does not know whether a brand,
bag, shoe, celebrity outfit, or style phrase is popular today. It does not search
Instagram, TikTok, X, Xiaohongshu, community tools, news sites, or exports. It
does not collect sources, inspect SQLite, run matching, run scoring, generate
reports, package digests, or write workflow files.

Treat a clean lint result as a local configuration quality signal. It is not a
ranking, hot-list, demand proof, source acquisition workflow, platform search,
social monitoring workflow, compliance review, or audit result.
