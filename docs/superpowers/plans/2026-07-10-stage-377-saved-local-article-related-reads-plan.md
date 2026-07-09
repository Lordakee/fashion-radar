# Stage 377 Saved Local Article Related Reads Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site only related saved local reads to `articles/<story-id>.html` so every saved local article can point readers to relevant same-site next reads from the same daily edition.

**Architecture:** Add one pure builder module that derives related-read cards from the current story, current edition stories, saved local article sidecars, content-section references, and already generated local article page hrefs. Wire the optional model into `_write_local_article_pages(...)` and `render_local_article_page_html(...)`, render it after the saved local article body, exclude safe sibling story ids already recommended by the pre-body local reading companion, and keep generated data artifacts, app/runtime/manifest contracts, source collection, and routing families unchanged.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, existing `templates.py` HTML helper style, pytest, ruff, uv with frozen `--no-config` commands.

---

## Product Gap

Stage 377 closes the article-page "read next" gap in the collect -> match ->
report pipeline. ROW ONE already saves full local article pages and homepage
organizers, but a reader finishing one saved local article has no same-site path
to a signal-based next relevant saved read at the end of the article body. The
existing pre-body local reading companion can show group-based "Read next
locally" cards when library and organization inputs are available; Stage 377 is
a post-body continuation layer that excludes companion candidates to avoid
duplicate same-page recommendations.

## File Map

- Create `src/fashion_radar/row_one/saved_article_local_related_reads.py`
  - Owns dataclasses, candidate filtering, safe sibling href validation,
    reference extraction, scoring, excerpt selection, and deterministic ordering.
  - Accepts `excluded_story_ids` so render integration can avoid repeating
    local reading companion candidates.
- Modify `src/fashion_radar/row_one/render.py`
  - Imports the builder.
  - Builds a story-id href map from current local article page specs.
  - Uses existing `_local_article_page_hrefs_by_story_id(page_specs)` rather
    than deriving page hrefs from raw story ids.
  - Builds one related-reads model per local article page inside
    `_write_local_article_pages(...)`.
  - Extracts safe story ids from `companion.related_items` and passes them to
    the new builder as exclusions.
  - Passes the optional model into `render_local_article_page_html(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Imports the new model.
  - Adds an optional `saved_article_local_related_reads` argument to
    `render_local_article_page_html(...)`.
  - Adds `_render_saved_article_local_related_reads(...)` and card/reference
    helpers.
  - Adds CSS selectors for the article-page related reads module.
- Create `tests/test_row_one_saved_article_local_related_reads.py`
  - Unit tests for builder behavior and href safety.
- Modify `tests/test_row_one_render.py`
  - Article-page rendering, placement, escaping, sibling hrefs, omission, CSS.
- Modify `tests/test_workflows.py`
  - Generated-site-only denylist for Stage 377 artifact/route names.
- Modify `tests/test_row_one_docs.py`
  - Stage 377 docs boundary and ordering test.
- Modify `README.md` and `docs/row-one.md`
  - Add Stage 377 generated-site-only documentation above Stage 376.
- Create review records under `docs/reviews/` during plan/code review.

## Task 1: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-377-plan-review.md`
- Create: `docs/reviews/opencode-stage-377-plan-review.md`
- Modify if needed: `docs/superpowers/specs/2026-07-10-stage-377-saved-local-article-related-reads-design.md`
- Modify if needed: `docs/superpowers/plans/2026-07-10-stage-377-saved-local-article-related-reads-plan.md`

- [ ] **Step 1: Ask Claude Code to review the plan**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 377 Saved Local Article Related Reads plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-10-stage-377-saved-local-article-related-reads-design.md and docs/superpowers/plans/2026-07-10-stage-377-saved-local-article-related-reads-plan.md. Goal: add generated-site-only related saved local reads inside articles/<story-id>.html using current-edition stories, saved local article sidecars, content-section references, and generated local article page routes. Technical stack: Python dataclasses, existing ROW ONE models, templates.py, render.py, pytest, ruff, uv. Implementation method: pure builder module, optional render_local_article_page_html model, _write_local_article_pages integration after story-id local article href map exists, no generated JSON artifacts or app/runtime/manifest contract changes. Check feasibility, article-page sibling href safety, placement after saved local article body, generated-site-only boundaries, duplication with existing homepage/library modules, selection scoring, and test plan. Return findings only ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-377-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains a complete review body.

