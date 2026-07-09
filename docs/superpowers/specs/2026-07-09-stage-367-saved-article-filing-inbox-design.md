# Stage 367 Saved Article Filing Inbox Design

## Objective

Stage 367 adds a generated-site-only **Saved Article Filing Inbox** to `articles/index.html`. The inbox aggregates unfiled saved paragraphs across the current ROW ONE saved article set so readers can find downloaded/local article content that has not yet been mapped into existing content sections.

## Why This Node

Stage 366 made filing status visible inside each first-class local article body. That helps after a reader opens one article, but it does not answer the library-level question: which saved paragraphs still need review because they are not attached to an organized content section?

The Saved Article Filing Inbox makes that remaining saved content discoverable from the article library. It is more valuable than another homepage strip because the gap is specifically about downloaded/saved article bodies, not the daily story feed. It is also more useful than another per-article navigator because article pages already have local reading companion, section binder, key signals, content segment deck, and body filing cues.

## Placement

Render the inbox only on `articles/index.html`.

Recommended placement:

- after the saved article organization jump index, when present.
- before reading queue and read-next clusters.
- before the main saved article source groups if no organization jump index is present.

Do not render it on:

- `index.html`
- `articles/<story-id>.html`
- `details/<story-id>.html`
- generated app/runtime/manifest JSON payloads
- any new route family or sidecar artifact

## Content Model

Add a small saved-article builder module:

- `src/fashion_radar/row_one/saved_article_filing_inbox.py`

The builder uses only:

- `RowOneEdition`
- current-edition `RowOneLocalArticle` sidecars already available in memory
- existing local article content-section item paragraph indices
- existing generated local article page hrefs

Each inbox row represents one saved article that has at least one unfiled nonblank paragraph. Each row includes:

- article title
- source name
- body-source label
- saved paragraph count
- organized section count
- unfiled paragraph count
- up to a capped number of unfiled paragraph links/excerpts

Each paragraph link points to:

- `articles/<story-id>.html#local-article-paragraph-N` when rendered from homepage context, or
- `<story-id>.html#local-article-paragraph-N` inside `articles/index.html`.

The rendered inbox in `articles/index.html` must use the relative article-library form:

- `<story-id>.html#local-article-paragraph-N`

## Filing Rules

A saved paragraph is filed when at least one valid content-section item references its zero-based paragraph index.

A saved paragraph is unfiled when:

- the paragraph text is nonblank, and
- its zero-based index is not referenced by any valid item-level `paragraph_indices`.

Validation must:

- ignore booleans.
- ignore strings.
- ignore negative indices.
- ignore overflow indices.
- ignore blank paragraph indices.
- dedupe repeated paragraph indices.
- preserve deterministic article/source order from existing saved article library ordering.

Do not access or invent `RowOneLocalArticleContentSection.paragraph_indices`; section-level paragraph indices do not exist in the current model.

## Safety and Limits

The inbox is capped to keep the library page compact:

- maximum article rows: 8
- maximum unfiled paragraph links per article: 3
- paragraph excerpt length: 140 characters

The builder must reject unsafe or missing article-page hrefs:

- no absolute URLs
- no protocol-relative URLs
- no `javascript:`
- no traversal paths
- no nested paths
- no whitespace
- no unsafe story IDs
- no malformed paragraph fragments

All rendered text must be escaped. The inbox must not render raw source HTML, raw script tags, or unsafe hrefs.

## Styling

Add scoped CSS under `.saved-article-filing-inbox`.

The section should feel like a compact editorial workbench:

- short header
- metrics row
- dense article rows
- paragraph chips/links with excerpts
- single-column mobile layout under existing responsive rules

Do not create a large card wall or another homepage-style hero block.

## Data Sources

Use only current generated-site render state:

- current edition stories
- current saved local article sidecars
- current local article page href map
- existing saved local article content sections and paragraph indices

No new database query, source collection, source fetch, extraction pass, matching pass, scoring pass, ranking pass, LLM call, connector, scheduler, deployment behavior, analytics behavior, recommendation behavior, personalization behavior, app-facing contract, schema, JSON artifact, or compliance-review behavior is introduced.

## Documentation and Guardrails

Document Stage 367 in `README.md` and `docs/row-one.md` before Stage 366.

Add tests that prove:

- article-library-only rendering.
- no homepage, first-class local article page, or detail-page rendering.
- no app/runtime/manifest contract leak.
- no JSON or HTML sidecar artifact.
- no compliance-review behavior.

## Non-Goals

- No `data/saved-article-filing-inbox.json`
- No `data/article-filing-inbox.json`
- No `data/filing-inbox.json`
- No app-facing payload field
- No schema/runtime/manifest version bump
- No new route
- No homepage section
- No local article page section
- No detail-page section
- No source collection, extraction, matching, scoring, ranking, LLM, connector, scheduler, deployment, analytics, personalization, recommendation, or compliance-review behavior

## Acceptance Criteria

- The builder returns an inbox only when at least one current saved local article has unfiled nonblank paragraphs and a safe local article page href.
- The builder preserves source/article order and caps article rows and paragraph links deterministically.
- `render_saved_article_library_html(...)` renders the inbox only on `articles/index.html`.
- Each inbox paragraph link points to an existing local article paragraph anchor.
- Unsafe hrefs, invalid paragraph indices, blank paragraphs, and duplicate paragraph references are filtered.
- The section is absent from homepage, detail pages, and `articles/<story-id>.html`.
- Generated contract payloads and generated artifacts do not contain Stage 367 names.
- Existing ROW ONE app contract versions remain unchanged.
- CSS selectors and responsive rules are covered by tests.
- Focused tests, full tests, lint, formatting, release hygiene, offline lock check, and diff check pass.
