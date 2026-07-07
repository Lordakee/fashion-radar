# Stage 333 ROW ONE Saved Article Library Text-Source Map Design

## Goal

Make the ROW ONE saved article library explain what kind of local text each
saved article card contains before a reader opens the detail page. The dedicated
`articles/index.html` page should show whether included saved bodies are
extracted article text, ROW ONE summary fallback, or skipped text-bearing
diagnostics.

## Current Gap

Stage 331 added `RowOneLocalArticle.body_source`, site metrics, readiness output,
and detail-page provenance. Stage 332 made `articles/index.html` a stronger
local reading page by adding saved article content groups. The remaining gap is
that article-library cards still treat every saved body as identical.

Readers can see source groups, paragraph counts, organized section counts,
signal index cards, and content groups, but they cannot see the body-source mix
until they open a detail page.

## Chosen Approach

Extend the existing generated-site-only saved article library view model:

- Add `body_source` to `RowOneSavedArticleLibraryEntry`.
- Add library-level included-article counts for:
  - extracted article text
  - ROW ONE summary fallback
  - skipped
- Render nonzero text-source counts in the saved article library metrics.
- Render one text-source chip on each saved article library card.

Counts apply only to articles included in `RowOneSavedArticleLibrary`; this page
already filters to current-edition, safe-route, safe-story-id saved articles
with nonblank saved paragraphs. Skipped sidecars usually do not appear because
they generally have no publishable paragraphs, but the model should remain
defensive if an included article has `body_source="skipped"`.

## UI Behavior

The article-library hero metrics and homepage saved-library entry metrics can
include compact nonzero text-source counts:

- `N extracted text`
- `N summary fallback`
- `N skipped`

Saved article cards render a compact bilingual text-source chip:

- extracted: `Text source / 正文来源: Extracted article text`
- summary fallback: `Text source / 正文来源: ROW ONE summary fallback`
- skipped: `Text source / 正文来源: Skipped`

Do not expose `reason` in this stage. Detail pages already show fallback reason
when present; repeating it in the article library would make the card feel like
a diagnostic report instead of a reading index.

## Architecture

Implementation stays inside existing generated-site objects:

- `saved_article_library.py` builds the view model from current local article
  sidecars.
- `templates.py` renders the view model to static HTML.
- `README.md` and `docs/row-one.md` document the generated-site-only boundary.

No `RowOneLocalArticle` schema change is needed because `body_source` already
exists. No new sidecar or contract JSON is needed because the article library is
HTML-only.

## Contract Boundaries

Do not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `row-one-runtime/v1`
- JSON schemas
- `data/articles/<story-id>.json` sidecar schema
- source collection
- fetching
- matching
- extraction
- scoring
- ranking
- LLM behavior
- connector behavior
- scheduling
- deployment behavior
- market grouping
- domestic/international classification
- compliance-review product behavior

Do not add:

- fallback reason display on article-library cards
- outbound article URLs
- new extraction diagnostics
- `data/saved-article-text-source-map.json`
- any new generated JSON contract for this section
- any new social-platform or community collection behavior

## Tests

Add focused builder, render, and docs tests that prove:

- `build_row_one_saved_article_library()` copies each included article's
  `body_source` into the corresponding entry.
- library-level counts distinguish extracted, summary fallback, and skipped
  among included library entries.
- zero-paragraph skipped sidecars remain excluded from the library.
- `articles/index.html` renders top text-source counts and per-card text-source
  chips.
- rendered chips are static text, not links.
- JSON contract payloads and generated files do not expose a
  `saved_article_text_source_map` artifact.
- `README.md` and `docs/row-one.md` document the Stage 333 generated-site-only
  boundary.

## Out Of Scope

- No crawler or social connector work.
- No article extraction dependency changes.
- No new fallback reason UI in the article library.
- No new database schema.
- No generated image work.
- No app contract change.
- No UI redesign.
- No compliance-review functionality.
