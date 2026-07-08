# Stage 348 ROW ONE Saved Article Source Routes Design

## Objective

Stage 348 adds generated-site-only Saved Article Source Routes inside
`articles/index.html`. The routes give readers a compact set of source chips in
the daily saved article summary so they can jump directly to each source group
and its Source Brief.

## Product Gap

Stages 345 through 347 improved the saved article library with a daily
orientation layer, article body guides, and source-level briefs. The remaining
navigation gap is source discovery: the daily summary can link to broad
surfaces such as Theme Digest, Reference Atlas, Content Organization, and Source
Grid, but it cannot take a reader directly to "what Vogue Business contributed
today" or "what WWD contributed today."

Source Routes close that gap with source-level anchors and factual source
chips. They organize the existing local saved article set without repeating
article text, source brief bullets, ranking, or new data contracts.

## Architecture

This is a generated-site-only rendering change in
`src/fashion_radar/row_one/templates.py`:

- `render_saved_article_library_html(...)` should build a stable mapping from
  each rendered `RowOneSavedArticleLibrarySourceGroup` to a safe same-page
  anchor.
- `_render_saved_article_library_source(...)` should receive the anchor id and
  render it on the existing source `<section>`.
- `_render_saved_article_daily_summary(...)` should receive the same source
  route data and render a compact Source Routes row after the daily-summary
  metrics and before the broad surface links.

The route data should be derived only from the existing
`RowOneSavedArticleLibrary` source groups. It should not create a new model,
schema, JSON artifact, route family, or external link surface.

## Rendering Behavior

For each source group that has at least one entry, Stage 348 should render:

- a stable source group `id`, for example
  `saved-article-source-vogue-business`;
- a daily-summary Source Routes row with up to four safe chips;
- each chip should show the source name plus factual counts such as article
  count and saved paragraph count;
- each chip should link to the matching source group anchor;
- source routes should preserve existing library source group order.

The row should be omitted when no safe source route can be built.

## Safety And Caps

Source anchor ids must be deterministic and safe for same-page links. They
should be derived from source names after normalizing to lowercase
ASCII-compatible slugs, replacing unsupported characters with hyphens, trimming
empty output, and adding a stable numeric suffix for duplicate slugs.

All visible source route text must be escaped. Route hrefs must be same-page
fragment links only. Source Routes must not expose outbound article URLs,
unsafe detail paths, local article body text, source brief bullet text, or raw
source names inside hrefs.

The daily summary should cap source route chips to four source groups so the
top orientation block stays compact.

## Out Of Scope

Stage 348 does not add article downloading, social-platform collection,
external tool adapters, scraping, browser automation, platform APIs,
account/session behavior, extraction changes, LLM summaries, ranking,
recommendation, analytics, personalization, scheduling, deployment, app contract
changes, schema changes, new route families, or compliance-review product
behavior.

It also does not create `data/saved-article-source-routes.json`,
`data/source-routes.json`, `saved-article-source-routes.html`, or any new
JSON/HTML artifact. Source Routes are rendered only inside the generated
`articles/index.html` saved article library.

## Acceptance Criteria

- `articles/index.html` renders source group anchors for saved article source
  groups that have entries.
- The daily summary renders a `saved-article-source-routes` row after metrics
  and before broad surface links.
- Route chips link only to safe same-page source group anchors.
- Source route chips are escaped, capped, deduped by anchor, and preserve source
  group order.
- Empty or unsafe source route sets omit the Source Routes shell.
- The feature does not appear on the homepage.
- No app-facing contract, schema, JSON artifact, route family, fetching,
  extraction, ranking, LLM, scheduling, deployment, or compliance-review
  product behavior changes.
- Documentation and workflow guards state the generated-site-only boundary for
  Stage 348.
