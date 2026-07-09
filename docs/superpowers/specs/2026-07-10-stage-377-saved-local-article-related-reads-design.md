# Stage 377 Saved Local Article Related Reads Design

## Objective

Stage 377 adds generated-site only **Saved Local Article Related Reads** to each
ROW ONE saved local article page at `articles/<story-id>.html`.

The feature closes a concrete article-reading gap: after a reader finishes a
locally saved article, ROW ONE should offer a small set of same-site next reads
from the same daily edition, based on shared article signals, section context,
and source overlap. This makes the local article pages behave more like a
professional daily fashion-news site without fetching new content, creating new
routes, or publishing full articles outside the existing saved local article
pages.

## Product Shape

The module appears inside `articles/<story-id>.html` after the saved local
article body section. It is omitted when fewer than one related saved local read
qualifies.

The section shows up to three cards. Each card contains:

- related article title
- source name
- a concise reason label
- one capped saved-text excerpt
- up to three reference chips from the shared signal context
- a same-site link to the related local article page in article-page context

Because the module lives inside `articles/<story-id>.html`, related links use
sibling-page hrefs such as:

```text
related-story-2222222222.html#local-article-paragraph-1
related-story-2222222222.html#local-article-digest
```

They do not use homepage/library paths such as:

```text
articles/related-story-2222222222.html#local-article-paragraph-1
```

which would resolve incorrectly from inside the `articles/` directory.

## Architecture

Create a focused builder module:

`src/fashion_radar/row_one/saved_article_local_related_reads.py`

The module owns immutable dataclasses:

```python
@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadReference:
    name: str
    label: str


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadCard:
    candidate_story_id: str
    title: LocalizedText
    source_name: str
    reason: LocalizedText
    excerpt: LocalizedText
    href: str
    references: tuple[RowOneSavedArticleLocalRelatedReadReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReads:
    title: LocalizedText
    dek: LocalizedText
    current_story_id: str
    card_count: int
    cards: tuple[RowOneSavedArticleLocalRelatedReadCard, ...]
```

Expose:

```python
def build_row_one_saved_article_local_related_reads(
    *,
    current_story: RowOneStory,
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    local_article_page_hrefs_by_story_id: Mapping[str, str],
    excluded_story_ids: Collection[str] = (),
) -> RowOneSavedArticleLocalRelatedReads | None:
    ...
```

The builder is pure and deterministic. It uses only:

- the current `RowOneStory`
- the current `RowOneEdition`
- already saved local article sidecars
- already generated local article page hrefs

It does not read or write files and does not call source collectors, extractors,
rankers, LLMs, schedulers, connectors, or network clients.

## Selection Rules

The current story qualifies only when:

- `current_story.id` is a safe local article story id
- a matching `RowOneLocalArticle` exists
- `current_article.story_id == current_story.id`
- the current article has at least one non-empty saved paragraph

Each candidate story in `edition.stories` qualifies only when:

- it is not the current story
- it is not in `excluded_story_ids`
- the story id is safe
- a matching `RowOneLocalArticle` exists
- `candidate_article.story_id == candidate_story.id`
- the candidate article has at least one non-empty saved paragraph
- `local_article_page_hrefs_by_story_id[candidate_story.id]` is a safe sibling
  article-page href matching the candidate story id
- the candidate has at least one relationship signal with the current story

Relationship signals, in priority order:

1. shared normalized reference names from local article content-section items
2. same ROW ONE section key
3. same normalized source name

The builder should not create generic fill cards when no relationship signal is
present.

## Scoring And Ordering

Candidate cards are scored deterministically:

- +100 for each shared normalized reference name
- +20 for same `section_key`
- +10 for same normalized source name
- +5 when both articles have content sections

Sorting:

1. higher score first
2. higher shared-reference count first
3. same-section candidates before non-section candidates
4. same-source candidates before non-source candidates
5. original edition story order
6. story id as final stable tie-breaker

Cards are capped at three.

## Text Rules

The card title uses `candidate_story.headline`, then `candidate_article.title`,
then the candidate story id.

All title sources are plain strings, so the builder wraps the final title as
`LocalizedText(en=title, zh=title)`. Stage 377 does not introduce title
translation or LLM rewriting.

The source uses `candidate_article.source_name`, then
`candidate_story.source_name`.

The excerpt uses the first non-empty saved paragraph from the candidate article.
When `paragraphs_zh` is aligned with `paragraphs` and the matching Chinese
paragraph is non-empty, it supplies the Chinese excerpt; otherwise the English
excerpt is reused. Excerpts are whitespace-normalized and capped.

The reason label is deterministic:

- shared references:
  - English: `Shared signal: <first shared reference>`
  - Chinese: `共同信号：<first shared reference>`
- same section only:
  - English: `Same ROW ONE section`
  - Chinese: `同一 ROW ONE 栏目`
- same source only:
  - English: `Same source desk`
  - Chinese: `同一来源`

Reference chips render up to three shared references first. If fewer than three
shared references exist, the builder may add candidate-local references from
content-section items until the cap is reached. Empty and duplicate references
are omitted.

Reference extraction searches every local article content-section item and uses
only non-empty `item.references`. In current generated content this mostly means
`entities` and `product_signals`, but the builder should not hard-code those
section keys; if `takeaways` or `brand_signals` items contain references in a
future sidecar, the same normalization and deduplication rules apply.

## Href Rules

The builder receives `local_article_page_hrefs_by_story_id`, whose values are
the one-file hrefs already used to write article pages, for example:

```text
related-story-2222222222.html
```

For article-page context, output hrefs must be sibling relative links:

