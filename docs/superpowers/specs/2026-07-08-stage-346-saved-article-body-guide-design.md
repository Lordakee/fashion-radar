# Stage 346 ROW ONE Saved Article Body Guide Design

## Objective

Stage 346 adds a generated-site-only Saved Article Body Guide to each saved
article card in `articles/index.html`. The guide turns already-saved local
article text into two concise reading bullets per article, so readers can see
what the locally saved body actually says before opening the article page.

## Product Gap

ROW ONE now has a strong saved-article library surface: daily orientation,
theme digest, reference atlas, signal index, reading paths, evidence board,
content organization, group summaries, coverage matrix, and local article
pages. Those modules organize links and evidence well, but the source cards in
the saved article library still behave mostly like route cards. A reader needs
brief body-level guidance inside each card: the most useful saved paragraphs or
content-section points, with a safe jump into the local article text.

The body guide closes that gap without adding a new dashboard, new data
artifact, or another top-level section. It is a small per-card information layer
that summarizes the saved local body from existing local article content.

## Architecture

This is a generated-site-only rendering change in
`src/fashion_radar/row_one/templates.py`. It should not modify models,
builders, schemas, JSON contracts, fetching, extraction, ranking, scheduling,
deployment, connectors, social-platform adapters, LLM behavior, or compliance
features.

The implementation should:

- build a private body-guide lookup inside `render_saved_article_library_html()`;
- derive guide candidates from existing
  `RowOneSavedArticleContentOrganizationCard` objects produced from local
  article `content_sections` and saved paragraph indices;
- reshape the existing per-card organized snippet surface into a
  `saved-article-body-guide` surface instead of adding a second parallel block;
- render at most two guide bullets inside each `saved-article-library-card`;
- reuse the existing safe detail-path and local paragraph href validation
  helpers;
- escape all text and keep excerpts capped;
- omit the guide shell when no usable local body-guide text exists.

## Rendering Behavior

For each saved article card, the guide should render a small bilingual block in
the existing organized-snippet slot before references/paragraph links.
Each guide item should include:

- a short section label, such as `Read First`, `People & Brands`, or
  `Products`;
- a concise excerpt derived from existing content-section item body or saved
  paragraph text;
- an optional safe paragraph link when the source card has a valid local
  paragraph index.

The guide is an information layer, not a navigation-only module. The text must
be the main value; links only provide traceability into the local article body.

## Sanitization And Caps

All guide text must be escaped. Guide candidates must be deduped per article and
capped to two items. Long body text must be shortened with the existing local
article excerpt helper so full article bodies do not get duplicated into
`articles/index.html`.

Guide links must be generated only from already-validated detail paths and
strict saved paragraph indices. Unsafe paths, unsafe fragments, traversal,
`javascript:` hrefs, boolean paragraph indices, negative indices, and oversized
indices must not render.

## Out Of Scope

Stage 346 does not add a new `articles/content-organization.html` page, new JSON
artifacts, app contract keys, schemas, new route families, source collection,
article downloading, scraping, browser automation, social-platform APIs,
account/cookie/session credential behavior, new extraction, LLM summaries, ranking,
recommendation, analytics, personalization, deployment changes, scheduling
changes, or compliance-review product features.

It also must not duplicate the existing per-card organized snippets as a second
body text block, nor duplicate Theme Digest, Reference Atlas, Evidence Board,
Content Organization, Organization Coverage Matrix, or Daily Summary content as
a new top-level section. The change stays inside existing saved article cards.

## Acceptance Criteria

- `articles/index.html` renders a `saved-article-body-guide` block in the
  existing per-card organized-snippet slot when existing saved local content
  provides usable guide text.
- Each card renders no more than two guide items, and long guide text is
  truncated.
- Guide content is escaped, deduped, and sourced only from existing saved local
  article content.
- Guide links point only to safe local paragraph anchors or are omitted.
- Empty guide shells do not render.
- The feature remains generated-site-only: no app-facing contract keys, schemas,
  route families, data artifacts, fetching, ranking, LLM, or deployment behavior
  changes.
- Documentation states the generated-site-only boundary for Stage 346.
