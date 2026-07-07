# Stage 327 ROW ONE Saved Signal Index Design

## Goal

Add a generated-site only Saved Signal Index to ROW ONE so readers can browse
today's locally saved fashion information by the brands, people, designers, and
products already identified inside saved article content sections.

## User Value

Stage 326 made one daily saved article library available at `articles/index.html`,
but that page is primarily organized by source. The next information-organization
gap is cross-article topical access: a reader should be able to ask "where does
today's edition mention The Row, Alaia, Margaux, this designer, this celebrity,
or this shoe?" without opening every article card.

Stage 327 adds an index layer inside the existing generated article library:

- A reader can scan the current edition's saved local article signals by
  reference name.
- Each signal card shows whether the reference is a brand, designer, person,
  bag, shoe, product, or other existing reference type.
- Supporting rows show the ROW ONE story, source, article section context, and
  links into existing local article section and paragraph anchors.
- The feature strengthens local content organization without creating a new
  data contract, new sidecar file, new fetcher, new ranking model, or app
  surface.

## Design Read

This should feel like a fashion newsroom signal desk embedded inside the saved
article library. It is not a trend scoreboard. It should use restrained editorial
language: "saved signals", "supporting saved articles", "paragraph links", and
"current edition". Dial values: design variance 4, motion intensity 1, visual
density 7. The page should remain scan-first and mobile-safe.

## Scope

- Generated ROW ONE HTML/CSS only.
- Extend the existing generated page at `articles/index.html`.
- Add a Saved Signal Index section after the saved article library hero and
  before the source-grouped article list.
- Optionally adjust the existing homepage article-library entry copy so it says
  readers can browse by signals or sources.
- Use only existing data available during `render_row_one_site()`:
  - `RowOneEdition`
  - `RowOneStory`
  - `RowOneLocalArticle`
  - `RowOneLocalArticle.content_sections`
  - `RowOneLocalArticleContentSection.title`
  - `RowOneLocalArticleContentItem.references`
  - `RowOneLocalArticleContentItem.paragraph_indices`
  - existing detail paths and existing local article anchors
- Add a private render/build helper module for the saved signal index.
- Add CSS selectors to the existing `row-one.css` output.
- Add tests and documentation for generated-site-only behavior.
- Build strictly from the current in-memory `edition.stories` and
  `local_articles_by_story_id` passed to `render_row_one_site()`. Do not scan
  `output_dir`, `data/articles/*.json`, or persisted sidecar files while
  rendering the index.

## Non-Goals

- Do not create a new top-level generated directory.
- Keep the feature embedded in `articles/index.html`; do not add another
  generated route for Stage 327.
- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not add `saved_signal_index`, `signal_index`, `entity_index`,
  `brand_index`, `product_index`, `saved_article_entity_index`,
  `saved_article_brand_index`, `saved_article_product_index`, or related keys to
  app/runtime/manifest JSON.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not change story IDs, detail routes, local article reader anchors,
  paragraph anchors, content-section anchors, or paragraph evidence anchors.
- Do not add source collection.
- Do not fetch article pages.
- Do not add article extraction behavior.
- Do not add matching, entity extraction, semantic inference from raw text,
  scoring, ranking, demand proof, platform coverage verification, LLM calls,
  translation calls, image generation, connectors, scheduling, deployment
  behavior, or compliance-review product features.
- Do not add dependencies.

## Behavior

### Signal Index Builder

Build a render-only `RowOneSavedSignalIndex` dataclass from the edition and
`local_articles_by_story_id`.

The builder must iterate the current `edition.stories` and look up each story in
the current `local_articles_by_story_id` mapping. It must not read local article
sidecar JSON from disk because non-`latest_only` renders may leave old sidecars
in `data/articles/`.

Only include a story/article pair when:

- `article.story_id` matches the story id.
- `safe_local_article_story_id(story.id)` returns true.
- `is_safe_row_one_detail_path(story.detail_path)` returns true.
- The article has at least one nonblank saved paragraph.
- At least one content item has a nonblank `RowOneReference.name`.
- The content item has at least one paragraph index that maps to a nonblank
  saved paragraph, or the containing content section can link to an existing
  `#local-article-content-section-N` anchor.

For each reference group, compute:

- display name from `RowOneReference.name`
- display type from `RowOneReference.type`, falling back to `signal`
- display label from `RowOneReference.label`, falling back to the display type
- article count across current-edition saved articles
- source count across current-edition saved articles
- supporting paragraph count from valid paragraph links
- up to four supporting rows

Top-level `supporting_article_count` and `source_count` count distinct current
edition articles and sources across all signal entries. Top-level
`supporting_paragraph_count` is the sum of per-entry supporting paragraph
counts; the same paragraph URL may count once for each signal entry that
references it.

For each supporting row, compute:

- ROW ONE story title
- source display name, falling back to `Unknown source`
- ROW ONE section title
- saved article content-section title
- content-section path using existing `#local-article-content-section-N`
- up to three paragraph links using existing `#local-article-paragraph-N`

Each story contributes at most one supporting row per signal entry. When the
same signal appears in multiple content sections for the same story, the first
matching content section in article order wins; paragraph links for that support
come from matching items inside that winning section, deduped in item order.

Normalize and dedupe reference groups by name and type, preserving first
appearance in edition order. The first display label for a normalized
name/type pair wins. Cap output to avoid very large pages:

- at most twelve signal cards
- at most four supporting rows per signal
- at most three paragraph links per supporting row

When no publishable saved signal exists, return `None`.

### Generated Section

When the saved signal index exists, render it inside `articles/index.html`.

The section should:

