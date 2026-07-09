# Stage 365 Local Article Content Segment Deck Design

## Objective

Stage 365 adds a generated-site-only **Local Article Content Segment Deck** to each first-class ROW ONE local article page at `articles/<story-id>.html`. The deck turns already-saved `RowOneLocalArticle.content_sections` into compact publish-page content cards so the page reads like a professional local fashion-news article before the full saved body.

## Why This Node

The current ROW ONE pipeline already downloads or generates local saved article text, writes first-class local article pages, and adds several scan aids. The user has asked to prioritize the content section itself: the website should show locally saved article content, not just links or external reading paths. This node strengthens the article page surface without adding collection, extraction, model calls, schema changes, or app-facing contracts.

## Placement

Render the deck only on `articles/<story-id>.html`.

Place it after Stage 356 `Saved Article Key Signals` when that section exists and before the full saved local article body (`id="local-article"`). If key signals are absent, place it after the existing Stage 355 `Saved Article Local Section Binder` or the last available local-article pre-body block and still before `id="local-article"`.

The deck must not render on:

- `index.html`
- `articles/index.html`
- `details/<story-id>.html`
- generated app/runtime/manifest JSON payloads

## Data Sources

Use only existing in-memory render data already available to `render_local_article_page_html(...)`:

- `RowOneLocalArticle.content_sections`
- `RowOneLocalArticleContentSection.title`
- optional section body
- section items, item labels, item bodies, item references, and paragraph indices
- already-rendered saved local article paragraph anchors
- existing content-section anchors
- existing local article source name and body-source labels

No new database query, collector, source fetch, LLM call, scoring pass, scheduler, deployment behavior, analytics behavior, recommendation behavior, or compliance-review behavior is introduced.

## Content Model

The deck is a render-only private view model derived in `templates.py`.

Each eligible content section becomes one segment card with:

- bilingual section title
- compact section body excerpt when present
- up to a small capped list of item rows
- each item row with bilingual label, compact item-body excerpt, capped reference chips, and capped paragraph links
- a section action linking to the already-rendered `#local-article-content-section-N`

Paragraph links point only to existing local article paragraph anchors using the current `_strict_valid_local_article_paragraph_indices(...)` and `_local_article_rendered_paragraph_indices(...)` patterns. If a section has no valid item paragraph index but has renderable content, the section card may still link to its content-section anchor. The deck should not duplicate the full saved article body.

## Caps and Omission Rules

Use deterministic caps to keep article pages readable:

- maximum segment cards: 4
- maximum items per segment: 3
- maximum references per segment: 5
- maximum paragraph links per item/segment: 3
- body/item excerpt length: short meta-style excerpt, not full body text

Omit the entire deck when there are no eligible content sections or no rendered saved local paragraphs. Omit an item row when it has no label, excerpt, reference, paragraph link, or useful content. Do not emit empty wrappers.

## Safety and Escaping

All data-derived text must be normalized and escaped with existing helpers. Links must be same-page anchors only:

- `#local-article-content-section-N`
- `#local-article-paragraph-N`

Do not accept outbound URLs, relative file paths, traversal paths, JavaScript URLs, malformed anchors, zero paragraph anchors, or leading-zero section anchors. Reuse existing local anchor and paragraph-index helper patterns instead of introducing a separate URL validator.

## Styling

Add scoped CSS selectors under `.local-article-content-segment-deck`. The deck should feel like a high-end editorial content block:

- restrained typography
- compact section cards
- reference chips
- paragraph/action links
- responsive single-column behavior on mobile

Do not restructure the page or create a new visual system.

## Documentation and Guardrails

Document Stage 365 in `README.md` and `docs/row-one.md` before Stage 364. The docs must say this is generated-site-only, article-page-only, and uses existing saved local article content sections.

Add workflow and documentation guards so future changes do not convert this into:

- an app contract field
- a schema version change
- a JSON artifact
- a new route family
- homepage/library/detail-page feature
- fetch/extraction/scoring/ranking/LLM/scheduling/analytics/recommendation/compliance-review feature

## Non-Goals

- No `data/local-article-content-segment-deck.json`
- No `data/article-content-segment-deck.json`
- No `data/content-segment-deck.json`
- No app-facing payload field
- No schema/runtime/manifest version bump
- No new route
- No homepage section
- No article library section
- No detail-page section
- No source collection, extraction, matching, scoring, ranking, LLM, connector, scheduler, deployment, analytics, personalization, recommendation, or compliance-review behavior

## Acceptance Criteria

- `render_local_article_page_html(...)` renders the deck for an article with eligible content sections.
- The deck appears before `id="local-article"`.
- Existing Stage 354/355/356 ordering remains intact.
- Unsafe or invalid anchors and paragraph indices are filtered.
- HTML escaping prevents raw hostile text from rendering.
- Site generation writes the deck only to `articles/<story-id>.html`.
- Contract JSON and generated artifacts do not contain Stage 365 names.
- Focused tests, full tests, lint, formatting, release hygiene, offline lock check, and diff check pass.