- [ ] **Step 2: Ask opencode to cross-check the plan**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 377 Saved Local Article Related Reads plan/spec. Read docs/reviews/claude-code-stage-377-plan-review.md if present, docs/superpowers/specs/2026-07-10-stage-377-saved-local-article-related-reads-design.md, and docs/superpowers/plans/2026-07-10-stage-377-saved-local-article-related-reads-plan.md. Check feasibility, article-page sibling href safety, generated-site-only boundaries, test coverage, docs boundaries, and whether the feature duplicates existing ROW ONE sections. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-377-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains a complete review body.

- [ ] **Step 3: Fix Critical and Important plan findings**

If either review raises Critical or Important findings, update the spec/plan and
run matching rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 377 Saved Local Article Related Reads plan/spec after fixes. Return remaining Critical and Important findings only." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-377-plan-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 377 Saved Local Article Related Reads plan/spec after fixes. Return remaining Critical and Important findings only." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-377-plan-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important planning findings.

## Task 2: Builder RED Tests

**Files:**
- Create: `tests/test_row_one_saved_article_local_related_reads.py`

- [ ] **Step 1: Add builder fixtures**

Create fixtures for model-valid `RowOneEdition`, `RowOneStory`,
`RowOneLocalArticle`, `RowOneLocalArticleContentSection`,
`RowOneLocalArticleContentItem`, and `RowOneReference`.

Use this fixture shape:

```python
from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentKey,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)


def _text(value: str) -> LocalizedText:
    return LocalizedText(en=value, zh=value)


def _ref(name: str, *, label: str = "Brand") -> RowOneReference:
    return RowOneReference(name=name, type=label.lower(), label=label)


def _story(
    story_id: str,
    *,
    headline: str | None = None,
    section_key: RowOneSectionKey = "top_stories",
    source_name: str = "Vogue Business",
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        story_type="tracked_entity",
        headline=headline or f"Headline {story_id}",
        summary=_text(f"Summary {story_id}"),
        why_it_matters=_text(f"Why {story_id} matters"),
        editorial_takeaway=_text(f"Takeaway {story_id}"),
        signal_context=_text(f"Signal {story_id}"),
        reader_path=_text(f"Reader path {story_id}"),
        source_name=source_name,
        detail_path=f"details/{story_id}.html",
    )


def _content_section(
    title: str,
    *,
    key: RowOneLocalArticleContentKey = "entities",
    refs: list[RowOneReference],
    paragraph_indices: list[int],
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,
        title=_text(title),
        body=_text(f"{title} body"),
        items=[
            RowOneLocalArticleContentItem(
                label=_text(f"{title} item"),
                body=_text(f"{title} item body"),
                references=refs,
                paragraph_indices=paragraph_indices,
            )
        ],
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=paragraphs_zh or [],
        brief_sections=[],
        content_sections=content_sections or [],
        body_source="extracted",
        skipped=False,
    )


def _edition(*stories: RowOneStory) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        edition_date=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        summary=_text("Daily fashion intelligence."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=_text("Top Stories"),
                dek=_text("Top stories."),
            ),
            RowOneSection(
                key="brand_moves",
                title=_text("Brand Moves"),
                dek=_text("Brand moves."),
            ),
        ],
        stories=list(stories),
    )


def _hrefs(*stories: RowOneStory) -> dict[str, str]:
    return {story.id: f"{story.id}.html" for story in stories}
```

`paragraph_indices` is intentionally a `list[int]` because
`RowOneLocalArticleContentItem.paragraph_indices` is modeled as a list. Use only
valid content-section keys: `"takeaways"`, `"entities"`, `"product_signals"`,
or `"brand_signals"`.

