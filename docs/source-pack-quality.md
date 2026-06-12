# Source-Pack Quality

`fashion-radar source-pack-lint` checks one local source YAML or source-pack YAML
file before collection. It is meant for daily source-set hygiene: catching
duplicate inputs, sources that will not run, and scoring defaults that are easy
to miss when editing YAML.

Linting is local and read-only. It does not fetch sources, check live feed
availability, collect source items, open SQLite, or create config, data, report,
or workflow artifacts. It is not a compliance, audit, policy, or source-terms
review workflow.

## Command Examples

Run the default table output:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
```

Print stable JSON for CI or scripts:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

Fail on warnings as well as errors:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
```

Use `--strict` when you want edited source packs to stay clean before a scheduled
run. Without `--strict`, warnings are visible but only errors fail the command.

## Table Output

Table output starts with a compact summary:

```text
Source pack: configs/source-packs/fashion-public.example.yaml
Sources: 16 total, 16 enabled, 0 disabled
Types: gdelt=10, rss=6
Findings: 0 errors, 0 warnings, 0 info
No source-pack quality findings.
```

The summary shows:

- `Source pack`: the local file that was linted.
- `Sources`: total source entries, enabled source entries, and disabled source
  entries.
- `Types`: source counts by configured source type.
- `Findings`: counts by severity.

When findings exist, table output adds one row per finding:

```text
Severity | Code | Source | Field | Message
warning | missing_tags | Example Feed | tags | Source has no tags.
```

The finding row shows the severity, stable code, source name when available,
source field when available, and a short explanation.

## JSON Output

JSON output contains the same information in a stable shape:

```json
{
  "path": "configs/source-packs/fashion-public.example.yaml",
  "source_count": 16,
  "enabled_count": 16,
  "disabled_count": 0,
  "type_counts": {
    "gdelt": 10,
    "rss": 6
  },
  "tag_counts": {
    "industry_news": 5,
    "gdelt": 10
  },
  "findings": [
    {
      "severity": "warning",
      "code": "missing_tags",
      "message": "Source has no tags.",
      "source_name": "Example Feed",
      "field": "tags"
    }
  ]
}
```

Use `source_count`, `enabled_count`, `disabled_count`, `type_counts`, and
`tag_counts` to understand the shape of the configured source set. Use
`findings` to decide what to fix before collection. JSON output does not include
fetched data, collected items, database state, source contents, or account data.

## Severity Meanings

- `error`: the source pack is structurally invalid or has a quality problem that
  would make daily collection ambiguous or empty. Errors exit non-zero.
- `warning`: the source pack can load, but it may double-count, lose useful
  classification detail, or behave differently than expected. Warnings exit
  non-zero only with `--strict`.
- `info`: the source pack has a setting worth reviewing. Informational findings
  do not fail the command.

## Finding Codes

- `invalid_config`: the YAML cannot be read, parsed, or loaded through the
  source config schema.
- `duplicate_source_name`: two or more sources have the same normalized name.
  This is an error because source health, run logs, attribution, and report
  summaries use source identity.
- `empty_enabled_pack`: no sources are enabled. This is an error because the
  next collection run would have no active configured inputs.
- `duplicate_source_target`: two or more RSS/RSSHub-compatible sources point to
  the same normalized feed URL. This is a warning because it can double-count
  the same daily items.
- `duplicate_gdelt_query`: two or more GDELT sources use the same normalized
  query. This is a warning because it can repeat the same metadata lane with
  different source names or weights.
- `missing_tags`: a source has no tags. This is a warning because tags help you
  review source balance and tune category-specific packs.
- `disabled_source`: a source is present but disabled. This is informational so
  intentional parking-lot entries are visible before a run.
- `implicit_weight`: the raw YAML omitted `weight`, so scoring uses the default.
  This is informational because default weights can be easy to overlook.
- `article_extraction_enabled`: an RSS/RSSHub-compatible source has article
  extraction enabled. This is informational and only reminds you that collection
  may attempt article-page extraction for that configured source during a later
  collection run.

## Why Findings Matter

Duplicate source names make daily diagnostics harder to read. If two entries
share a name, source health, source counts, and report attribution can become
ambiguous even when the underlying URLs differ.

Duplicate feed URLs can make the same article appear through multiple source
entries. Fashion Radar de-duplicates stored items by normalized URL, but
duplicate configured targets still make source intent less clear and can confuse
source-set maintenance.

Duplicate GDELT queries can make one query lane look broader than it is. If the
same query appears twice under different names or weights, daily metadata
signals may feel more diverse than the configured inputs really are.

Missing tags reduce your ability to reason about source balance. Tags such as
`industry_news`, `celebrity_style`, `retail`, `resale`, `footwear`,
`accessories`, `runway`, or `creative_director_moves` make it easier to see
which parts of the configured local source set are carrying the report.

Disabled sources are useful while editing, but they also reduce active source
diversity. Linting makes them visible before a run so an all-disabled or
partially disabled pack does not quietly narrow daily inputs.

Implicit weights can hide scoring decisions. A source with omitted `weight`
uses the default, which may be fine for general fashion media but too high or
too low for a specialized lane.

Article extraction settings affect how much work a later collection run may do.
The lint command does not fetch article pages, but it flags enabled extraction
as a local-pack quality reminder so you can decide whether that source should
stay metadata-only.

## Tuning Tags And Weights

Tags should describe why a source is in the configured source set. Weights should
describe how much a mention from that source should matter in local heat scores.
Start with conservative weights, run reports for a few days, and adjust based on
whether the report reflects your research priorities.

For brands and designer brands, tag sources with lanes such as `brand_news`,
`designer_brands`, `luxury`, `industry_news`, and `trade_media`. Give higher
weights to sources that reliably publish primary brand, runway, earnings,
appointment, or product-launch context. Keep broader culture feeds lower when
they mostly provide secondary mentions.

For celebrities, use tags such as `celebrity_style`, `red_carpet`, `culture`,
and `fashion_media`. Keep weights modest unless a source consistently provides
fashion-specific context rather than general celebrity coverage.

For footwear, use `footwear`, `sneakers`, `streetwear`, and `retail`. Balance
trade sources with culture sources so a single sneaker-heavy lane does not
overwhelm quieter footwear signals.

For bags and accessories, use `bags`, `handbags`, `accessories`, `luxury`, and
`products`. If the report is missing product signals, add or raise sources that
focus on product launches, retailer edits, and resale observations from sources
you have configured.

For runway and fashion week, use `runway`, `fashion_week`,
`emerging_designers`, and `designer_brands`. Runway lanes can spike during show
periods, so review whether their weights should be seasonal or lower than daily
trade sources.

For retail and resale, use `retail`, `resale`, `commerce`, and `industry_news`.
These sources can be useful for demand-adjacent local signals inside the source
set, but they should not be described as proof of demand outside it.

For creative-director and executive moves, use tags such as
`creative_director_moves`, `executive_moves`, `designer_brands`, and
`industry_news`. These sources often matter even when mention volume is low, so
slightly higher weights can be appropriate for trusted trade or brand-news
sources.

## Limits

`source-pack-lint` checks the configured YAML file only. It does not know whether
a feed is live today, whether a GDELT query will return records, or whether a
source will publish fashion-relevant items in the next run. Treat a clean lint
result as a local configuration quality signal, not as a source availability
guarantee.
