# Stage 372 Daily Local Reading Itinerary Design

## Goal

Add a generated-site-only ROW ONE homepage section that turns today's saved local article content into a compact, ordered reading path. The section should answer "what should I read first, skim next, and use as evidence" without forcing the reader to assemble the path from multiple existing modules.

## User Value

ROW ONE now saves article bodies locally and renders many article-backed homepage organizers. The remaining gap is sequence. A reader can see lanes, signals, source desks, and content organization, but the homepage still lacks a single short "start here" itinerary that explains the best order to consume today's local material.

Stage 372 adds that sequence. It keeps the site content-first, local, and lightweight by reusing existing saved article text and generated article anchors. It does not add recommendation infrastructure or app-facing payloads.

## Product Shape

The new homepage section is named `Daily Local Reading Itinerary` / `每日本地阅读路径`.

It renders in `index.html` after Stage 371 `Daily Local Saved Article Organizer` and before `Saved Article Content Organization`.

It contains three capped groups:

1. `Start Here` / `先读这篇`: one strongest current-edition saved local article with a short reason and same-site anchor.
2. `Skim Next` / `随后快读`: up to four article-backed cards that expose different reasons to continue reading, such as brand signal, product signal, source context, designer/person signal, or theme.
3. `Evidence Trail` / `证据路径`: up to six compact chips linking to existing generated article anchors for paragraph or content-section evidence.

Each itinerary card includes:

- article title
- source name
- reason label
- a short article-backed excerpt
- same-site href to an existing generated local article page anchor
- optional coverage labels derived from existing content-section item references or source context

The homepage must not publish full article bodies. Excerpts are capped and should be short enough for a homepage reading guide.

## Data Sources

Stage 372 reuses only current-edition generated-site data:

- `RowOneEdition.stories`
- `local_articles_by_story_id`
- generated local article page hrefs from `render_row_one_site`
- `RowOneLocalArticle.title`
- `RowOneLocalArticle.source_name`
- `RowOneLocalArticle.paragraphs`
- `RowOneLocalArticle.paragraphs_zh`
- `RowOneLocalArticle.brief_sections`
- `RowOneLocalArticle.content_sections`
- `RowOneLocalArticleContentSection.items`
- item references and valid item-level paragraph indices
- existing local article paragraph anchors
- existing local article content-section anchors

It does not call source collection, fetching, matching, extraction, scoring, ranking, LLMs, connectors, scheduling, deployment, analytics, personalization, recommendation, or compliance-review code.

## Builder Contract

Create `src/fashion_radar/row_one/daily_local_reading_itinerary.py`.

The builder returns `RowOneDailyLocalReadingItinerary | None`.

Suggested constants:

- `DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS = 4`
- `DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS = 6`
- `DAILY_LOCAL_READING_ITINERARY_MAX_LABELS_PER_CARD = 4`
- `DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS = 170`

Suggested dataclasses:

- `RowOneDailyLocalReadingItineraryCard`
- `RowOneDailyLocalReadingItineraryEvidence`
- `RowOneDailyLocalReadingItinerary`

The builder should:

- iterate current-edition stories in edition order
- require safe story ids and matching local article sidecars
- require safe generated page hrefs for the same story id
- build candidates only from existing local article content
- define `_first_paragraph_anchor(article, page_href) -> str | None` as the full same-site href for the first non-empty paragraph, or `None` when no non-empty paragraph exists
- choose the first valid `Start Here` card from a brief section body when `_first_paragraph_anchor(article, page_href)` returns a safe href
- fall back to the first non-empty paragraph when no anchored brief section is usable
- build `Skim Next` cards from content-section items with item body, valid indexed paragraph fallback, or section body
- link paragraph-index fallback cards to the content-section anchor for the containing section, not to the paragraph anchor
- map product-like references and product content-section families to reason label `Product signal`
- map brand, designer, celebrity, person, and entity-like references or content-section families to `Brand / people signal`
- emit one `Source context` card per article when a paragraph anchor exists, regardless of whether Brand/Product cards were also emitted for that article
- build `Source context` excerpts from source name, `body_source`, and paragraph-count metadata rather than repeating the raw `Start Here` paragraph text
- use only valid paragraph indices, ignoring bools, negative indices, out-of-range indices, duplicate indices, and blank paragraphs
- omit label-only content-section items when there is no item body, no valid paragraph fallback, and no section body
- dedupe cards by the `(href, normalized reason label)` tuple across `Start Here` and `Skim Next`
- compute `selected_count` as the number of unique story ids represented across the rendered `Start Here` and `Skim Next` cards
- compute `source_count` as the number of unique source names represented across the rendered `Start Here` and `Skim Next` cards
- compute `evidence_count` as `len(evidence_trail)`
- cap `Skim Next`, evidence chips, labels, and excerpts
- return `None` when no usable `Start Here` or `Skim Next` content exists

