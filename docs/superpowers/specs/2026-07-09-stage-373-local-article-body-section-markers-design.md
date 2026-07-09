# Stage 373 Local Article Body Section Markers Design

## Goal

Stage 373 adds generated-site-only Local Article Body Section Markers inside each `articles/<story-id>.html` saved local article body. The feature turns the existing flat saved paragraph stream into a more readable local article by inserting compact section-start markers before the first rendered paragraph cited by each existing content section.

## User Value

ROW ONE now downloads or saves article bodies locally and already exposes many pre-body organizers. The remaining article-page gap is inside the body itself: a reader can see summaries and routes before the saved text, but the saved body still reads like an uninterrupted paragraph list.

Stage 373 makes the saved body more usable without adding another outbound link surface. Each marker tells the reader which existing local content section is starting, which labels or references support it, and where the matching content segment lives on the same page.

## Product Shape

Feature name: **Local Article Body Section Markers** / **本地正文分节标记**.

The markers render only inside `articles/<story-id>.html`, inside the existing `#local-article-body` saved body, immediately before the paragraph whose original saved paragraph index is the first valid paragraph filed under an existing `RowOneLocalArticle.content_sections` group.

Each marker contains:

- content-section title, with fallback `Section N`
- compact support excerpt from the section body, item body, or cited saved paragraph
- capped item label chips
- capped reference chips
- same-page link back to the matching existing `#local-article-content-section-N` anchor
- same-page link to the paragraph that follows the marker

The marker is an in-body reading aid. It does not replace the saved paragraph, move paragraphs, or duplicate the full article body.

## Data Sources

Stage 373 reuses only current local article page data:

- current `RowOneStory`
- matching `RowOneLocalArticle`
- `RowOneLocalArticle.title`
- `RowOneLocalArticle.source_name`
- `RowOneLocalArticle.paragraphs`
- `RowOneLocalArticle.paragraphs_zh`
- `RowOneLocalArticle.content_sections`
- `RowOneLocalArticleContentSection.title`
- `RowOneLocalArticleContentSection.body`
- `RowOneLocalArticleContentSection.items`
- item labels
- item bodies
- item references
- item-level `paragraph_indices`
- existing content-section anchors
- existing paragraph anchors

It does not call source collection, fetching, matching, extraction, scoring, ranking, LLMs, connectors, scheduling, deployment, analytics, personalization, recommendation, app UI, or compliance-review code.

## Builder Contract

Create `src/fashion_radar/row_one/local_article_body_section_markers.py`.

The builder returns `tuple[RowOneLocalArticleBodySectionMarker, ...]`.

Suggested constants:

- `LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS = 8`
- `LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_LABELS = 3`
- `LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_REFERENCES = 4`
- `LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS = 150`

Suggested dataclass:

```python
@dataclass(frozen=True)
class RowOneLocalArticleBodySectionMarker:
    paragraph_index: int
    paragraph_href: str
    section_position: int
    section_href: str
    title: LocalizedText
    support: LocalizedText
    item_labels: tuple[LocalizedText, ...]
    references: tuple[RowOneReference, ...]
```

The builder should:

- require `story.id == local_article.story_id`
- require `safe_local_article_story_id(story.id)`
- iterate existing content sections in local article order
- validate item-level paragraph indices strictly, rejecting bools, non-ints, negative indices, out-of-range indices, duplicates, and blank paragraphs
- choose the first valid cited paragraph as the marker insertion point
- skip a section when it has no valid cited paragraph
- avoid stacked duplicate markers by allowing at most one marker per paragraph index
- use section title with fallback `Section N` / `第 N 节`
- build support excerpt from section body, then item body, then cited saved paragraph
- use aligned Chinese support text when `paragraphs_zh` aligns with `paragraphs`, falling back to English text otherwise
- dedupe item labels case-insensitively and cap them
- dedupe references by `(name, type, label)` case-insensitively and cap them
- return markers sorted by paragraph index, then section position, so they render in reading order
- return an empty tuple when no meaningful marker can be built

## Rendering Contract

Modify only the local article body rendering path:

