# Stage 326 ROW ONE Daily Saved Article Library Design

## Goal

Add a generated-site only daily saved article library page for ROW ONE so readers can browse the local article text saved for the current edition from one professional, bilingual index instead of opening each story card one by one.

## User Value

The user wants ROW ONE to organize the downloaded local fashion information, not only point to source links. Recent stages made saved local articles readable in detail pages, added local-first reading links, and mapped saved paragraphs to organized content evidence.

Stage 326 adds a daily library layer:

- A reader can open one page for all locally saved articles in today's edition.
- The page groups saved articles by source so it is clear which local source set is powering the edition.
- Each article entry shows the ROW ONE section, saved paragraph count, organized section count, reference chips, and direct links into the existing detail-page local article anchors.
- The homepage gets a clear entry point to the library when saved local articles exist.

This keeps the project moving toward a daily fashion news website that renders and organizes local article content while staying inside the existing generated HTML surface.

## Design Read

Reading this as an editorial content index for fashion research readers, with a restrained professional media-library language, leaning toward the existing static ROW ONE HTML/CSS system. Dial values: design variance 5, motion intensity 2, visual density 6. The feature should feel like a fashion newsroom source desk, not a marketing landing page or a dense admin dashboard.

## Scope

- Generated ROW ONE HTML/CSS only.
- Create a top-level generated page at `articles/index.html`.
- Add a homepage entry point to `articles/index.html` when a publishable saved article library exists.
- Use only existing data available during `render_row_one_site()`:
  - `RowOneEdition`
  - `RowOneStory`
  - `RowOneLocalArticle`
  - `RowOneLocalArticle.content_sections`
  - `RowOneLocalArticleContentItem.references`
  - `RowOneLocalArticleContentItem.paragraph_indices`
  - existing detail paths and existing local article anchors
- Add a private render/build helper module for the saved article library.
- Add CSS selectors to the existing `row-one.css` output.
- Add tests and documentation for generated-site-only behavior.
- Build strictly from the current in-memory `edition.stories` and `local_articles_by_story_id` passed to `render_row_one_site()`. Do not scan `output_dir`, `data/articles/*.json`, or any persisted sidecar files while rendering the library.

## Non-Goals

- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not add `saved_article_library`, `daily_saved_article_library`, `article_library`, or related keys to app/runtime/manifest JSON.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not change story IDs, detail routes, local article reader anchors, paragraph anchors, content-section anchors, or paragraph evidence anchors.
- Do not add source collection.
- Do not fetch article pages.
- Do not add article extraction behavior.
- Do not add scoring, ranking, matching, LLM calls, translation calls, image generation, connectors, scheduling, deployment behavior, or compliance-review product features.
- Do not add dependencies.

## Behavior

### Library Builder

Build a render-only `RowOneSavedArticleLibrary` dataclass from the edition and `local_articles_by_story_id`.

The builder must iterate the current `edition.stories` and look up each story in the current `local_articles_by_story_id` mapping. It must not read local article sidecar JSON from disk because non-`latest_only` renders may leave old sidecars in `data/articles/`.

Only include a story/article pair when:

- `article.story_id` matches the story id.
- `safe_local_article_story_id(story.id)` returns true.
- `is_safe_row_one_detail_path(story.detail_path)` returns true.
- The article has at least one nonblank saved paragraph.

For each included article, compute:

- display title from the article title, falling back to the ROW ONE story headline
- source display name, falling back to `Unknown source`
- ROW ONE section title
- saved paragraph count
- organized section count from all current `article.content_sections`, matching the existing saved article coverage module
- up to six deduped references collected from content items
- up to four paragraph links for valid rendered paragraph indices. Local article paragraph indices are zero-based in `RowOneLocalArticleContentItem.paragraph_indices`, but existing generated fragments are one-based, so index `0` links to `#local-article-paragraph-1`.
- detail links to existing anchors:
  - `#local-article-digest`
  - `#local-article-reader`
  - `#local-article-paragraph-evidence`
  - `#local-article-paragraph-N`

Group entries by normalized source name while preserving the first source appearance in edition order. Cap the output to avoid very large generated pages:

- at most eight source groups
- at most eight entries per source group
- at most six reference chips per entry
- at most four paragraph chips per entry

When no publishable saved article exists, return `None`.

### Generated Page

When the library exists, write `articles/index.html`.

The page should:

- use the existing ROW ONE language toggle
- link `../assets/row-one.css` and `../assets/row-one.js`
- include a back link to `../index.html`
- show bilingual headings:
  - `Daily Saved Article Library`
  - `每日本地文章库`