- [ ] **Step 2: Add failing builder tests**

Add these tests:

- `test_saved_article_local_related_reads_scores_shared_refs_section_source`
- `test_saved_article_local_related_reads_filters_unrelated_and_current_article`
- `test_saved_article_local_related_reads_filters_excluded_companion_story_ids`
- `test_saved_article_local_related_reads_prefers_shared_ref_paragraph_anchor`
- `test_saved_article_local_related_reads_uses_aligned_paragraphs_zh_excerpt`
- `test_saved_article_local_related_reads_rejects_unsafe_hrefs_and_bad_indices`
- `test_saved_article_local_related_reads_rejects_mismatched_story_href`
- `test_saved_article_local_related_reads_caps_cards_and_reference_chips`
- `test_saved_article_local_related_reads_returns_none_without_related_cards`

Expected assertion examples:

```python
related = build_row_one_saved_article_local_related_reads(
    current_story=current,
    edition=edition,
    local_articles_by_story_id=articles,
    local_article_page_hrefs_by_story_id=hrefs,
)
assert related is not None
assert [card.title.en for card in related.cards] == [
    "Shared The Row signal",
    "Same section read",
    "Same source read",
]
assert related.cards[0].href == "shared-row-2222222222.html#local-article-paragraph-2"
assert related.cards[0].candidate_story_id == "shared-row-2222222222"
assert "articles/shared-row-2222222222.html" not in related.cards[0].href
assert related.cards[0].reason.en == "Shared signal: The Row"
assert [ref.name for ref in related.cards[0].references] == ["The Row"]
assert related.card_count == len(related.cards)
```

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
```

Expected: fails because `fashion_radar.row_one.saved_article_local_related_reads`
does not exist yet.

## Task 3: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_local_related_reads.py`
- Test: `tests/test_row_one_saved_article_local_related_reads.py`

- [ ] **Step 1: Implement dataclasses and constants**

Create:

```python
SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS = 3
SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS = 3
SAVED_ARTICLE_LOCAL_RELATED_READS_EXCERPT_CHARS = 180


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadReference:
    name: str
    label: str
```

Continue with the three dataclasses from the spec. The card dataclass must
include `candidate_story_id: str` before `title` so the renderer can revalidate
that `href` targets the expected sibling article page. Import:

```python
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.local_article_anchors import local_article_paragraph_anchor
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph
```

- [ ] **Step 2: Implement safe sibling href validation**

Add:

```python
def _safe_sibling_article_href(story_id: str, href: str) -> str | None:
    clean = href.strip()
    expected = f"{story_id}.html"
    if clean != href or clean != expected:
        return None
    if (
        not safe_local_article_story_id(story_id)
        or not clean.endswith(".html")
        or any(ch.isspace() for ch in clean)
        or "://" in clean
        or clean.startswith(("//", "/", "."))
        or "/" in clean
        or "\\" in clean
        or ".." in clean
    ):
        return None
    return clean
```

- [ ] **Step 3: Implement reference and paragraph helpers**

Add helpers:

```python
def _reference_key(reference: RowOneReference) -> str:
    return normalize_row_one_paragraph(reference.name).casefold()


def _valid_paragraph_index(index: object, article: RowOneLocalArticle) -> int | None:
    if isinstance(index, bool) or not isinstance(index, int):
        return None
    if index < 0 or index >= len(article.paragraphs):
        return None
    if not normalize_row_one_paragraph(article.paragraphs[index]):
        return None
    return index
```

Also add `_article_references(...)`, `_shared_reference_names(...)`,
`_first_nonblank_paragraph(...)`, `_shared_reference_paragraph(...)`,
`_excerpt(...)`, `_localized_excerpt(...)`, and `_reference_chips(...)` using
the exact rules in the spec. Paragraph indices from content-section items are
zero-based model values; call `local_article_paragraph_anchor(index)` to build
one-based HTML fragments such as `local-article-paragraph-2` for index `1`.
Add one builder test fixture where `paragraphs_zh` has the same length as
`paragraphs` and a non-empty aligned paragraph, and assert the card excerpt uses
that Chinese text.