- `render_local_article_page_html(...)` builds markers where both `story` and `local_article` are in scope.
- `_render_local_article(...)` accepts prebuilt markers as an internal keyword-only argument and keeps its current public behavior for callers that do not pass markers.
- `_render_local_article_paragraphs(...)` accepts prebuilt markers as an internal keyword-only argument.
- Before rendering a paragraph, it inserts all marker HTML whose `paragraph_index` matches that paragraph.
- When a paragraph carries a body section marker, suppress the existing inline Stage 366 body filing cue for that paragraph so the reader does not see the same section name and content-section link twice in adjacent elements.
- Paragraph IDs and paragraph order remain unchanged.

Template helpers render:

- marker eyebrow: `Section starts here` / `本节从这里开始`
- section title
- support excerpt
- capped item labels
- capped reference chips
- `View content segment` same-page section link
- `Continue paragraph` same-page paragraph link

The marker and Stage 366 filing cues intentionally coexist by surface: marker paragraphs use the block marker, and non-marker paragraphs keep the existing inline filing cue/unfiled cue behavior.

All user-derived text is escaped. Render-time href validation must accept only same-page fragments:

- `#local-article-content-section-N`
- `#local-article-paragraph-N`
- `N >= 1`

Render-time validation must reject empty hrefs, whitespace, protocol URLs, protocol-relative URLs, traversal, absolute paths, missing fragments, zero-valued anchors, nonnumeric anchors, and malformed fragments.

The renderer must reuse the existing `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` patterns rather than adding new regexes.

## Site Integration

Stage 373 is article-page-only and generated-site-only.

It does not write:

- `data/local-article-body-section-markers.json`
- `data/article-body-section-markers.json`
- `data/body-section-markers.json`
- `local-article-body-section-markers.html`
- `article-body-section-markers.html`
- `body-section-markers.html`

It does not alter `index.html`, `articles/index.html`, or detail pages. It does not publish full articles outside existing local article pages and does not add outbound article URLs as primary navigation.

## Documentation Boundary Paragraph

Stage 373 adds generated-site only Local Article Body Section Markers inside the saved body of `articles/<story-id>.html`; it reuses current-edition saved local article sidecars, existing saved local paragraphs, existing local article content sections, existing content-section item bodies, existing item labels, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to insert compact section-start markers before the first rendered saved paragraph filed under each existing content section without changing app-facing contracts; it does not create `data/local-article-body-section-markers.json`, does not create `data/article-body-section-markers.json`, does not create `data/body-section-markers.json`, does not create `local-article-body-section-markers.html`, does not create `article-body-section-markers.html`, does not create `body-section-markers.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

## Tests

Builder tests should prove:

- markers are built from existing content sections and valid paragraph indices
- marker insertion point uses original saved paragraph index and 1-based href anchors
- invalid indices and blank paragraphs are filtered
- duplicate paragraph insertion points are not stacked
- support excerpt fallback uses section body, item body, then saved paragraph
- Chinese support falls back safely when translated paragraph alignment is missing
- item labels and references are deduped and capped
- output is deterministic and capped
- builder returns an empty tuple without meaningful marker content

Render tests should prove:

- local article pages include markers inside `#local-article-body`
- markers render before the target paragraph and preserve paragraph IDs/order
- marker text and chips are escaped
- unsafe hrefs are filtered at render time
- markers do not appear on homepage, article library index, or detail pages
- data contract payloads do not contain Stage 373 identifiers
- no Stage 373 JSON/HTML artifacts are written
- CSS selectors and mobile rules exist

Docs/workflow tests should prove:

- README and `docs/row-one.md` include the exact Stage 373 boundary paragraph before Stage 372
- stale boundary phrases are absent
- app contract denylist includes Stage 373 names
- artifact stem denylist includes Stage 373 stems
- a generated-site-only workflow guard proves contracts and routes still pass when marker rendering is disabled

## Out of Scope

Stage 373 does not add social platform connectors, crawling, article acquisition, fetch scheduling, LLM summarization, recommendation logic, analytics, app UI, deployment, image generation, homepage modules, library index modules, detail-page modules, article-page pre-body summary sections, or compliance-review behavior.