- show edition-level metrics:
  - saved article count
  - source count
  - saved paragraph count
  - organized section count
- render source groups with article entries
- render direct links into the generated detail pages using paths relative to `articles/index.html`, for example `../details/example.html#local-article-reader`

When the library is absent:

- do not create `articles/index.html`
- do not render the homepage entry point

### Homepage Entry Point

When the library exists, render a compact homepage section after saved article coverage and before saved article briefs.

The homepage entry point should:

- link to `articles/index.html`
- show bilingual copy that describes the saved local source set
- show the same high-level counts
- avoid duplicating the full library content on the homepage

### Latest-Only Cleanup

When `render_row_one_site(..., latest_only=True)` cleans generated children, it must remove the new top-level `articles/` directory along with the existing generated children. It must preserve the existing marker safety check.

## Link Safety

- Do not derive filenames, ids, classes, or href fragments from article text, source names, reference names, labels, or user-facing strings.
- Use only existing validated `story.detail_path` values.
- Use only fixed fragment names or numeric paragraph anchors.
- Only produce paragraph links for integer indices that are not booleans and that map to nonblank saved paragraphs.
- Render library page detail links with a fixed `../` prefix after the detail path has passed `is_safe_row_one_detail_path`.
- Escape all displayed titles, source names, section names, counts, paragraphs, and references with existing template escaping.

## Styling

Add compact editorial styles using the existing ROW ONE visual language:

- `.saved-article-library-entry`
- `.saved-article-library-entry-header`
- `.saved-article-library-entry-metrics`
- `.saved-article-library-page`
- `.saved-article-library-hero`
- `.saved-article-library-metrics`
- `.saved-article-library-source`
- `.saved-article-library-grid`
- `.saved-article-library-card`
- `.saved-article-library-card-meta`
- `.saved-article-library-actions`
- `.saved-article-library-refs`
- `.saved-article-library-paragraphs`

The page should be professional, scan-first, and mobile-safe. It should not use decorative motion, fake screenshots, large hero marketing copy, or new visual dependencies.

## Testing Requirements

- Builder test: groups valid saved articles by source, preserves edition order, computes counts, and builds detail/deep links.
- Builder test: filters mismatched story ids, invalid story ids, unsafe detail paths, and articles without nonblank saved paragraphs.
- Builder test: filters invalid paragraph indices, including booleans, negatives, non-integers, out-of-range values, duplicates, and indices pointing to blank saved paragraphs.
- Builder test: caps source groups, entries per source group, references, and paragraph chips.
- Builder test: escapes are left to templates, but builder never derives unsafe href fragments from user-facing text.
- Render test: `render_row_one_site()` writes `articles/index.html` when saved local articles exist.
- Render test: the library page includes bilingual headings, metrics, grouped source names, article metadata, reference chips, and deep links to existing detail anchors.
- Render test: homepage includes a compact library entry link only when the library exists.
- Render test: unsafe display strings are escaped on both homepage entry and library page.
- Render test: no library page or homepage entry is rendered without saved local articles.
- Render test: `latest_only=True` removes a stale top-level `articles/` directory.
- Render/CSS test: `row_one_css()` includes the saved article library entry and page selectors.
- Workflow boundary test: generated HTML can contain the library markers, while `edition`, `manifest`, and `runtime` JSON do not contain Stage 326 private keys.
- Docs test: README and `docs/row-one.md` describe the library as generated-site-only and explicitly state no contract/schema/artifact/source/fetching/scoring/LLM/connector/compliance changes.
- Docs test: the generated files inventory lists `articles/index.html` and describes it as a generated child removed by latest-only cleanup.

## Risks

- Duplicate content: keep the homepage entry compact and put the full browsing experience on `articles/index.html`.
- Contract drift: do not add JSON fields or app payload keys.
- Link mistakes: remember that library-page links are one directory below the site root and need `../`.
- Claim strength: use wording like `saved local source set` and `saved local articles`, not verified coverage, trend proof, or compliance language.
- Cleanup safety: adding `articles` to generated children is necessary, but the existing marker guard must remain unchanged.

## Definition Of Done

- Stage 326 spec and plan are reviewed by Claude Code before implementation.
- `articles/index.html` is generated only when there are publishable saved local articles.
- The homepage links to the library only when the library exists.
- The library organizes saved local articles by source and provides deep links into existing local article detail anchors.
- The feature remains generated-site only and keeps all JSON contracts stable.
- Focused tests, full tests, Ruff, lock check, release hygiene, and secret marker scan pass.
- Claude Code code review has no unresolved Critical or Important findings.
- Changes are committed and pushed to `origin/main`.
