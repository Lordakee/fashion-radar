# Stage 352 ROW ONE Saved Article Reading Queue Design

## Objective

Stage 352 adds a generated-site-only Saved Article Reading Queue inside
`articles/index.html`. The queue turns the existing saved local article library
into a short, scan-first sequence of local article links so readers can start
with the most readable saved bodies before browsing the full source grid.

## Product Gap

Stages 346-351 improved the saved article library with body guides, source
routes, signal facets, daily signal rollups, and a navigation index. The page
still lacks a compact "what should I open next?" queue that uses only existing
local article metadata and safe local article/detail anchors.

The Reading Queue closes that gap as editorial navigation. It is not a ranking
model, recommendation system, market heat signal, analytics layer, or external
popularity signal.

## Architecture

This is a generated-site-only presentation feature:

- `src/fashion_radar/row_one/saved_article_reading_queue.py` builds a compact
  queue from `RowOneSavedArticleLibrary` only.
- Each queue item includes localized title, source name, body-source label,
  saved paragraph count, organized section count, and one safe local reading
  href.
- The builder keeps existing source/article order, filters unsafe links, and
  caps the queue to five items.
- `src/fashion_radar/row_one/templates.py` renders the queue inside
  `articles/index.html` after the Stage 351 Organization Jump Index and before
  Signal Facets.
- `src/fashion_radar/row_one/render.py` passes no new app-contract payloads and
  continues to write the feature only through the saved article library page.

The feature creates no schema, SQLite table, JSON artifact, route family,
collector, extraction path, ranking model, LLM call, scheduler, deployment,
app-facing contract field, analytics, personalization, recommendation, or
compliance-review product behavior.

## Rendering Behavior

When at least one safe queue item exists, Stage 352 renders a
`saved-article-reading-queue` section in `articles/index.html`.

Each item should show:

- article title;
- source name;
- body-source label such as `Extracted article text`, `ROW ONE summary
  fallback`, or `Skipped`;
- saved paragraph and organized section counts;
- a safe local article page link when available, otherwise a safe detail digest
  anchor.

The section is omitted when no safe queue item can be built. It should not
appear on the homepage or detail article pages.

## Data Sources

Stage 352 should reuse only `RowOneSavedArticleLibrary.groups` and existing
safe local article/detail anchors already represented by saved article library
entries. It should not inspect raw article text, raw references, source URLs,
imported signals, external search results, social platform data, downloaded
article HTML, or LLM output.

## Safety And Caps

All visible titles, source names, body-source labels, and counts must be escaped
by the template layer. Links must reuse existing safe local article page hrefs
or safe same-site detail digest anchors.

The canonical detail fallback form for `articles/index.html` is
`../details/<safe-detail-file>.html#local-article-digest`. That exact
page-relative same-site form is allowed. Other traversal, outbound URLs,
protocol-relative URLs, JavaScript URLs, whitespace-bearing hrefs, and empty
hrefs must be rejected.

Caps:

- up to five queue items;
- no full article body text;
- no source brief bullets;
- no copied article summaries;
- no outbound links.

## Out Of Scope

Stage 352 does not add article downloading, social-platform collection,
external tool adapters, scraping, browser automation, platform APIs,
account/session behavior, extraction changes, LLM summaries, ranking,
recommendation, analytics, personalization, scheduling, deployment, app
contract changes, schema changes, new route families, or compliance-review
product behavior.

It also does not create `data/saved-article-reading-queue.json`,
`data/article-reading-queue.json`, `saved-article-reading-queue.html`, or any
new JSON/HTML artifact.

## Acceptance Criteria

- `articles/index.html` renders a `saved-article-reading-queue` section after
  the Organization Jump Index and before Signal Facets when at least one safe
  queue item exists.
- Items preserve existing saved article library order instead of sorting by
  support counts, source counts, products, or themes.
- Items link only to safe local article page hrefs or safe same-site detail
  digest anchors.
- The template accepts canonical `../details/...#local-article-digest` fallback
  links and rejects all other traversal or outbound href forms.
- Empty or unsafe inputs omit the whole queue shell.
- Labels, titles, source names, body-source labels, and counts are escaped.
- The feature does not appear on the homepage or detail article pages.
- No app-facing contract, schema, JSON artifact, route family, fetching,
  extraction, ranking, LLM, scheduling, deployment, analytics, personalization,
  recommendation, or compliance-review product behavior changes.
- Documentation and workflow guards state the generated-site-only boundary for
  Stage 352.