- [ ] **Step 4: Implement builder scoring and output**

Implement:

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

The function must return `None` for invalid current article state, skip
unrelated candidates, skip safe candidates in `excluded_story_ids`, score and
sort candidates as specified, cap to three cards, and set:

```python
title=LocalizedText(en="Related Saved Local Reads", zh="相关本地保存阅读")
dek=LocalizedText(
    en="Same-edition reads connected by references, section, or source.",
    zh="按同日信号、栏目或来源连接的相关阅读。",
)
```

When building `RowOneSavedArticleLocalRelatedReadCard.title`, select the first
non-empty string from `candidate_story.headline`, `candidate_article.title`, and
candidate story id, then wrap it as `LocalizedText(en=title, zh=title)`. Stage
377 does not create translated titles. Set `candidate_story_id` to the safe
candidate story id used for the sibling article href.
Always set `card_count=len(cards)` in the returned model and assert this in
builder tests.

- [ ] **Step 5: Verify builder tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
```

Expected: all tests in the file pass.

## Task 4: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add article-page render tests**

Add tests that import the new dataclasses and call `render_local_article_page_html(...)`
directly:

- `test_render_local_article_page_includes_related_reads_after_local_article_body`
- `test_render_local_article_page_escapes_related_reads_content`
- `test_render_local_article_page_omits_empty_related_reads`
- `test_render_local_article_page_drops_related_read_with_mismatched_story_id_href`
- `test_render_local_article_page_related_reads_css_exists`
- `test_companion_related_story_ids_accepts_only_safe_sibling_hrefs`
- `test_render_row_one_site_excludes_companion_related_story_from_post_body_related_reads`

Concrete assertions:

```python
assert '<section class="saved-article-local-related-reads"' in html
assert html.index('id="local-article"') < html.index(
    'class="saved-article-local-related-reads"'
)
article_body = html.split('<div class="local-article-page-article">', 1)[1]
assert article_body.index('id="local-article"') < article_body.index(
    'class="saved-article-local-related-reads"'
)
assert article_body.index('class="saved-article-local-related-reads"') < (
    article_body.rindex("</div>")
)
assert 'href="related-row-2222222222.html#local-article-paragraph-1"' in html
assert "articles/related-row-2222222222.html" not in html
assert "&lt;script&gt;" in html
```

- [ ] **Step 2: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "related_reads"
```

Expected: fails because `render_local_article_page_html(...)` has no
`saved_article_local_related_reads` argument and the renderer does not exist.

## Task 5: Render Integration

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/row_one/render.py`
- Test: `tests/test_row_one_render.py`

- [ ] **Step 1: Add template import and function argument**

Import `RowOneSavedArticleLocalRelatedReads` in `templates.py`.
Also import `safe_local_article_story_id` from
`fashion_radar.row_one.articles` for renderer-side href validation.

Update `render_local_article_page_html(...)` signature:

```python
saved_article_local_related_reads: (
    RowOneSavedArticleLocalRelatedReads | None
) = None,
```

- [ ] **Step 2: Render the module after the local article section**

Inside `render_local_article_page_html(...)`, compute:

```python
local_related_reads = _render_saved_article_local_related_reads(
    saved_article_local_related_reads
)
```

Place `{local_related_reads}` immediately after `{local_article_section}` in the
article page HTML, before the closing `</div>` for
`<div class="local-article-page-article">`. This keeps the module inside the
saved article reading container and inside `<article class="local-article-page">`.

- [ ] **Step 3: Add template helpers**

Implement:

```python
def _render_saved_article_local_related_reads(
    related_reads: RowOneSavedArticleLocalRelatedReads | None,
) -> str:
    if related_reads is None or not related_reads.cards:
        return ""
    ...
