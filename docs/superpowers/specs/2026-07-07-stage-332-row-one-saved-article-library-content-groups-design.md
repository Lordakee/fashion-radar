# Stage 332 ROW ONE Saved Article Library Content Groups Design

## Goal

Make the dedicated ROW ONE saved article library at `articles/index.html`
organize saved local article bodies by content type, not only by source. The
page should let readers scan local saved text through the existing content
groups: read-first, people/brands, products, and source structure.

## Current Gap

ROW ONE already generates several local-content views:

- detail pages render saved local article text, digest, reader anchors, and
  paragraph evidence
- the homepage renders `Saved Article Content Organization` from existing
  `RowOneLocalArticle.content_sections`
- `articles/index.html` renders the daily saved article library by source and
  can render the saved signal index

The gap is that `articles/index.html` is the natural place for saved article
reading, but it does not show the same content-group organization that already
exists on the homepage. Readers can browse source groups, but they cannot use
the dedicated saved article library page to jump directly into grouped local
article content sections.

## Chosen Approach

Reuse the existing `RowOneSavedArticleContentOrganization` view model and render
it inside `articles/index.html`.

Placement:

1. saved article library hero
2. optional saved signal index
3. saved article content organization
4. saved article source grid

The existing homepage renderer remains unchanged in behavior. The same section
HTML can be reused if the renderer accepts a context-specific href prefix:

- homepage links stay `details/<story>.html#...`
- `articles/index.html` links become `../details/<story>.html#...`

The prefix must be applied only after the existing detail-path and fragment
safety checks pass. Unsafe `javascript:`, traversal, wrong-fragment, and invalid
paragraph-index cases must continue to be filtered out.

## Alternatives Considered

### Alternative 1: Add Text-Source Chips To Article Library Cards

This would surface Stage 331 body provenance in `articles/index.html`, showing
which local bodies are extracted article text versus ROW ONE summary fallback.
It is useful and small, but it is more of a provenance enhancement than a
content organization enhancement. It is a good follow-up node.

### Alternative 2: Add New Content Shortcuts To Each Source Card

Each source-group card could gain direct links to content sections. This is
useful, but it requires extending the saved article library builder model. The
existing content organization view already solves the browsing problem with
less schema churn.

### Alternative 3: Reuse Existing Homepage Content Groups In Article Library

This is the recommended approach. It adds a stronger saved-text browsing surface
while avoiding new sidecars, new contracts, and new extraction behavior.

## Architecture

Implementation stays inside the generated ROW ONE site:

- `render_row_one_site()` already builds `saved_article_content_organization`
  for the homepage.
- `_write_saved_article_library_page()` will accept that same object.
- `render_saved_article_library_html()` will accept an optional
  `saved_article_content_organization`.
- `_render_saved_article_content_organization()` and its child renderers will
  accept `href_prefix=""`.
- The article-library page will call the renderer with `href_prefix="../"`.

No new dataclass, Pydantic model, sidecar, JSON artifact, route, fetcher,
collector, scheduler, ranker, connector, or compliance-review feature is
needed.

## UI Behavior

When the current edition has publishable saved local article content sections,
`articles/index.html` shows the existing bilingual section:

- `Saved Article Content Organization`
- `保存正文内容整理`

Cards keep the existing labels, digest excerpts, chips, and evidence paragraph
links. The only context-specific change is that links from `articles/index.html`
must correctly navigate to `../details/...`.

If no valid cards survive safety filtering, no empty content-organization
section is rendered.

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

- `data/saved-article-content-organization.json`
- any new generated JSON contract for this section
- any new social-platform or community collection behavior

## Tests

Add focused render and docs tests that prove:

- `render_row_one_site()` includes the saved article content organization in
  `articles/index.html`
- the section appears between the optional saved signal index and source grid
- content-section links are prefixed as `../details/...` on the article-library
  page
- evidence paragraph links are prefixed as `../details/...` on the
  article-library page
- unsafe paths, traversal paths, wrong fragments, and invalid paragraph indices
  are still filtered
- existing homepage links remain unprefixed as `details/...`
- no generated JSON contracts or new JSON artifacts contain this HTML-only
  section
- `README.md` and `docs/row-one.md` document the Stage 332 generated-site-only
  boundary

## Out Of Scope

- No crawler or social connector work.
- No article extraction dependency changes.
- No body provenance/text-source chips in this node.
- No new database schema.
- No generated image work.
- No app contract change.
- No UI redesign beyond rendering the existing section in the saved article
  library page.
- No compliance-review functionality.
