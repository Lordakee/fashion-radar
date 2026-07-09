# Stage 370 Daily Local Article Intelligence Brief Design

## Objective

Stage 370 adds a generated-site-only Daily Local Article Intelligence Brief to
the ROW ONE homepage. The section turns already-saved current-edition local
article bodies into a concise daily reading layer so the homepage explains what
today's downloaded articles collectively signal, instead of only offering
article links or per-article sections.

## Placement

Render the section inside `index.html` after Daily Local Theme Summary Strip and
before Saved Article Content Organization. This keeps the homepage flow ordered
from daily signal summaries into a concise cross-article brief, then into the
larger saved-article organization surface.

## Inputs

The feature reuses only current generated-site inputs:

- current `RowOneEdition.stories`
- matching current-edition `RowOneLocalArticle` sidecars
- Stage 369 `build_row_one_local_article_intelligence_brief`
- existing generated local article page hrefs
- existing paragraph anchors and content-section anchors
- existing story references and local article source names

It does not collect sources, fetch article pages, call LLMs, create connectors,
read historical data, or introduce new app payload fields.

## Output

The homepage section presents:

- **Opening Read**: one short daily thesis from the strongest local article
  opening signals.
- **Signal Lanes**: capped chips for brands, products, people, and themes found
  across saved local articles.
- **Article Cards**: capped same-site links into local article pages, each with
  source, opening signal, local evidence count, and a primary href set to the
  first safe paragraph or content-section route.
- **Reader Route**: same-site links to local article pages and anchors only.

The rendered section is bilingual where current model text is bilingual. It must
escape all text and accept only same-site `articles/<story-id>.html#fragment`
links where the source page href validates as the bare generated filename
`<story-id>.html`, the final homepage href prepends `articles/`, and `fragment`
matches `local-article-paragraph-N` or `local-article-content-section-N` with
1-based positive integers.

## Scope Boundaries

Stage 370 is homepage-only and generated-site-only.

It must not:

- create `data/daily-local-article-intelligence-brief.json`
- create `data/local-article-intelligence-brief.json`
- create `data/article-intelligence-brief.json`
- create `daily-local-article-intelligence-brief.html`
- create `local-article-intelligence-brief.html`
- create `article-intelligence-brief.html`
- alter `articles/index.html`, `articles/<story-id>.html`, or detail pages
- publish full article bodies on the homepage
- add outbound article URLs as primary navigation
- change `row-one-app/v7`, `row-one-manifest/v1`, or `row-one-runtime/v1`
- change schemas, JSON artifacts, source collection, fetching, matching,
  extraction, scoring, ranking, LLM, connector, scheduling, deployment, market
  grouping, domestic/international classification, analytics, personalization,
  recommendation, or compliance-review behavior

## Builder Shape

Create a small focused builder module:

`src/fashion_radar/row_one/daily_local_article_intelligence_brief.py`

The builder returns `None` when no saved local article can produce a Stage 369
brief or no safe local article href exists. Otherwise it returns a dataclass
with:

- title: localized section label
- opening_signal: localized daily thesis
- metrics: article count, source count, signal count, evidence count
- lanes: capped lane summaries by brands/products/people/themes
- articles: capped article cards with source, title, opening signal, safe
  primary href, evidence count, and safe anchor routes

Sorting is deterministic:

1. stories stay in current edition order for article-card eligibility.
2. lane chips sort by support count descending, then first seen story order, then
   normalized label.
3. articles cap in edition order.

`signal_count` is the sum of aggregate lane `total_count` values after all
eligible per-article Stage 369 briefs are merged. `evidence_count` is the sum of
`len(brief.evidence)` across all included per-article Stage 369 briefs.
Article primary hrefs are never bare article-page links; they use the first safe
converted Stage 369 route, such as
`articles/<story-id>.html#local-article-content-section-1` or
`articles/<story-id>.html#local-article-paragraph-1`.

## Rendering

`render_index_html()` accepts an optional
`daily_local_article_intelligence_brief` value. `render_row_one_site()` builds
that value after local article page specs are available, because the homepage
section needs generated local article page hrefs.

The section uses class prefix
`.daily-local-article-intelligence-brief` and follows the existing homepage
section style: header, metrics row, lane grid, card grid, and mobile one-column
rules.

## Tests

Add TDD coverage for:

- builder summarizes multiple local article Stage 369 briefs
- builder filters mismatched story IDs, unsafe story IDs, missing article hrefs,
  invalid fragments, and blank bodies
- builder caps lanes, chips, articles, and routes deterministically
- homepage render places the section after Daily Local Theme Summary Strip and
  before Saved Article Content Organization
- generated site writes the section only to `index.html`
- app contracts and generated artifacts do not include Stage 370 names
- CSS includes desktop and mobile selectors
- docs describe exact Stage 370 generated-site boundary
- workflow guard keeps Stage 370 out of app contracts and artifacts

## Review Notes

The implementation should reuse Stage 369's per-article brief builder rather
than re-parsing local articles independently. If the Stage 369 builder returns
`None` for an article, Stage 370 should skip it.