```

Render cards with escaped bilingual title, dek, reason, excerpt, references,
and href. The renderer should re-check each card href before emitting it and
drop cards with unsafe hrefs. It should not rewrite hrefs or convert sibling
links into homepage-context `articles/...` links.

The renderer-side check should use both `card.candidate_story_id` and
`card.href`. It should accept only:

```python
f"{card.candidate_story_id}.html#local-article-digest"
```

or:

```python
f"{card.candidate_story_id}.html#local-article-paragraph-N"
```

where `N` is a positive integer without leading zeroes. It should reject
protocols, protocol-relative URLs, absolute paths, leading dots, slashes before
the fragment, whitespace, traversal, mismatched story ids, unsafe story ids,
fragment `0`, leading-zero fragments, malformed fragments, and external URLs.
Name the private helper `_safe_saved_article_local_related_read_href(...)` so
tests and future reviews can locate the defense-in-depth check.

- [ ] **Step 4: Add CSS selectors**

Add selectors near the local article page CSS block:

```css
.saved-article-local-related-reads { ... }
.saved-article-local-related-reads-header { ... }
.saved-article-local-related-reads-grid { ... }
.saved-article-local-related-read-card { ... }
.saved-article-local-related-read-meta { ... }
.saved-article-local-related-read-references { ... }
.saved-article-local-related-read-reference { ... }
```

Use an adjacent locator near existing local article page/companion styles in
`ROW_ONE_CSS` so future stages can find this module without scanning the whole
template file.

- [ ] **Step 5: Wire render.py**

Import the builder:

```python
from fashion_radar.row_one.saved_article_local_related_reads import (
    build_row_one_saved_article_local_related_reads,
)
```

Inside `_write_local_article_pages(...)`, derive:

```python
hrefs_by_story_id = _local_article_page_hrefs_by_story_id(page_specs)
```

This intentionally recomputes the pure story-id map from the already
materialized `page_specs` at the article-page write boundary. It keeps
`_write_local_article_pages(...)` self-contained without changing its public
call sites, and it must use the helper rather than rebuilding hrefs from raw
story ids.

Add a private render helper near `_write_local_article_pages(...)`:

```python
def _companion_related_story_ids(
    companion: RowOneSavedArticleLocalReadingCompanion | None,
) -> tuple[str, ...]:
    ...
```

It should inspect each `companion.related_items` entry's existing `.href`
attribute, accept only sibling hrefs shaped as
`<story-id>.html#local-article-digest` or
`<story-id>.html#local-article-paragraph-N` or
`<story-id>.html#local-article-content-section-N`, extract `<story-id>`, reject
unsafe ids with `safe_local_article_story_id`, dedupe while preserving companion
order, and return an empty tuple when the companion is absent. It must not parse
external URLs, detail-page hrefs, or homepage-context `articles/...` hrefs.

Add a focused render test for this helper:

```python
assert _companion_related_story_ids(None) == ()
assert _companion_related_story_ids(_companion_with_hrefs(
    "safe-row-1111111111.html#local-article-digest",
    "safe-row-1111111111.html#local-article-paragraph-1",
    "section-row-3333333333.html#local-article-content-section-3",
    "second-row-2222222222.html#local-article-paragraph-2",
)) == ("safe-row-1111111111", "section-row-3333333333", "second-row-2222222222")
assert _companion_related_story_ids(_companion_with_hrefs(
    "articles/safe-row-1111111111.html#local-article-digest",
    "https://example.com/safe-row-1111111111.html#local-article-digest",
    "/safe-row-1111111111.html#local-article-digest",
    "../details/safe-row-1111111111.html#local-article-digest",
    "bad story.html#local-article-digest",
    "safe-row-1111111111.html#local-article-paragraph-0",
)) == ()
```

`_companion_with_hrefs(...)` should construct a minimal
`RowOneSavedArticleLocalReadingCompanion` whose `related_items` contain
`RowOneSavedArticleLocalReadingCompanionItem(href=value, ...)`. The helper must
read the existing `.href` attribute exactly.

For each page:

