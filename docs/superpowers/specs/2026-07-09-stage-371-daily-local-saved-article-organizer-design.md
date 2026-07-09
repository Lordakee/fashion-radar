# Stage 371 Daily Local Saved Article Organizer Design

## Goal

Add a generated-site-only ROW ONE homepage section that turns already-saved local article text into organized, readable editorial lanes. The section should help the reader understand what today's downloaded articles say without forcing them to open every source link first.

## User Value

The current site has strong route, signal, and source organization, but some homepage modules still behave like navigation surfaces. Stage 371 adds a content-first organizer: short article-backed excerpts, grouped by editorial use case, with same-site anchors for deeper reading.

## Product Shape

The new homepage section is named `Daily Local Saved Article Organizer` / `每日保存文章整理器`.

It renders in `index.html` after the Stage 370 `Daily Local Article Intelligence Brief` and before `Saved Article Content Organization`.

It contains up to four lanes:

1. `Read First` / `优先阅读`: the strongest available opening paragraph or local article brief body for each current-edition story.
2. `People & Brands` / `品牌与人物`: content-section items or references that explain brand, designer, celebrity, or person context.
3. `Products` / `单品`: content-section items or references for bags, shoes, apparel, accessories, and product-like references.
4. `Source Context` / `来源语境`: source-name and body-source oriented cards that explain where the saved local content came from without repeating the same excerpt emitted by `Read First`.

Each lane contains capped cards. A card includes:

- article title
- source name
- lane label
- a short excerpt from saved local article text, local article brief section, content-section body, or content-section item body
- reference chips when available
- a same-site href to `articles/<story-id>.html#local-article-content-section-N` or `articles/<story-id>.html#local-article-paragraph-N`

The homepage does not publish full articles. Excerpts are short and capped.

## Data Sources

Stage 371 reuses only existing current-edition data:

- `RowOneEdition.stories`
- `local_articles_by_story_id`
- generated local article page hrefs from `render_row_one_site`
- `RowOneLocalArticle.paragraphs`
- `RowOneLocalArticle.paragraphs_zh`
- `RowOneLocalArticle.brief_sections`
- `RowOneLocalArticle.content_sections`
- `RowOneLocalArticleContentSection.items`
- item references and valid item-level paragraph indices
- existing local article content-section and paragraph anchors

It does not call source collection, fetching, matching, extraction, scoring, ranking, LLMs, connectors, scheduling, deployment, analytics, personalization, recommendation, or compliance-review code.

## Builder Contract

Create `src/fashion_radar/row_one/daily_local_saved_article_organizer.py`.

The builder returns `RowOneDailyLocalSavedArticleOrganizer | None`.

Suggested constants:

- `DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_LANES = 4`
- `DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE = 3`
- `DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD = 4`
- `DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS = 180`

Suggested dataclasses:

- `RowOneDailyLocalSavedArticleOrganizerReference`
- `RowOneDailyLocalSavedArticleOrganizerCard`
- `RowOneDailyLocalSavedArticleOrganizerLane`
- `RowOneDailyLocalSavedArticleOrganizer`

The builder should:

- iterate current-edition stories in edition order
- require safe story ids and matching local article sidecars
- require safe generated page hrefs for the same story id
- create lane cards from existing local article content only
- validate paragraph indices before using them, ignoring invalid indices and allowing valid indexed paragraphs to provide fallback excerpts when an item body is empty
- prefer same-site content-section anchors for content-section cards
- fall back to same-site paragraph anchors for paragraph/brief/source-context cards only when the target paragraph anchor exists
- omit label-only content-section items when there is no item body, no valid paragraph-index fallback, and no section body
- dedupe cards by lane and href
- cap cards per lane
- omit empty lanes
- return `None` if no lane has cards

## Rendering Contract

`render_index_html()` gets an optional `daily_local_saved_article_organizer` argument.

Template helpers render:

- section header
- metrics: lane count, card count, source count, reference count
- lane grid
- cards with excerpt text and reference chips

All user-derived text is escaped. Render-time href validation must accept only:

- path: `articles/<safe-story-id>.html`
- fragment: `local-article-content-section-N` or `local-article-paragraph-N`
- `N >= 1`

Render-time validation must reject whitespace, traversal, absolute paths, protocol URLs, `//`, empty fragments, and zero-valued anchors.

## Site Integration

`render_row_one_site()` builds the organizer after local article page href maps exist and passes it only to the homepage renderer.

Stage 371 does not write:

- `data/daily-local-saved-article-organizer.json`
- `data/local-saved-article-organizer.json`
- `data/saved-article-organizer.json`
- `daily-local-saved-article-organizer.html`
- `local-saved-article-organizer.html`
- `saved-article-organizer.html`

It does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages.

## Documentation Boundary Paragraph

Stage 371 adds generated-site only Daily Local Saved Article Organizer inside `index.html` between the Daily Local Article Intelligence Brief and Saved Article Content Organization; it reuses current-edition stories, current-edition saved local article sidecars, generated local article page routes, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing content-section item bodies, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to organize today's saved articles into short homepage editorial lanes with article-backed excerpts, reference chips, and same-site reader anchors without changing app-facing contracts; it does not create `data/daily-local-saved-article-organizer.json`, does not create `data/local-saved-article-organizer.json`, does not create `data/saved-article-organizer.json`, does not create `daily-local-saved-article-organizer.html`, does not create `local-saved-article-organizer.html`, does not create `saved-article-organizer.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

## Tests

Builder tests should prove:

- lanes are built from saved local article text and content-section items
- invalid story ids, mismatched sidecars, unsafe page hrefs, invalid paragraph indices, and empty content are filtered
- caps and deterministic ordering hold
- no full article body appears in the organizer representation

Render tests should prove:

- homepage includes the section when given a fixture
- HTML escapes title, source, excerpt, and reference chips
- unsafe hrefs are filtered
- section placement is after Stage 370 and before Saved Article Content Organization
- `render_row_one_site()` writes it only on `index.html`
- article/library/detail pages do not contain the section
- data contract payloads do not contain Stage 371 names
- no Stage 371 JSON/HTML artifacts are written
- CSS selectors and mobile collapse rules exist

Docs/workflow tests should prove:

- README and docs/row-one include the exact Stage 371 paragraph before Stage 370
- stale boundary phrases are absent
- app contract denylist includes Stage 371 names
- artifact stem denylist includes Stage 371 stems
- a wrapper guard proves generated-site-only behavior

## Out of Scope

Stage 371 does not add social platform connectors, source acquisition, crawling, fetch scheduling, LLM summarization, recommendation logic, analytics, app UI, deployment, image generation, article-page redesign, or compliance-review behavior.
