# Stage 341 ROW ONE Local Article Information Panel Design

## Objective

Stage 341 improves the first-class ROW ONE local article pages by adding a compact article-specific information panel before the full saved local article body.

Stages 339 and 340 made local article reading more complete: Stage 339 created first-class `articles/<story-id>.html` pages, and Stage 340 cleaned obvious extraction noise before saved paragraphs are rendered. The remaining gap is scanability inside the standalone article page itself. A reader can open a local article page, but the page does not yet start with a compact dossier that summarizes what the saved article contains, where to jump, which source/body type it uses, and which saved references/sections are available.

## User-Facing Result

When ROW ONE generates `articles/<story-id>.html` for a saved local article:

- The page opens with a generated HTML-only “Local Article Information” panel before the existing local article section.
- The panel shows compact source and organization metrics from existing `RowOneStory` and `RowOneLocalArticle` fields.
- The panel links only to existing page-local or safe internal anchors such as `#local-article-reader`, `#local-article-digest`, `#local-article-paragraph-evidence`, `#local-article-content-section-N`, and `#local-article-paragraph-N`.
- The panel surfaces capped section cards and reference chips from existing `content_sections`, so the reader can scan people/brands, products, takeaways, and paragraph pointers without leaving the page.
- Existing local article body rendering, detail-page anchors, saved article library routes, and app-facing JSON contracts remain unchanged.

## Scope

### In Scope

- Add `_render_local_article_information_panel(edition, story, local_article, section_title)` in `src/fashion_radar/row_one/templates.py`.
- Call the panel from `render_local_article_page_html()` before the existing `{local_article_section}`.
- Reuse existing `RowOneStory`, `RowOneLocalArticle`, `LocalizedText`, `RowOneReference`, and `content_sections` values.
- Render only generated HTML/CSS on `articles/<story-id>.html`.
- Add CSS selectors for the information panel inside `row_one_css()`.
- Add render tests for panel presence, safe local anchors, escaping/dedupe/capping, invalid paragraph-index filtering, CSS selectors, and contract stability.
- Document Stage 341 boundaries in `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, and `tests/test_workflows.py`.

### Out of Scope

- No new pages, routes, JSON artifacts, sidecar fields, model fields, schemas, app contract fields, or runtime/manifest versions.
- No change to `render.py`, collection, fetching, matching, extraction, paragraph filtering, scoring, ranking, LLM behavior, social connectors, scheduling, deployment, analytics, personalization, recommendations, market grouping, domestic/international classification, or compliance-review behavior.
- No full article publication on `articles/index.html`.
- No outbound article URLs as primary navigation.
- No mutation of `paragraphs`, `paragraphs_zh`, `content_sections`, or existing fragment IDs.

## Architecture

Stage 341 stays inside the ROW ONE template layer.

`render_row_one_site()` already passes the current edition story and `RowOneLocalArticle` into `render_local_article_page_html()` for each eligible `articles/<story-id>.html` page. That template currently renders the article header, safe links back to the article library and organized detail page, and then inserts `_render_local_article(local_article)`.

Stage 341 adds one article-page-local panel between the article heading/source line and the existing local article section. The panel is derived only from values already available in the template:

- `edition.brand`
- `story.headline`, `story.section_key`, `story.summary`, `story.entity_refs`, `story.product_refs`
- `section_title`
- `local_article.source_name`, `body_source`, `paragraphs`, `content_sections`, `brief_sections`, and references inside content items

Because the panel is HTML-only and uses existing safe local anchors, no changes are needed in `render.py`, data models, sidecar generation, status integrity, or app/runtime/manifest payloads.

## Panel Content

The panel should render a section like:

```html
<section class="local-article-information" aria-labelledby="local-article-information-title">
  ...
</section>
```

Suggested content:

- Header: “Local Article Information” / “本地文章信息”.
- Short explanatory dek: tells the reader this is a scan-first organizer for the saved local article.
- Metrics:
  - source name
  - body source label (`Extracted article`, `ROW ONE summary fallback`, or `Skipped`)
  - saved paragraph count
  - organized section count
- Quick jumps:
  - `#local-article-reader`
  - `#local-article-digest`
  - `#local-article-paragraph-evidence`
  - first few valid `#local-article-content-section-N` links
  - first few valid referenced `#local-article-paragraph-N` links
- Capped section cards:
  - section title
  - first one or two item titles/bodies
  - capped reference chips
  - only valid page-local paragraph links

## Safety Rules

- Escape all displayed strings.
- Link only to same-page anchors beginning with `#local-article-`.
- Use strict paragraph-index validation with the existing rendered-paragraph index set from `_local_article_rendered_paragraph_indices(article)`: reject bools, non-ints, duplicates, out-of-range indices, and indices pointing to blank paragraphs.
- Cap rendered sections, items, references, and paragraph links to avoid clutter.
- Dedupe reference chips by normalized `(name, type, label)`.
- Keep the existing string-returning `_local_article_body_source_label()` unchanged; add a separate localized helper for bilingual panel body-source labels.
- Do not render the panel when the local article section would be empty.
- Preserve existing `id="local-article"` and `id="local-article-paragraph-N"` anchors.
- Do not add any Stage 341 terms to `edition.json`, `manifest.json`, or `runtime.json`.

## Testing Strategy

Tests should verify:

- `render_local_article_page_html()` includes the information panel before the existing local article section.
- The panel links only to local anchors, not outbound article URLs.
- The panel includes source/body/paragraph/section metrics.
- The panel dedupes and caps reference chips and paragraph links.
- Unsafe HTML in titles, source names, references, and content item text is escaped.
- Invalid paragraph indices, bool indices, duplicate indices, and out-of-range indices are omitted.
- `row_one_css()` includes the panel selectors.
- Existing first-class article page tests continue to pass.
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` remain contract-stable and do not contain Stage 341 vocabulary.
- No `data/local-article-reading-improvements.json` or equivalent artifact is written.

## Documentation

Update:

- `README.md` stage history with Stage 341 boundaries.
- `docs/row-one.md` generated ROW ONE page docs with the same boundary.
- `tests/test_row_one_docs.py` with a Stage 341 boundary guard.
- `tests/test_workflows.py` with no-contract/no-artifact assertions.

## Definition of Done

Stage 341 is complete when:

- `articles/<story-id>.html` pages include a compact local article information panel built from existing saved local article data.
- The panel uses safe local anchors and does not introduce outbound navigation.
- Existing local article sections, paragraph anchors, and library/detail routes continue to work.
- No JSON/app/runtime/manifest contract changes are introduced.
- Focused render/docs/workflow tests, full pytest, ruff, format check, lock check, diff check, staged secret scan, code review, commit, and push all pass.