```python
excluded_story_ids = _companion_related_story_ids(companion)
related_reads = build_row_one_saved_article_local_related_reads(
    current_story=story,
    edition=edition,
    local_articles_by_story_id=local_articles_by_story_id,
    local_article_page_hrefs_by_story_id=hrefs_by_story_id,
    excluded_story_ids=excluded_story_ids,
)
```

Pass it to `render_local_article_page_html(...)`.

- [ ] **Step 6: Verify render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "related_reads"
```

Expected: all related-read render tests pass.

## Task 6: Workflow And Docs RED Tests

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add generated-site-only workflow guard**

Add a Stage 377 denylist assertion that generated output does not contain:

```python
{
    "data/saved-local-article-related-reads.json",
    "data/local-article-related-reads.json",
    "data/related-reads.json",
    "saved-local-article-related-reads.html",
    "local-article-related-reads.html",
    "related-reads.html",
}
```

- [ ] **Step 2: Add docs ordering test**

Update the docs test so Stage 377 appears above Stage 376 in both `README.md`
and `docs/row-one.md` and states the generated-site-only boundary.

- [ ] **Step 3: Verify RED where docs are not yet updated**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q -k "stage_377 or related_reads"
```

Expected: docs-related tests fail until README and `docs/row-one.md` are updated.

## Task 7: Docs And Focused Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Test: `tests/test_workflows.py`
- Test: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add Stage 377 docs**

Add a concise Stage 377 paragraph above Stage 376:

```markdown
Stage 377 adds generated-site only Saved Local Article Related Reads inside
`articles/<story-id>.html`. Each saved local article can now show up to three
same-edition next reads connected by shared references, section, or source,
using sibling same-site article links and short saved-text excerpts. It creates
no new JSON artifact, route family, source connector, scheduler, app/runtime
contract, manifest field, schema, ranking system, or compliance-review feature.
```

- [ ] **Step 2: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q -k "related_reads or stage_377"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_local_related_reads.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_local_related_reads.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_local_related_reads.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_local_related_reads.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
```

Expected: focused tests and lint/format checks pass.

## Task 8: Code Review, Full Gates, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-377-code-review.md`
- Create: `docs/reviews/opencode-stage-377-code-review.md`
- Modify if needed: implementation files from Tasks 3-7

- [ ] **Step 1: Ask Claude Code to review new code**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 377 code in /home/ubuntu/fashion-radar. Focus on newly added Saved Local Article Related Reads implementation and tests. Check builder correctness, article-page sibling href safety, placement after saved local article body, escaping, generated-site-only boundaries, no app/runtime/manifest/schema/route artifact leakage, and test adequacy. Return findings only ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-377-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 2: Ask opencode to cross-check new code**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 377 code. Read docs/reviews/claude-code-stage-377-code-review.md if present and the changed files for Saved Local Article Related Reads. Check builder correctness, article-page sibling href safety, escaping, generated-site-only boundaries, and test adequacy. Return final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-377-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 3: Fix Critical and Important code findings**

If either reviewer raises Critical or Important findings, patch the code/tests
and run matching rereviews saved as:

- `docs/reviews/claude-code-stage-377-code-rereview.md`
- `docs/reviews/opencode-stage-377-code-rereview.md`

- [ ] **Step 4: Run full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
git diff --cached --check
```

Expected: all commands pass.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-07-10-stage-377-saved-local-article-related-reads-design.md \
  docs/superpowers/plans/2026-07-10-stage-377-saved-local-article-related-reads-plan.md \
  docs/reviews/claude-code-stage-377-plan-review.md \
  docs/reviews/opencode-stage-377-plan-review.md \
  docs/reviews/claude-code-stage-377-code-review.md \
  docs/reviews/opencode-stage-377-code-review.md \
  src/fashion_radar/row_one/saved_article_local_related_reads.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_saved_article_local_related_reads.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/row-one.md
git commit -m "Stage 377: add saved local article related reads"
git push origin main
```

Expected: commit and push succeed.

- [ ] **Step 6: Write Handoff Summary**

Report:

- repo status
- pushed commit hash
- verified commands
- uncommitted files
- next recommended stage