- use bilingual headings:
  - `Saved Signal Index`
  - `本地信号索引`
- use bilingual dek copy:
  - `Browse the current edition's saved local articles by the brands, people, designers, and products already identified in ROW ONE sections.`
  - `按 ROW ONE 已整理栏目中的品牌、人物、设计师与产品线索浏览当前版本的本地保存文章。`
- show metrics:
  - signal count
  - supporting saved article count
  - source count
  - supporting paragraph count
- use exact English metric labels `saved signals`, `supporting articles`,
  `sources`, and `supporting paragraphs`
- render signal cards with supporting rows
- render direct links into generated detail pages using paths relative to
  `articles/index.html`, for example
  `../details/example.html#local-article-paragraph-1`

When the index is absent:

- do not render the Saved Signal Index section
- keep `articles/index.html` generation controlled by the existing saved article
  library behavior
- do not create any new page or JSON artifact

### Homepage Entry Copy

When the existing saved article library homepage entry exists and the saved
signal index is present, its description may mention that the library can be
browsed by saved signals or sources. When the saved signal index is absent, the
homepage entry must keep source-only copy so it does not promise signal browsing
that is not present. The homepage should not duplicate signal cards.

### Latest-Only Cleanup

No new generated child is added in Stage 327. The existing Stage 326
`articles/` cleanup continues to remove the page that contains the Saved Signal
Index when `render_row_one_site(..., latest_only=True)` runs. The existing marker
safety check must remain unchanged.

## Link Safety

- Do not derive filenames, ids, classes, or href fragments from article text,
  source names, reference names, labels, or user-facing strings.
- Use only existing validated `story.detail_path` values.
- Use only fixed fragment names or numeric section/paragraph anchors.
- Local article paragraph indices are zero-based in
  `RowOneLocalArticleContentItem.paragraph_indices`, but existing generated
  fragments are one-based, so index `0` links to
  `#local-article-paragraph-1`.
- Only produce paragraph links for integer indices that are not booleans and
  that map to nonblank saved paragraphs.
- Render signal-index links with a fixed `../` prefix after root detail paths
  have passed validation.
- Escape all displayed titles, source names, section names, counts, reference
  names, reference labels, and reference types with existing template escaping.

## Styling

Add compact editorial styles using the existing ROW ONE visual language:

- `.saved-signal-index`
- `.saved-signal-index-header`
- `.saved-signal-index-metrics`
- `.saved-signal-index-grid`
- `.saved-signal-index-card`
- `.saved-signal-index-card-header`
- `.saved-signal-index-card-meta`
- `.saved-signal-index-support`
- `.saved-signal-index-support-row`
- `.saved-signal-index-support-meta`
- `.saved-signal-index-actions`
- `.saved-signal-index-paragraphs`

The section should be professional, scan-first, and mobile-safe. It should not
use decorative motion, fake screenshots, large hero marketing copy, or new
visual dependencies.

## Testing Requirements

- Builder test: groups valid saved article references by normalized name/type,
  preserves first appearance, computes article/source/paragraph counts, and
  builds safe content-section and paragraph links.
- Builder test: filters mismatched story ids, invalid story ids, unsafe detail
  paths, blank saved paragraphs, blank reference names, and unusable articles.
- Builder test: filters invalid paragraph indices, including booleans, negatives,
  non-integers, out-of-range values, duplicates, and indices pointing to blank
  saved paragraphs.
- Builder test: caps signal cards, supporting rows, and paragraph links.
- Builder test: uses current edition plus in-memory local articles only and
  ignores local articles for story ids not in the edition.
- Builder test: href fragments are fixed or numeric and never derived from
  reference names, labels, article text, or source names.
- Render test: `articles/index.html` includes Saved Signal Index when saved
  local articles contain publishable references.
- Render test: the signal section includes bilingual heading/dek, metrics,
  reference cards, supporting rows, and safe relative links.
- Render test: homepage entry copy mentions signal/source browsing when the
  existing saved article library exists.
- Render test: unsafe display strings are escaped inside the signal section.
- Render test: no signal section is rendered without publishable references.
- Render/CSS test: `row_one_css()` includes the Saved Signal Index selectors and
  long-text wrapping safeguards.
- Workflow boundary test: generated HTML can contain Saved Signal Index markers,
  while `edition`, `manifest`, and `runtime` JSON do not contain Stage 327
  private keys, class names, English heading, or Chinese heading.
- Docs test: README and `docs/row-one.md` describe the feature as
  generated-site-only and explicitly state no contract/schema/artifact/source/
  fetching/scoring/ranking/LLM/connector/scheduling/deployment/compliance
  changes.

## Risks

- Claim strength: use wording like `saved signals` and `supporting saved
  articles`, not verified trends, brand heat, demand proof, platform momentum,
  or coverage verification.
- Contract drift: do not add JSON fields or app payload keys.
- Link mistakes: remember that `articles/index.html` is one directory below site
  root and needs `../` links into `details/`.
- Duplicate content: keep signal cards compact; the full saved article browsing
  remains in the source-grouped library below.
- Ordering ambiguity: preserve first appearance from current edition story order,
  not score or inferred importance.

## Definition Of Done

- Stage 327 spec and plan are reviewed before implementation.
- Saved Signal Index appears inside `articles/index.html` only when current
  in-memory saved local articles contain publishable references.
- The index organizes current-edition saved local articles by reference and
  provides links into existing detail-page local article anchors.
- The feature remains generated-site only and keeps all JSON contracts stable.
- Focused tests, full tests, Ruff, lock check, release hygiene, and secret marker
  scan pass.
- Code review has no unresolved Critical or Important findings.
- Changes are committed and pushed to `origin/main`.
