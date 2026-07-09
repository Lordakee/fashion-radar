# Stage 376 Daily Local News Timeline Design

## Objective

Stage 376 adds a generated-site only **Daily Local News Timeline** to the ROW
ONE homepage. The feature closes a concrete news-site gap: a reader can see
today's locally saved fashion stories in publication-time order before moving
into deeper theme, signal, and reading-path sections.

This moves ROW ONE closer to the requested daily fashion-news website by making
the first-screen daily experience answer: "What is newest, from which source,
and where can I read the locally saved text?"

## Product Shape

The timeline appears on `index.html` after Daily Local Theme Summary Strip and
before Daily Local Article Intelligence Brief.

The section shows up to six entries. Each entry contains:

- a publication date label
- the story headline
- the source name
- a short excerpt from the first non-empty saved local paragraph
- a same-site link to `articles/<story-id>.html#local-article-paragraph-N`

The timeline is omitted when no usable timed local article exists.

## Architecture

Create a focused model/builder module:

`src/fashion_radar/row_one/daily_local_news_timeline.py`

The module owns immutable dataclasses:

```python
@dataclass(frozen=True)
class RowOneDailyLocalNewsTimelineItem:
    title: LocalizedText
    source_name: str
    published_at: datetime
    published_label: LocalizedText
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalNewsTimeline:
    title: LocalizedText
    dek: LocalizedText
    item_count: int
    source_count: int
    latest_label: LocalizedText
    items: tuple[RowOneDailyLocalNewsTimelineItem, ...]
```

Expose:

```python
def build_row_one_daily_local_news_timeline(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalNewsTimeline | None
```

The builder is pure and deterministic. It uses only the current `RowOneEdition`,
already saved local article sidecars, and already generated local article page
hrefs.

## Timeline Rules

For each `edition.stories` entry, the builder considers the saved local article
only when:

- the story id is a safe local article story id
- a `RowOneLocalArticle` exists for the same story id
- `article.story_id == story.id`
- `article_hrefs_by_story_id[story.id]` is a safe one-file local article page
  href matching the story id
- the article has at least one non-empty saved paragraph
- either `article.published_at` or `story.published_at` is present

Publication time selection:

1. use `article.published_at`
2. fall back to `story.published_at`

Sorting:

1. newest `published_at` first
2. original edition story order as tie-breaker
3. story id as final deterministic tie-breaker

Entries are capped at six items.

The link target is the first non-empty saved paragraph:

`articles/<story-id>.html#local-article-paragraph-N`

where `N` is the original one-based paragraph position. Blank paragraphs are
skipped but do not shift later paragraph numbers.

Article page href validation remains same-site and one-file only. Hrefs with
protocols, protocol-relative prefixes, absolute paths, traversal, whitespace,
non-`.html` names, mismatched story ids, or unsafe story ids are rejected before
fragment anchors are appended.

## Text Rules

The title uses `story.headline` with `article.title` as fallback and story id as
the last fallback.

The excerpt uses the first non-empty saved paragraph. If aligned
`article.paragraphs_zh` is available for the same paragraph index, it supplies
the Chinese excerpt; otherwise the English excerpt is reused. Excerpts are
normalized and capped to a short readable length.

The builder helper contract is explicit:

```python
def _first_paragraph(article: RowOneLocalArticle) -> tuple[int, LocalizedText] | None:
    ...

def _localized_excerpt(value: str) -> str:
    ...
```

`_first_paragraph(...)` returns the original zero-based paragraph index and the
localized excerpt. It scans `article.paragraphs` in original order, normalizes
each English paragraph, skips blanks, preserves the found index for the anchor,
and uses `article.paragraphs_zh[index]` only when
`len(article.paragraphs_zh) == len(article.paragraphs)` and the aligned Chinese
paragraph normalizes to a non-empty value. Otherwise the Chinese excerpt reuses
the English excerpt. `_localized_excerpt(...)` normalizes whitespace and
truncates values longer than the configured character cap with a trailing
ellipsis.

The source name uses `article.source_name` with `story.source_name` as fallback.
`source_count` is the case-insensitive count of distinct non-empty source names
among rendered timeline items.

The date label is local and compact:

- English: `Jul 10, 2026`
- Chinese: `2026-07-10`

No relative date labels such as "today" or "yesterday" are introduced because
they would require runtime clock semantics.

## Rendering

Extend `render_index_html(...)` with an optional
`daily_local_news_timeline: RowOneDailyLocalNewsTimeline | None = None` argument.

Render with a private helper in `templates.py`:

`_render_daily_local_news_timeline(...)`

The renderer must:

- escape titles, sources, labels, and excerpts
- render only validated same-site hrefs from the builder
- include bilingual labels via existing `data-lang` spans
- omit the section when the model is `None` or has no items
- not publish full articles on the homepage

`render_row_one_site(...)` builds the timeline after
`local_article_page_hrefs_by_story_id` is available and passes it to
`render_index_html(...)`.

## Boundaries

Stage 376 is generated-site only.

It does not:

- create `data/daily-local-news-timeline.json`
- create `data/local-news-timeline.json`
- create `data/news-timeline.json`
- create `daily-local-news-timeline.html`
- create `local-news-timeline.html`
- create `news-timeline.html`
- create new article-source sidecars
- create new route families
- alter `articles/index.html`, `articles/<story-id>.html`, or detail pages
- publish full articles on the homepage
- add outbound article URLs as primary navigation
- change row-one-app/v7
- change row-one-manifest/v1
- change row-one-runtime/v1
- change schemas or generated JSON artifacts
- change source collection, fetching, matching, extraction, scoring, ranking,
  LLM, connector, scheduling, deployment, market grouping,
  domestic/international classification, analytics, personalization,
  recommendation, or compliance-review behavior

## Product Gap Closed

Previous stages organize saved local content by theme, source, signal, reading
sequence, entity references, and health checks. They do not provide a simple
chronological news timeline. Stage 376 adds that chronological layer without
replacing or duplicating existing reading organizers.

## Test Plan

Builder tests:

- orders items newest-first with edition-order tie-breaking
- uses `article.published_at` before `story.published_at`
- links to the first non-empty local paragraph while preserving original
  one-based paragraph numbering
- filters unsafe story ids, mismatched article/story ids, unsafe article hrefs,
  missing timestamps, and blank saved text
- caps entries at six
- returns `None` without usable content

Render tests:

- homepage includes the timeline and places it between Theme Summary Strip and
  Article Intelligence Brief
- rendering escapes text and filters unsafe hrefs
- generated site writes the timeline only on `index.html`
- generated JSON contracts do not include timeline tokens
- no standalone timeline artifacts are created

Docs/workflow tests:

- README and `docs/row-one.md` include the exact Stage 376 boundary paragraph
  before Stage 375
- workflow denylist checks include timeline tokens
