# Stage 350 ROW ONE Saved Article Daily Signal Leaderboard Design

## Objective

Stage 350 adds a generated-site-only Saved Article Daily Signal Leaderboard
inside `articles/index.html`. The leaderboard summarizes the day&apos;s saved
local article signal chips into compact brand, product, and theme rollups so a
reader can see which signals recur across the local saved article set without
opening each article row.

## Product Gap

Stage 349 added article-level Signal Facets that show brands, products, and
themes for each saved local article. That matrix helps answer which article
carries which signal, but it does not answer the daily editorial question:
which brands, products, or themes appear most often across today&apos;s saved
local article set?

The Daily Signal Leaderboard closes that gap by aggregating the already-safe
Signal Facets rows. It is a presentation rollup over local saved article
signals, not a popularity score, market heat rank, recommendation system, or
external demand signal.

## Architecture

This is a generated-site-only local article organization change that reuses the
Stage 349 Signal Facets output:

- `src/fashion_radar/row_one/saved_article_daily_signal_leaderboard.py` should
  build the leaderboard from `RowOneSavedArticleSignalFacets` only.
- The builder should aggregate existing facet chips into three buckets:
  `Brands`, `Products`, and `Themes`.
- Each leaderboard item should include a label, article count, source count,
  and capped supporting article links derived from existing Signal Facets rows.
- The builder should dedupe labels case-insensitively while preserving a stable
  first-seen article order.
- Sorting should be deterministic: article count descending, first-seen order
  ascending, and normalized English label ascending as a final tie-break.
- `src/fashion_radar/row_one/render.py` should build the leaderboard after
  `saved_article_signal_facets` and pass it only into the generated saved
  article library page renderer.
- `src/fashion_radar/row_one/templates.py` should render the leaderboard inside
  `articles/index.html`, after Signal Facets and before Theme Digest, with
  safe local/detail article links and no outbound article URLs.
- The saved article daily summary should include a jump link to the leaderboard
  and count it as one generated saved article surface when the section is
  present.

The feature creates no schema, JSON artifact, route family, collector,
extraction path, ranking model, LLM call, scheduler, deployment, app-facing
contract field, or compliance-review product behavior.

## Rendering Behavior

When at least one bucket contains leaderboard items, Stage 350 should render a
`saved-article-daily-signal-leaderboard` section in the generated saved article
library page.

For each bucket, it should show:

- a localized bucket heading;
- up to five signal items;
- the signal label;
- factual support metrics such as article count and source count;
- up to three supporting article links pointing to existing safe local article
  digest anchors.

The section should be omitted when no safe leaderboard item can be built. It
should not appear on the homepage.

## Signal Sources

Stage 350 should aggregate only these Stage 349 values:

- `RowOneSavedArticleSignalFacetRow.brands`
- `RowOneSavedArticleSignalFacetRow.products`
- `RowOneSavedArticleSignalFacetRow.themes`

It should not inspect raw article text, raw references, source URLs, imported
signals, external search results, or social platform data. This keeps the
leaderboard a rollup of already accepted local article chips.

The `Themes` bucket rolls up the Stage 349 content-organization group-title
chips. Those labels describe saved article organization groups such as
`Read First` or `Products`; they are not inferred editorial fashion themes,
trend rankings, or market heat signals.

## Safety And Caps

All visible labels, article titles, and source names must be escaped by the
template layer. All supporting article links must reuse existing safe
same-site local article/detail anchors already represented by Signal Facets.

Caps:

- up to three buckets;
- up to five items per bucket;
- up to three supporting article links per item;
- no full article body text;
- no source brief bullets copied into the leaderboard.

## Out Of Scope

Stage 350 does not add article downloading, social-platform collection,
external tool adapters, scraping, browser automation, platform APIs,
account/session behavior, extraction changes, LLM summaries, ranking,
recommendation, analytics, personalization, scheduling, deployment, app
contract changes, schema changes, new route families, or compliance-review
product behavior.

It also does not create
`data/saved-article-daily-signal-leaderboard.json`,
`data/article-chip-leaderboard.json`,
`saved-article-daily-signal-leaderboard.html`, or any new JSON/HTML artifact.

## Acceptance Criteria

- `articles/index.html` renders a `saved-article-daily-signal-leaderboard`
  section after Signal Facets and before Theme Digest when at least one safe
  leaderboard item exists.
- The saved article daily summary links to the leaderboard when it is rendered.
- Buckets aggregate only Stage 349 Signal Facet chips for brands, products, and
  themes.
- Items show deterministic support counts, source counts, and capped supporting
  article links.
- Labels are escaped, deduped case-insensitively, capped, and sorted
  deterministically.
- Partially empty inputs omit empty buckets instead of rendering empty bucket
  shells.
- Empty or unsafe inputs omit the leaderboard shell.
- The feature does not appear on the homepage.
- No app-facing contract, schema, JSON artifact, route family, fetching,
  extraction, ranking, LLM, scheduling, deployment, or compliance-review
  product behavior changes.
- Documentation and workflow guards state the generated-site-only boundary for
  Stage 350.