## Rendering Contract

`render_index_html()` gets an optional `daily_local_reading_itinerary` argument.

Template helpers render:

- section header
- dek
- metrics: selected read count, source count, evidence count
- `Start Here` article card
- `Skim Next` compact cards
- `Evidence Trail` chips

All user-derived text is escaped. Render-time href validation must accept only:

- path: `articles/<safe-story-id>.html`
- fragment: `local-article-content-section-N` or `local-article-paragraph-N`
- `N >= 1`

Render-time validation must reject whitespace, traversal, absolute paths, protocol URLs, `//`, empty fragments, and zero-valued anchors.

The template must render nothing when the builder returns `None`, when all cards have unsafe hrefs, or when the section has no article-backed content after render-time filtering.

Evidence chip labels are generated from the best available article-backed label in this order: reference name, content-section item label, content-section title, article title, then paragraph label such as `Paragraph 1`.

## Site Integration

`render_row_one_site()` builds the itinerary after local article page href maps exist and passes it only to the homepage renderer.

Stage 372 does not write:

- `data/daily-local-reading-itinerary.json`
- `data/local-reading-itinerary.json`
- `data/reading-itinerary.json`
- `daily-local-reading-itinerary.html`
- `local-reading-itinerary.html`
- `reading-itinerary.html`

It does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages.

## Documentation Boundary Paragraph

Stage 372 adds generated-site only Daily Local Reading Itinerary inside `index.html` between the Daily Local Saved Article Organizer and Saved Article Content Organization; it reuses current-edition stories, current-edition saved local article sidecars, generated local article page routes, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing content-section item bodies, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to arrange today's saved articles into a short Start Here, Skim Next, and Evidence Trail reading sequence with article-backed excerpts, reason labels, and same-site reader anchors without changing app-facing contracts; it does not create `data/daily-local-reading-itinerary.json`, does not create `data/local-reading-itinerary.json`, does not create `data/reading-itinerary.json`, does not create `daily-local-reading-itinerary.html`, does not create `local-reading-itinerary.html`, does not create `reading-itinerary.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

## Tests

Builder tests should prove:

- the itinerary builds `Start Here`, `Skim Next`, and `Evidence Trail` from saved local article text
- invalid story ids, mismatched sidecars, unsafe page hrefs, invalid paragraph indices, and empty content are filtered
- label-only content-section items are omitted
- caps, dedupe, deterministic ordering, and excerpt truncation hold
- the representation does not contain full article bodies

Render tests should prove:

- homepage includes the section when given a fixture
- HTML escapes title, source, reason, excerpt, labels, and evidence chips
- unsafe hrefs are filtered
- section placement is after Stage 371 and before Saved Article Content Organization
- `render_row_one_site()` writes it only on `index.html`
- article/library/detail pages do not contain the section
- data contract payloads do not contain Stage 372 names
- no Stage 372 JSON/HTML artifacts are written
- CSS selectors and mobile collapse rules exist

Docs/workflow tests should prove:

- README and docs/row-one include the exact Stage 372 paragraph before Stage 371
- stale boundary phrases are absent
- app contract denylist includes Stage 372 names
- artifact stem denylist includes Stage 372 stems
- a wrapper guard proves generated-site-only behavior

## Out of Scope

Stage 372 does not add social platform connectors, source acquisition, crawling, fetch scheduling, LLM summarization, recommendation logic, analytics, app UI, deployment, image generation, article-page redesign, or compliance-review behavior.
