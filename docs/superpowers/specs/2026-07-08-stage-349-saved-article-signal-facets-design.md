# Stage 349 ROW ONE Saved Article Signal Facets Design

## Objective

Stage 349 adds generated-site-only Saved Article Signal Facets inside
`articles/index.html`. The section gives readers a compact article-by-article
matrix of which saved local articles carry which brands, products, and editorial
themes.

## Product Gap

Stages 341 through 348 made saved local articles readable, searchable by source,
and easier to navigate through daily summaries, body guides, source briefs, and
source routes. The remaining information-organization gap is article-level
facet scanning: a reader can find brands and products in the Reference Atlas,
and themes in the Theme Digest, but cannot quickly answer "which saved article
mentions The Row, which one carries product signals, and which theme does it
belong to?"

Signal Facets close that gap with a deterministic matrix. It organizes existing
local saved article metadata and content-organization cards without adding new
analysis pipelines, ranking, scoring, extraction, LLM summaries, or app
contracts.

## Architecture

This is a generated-site-only local article organization change split between a
small internal builder and the existing saved article library renderer:

- `src/fashion_radar/row_one/saved_article_signal_facets.py` should build
  Signal Facet view data from the existing `RowOneSavedArticleLibrary` and
  existing `RowOneSavedArticleContentOrganization` cards.
- `src/fashion_radar/row_one/saved_article_reference_atlas.py` should expose
  the existing reference bucket classifier so Signal Facets reuse the exact same
  brand/product vocabulary as the Reference Atlas instead of creating a second
  classifier.
- `src/fashion_radar/row_one/render.py` should build the facet object alongside
  the existing saved article digest, atlas, reading path, evidence, and source
  surfaces.
- `src/fashion_radar/row_one/templates.py` should only render the typed facet
  rows, place the generated-site-only section, and provide CSS.
- The facet builder should match organization cards back to saved article
  library entries by safe detail path only.
- The renderer should output one compact matrix section after the saved article
  daily summary and before Theme Digest.
- Each matrix row should represent one saved local article and show capped
  chips for brands, products, and themes.

The feature creates no schema, JSON artifact, route family, collector,
extraction path, ranking model, LLM call, scheduler, or app-facing contract
field. The internal builder module is Python-only and feeds the generated HTML
surface.

## Rendering Behavior

For each saved article that has at least one safe facet, Stage 349 should render:

- an article title and source label;
- a safe local article/detail link to the existing local article digest or safe
  content-section anchor;
- up to four brand chips derived from existing `RowOneReference` values that
  the existing Reference Atlas bucket classifier classifies as `brands`;
- up to four product chips derived from existing `RowOneReference` values that
  the existing Reference Atlas bucket classifier classifies as `products`;
- up to four theme chips derived from the existing content organization group
  titles only, using the established group vocabulary such as `Read First`,
  `People & Brands`, `Products`, and `Source Structure`;
- factual row metrics such as article source and an uncapped safe-card count.

The section should be omitted when no safe facet rows can be built.

## Facet Classification

Signal Facets should reuse the same vocabulary already implied by the Reference
Atlas:

- brand facets come from references classified into the Reference Atlas
  `brands` bucket;
- product facets come from references classified into the Reference Atlas
  `products` bucket;
- people and source-context references are intentionally not rendered as Stage
  349 chips;
- theme facets come only from existing content-organization group titles, not
  from ad hoc card labels or new theme extraction.

The builder should dedupe facets case-insensitively while preserving first-seen
order. It should cap chips in each facet column so the matrix stays compact.
It should preserve content-organization group context while grouping cards by
detail path so group titles are available to the theme column.

## Safety And Caps

All visible article titles, source names, and facet names must be escaped. All
links must point only to existing safe local article/detail anchors. Unsafe
detail paths, outbound URLs, JavaScript URLs, traversal paths, invalid fragments,
empty labels, and duplicate chips should be filtered out.

The matrix should cap rows and chips to preserve scanability:

- up to six article rows;
- up to four chips each for brands, products, and themes;
- no full article body text;
- no source brief bullets copied into the matrix.

## Out Of Scope

Stage 349 does not add article downloading, social-platform collection,
external tool adapters, scraping, browser automation, platform APIs,
account/session behavior, extraction changes, LLM summaries, ranking,
recommendation, analytics, personalization, scheduling, deployment, app contract
changes, schema changes, new route families, or compliance-review product
behavior.

It also does not create `data/saved-article-signal-facets.json`,
`data/article-signal-facets.json`, `saved-article-signal-facets.html`, or any
new JSON/HTML artifact. Signal Facets are rendered only inside the generated
`articles/index.html` saved article library.

## Acceptance Criteria

- `articles/index.html` renders a `saved-article-signal-facets` section after
  the saved article daily summary and before Theme Digest when at least one safe
  facet row exists.
- Each row links only to safe same-site local article/detail anchors.
- Brand, product, and theme chips are escaped, deduped, capped, and preserve
  first-seen order.
- Empty or unsafe facet sets omit the Signal Facets shell.
- The feature does not appear on the homepage.
- No app-facing contract, schema, JSON artifact, route family, fetching,
  extraction, ranking, LLM, scheduling, deployment, or compliance-review product
  behavior changes.
- Documentation and workflow guards state the generated-site-only boundary for
  Stage 349.