```text
related-story-2222222222.html#local-article-paragraph-1
related-story-2222222222.html#local-article-digest
```

The builder rejects candidate page hrefs that:

- are blank
- contain whitespace
- contain `://`
- start with `//`
- start with `/`
- start with `.`
- contain path separators
- contain `..`
- do not end in `.html`
- do not exactly match `<candidate-story-id>.html`
- reference an unsafe story id

The bare sibling page href is validated before any fragment is appended. If the
base href is rejected, the candidate is skipped and no paragraph or digest
fragment is constructed from that base.

The preferred card link target is the first candidate paragraph cited by a
content-section item that shares a reference with the current article. The
paragraph index must be an integer, not a bool, zero-based, within the candidate
paragraph list, and point to a non-empty rendered paragraph.

Fragment numbers are one-based. A model paragraph index of `0` renders as
`local-article-paragraph-1`, so the builder should use
`local_article_anchors.local_article_paragraph_anchor(paragraph_index)` instead
of constructing paragraph fragment strings by hand.

If no shared-reference paragraph qualifies, the card links to the candidate's
first non-empty paragraph. If that cannot be resolved, it links to
`#local-article-digest`.

The builder never emits paragraph fragments with `0`, leading zeros,
negative values, malformed suffixes, external URLs, absolute paths, traversal,
or homepage-context `articles/...` prefixes.

## Rendering

Extend `render_local_article_page_html(...)` with:

```python
saved_article_local_related_reads: (
    RowOneSavedArticleLocalRelatedReads | None
) = None
```

Render with a private helper in `templates.py`:

`_render_saved_article_local_related_reads(...)`

The renderer must:

- omit the section when the model is `None` or has no cards
- escape titles, sources, reason labels, excerpts, reference names, and hrefs
- preserve bilingual text with existing `data-lang` spans
- render cards after `local_article_section` so the module appears after the
  saved local article body, inside `<div class="local-article-page-article">`
  and inside `<article class="local-article-page">`
- render only same-site sibling article hrefs generated by the builder and
  drop any card whose `candidate_story_id` and `href` fail the renderer-side
  sibling href validator

`render_row_one_site(...)` should build one related-reads model for each page
inside `_write_local_article_pages(...)`, after the local article page specs and
story-id href map are available.

## Co-Existence With Local Reading Companion

ROW ONE already has `Saved Article Local Reading Companion` before the saved
body. That companion is library/organization-driven: it explains the current
article and can show "Read next locally" cards from the same organized group
when `saved_article_library` and `saved_article_content_organization` are
available.

Stage 377 is complementary, not a replacement. It appears after the saved body
and uses current-edition local article signals directly: shared references,
same ROW ONE section, and same source. It also still works when the companion
cannot build related items because library or organization inputs are absent.

When both modules co-render, `_write_local_article_pages(...)` should build the
companion first, extract safe sibling story ids from each
`companion.related_items` entry's `.href` field, and pass those ids as
`excluded_story_ids` to
`build_row_one_saved_article_local_related_reads(...)`. Stage 377 then avoids
recommending the same sibling article already shown in the companion while still
providing an after-body continuation path.

## Boundaries

Stage 377 is generated-site only.

It does not:

- create `data/saved-local-article-related-reads.json`
- create `data/local-article-related-reads.json`
- create `data/related-reads.json`
- create `saved-local-article-related-reads.html`
- create `local-article-related-reads.html`
- create `related-reads.html`
- create article-source sidecars
- create new route families
- alter `index.html`, `articles/index.html`, or organized detail pages
- publish full related articles outside existing local article pages
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

Previous stages let readers inspect the saved text of one article and browse
daily modules on the homepage/library. The existing local reading companion can
show before-body group-based next reads when its library and organization inputs
are available, but there is no after-body signal-based continuation that works
directly from same-edition local article sidecars. Stage 377 adds that
article-page continuation layer while staying inside existing current-day local
content and same-site article pages.

## Test Plan

Builder tests:

- returns related cards ordered by shared-reference, section, source, edition
  order, and story-id tie-breakers
- excludes the current article and unrelated candidates
- excludes safe story ids already recommended by the local reading companion
- prefers shared-reference paragraph anchors, then first non-empty paragraph
  anchors, then digest anchors
- uses aligned `paragraphs_zh` as the Chinese excerpt when present and falls
  back to the English excerpt when it is absent or blank
- rejects unsafe story ids, mismatched article/story ids, unsafe sibling hrefs,
  blank articles, bool paragraph indices, invalid paragraph indices, and
  homepage-context `articles/...` hrefs
- caps cards at three
- normalizes/deduplicates reference chips and caps chips at three
- returns `None` when no related saved local reads qualify

Render tests:

- article pages render the related reads section after the saved local article
  body
- related hrefs are sibling article-page links, not `articles/...` links
- unsafe hrefs are not rendered
- `_companion_related_story_ids(...)` accepts valid sibling `.href` values from
  `companion.related_items`, dedupes safe story ids, and rejects
  homepage-context `articles/...` hrefs, external URLs, absolute paths,
  unsafe story ids, malformed fragments, and absent companions. Valid companion
  fragments include `local-article-digest`, `local-article-paragraph-N`, and
  `local-article-content-section-N`.
- HTML escapes dynamic titles, sources, reasons, excerpts, and reference chips
- the section is omitted when the model is absent or empty
- CSS selectors for the module exist

Integration/workflow tests:

- `render_row_one_site(...)` writes related reads only into
  `articles/<story-id>.html`
- no new data artifact or route family is generated
- app/runtime/manifest/schema contracts remain unchanged
- Stage 377 docs preserve the generated-site-only boundary
