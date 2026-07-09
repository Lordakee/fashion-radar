# Stage 368 Local Article Body Organizer Design

## Objective

Stage 368 adds a generated-site-only **Local Article Body Organizer** to each first-class ROW ONE local article page at `articles/<story-id>.html`. The organizer turns already-saved local article body paragraphs into a compact article-level filing view so readers can understand which paragraphs are already attached to existing content sections and which saved paragraphs remain unfiled.

## Why This Node

Stage 367 made unfiled saved paragraphs discoverable from `articles/index.html`, but the library-level inbox only tells readers where unfiled text exists. Once a reader opens a saved article, there is still no single article-level surface that summarizes filed paragraphs, unfiled paragraphs, saved-body coverage, and a concise read-first route through the downloaded/local text.

The Local Article Body Organizer closes that content整理 gap without adding new collection or app-facing behavior. It reuses the local article body, existing content-section item paragraph indices, existing same-page section anchors, and existing paragraph anchors. It is deliberately a compact body-level organizer, not another homepage section and not a replacement for the existing reader, content segment deck, key signals, section binder, or inline filing cues.

## Placement

Render the organizer only on first-class local article pages:

- `articles/<story-id>.html`

Recommended placement:

- between the local article content segment deck and the saved local article
  body.
- after Saved Article Key Signals, because the current first-class local article
  page template renders Saved Article Key Signals before the content segment
  deck.
- omit entirely when there is no meaningful body organization surface to show.

Do not render it on:

- `index.html`
- `articles/index.html`
- `details/<story-id>.html`
- generated app/runtime/manifest JSON payloads
- any new route family or sidecar artifact

## Content Model

Add a small generated-site-only builder module:

- `src/fashion_radar/row_one/saved_article_body_organizer.py`

The builder uses only:

- the current `RowOneStory`
- the matching current-edition `RowOneLocalArticle`
- existing `RowOneLocalArticle.content_sections`
- existing content-section item-level `paragraph_indices`
- existing saved local article paragraphs and optional aligned `paragraphs_zh`

Each organizer includes:

- article title
- source name
- saved paragraph count
- filed paragraph count
- unfiled paragraph count
- organized section count
- a capped read-first paragraph route in original paragraph order
- filed section rows grouped by existing content sections/items
- a capped unfiled paragraph queue

The read-first route is intentionally separate from the existing saved text
digest "Read First" card. The organizer route is a body filing/navigation lane
near the saved article body, while the digest card remains part of the broader
local article digest. Renderer tests must keep their CSS classes distinct.

Each filed section row includes:

- existing content-section title
- same-page section anchor: `#local-article-content-section-N`
- capped item labels or section/body support text when present
- capped paragraph links/excerpts for valid item-level paragraph references

`section_position` is derived by enumerating `local_article.content_sections`
with `start=1`, matching the existing rendered
`id="local-article-content-section-N"` anchors.

Each paragraph link points only to:

- `#local-article-paragraph-N`

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
- dedupe repeated paragraph indices within each row and globally where needed.
- preserve deterministic section order and paragraph order from the article.

Do not access or invent `RowOneLocalArticleContentSection.paragraph_indices`; section-level paragraph indices do not exist in the current model.

Stage 368 intentionally keeps paragraph-index helper logic local to the new
builder, with an inline comment pointing to the Stage 367 filing inbox sibling.
Stage 368 implementation also adds a reciprocal comment near the Stage 367
helper so future changes keep both validation paths aligned. The validation
semantics must stay aligned with Stage 367, while Stage 368 keeps ordered tuple
output for article-body routing and section row rendering.

## Safety and Limits

The organizer is capped to keep article pages readable:

- maximum filed section rows: 5
- maximum item labels per section row: 3
- maximum paragraph links per section row: 3
- maximum unfiled paragraph rows: 4
- maximum read-first route links: 5
- paragraph excerpt length: 150 characters
- support text excerpt length: 120 characters

The builder should return `None` when:

- the story id does not match the local article story id.
- the story id is not a safe local article story id.
- the article has no nonblank saved paragraphs.
- the article has no filed rows and no unfiled rows.

All renderer output must be escaped. The organizer must not render raw source HTML, raw script tags, external URLs, traversal paths, JavaScript URLs, malformed paragraph fragments, or malformed content-section fragments.

## Styling

Add scoped CSS under `.local-article-body-organizer`.

The section should feel like a compact editorial workbench:

- short header and summary metrics
- filed section rows
- paragraph route chips
- unfiled paragraph queue
- single-column mobile layout under existing responsive rules

Do not create a large card wall, homepage-style hero, or visual redesign.

## Data Sources

Use only current generated-site render state:

- current edition story
- current saved local article sidecar already passed to rendering
- existing saved local article content sections and paragraph indices
- existing saved local article paragraphs and anchors

No new database query, source collection, source fetch, extraction pass, matching pass, scoring pass, ranking pass, LLM call, connector, scheduler, deployment behavior, analytics behavior, recommendation behavior, personalization behavior, app-facing contract, schema, JSON artifact, or compliance-review behavior is introduced.

## Documentation and Guardrails

Document Stage 368 in `README.md` and `docs/row-one.md` before Stage 367.

Add tests that prove:

- local-article-page-only rendering.
- no homepage, saved article library, or detail-page rendering.
- no app/runtime/manifest contract leak.
- no JSON or HTML sidecar artifact.
- no compliance-review behavior.

## Non-Goals

- No `data/local-article-body-organizer.json`
- No `data/article-body-organizer.json`
- No `data/body-organizer.json`
- No `local-article-body-organizer.html`
- No `article-body-organizer.html`
- No `body-organizer.html`
- No app-facing payload field
- No schema/runtime/manifest version bump
- No new route
- No homepage section
- No saved article library section
- No detail-page section
- No source collection, extraction, matching, scoring, ranking, LLM, connector, scheduler, deployment, analytics, personalization, recommendation, or compliance-review behavior

## Acceptance Criteria

- The builder returns an organizer only when a current saved local article has nonblank paragraphs and meaningful filed or unfiled body organization.
- The builder preserves section order and paragraph order while capping rows deterministically.
- Invalid paragraph indices, blank paragraphs, duplicate references, and malformed inputs are filtered.
- The renderer emits the organizer only inside `articles/<story-id>.html`.
- Each paragraph link points to an existing same-page local article paragraph anchor.
- Each section link points to an existing same-page local article content-section anchor.
- The section is absent from homepage, `articles/index.html`, and detail pages.
- Generated contract payloads and generated artifacts do not contain Stage 368 names.
- Existing ROW ONE app contract versions remain unchanged.
- CSS selectors and responsive rules are covered by tests.
- Focused tests, full tests, lint, formatting, release hygiene, offline lock check, and diff check pass.
