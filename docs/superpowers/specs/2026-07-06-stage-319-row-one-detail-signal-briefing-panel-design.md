# Stage 319 ROW ONE Detail Signal Briefing Panel Design

## Objective

Stage 319 adds a generated-site-only `Signal Briefing / 信号简报` panel to ROW
ONE detail pages. The panel should organize the article into a compact editorial
brief using existing story fields, existing references, and existing saved local
article sections, so a reader can understand the signal before reading the full
local article body.

## User Value

ROW ONE already saves article bodies locally, renders structured local article
sections, previews saved paragraphs, and offers internal next reads. The next
gap is synthesis at the top of a detail page: readers need a concise, local,
fashion-focused briefing instead of only a source link, summary paragraph, and
long saved text. Stage 319 makes each detail page feel more like a professional
fashion news article by grouping the existing information into a quick briefing
surface.

## Scope

This is a generated-site detail-page presentation enhancement only.

It reuses:

- existing `RowOneEdition`
- existing `RowOneStory`
- existing `RowOneStory.summary`
- existing `RowOneStory.why_it_matters`
- existing `RowOneStory.signal_context`
- existing `RowOneStory.reader_path`
- existing `RowOneStory.entity_refs`
- existing `RowOneStory.designer_refs`
- existing `RowOneStory.product_refs`
- existing `RowOneStory.evidence`
- existing `RowOneLocalArticle.brief_sections`
- existing `RowOneLocalArticle.content_sections`
- existing paragraph anchors when local article content items point to saved
  paragraphs

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

## Placement

Render the panel on detail pages after the existing `Detail Information Map` and
before `Summary`.

```text
Article Contents
Detail Information Map
Signal Briefing
Summary
Local Article
Why It Matters
Editorial Takeaway
Evidence Trail
Continue Reading
```

Do not add the panel to `article-contents` navigation. The panel is a scan-first
briefing surface, not a long section that needs a table-of-contents anchor.

## Panel Structure

The panel should render as:

- Section label: `Signal Briefing / 信号简报`
- Heading: `What To Know / 重点整理`
- Four deterministic cards where content exists:
  - `Signal / 信号`: cleaned story summary.
  - `Why It Matters / 为什么重要`: existing `story.why_it_matters`.
  - `Source Context / 来源背景`: existing `story.signal_context`, with a compact
    source/evidence count line.
  - `Names To Track / 需要关注`: de-duplicated references from story refs and
    saved local article refs.
- Optional `Local Article Cues / 本地正文线索` row when a local article has
  non-empty `brief_sections` or `content_sections`.

The panel should omit empty optional portions, but the main panel should render
for every detail page because `RowOneStory` already has summary, why-it-matters,
and signal-context fields.

The evidence count line should count only evidence links accepted by
`_safe_external_url(link.url)`, which is the same safety helper used by existing
evidence rendering. Unsafe evidence rows stay out of the count.

## Reference Rules

`Names To Track` should be deterministic and capped:

1. Read references in this order:
   - `story.entity_refs`
   - `story.designer_refs`
   - `story.product_refs`
   - refs from `local_article.content_sections[*].items[*].references`
2. De-duplicate by normalized lowercase `(name, type, label)`.
3. Preserve first-seen order. For local article references, iterate content
   sections in list order, items in list order, and references in list order.
4. Cap at eight chips.
5. Omit the card if no references exist.

## Local Article Cue Rules

`Local Article Cues` should use only existing saved local article structure:

1. Prefer `local_article.brief_sections` in render order.
2. Fill from `local_article.content_sections` in render order.
3. Cap at three cues.
4. Each cue includes title. Brief-section cues always include body because
   `RowOneLocalArticleBriefSection.body` is required; content-section cues
   include body only when `RowOneLocalArticleContentSection.body` exists.
5. For cues sourced from `content_sections`, collect `paragraph_indices` from
   all `section.items` in item order, de-duplicate while preserving first-seen
   order, and render one `Saved paragraph N / 保存段落 N` link for the first valid
   paragraph index only.
6. Filter paragraph links with the two existing helpers:
   `rendered = _local_article_rendered_paragraph_indices(article)` and
   `valid = _valid_local_article_paragraph_indices(indices, rendered)`, so links
   never target a missing paragraph.
7. Omit the cue row entirely when no cues exist.

## Escaping and Display

All visible text must be escaped. Story summary text should use the same cleaned
display path used elsewhere on detail pages. Cue bodies should use existing
localized text from local article brief/content sections. No HTML from source
articles should be trusted as raw markup.

## Implementation Shape

Modify only `src/fashion_radar/row_one/templates.py` for production behavior.

Suggested helpers:

- `DETAIL_SIGNAL_BRIEFING_MAX_REFS = 8`
- `DETAIL_SIGNAL_BRIEFING_MAX_CUES = 3`
- `_render_detail_signal_briefing(story: RowOneStory, local_article: RowOneLocalArticle | None)`
- `_render_detail_signal_briefing_references(story: RowOneStory, local_article: RowOneLocalArticle | None)`
- `_detail_signal_briefing_references(story: RowOneStory, local_article: RowOneLocalArticle | None)`
- `_render_detail_signal_briefing_cues(local_article: RowOneLocalArticle | None)`
- `_detail_signal_briefing_cues(local_article: RowOneLocalArticle)`

The helper should be called from `render_detail_html()` after
`detail_information_map` is created.

## Test Strategy

Add focused render tests in `tests/test_row_one_render.py`:

- the panel appears on detail pages before `Summary`
- the panel includes bilingual labels and headings
- the panel uses cleaned/escaped story summary
- source context includes source name and safe evidence count
- references are de-duplicated and capped
- local article cues prefer brief sections, fill from content sections, cap at
  three, and link only to the first valid rendered paragraph anchor for each
  content-section cue
- the existing lower `#why-it-matters` section still renders after the new
  briefing card with the same title
- local article cues are omitted when no local article structure exists
- source HTML/script text is escaped across summary, signal context, and
  reference names
- CSS selectors for the panel are present in generated stylesheet

Extend generated-site workflow boundary in `tests/test_workflows.py`:

- generated detail page contains the signal briefing panel
- generated contract payloads do not contain Stage 319-only keys
- SQLite item row, matches, and item count remain unchanged
- `edition.json`, `manifest.json`, and `runtime.json` contract versions remain
  pinned
- top-level `data/*.json` allowlist remains unchanged

Extend docs boundary in `tests/test_row_one_docs.py`:

- update Stage 318 docs slice to end at Stage 319
- add Stage 319 docs guard
- preserve forbidden-phrase guards for schema, contract, collection, fetching,
  scoring, connector, LLM, and compliance drift
