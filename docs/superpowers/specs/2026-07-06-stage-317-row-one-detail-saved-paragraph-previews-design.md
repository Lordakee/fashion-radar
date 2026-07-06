# Stage 317 ROW ONE Detail Saved Paragraph Previews Design

## Objective

Stage 317 improves ROW ONE generated detail pages by showing capped saved
paragraph previews directly inside organized local article content items. Stage
316 made homepage cards link to `#local-article-content-section-N`; Stage 317
makes that landing point immediately useful by surfacing the exact saved
paragraph snippets referenced by each content item.

## User Value

Readers should not land on a detail-page content section and see only a label,
a short derived body, and paragraph-number links. They should see the source
paragraph evidence inline, with links to the authoritative saved paragraph
anchors below.

## Scope

This is a generated-site detail-page presentation enhancement only.

It reuses:

- existing `RowOneLocalArticle.paragraphs`
- existing `RowOneLocalArticle.paragraphs_zh`
- existing `RowOneLocalArticle.content_sections`
- existing detail routes
- existing `#local-article-paragraph-N` anchors
- existing generated `data/articles/<story-id>.json` sidecars

It does not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `data/manifest.json`
- `row-one-runtime/v1`
- `data/runtime.json`
- schemas
- detail routes
- paragraph anchors
- source collection
- article fetching/extraction
- scoring
- connectors
- LLM calls
- compliance-review product behavior

It does not write a new JSON artifact.

## Proposed UI Behavior

Inside each rendered local article content item, after the item body and before
the existing meta/reference output, render a compact preview list when the item
has valid paragraph indices.

Each preview should include:

- label:
  - EN: `Saved paragraph N`
  - ZH: `保存段落 N`
- link to `#local-article-paragraph-N`
- excerpt from the referenced saved paragraph
- bilingual excerpt only when `paragraphs_zh` aligns with `paragraphs`

Caps and filtering:

- maximum two previews per content item
- skip negative indices
- skip out-of-range indices
- skip duplicate indices
- skip blank saved paragraphs
- preserve first-seen order

Escaping:

- all visible text must go through existing HTML escaping
- preview links must only use internally generated paragraph anchors

## Implementation Shape

Modify only `src/fashion_radar/row_one/templates.py` for production behavior.

Suggested helpers:

- `LOCAL_ARTICLE_CONTENT_PREVIEW_MAX_ITEMS = 2`
- `LOCAL_ARTICLE_CONTENT_PREVIEW_EXCERPT_CHARS = 140`
- `_render_local_article_content_paragraph_previews(article, item, rendered_indices)`
- `_local_article_content_preview_excerpt(text)`

Update call flow:

1. `_render_local_article_content_sections(article, rendered_indices=...)`
2. pass `article` into `_render_local_article_content_item(...)`
3. `_render_local_article_content_item(...)` renders previews before existing meta

## Test Strategy

Add focused render tests in `tests/test_row_one_render.py`:

- previews render under content items with valid paragraph indices
- previews include bilingual labels and excerpts when zh paragraphs align
- previews link to existing `#local-article-paragraph-N` anchors
- previews cap at two per item and preserve first-seen order
- previews skip duplicate, blank, negative, and out-of-range indices
- preview text is escaped
- mismatched zh paragraphs do not render incorrect zh previews

Extend generated-site workflow boundary in `tests/test_workflows.py`:

- generated detail page contains the new preview class/label
- SQLite item row, item matches, and item count remain unchanged
- `edition.json`, `manifest.json`, and `runtime.json` contract versions remain pinned
- generated contract payloads do not contain a Stage 317-only key
- top-level `data/*.json` allowlist remains unchanged

Extend docs boundary in `tests/test_row_one_docs.py`:

- add Stage 317 docs guard
- update Stage 316 slice to end at Stage 317 if Stage 317 is inserted before Stage 310
- preserve forbidden-phrase guards for schema, contract, collection, scoring, connector,
  LLM, and compliance drift

