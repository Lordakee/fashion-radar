# Stage 371 Daily Local Saved Article Organizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Daily Local Saved Article Organizer to the ROW ONE homepage.

**Architecture:** Build a focused homepage aggregate from current-edition saved local article sidecars and generated local article page anchors, then render it in `index.html` after Stage 370 Daily Local Article Intelligence Brief and before Saved Article Content Organization. Keep the feature out of app contracts, JSON artifacts, article pages, detail pages, source collection, fetching, scoring, LLM, connector, scheduling, analytics, recommendation, and compliance-review paths.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, static HTML string templates, existing CSS bundle in `templates.py`, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config`.

---

## File Structure

- Create `src/fashion_radar/row_one/daily_local_saved_article_organizer.py`
  - Builds `RowOneDailyLocalSavedArticleOrganizer | None`.
  - Owns lane/card/reference dataclasses, excerpting, grouping, safe page href validation, paragraph index validation, and caps.
- Create `tests/test_row_one_daily_local_saved_article_organizer.py`
  - Builder tests only.
- Modify `src/fashion_radar/row_one/render.py`
  - Import builder.
  - Build organizer after `local_article_page_hrefs_by_story_id`.
  - Pass organizer into `render_index_html`.
  - Do not write new artifacts.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import organizer dataclasses.
  - Add optional `daily_local_saved_article_organizer` parameter to `render_index_html`.
  - Render after `{daily_local_article_intelligence_brief_section}` and before `{saved_article_content_organization_section}`.
  - Add render helpers and CSS selectors.
- Modify `tests/test_row_one_render.py`
  - Render fixture, unsafe href filtering, homepage-only integration, CSS selector/mobile tests.
- Modify `README.md` and `docs/row-one.md`
  - Add exact Stage 371 boundary paragraph before Stage 370.
- Modify `tests/test_row_one_docs.py`
  - Exact paragraph and stale phrase guard.
- Modify `tests/test_workflows.py`
  - App contract denylist, artifact stem denylist, generated-site-only wrapper guard.
- Add review artifacts:
  - `docs/reviews/claude-code-stage-371-plan-review.md`
  - `docs/reviews/opencode-stage-371-plan-review.md`
  - `docs/reviews/claude-code-stage-371-code-review.md`
  - `docs/reviews/opencode-stage-371-code-review.md`

## Plan Review Fixes Incorporated

The Claude Code and opencode plan reviews approved the stage with local fixes. The implementation in this plan must treat the following points as authoritative:

- `_read_first_card` must never hardcode `#local-article-paragraph-1` unless paragraph index `0` is present and non-empty. If a brief section supplies the excerpt, first derive the existing paragraph anchor through `_first_paragraph`; if no paragraph anchor exists, skip the brief card.
- Content-section items with valid `paragraph_indices` may use the first valid indexed paragraph as a fallback excerpt when `item.body` is empty. Invalid indices, negative indices, bools, out-of-range indices, duplicates, and blank paragraphs are ignored.
- Content-section items with only a label/title and no item body, no valid paragraph fallback, and no section body are omitted so the organizer remains article-backed rather than label-only navigation.
- The `entities`, `brand`, and `people` content-section families map to `people_brands`; `product` maps to `products`. Items outside these families and without recognized reference labels are intentionally omitted and covered by tests.
- `source_context` must use source name and `row_one_body_source_label(article.body_source)` context so it is not a duplicate of `read_first`; it may still deep-link to the first available paragraph anchor.
- The render-time `_safe_daily_local_saved_article_organizer_href` helper must reject whitespace, traversal, absolute paths, protocol URLs, `//`, empty fragments, and zero-valued anchors while accepting only `articles/<safe-story-id>.html#local-article-content-section-N` and `articles/<safe-story-id>.html#local-article-paragraph-N`.
- Daily Local Saved Article Organizer mobile CSS must be placed inside the existing responsive `@media` block, and tests must also assert the desktop `repeat(4, minmax(0, 1fr))` rule remains.

---

### Task 1: Builder Tests

**Files:**
- Create: `tests/test_row_one_daily_local_saved_article_organizer.py`

- [ ] **Step 1: Write the failing builder tests**

Create `tests/test_row_one_daily_local_saved_article_organizer.py` with:

```python
from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_saved_article_organizer import (
    DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE,
    DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD,
    build_row_one_daily_local_saved_article_organizer,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 9, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _ref(name: str, *, ref_type: str = "brand", label: str = "brand") -> RowOneReference:
    return RowOneReference(name=name, type=ref_type, label=label)


def _story(story_id: str, *, headline: str | None = None) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline or f"Headline {story_id}",
        summary=_lt("Summary", "摘要"),
        why_it_matters=_lt("Why it matters", "为什么重要"),
        editorial_takeaway=_lt("Takeaway", "编辑判断"),
        signal_context=_lt("Signal context", "信号背景"),
        reader_path=_lt("Reader path", "阅读路径"),
        source_name="Vogue Business",
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
        entity_refs=[],
    )


def _edition(*stories: RowOneStory) -> RowOneEdition:
    return RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=_lt("Daily summary", "每日摘要"),
        sections=[
            RowOneSection(
                key="top_stories",
                title=_lt("Top Stories", "今日重点"),
                dek=_lt("Top saved reads", "重点保存阅读"),
            )
        ],
        stories=list(stories),
    )


def _brief(body: str) -> RowOneLocalArticleBriefSection:
    return RowOneLocalArticleBriefSection(
        key="why_it_matters",
        title=_lt("Why It Matters", "为什么重要"),
        body=_lt(body, f"{body} zh"),
    )


def _item(
    label: str,
    *,
    body: str | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=_lt(body or f"{label} support", f"{label} 支撑"),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str,
    *,
    key: str = "brand_signals",
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, f"{title} zh"),
        body=_lt(f"{title} section body", f"{title} 栏目正文"),
        items=items or [],
    )


def _article(
    story_id: str,
    *,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"Local article {story_id}",
        url="https://example.com/source",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs
        or [
            "The Row leads the saved local story with a sharper retail read.",
            "The Margaux bag turns the read into product evidence.",
            "Mary-Kate Olsen gives the coverage a people and brand frame.",
        ],
        paragraphs_zh=[
            "The Row 以更清晰的零售解读开启本地保存故事。",
            "Margaux 包把阅读转化为单品证据。",
            "Mary-Kate Olsen 为报道提供人物与品牌框架。",
        ],
        brief_sections=[_brief("Read this first because it frames the local article.")],
        content_sections=content_sections
        if content_sections is not None
        else [
            _section(
                "People & Brands",
                key="brand_signals",
                items=[
                    _item(
                        "The Row",
                        references=[
                            _ref("The Row", ref_type="brand", label="brand"),
                            _ref("Mary-Kate Olsen", ref_type="designer", label="person"),
                        ],
                        paragraph_indices=[0, 2],
                    )
                ],
            ),
            _section(
                "Products",
                key="product_signals",
                items=[
                    _item(
                        "Margaux bag",
                        references=[
                            _ref("Margaux bag", ref_type="bag", label="product"),
                            _ref("Ballet flat", ref_type="shoe", label="product"),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )


def test_build_daily_local_saved_article_organizer_groups_saved_content() -> None:
    story = _story("the-row-signal-1234567890", headline="The Row signal")

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(story),
        {story.id: _article(story.id)},
        {story.id: f"{story.id}.html"},
    )

    assert organizer is not None
    assert organizer.title.en == "Daily Local Saved Article Organizer"
    assert organizer.title.zh == "每日保存文章整理器"
    assert organizer.article_count == 1
    assert organizer.card_count >= 4
    by_key = {lane.key: lane for lane in organizer.lanes}
    assert [lane.key for lane in organizer.lanes] == [
        "read_first",
        "people_brands",
        "products",
        "source_context",
    ]
    assert by_key["read_first"].cards[0].excerpt.en == (
        "Read this first because it frames the local article."
    )
    assert by_key["people_brands"].cards[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-content-section-1"
    )
    assert by_key["products"].cards[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-content-section-2"
    )
    assert by_key["source_context"].cards[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-paragraph-1"
    )
    assert [ref.name for ref in by_key["products"].cards[0].references] == [
        "Margaux bag",
        "Ballet flat",
    ]


def test_build_daily_local_saved_article_organizer_filters_unsafe_inputs() -> None:
    valid = _story("valid-signal-1111111111")
    mismatched = _story("mismatched-signal-2222222222")
    unsafe = _story("unsafe/story")
    bad_href = _story("bad-href-3333333333")

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(valid, mismatched, unsafe, bad_href),
        {
            valid.id: _article(valid.id),
            mismatched.id: _article("other-signal-4444444444"),
            unsafe.id: _article(unsafe.id),
            bad_href.id: _article(bad_href.id),
        },
        {
            valid.id: f"{valid.id}.html",
            mismatched.id: f"{mismatched.id}.html",
            unsafe.id: "unsafe/story.html",
            bad_href.id: "../bad-href-3333333333.html",
        },
    )

    assert organizer is not None
    emitted = repr(organizer)
    assert "articles/valid-signal-1111111111.html" in emitted
    assert "../" not in emitted
    assert "unsafe/story" not in emitted
    assert "mismatched-signal-2222222222.html" not in emitted
    assert "bad-href-3333333333.html" not in emitted


def test_build_daily_local_saved_article_organizer_caps_and_dedupes() -> None:
    story = _story("cap-signal-1111111111")
    refs = [
        _ref("The Row", ref_type="brand", label="brand"),
        _ref("Margaux bag", ref_type="bag", label="product"),
        _ref("Ballet flat", ref_type="shoe", label="product"),
        _ref("Mary-Kate Olsen", ref_type="designer", label="person"),
        _ref("Hidden overflow", ref_type="brand", label="brand"),
    ]
    article = _article(
        story.id,
        content_sections=[
            _section(
                f"Products {index}",
                key="product_signals",
                items=[
                    _item(
                        f"Margaux bag {index}",
                        references=refs,
                        paragraph_indices=[0, 1],
                    )
                ],
            )
            for index in range(6)
        ],
    )

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert organizer is not None
    by_key = {lane.key: lane for lane in organizer.lanes}
    assert len(by_key["products"].cards) == DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE
    assert (
        len(by_key["products"].cards[0].references)
        == DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD
    )
    assert "Hidden overflow" not in repr(by_key["products"].cards[0])
    assert "Products 5" not in repr(organizer)


def test_build_daily_local_saved_article_organizer_returns_none_without_content() -> None:
    story = _story("empty-signal-1111111111")

    assert (
        build_row_one_daily_local_saved_article_organizer(
            _edition(story),
            {},
            {story.id: f"{story.id}.html"},
        )
        is None
    )
    assert (
        build_row_one_daily_local_saved_article_organizer(
            _edition(story),
            {story.id: _article(story.id, paragraphs=["", " "], content_sections=[])},
            {story.id: f"{story.id}.html"},
        )
        is None
    )
```

- [ ] **Step 2: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_saved_article_organizer.py -q
```

Expected: import failure for `fashion_radar.row_one.daily_local_saved_article_organizer`.

---

### Task 2: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/daily_local_saved_article_organizer.py`
- Test: `tests/test_row_one_daily_local_saved_article_organizer.py`

- [ ] **Step 1: Implement the builder**

Create `src/fashion_radar/row_one/daily_local_saved_article_organizer.py` with:

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_LANES = 4
DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE = 3
DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD = 4
DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS = 180


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizerReference:
    name: str
    label: str


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizerCard:
    title: LocalizedText
    source_name: str
    lane_label: LocalizedText
    excerpt: LocalizedText
    href: str
    references: tuple[RowOneDailyLocalSavedArticleOrganizerReference, ...] = ()


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizerLane:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: tuple[RowOneDailyLocalSavedArticleOrganizerCard, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizer:
    title: LocalizedText = field(
        default_factory=lambda: LocalizedText(
            en="Daily Local Saved Article Organizer",
            zh="每日保存文章整理器",
        )
    )
    dek: LocalizedText = field(
        default_factory=lambda: LocalizedText(
            en="Short, article-backed lanes from today's saved local text.",
            zh="从今日保存本地正文整理出的短篇编辑阅读线。",
        )
    )
    article_count: int = 0
    source_count: int = 0
    card_count: int = 0
    reference_count: int = 0
    lanes: tuple[RowOneDailyLocalSavedArticleOrganizerLane, ...] = ()


_LANE_TITLES = {
    "read_first": LocalizedText(en="Read First", zh="优先阅读"),
    "people_brands": LocalizedText(en="People & Brands", zh="品牌与人物"),
    "products": LocalizedText(en="Products", zh="单品"),
    "source_context": LocalizedText(en="Source Context", zh="来源语境"),
}
_LANE_DEKS = {
    "read_first": LocalizedText(
        en="The shortest route into today's saved article set.",
        zh="进入今日保存文章组的最短阅读路径。",
    ),
    "people_brands": LocalizedText(
        en="Brand, designer, celebrity, and people context pulled from saved text.",
        zh="从保存正文提取品牌、设计师、明星与人物语境。",
    ),
    "products": LocalizedText(
        en="Product evidence and item-level cues from the local articles.",
        zh="来自本地文章的单品证据与物件级线索。",
    ),
    "source_context": LocalizedText(
        en="Where the saved read came from and what the first local paragraph says.",
        zh="保存阅读来自哪里，以及第一段本地正文说了什么。",
    ),
}
_PEOPLE_BRAND_TYPES = {
    "brand",
    "designer",
    "person",
    "people",
    "celebrity",
    "founder",
    "creative_director",
}
_PRODUCT_TYPES = {
    "product",
    "bag",
    "shoe",
    "shoes",
    "sneaker",
    "flat",
    "boot",
    "apparel",
    "accessory",
    "watch",
    "jewelry",
    "fragrance",
}


def build_row_one_daily_local_saved_article_organizer(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalSavedArticleOrganizer | None:
    cards_by_lane: dict[str, list[RowOneDailyLocalSavedArticleOrganizerCard]] = {
        key: [] for key in _LANE_TITLES
    }
    totals = {key: 0 for key in _LANE_TITLES}
    seen_hrefs = {key: set[str]() for key in _LANE_TITLES}
    source_names: set[str] = set()
    article_ids: set[str] = set()

    for story in edition.stories:
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue
        article_title = _article_title(story.headline, article.title, story.id)
        source_name = normalize_row_one_paragraph(article.source_name or story.source_name)
        if source_name:
            source_names.add(source_name.casefold())
        article_ids.add(story.id)

        _add_card(
            cards_by_lane,
            totals,
            seen_hrefs,
            "read_first",
            _read_first_card(
                article,
                title=article_title,
                source_name=source_name,
                page_href=page_href,
            ),
        )
        for section_position, section in enumerate(article.content_sections, start=1):
            section_href = f"articles/{page_href}#local-article-content-section-{section_position}"
            for item in section.items:
                references = _references(item.references)
                lane_key = _item_lane_key(references, section.key)
                if lane_key is None:
                    continue
                excerpt = _localized_excerpt(
                    item.body.en or section.body.en or item.label.en or section.title.en,
                    item.body.zh or section.body.zh or item.label.zh or section.title.zh,
                )
                if excerpt is None:
                    continue
                _add_card(
                    cards_by_lane,
                    totals,
                    seen_hrefs,
                    lane_key,
                    RowOneDailyLocalSavedArticleOrganizerCard(
                        title=article_title,
                        source_name=source_name,
                        lane_label=_clean_localized(item.label, fallback=section.title),
                        excerpt=excerpt,
                        href=section_href,
                        references=references,
                    ),
                )

        _add_card(
            cards_by_lane,
            totals,
            seen_hrefs,
            "source_context",
            _source_context_card(
                article,
                title=article_title,
                source_name=source_name,
                page_href=page_href,
            ),
        )

    lanes = tuple(
        RowOneDailyLocalSavedArticleOrganizerLane(
            key=lane_key,
            title=_LANE_TITLES[lane_key],
            dek=_LANE_DEKS[lane_key],
            cards=tuple(cards_by_lane[lane_key]),
            total_count=totals[lane_key],
        )
        for lane_key in ("read_first", "people_brands", "products", "source_context")
        if cards_by_lane[lane_key]
    )[:DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_LANES]
    if not lanes:
        return None
    return RowOneDailyLocalSavedArticleOrganizer(
        article_count=len(article_ids),
        source_count=len(source_names),
        card_count=sum(len(lane.cards) for lane in lanes),
        reference_count=sum(len(card.references) for lane in lanes for card in lane.cards),
        lanes=lanes,
    )


def _add_card(
    cards_by_lane: dict[str, list[RowOneDailyLocalSavedArticleOrganizerCard]],
    totals: dict[str, int],
    seen_hrefs: dict[str, set[str]],
    lane_key: str,
    card: RowOneDailyLocalSavedArticleOrganizerCard | None,
) -> None:
    if card is None:
        return
    totals[lane_key] += 1
    if card.href in seen_hrefs[lane_key]:
        return
    if len(cards_by_lane[lane_key]) >= DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE:
        return
    seen_hrefs[lane_key].add(card.href)
    cards_by_lane[lane_key].append(card)


def _read_first_card(
    article: RowOneLocalArticle,
    *,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalSavedArticleOrganizerCard | None:
    for section in article.brief_sections:
        excerpt = _localized_excerpt(section.body.en, section.body.zh)
        if excerpt is not None:
            return RowOneDailyLocalSavedArticleOrganizerCard(
                title=title,
                source_name=source_name,
                lane_label=_clean_localized(section.title, fallback=_LANE_TITLES["read_first"]),
                excerpt=excerpt,
                href=f"articles/{page_href}#local-article-paragraph-1",
            )
    paragraph = _first_paragraph(article)
    if paragraph is None:
        return None
    index, paragraph_en, paragraph_zh = paragraph
    excerpt = _localized_excerpt(paragraph_en, paragraph_zh)
    if excerpt is None:
        return None
    return RowOneDailyLocalSavedArticleOrganizerCard(
        title=title,
        source_name=source_name,
        lane_label=_LANE_TITLES["read_first"],
        excerpt=excerpt,
        href=f"articles/{page_href}#local-article-paragraph-{index + 1}",
    )


def _source_context_card(
    article: RowOneLocalArticle,
    *,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalSavedArticleOrganizerCard | None:
    paragraph = _first_paragraph(article)
    if paragraph is None:
        return None
    index, paragraph_en, paragraph_zh = paragraph
    excerpt = _localized_excerpt(paragraph_en, paragraph_zh)
    if excerpt is None:
        return None
    return RowOneDailyLocalSavedArticleOrganizerCard(
        title=title,
        source_name=source_name,
        lane_label=LocalizedText(en=source_name or "Saved source", zh=source_name or "保存来源"),
        excerpt=excerpt,
        href=f"articles/{page_href}#local-article-paragraph-{index + 1}",
    )


def _first_paragraph(article: RowOneLocalArticle) -> tuple[int, str, str] | None:
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    for index, paragraph in enumerate(article.paragraphs):
        normalized = normalize_row_one_paragraph(paragraph)
        if not normalized:
            continue
        zh = article.paragraphs_zh[index] if aligned_zh else normalized
        return index, normalized, normalize_row_one_paragraph(zh) or normalized
    return None


def _item_lane_key(
    references: Sequence[RowOneDailyLocalSavedArticleOrganizerReference],
    section_key: str,
) -> str | None:
    normalized_section_key = normalize_row_one_paragraph(section_key).casefold()
    if "product" in normalized_section_key:
        return "products"
    if "brand" in normalized_section_key or "people" in normalized_section_key:
        return "people_brands"
    labels = {reference.label.casefold() for reference in references}
    if labels & _PRODUCT_TYPES:
        return "products"
    if labels & _PEOPLE_BRAND_TYPES:
        return "people_brands"
    return None


def _references(
    refs: Sequence[RowOneReference],
) -> tuple[RowOneDailyLocalSavedArticleOrganizerReference, ...]:
    rendered: list[RowOneDailyLocalSavedArticleOrganizerReference] = []
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        name = normalize_row_one_paragraph(ref.name)
        label = normalize_row_one_paragraph(ref.label) or normalize_row_one_paragraph(ref.type)
        if not name:
            continue
        key = (name.casefold(), label.casefold())
        if key in seen:
            continue
        seen.add(key)
        rendered.append(RowOneDailyLocalSavedArticleOrganizerReference(name=name, label=label))
        if len(rendered) >= DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD:
            break
    return tuple(rendered)


def _article_title(headline: str, article_title: str, story_id: str) -> LocalizedText:
    title = normalize_row_one_paragraph(headline) or normalize_row_one_paragraph(article_title)
    title = title or story_id
    return LocalizedText(en=title, zh=title)


def _clean_localized(value: LocalizedText, *, fallback: LocalizedText) -> LocalizedText:
    en = normalize_row_one_paragraph(value.en)
    zh = normalize_row_one_paragraph(value.zh)
    if not en and not zh:
        return fallback
    return LocalizedText(en=en or zh, zh=zh or en)


def _localized_excerpt(en: str, zh: str) -> LocalizedText | None:
    clean_en = _truncate(en)
    clean_zh = _truncate(zh)
    if not clean_en and not clean_zh:
        return None
    return LocalizedText(en=clean_en or clean_zh, zh=clean_zh or clean_en)


def _truncate(value: str) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS:
        return normalized
    return (
        normalized[: max(0, DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS - 3)].rstrip()
        + "..."
    )


def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return path.name
```

- [ ] **Step 2: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_saved_article_organizer.py -q
```

Expected: all tests pass.

- [ ] **Step 3: Run builder lint**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/daily_local_saved_article_organizer.py tests/test_row_one_daily_local_saved_article_organizer.py
```

Expected: `All checks passed!`

---

### Task 3: Homepage Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add render RED tests**

In `tests/test_row_one_render.py`:

- import the new dataclasses
- add `_daily_local_saved_article_organizer_section_html`
- add `_daily_local_saved_article_organizer_fixture`
- add tests:
  - `test_render_index_html_includes_daily_local_saved_article_organizer`
  - `test_render_daily_local_saved_article_organizer_escapes_and_filters_links`
  - `test_render_row_one_site_writes_daily_local_saved_article_organizer_homepage_only`
  - `test_row_one_css_includes_daily_local_saved_article_organizer_styles`

Core assertions:

```python
assert "Daily Local Saved Article Organizer" in section_html
assert "每日保存文章整理器" in section_html
assert "Read First" in section_html
assert "People &amp; Brands" in section_html
assert "The Row leads the saved local story" in section_html
assert 'href="articles/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
assert 'href="articles/the-row-signal-1234567890.html#local-article-content-section-1"' in section_html
assert html.index('class="daily-local-article-intelligence-brief"') < html.index(
    'class="daily-local-saved-article-organizer"'
)
assert html.index('class="daily-local-saved-article-organizer"') < html.index(
    'class="saved-article-content-organization"'
)
```

Unsafe href assertions:

```python
assert "#local-article-paragraph-0" not in section_html
assert "https://example.com" not in section_html
assert "../" not in section_html
assert "<script>" not in section_html
assert "&lt;script&gt;" in section_html
```

Homepage-only assertions:

```python
assert 'class="daily-local-saved-article-organizer"' not in library_html
assert 'class="daily-local-saved-article-organizer"' not in article_html
assert 'class="daily-local-saved-article-organizer"' not in detail_html
assert "daily_local_saved_article_organizer" not in generated_contract_payload
assert "daily-local-saved-article-organizer" not in generated_contract_payload
assert "Daily Local Saved Article Organizer" not in generated_contract_payload
```

CSS assertions:

```python
for selector in (
    ".daily-local-saved-article-organizer",
    ".daily-local-saved-article-organizer-header",
    ".daily-local-saved-article-organizer-metrics",
    ".daily-local-saved-article-organizer-grid",
    ".daily-local-saved-article-organizer-lane",
    ".daily-local-saved-article-organizer-card",
    ".daily-local-saved-article-organizer-card-title",
    ".daily-local-saved-article-organizer-refs",
    ".daily-local-saved-article-organizer-ref",
):
    assert selector in css
assert re.search(
    r"\.daily-local-saved-article-organizer-grid\s*\{[^}]*grid-template-columns:\s*1fr",
    css,
)
```

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_saved_article_organizer"
```

Expected: failures because `render_index_html` does not yet accept `daily_local_saved_article_organizer` and no section/CSS exists.

---

### Task 4: Homepage Render Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/row_one/render.py`

- [ ] **Step 1: Wire render pipeline**

In `src/fashion_radar/row_one/render.py`:

```python
from fashion_radar.row_one.daily_local_saved_article_organizer import (
    build_row_one_daily_local_saved_article_organizer,
)
```

After `daily_local_article_intelligence_brief`:

```python
daily_local_saved_article_organizer = build_row_one_daily_local_saved_article_organizer(
    edition,
    local_articles_by_story_id,
    local_article_page_hrefs_by_story_id,
)
```

Pass into `render_index_html`:

```python
daily_local_saved_article_organizer=daily_local_saved_article_organizer,
```

- [ ] **Step 2: Add template imports and optional parameter**

In `src/fashion_radar/row_one/templates.py`, import:

```python
from fashion_radar.row_one.daily_local_saved_article_organizer import (
    RowOneDailyLocalSavedArticleOrganizer,
    RowOneDailyLocalSavedArticleOrganizerCard,
    RowOneDailyLocalSavedArticleOrganizerLane,
    RowOneDailyLocalSavedArticleOrganizerReference,
)
```

Add optional parameter:

```python
daily_local_saved_article_organizer: RowOneDailyLocalSavedArticleOrganizer | None = None,
```

Compute section:

```python
daily_local_saved_article_organizer_section = _render_daily_local_saved_article_organizer(
    daily_local_saved_article_organizer
)
```

Insert in main template:

```html
{daily_local_article_intelligence_brief_section}
{daily_local_saved_article_organizer_section}
{saved_article_content_organization_section}
```

- [ ] **Step 3: Add template helpers**

Add helpers near Stage 370 helpers:

```python
def _render_daily_local_saved_article_organizer(
    organizer: RowOneDailyLocalSavedArticleOrganizer | None,
) -> str:
    if organizer is None or not organizer.lanes:
        return ""
    lanes = [
        lane_html
        for lane in organizer.lanes
        if (lane_html := _render_daily_local_saved_article_organizer_lane(lane))
    ]
    if not lanes:
        return ""
    return f"""<section class="daily-local-saved-article-organizer"
  aria-label="Daily local saved article organizer">
  <div class="daily-local-saved-article-organizer-header">
    <div>
      <p class="story-section">
        <span data-lang="en">{_esc(organizer.title.en)}</span>
        <span data-lang="zh">{_esc(organizer.title.zh)}</span>
      </p>
      <h2>
        <span data-lang="en">Article-backed lanes for today's saved read</span>
        <span data-lang="zh">今日保存阅读的文章支撑整理线</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(organizer.dek.en)}</span>
      <span data-lang="zh">{_esc(organizer.dek.zh)}</span>
    </p>
  </div>
  <div class="daily-local-saved-article-organizer-metrics">
    <span>{_esc(_count_label(len(lanes), "lane", "lanes"))}</span>
    <span>{_esc(_count_label(organizer.card_count, "card", "cards"))}</span>
    <span>{_esc(_count_label(organizer.source_count, "source", "sources"))}</span>
    <span>{_esc(_count_label(organizer.reference_count, "reference", "references"))}</span>
    <span data-lang="en">Homepage only</span>
    <span data-lang="zh">仅首页展示</span>
  </div>
  <div class="daily-local-saved-article-organizer-grid">
{"".join(lanes)}
  </div>
</section>"""
```

Also add:

- `_render_daily_local_saved_article_organizer_lane`
- `_render_daily_local_saved_article_organizer_card`
- `_render_daily_local_saved_article_organizer_ref`
- `_safe_daily_local_saved_article_organizer_href`

Use the Stage 370 href validator shape, accepting only:

```python
articles/<safe-story-id>.html#local-article-content-section-N
articles/<safe-story-id>.html#local-article-paragraph-N
```

- [ ] **Step 4: Add CSS**

Add CSS near Stage 370 styles:

```css
.daily-local-saved-article-organizer { border-bottom: 1px solid var(--ink); margin: 0 0 32px; padding: 0 0 32px; }
.daily-local-saved-article-organizer-header { display: grid; gap: 10px; grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr); margin-bottom: 18px; }
.daily-local-saved-article-organizer-header h2 { font-family: RowOneSerif, Georgia, serif; font-size: clamp(2.1rem, 4.8vw, 5.5rem); font-weight: 500; letter-spacing: 0; line-height: 0.94; margin: 0; }
.daily-local-saved-article-organizer-header p { align-self: end; color: var(--muted); line-height: 1.45; margin: 0; max-width: 720px; }
.daily-local-saved-article-organizer-metrics { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 14px; }
.daily-local-saved-article-organizer-metrics span, .daily-local-saved-article-organizer-ref, .daily-local-saved-article-organizer-ref span, .daily-local-saved-article-organizer-card-meta span { border: 1px solid var(--line); color: var(--muted); display: inline-flex; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; overflow-wrap: anywhere; padding: 5px 8px; text-transform: uppercase; }
.daily-local-saved-article-organizer-grid { background: var(--line); border: 1px solid var(--line); display: grid; gap: 1px; grid-template-columns: repeat(4, minmax(0, 1fr)); }
.daily-local-saved-article-organizer-lane { background: var(--panel); display: grid; gap: 14px; min-height: 320px; padding: 16px; }
.daily-local-saved-article-organizer-lane h3 { font-family: RowOneSerif, Georgia, serif; font-size: clamp(1.35rem, 2.2vw, 2.35rem); font-weight: 500; letter-spacing: 0; line-height: 1; margin: 0; }
.daily-local-saved-article-organizer-lane p, .daily-local-saved-article-organizer-card p { color: var(--muted); line-height: 1.45; margin: 0; }
.daily-local-saved-article-organizer-card { border-top: 1px solid var(--line); display: grid; gap: 10px; padding-top: 12px; }
.daily-local-saved-article-organizer-card-title { color: var(--ink); display: grid; font-family: RowOneSerif, Georgia, serif; font-size: clamp(1.12rem, 1.7vw, 1.7rem); font-weight: 500; letter-spacing: 0; line-height: 1; text-decoration-color: var(--line); text-underline-offset: 4px; }
.daily-local-saved-article-organizer-card-meta, .daily-local-saved-article-organizer-refs { display: flex; flex-wrap: wrap; gap: 6px; }
.daily-local-saved-article-organizer-ref { color: var(--ink); gap: 4px; }
.daily-local-saved-article-organizer-ref span:last-child { color: var(--muted); }
```

Add mobile rules:

```css
.daily-local-saved-article-organizer-header { grid-template-columns: 1fr; }
.daily-local-saved-article-organizer-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 5: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_saved_article_organizer"
```

Expected: all Stage 371 render tests pass.

- [ ] **Step 6: Run render lint**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/templates.py src/fashion_radar/row_one/render.py tests/test_row_one_render.py
```

Expected: `All checks passed!`

---

### Task 5: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add docs paragraph**

Add this exact paragraph before Stage 370 in both docs:

```text
Stage 371 adds generated-site only Daily Local Saved Article Organizer inside `index.html` between the Daily Local Article Intelligence Brief and Saved Article Content Organization; it reuses current-edition stories, current-edition saved local article sidecars, generated local article page routes, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing content-section item bodies, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to organize today's saved articles into short homepage editorial lanes with article-backed excerpts, reference chips, and same-site reader anchors without changing app-facing contracts; it does not create `data/daily-local-saved-article-organizer.json`, does not create `data/local-saved-article-organizer.json`, does not create `data/saved-article-organizer.json`, does not create `daily-local-saved-article-organizer.html`, does not create `local-saved-article-organizer.html`, does not create `saved-article-organizer.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs test**

In `tests/test_row_one_docs.py`, add `test_row_one_docs_describe_stage_371_daily_local_saved_article_organizer_boundary`.

Assert:

- exact paragraph appears in both docs
- Stage 371 appears before Stage 370
- stale phrases are absent, including:
  - `creates data/daily-local-saved-article-organizer.json`
  - `writes data/daily-local-saved-article-organizer.json`
  - `creates data/local-saved-article-organizer.json`
  - `writes data/local-saved-article-organizer.json`
  - `creates data/saved-article-organizer.json`
  - `writes data/saved-article-organizer.json`
  - `creates daily-local-saved-article-organizer.html`
  - `writes daily-local-saved-article-organizer.html`
  - `creates local-saved-article-organizer.html`
  - `writes local-saved-article-organizer.html`
  - `creates saved-article-organizer.html`
  - `writes saved-article-organizer.html`
  - `row-one-app/v8`
  - `row-one-manifest/v2`
  - `row-one-runtime/v2`
  - `adds compliance review`
  - `adds compliance-review`
  - `adds compliance-review behavior`

- [ ] **Step 3: Update workflow guards**

In `tests/test_workflows.py`, extend generated contract payload denylist with:

```python
assert "daily_local_saved_article_organizer" not in generated_contract_payload
assert "local_saved_article_organizer" not in generated_contract_payload
assert "saved_article_organizer" not in generated_contract_payload
assert "RowOneDailyLocalSavedArticleOrganizer" not in generated_contract_payload
assert "Daily Local Saved Article Organizer" not in generated_contract_payload
assert "Local Saved Article Organizer" not in generated_contract_payload
assert "Saved Article Organizer" not in generated_contract_payload
assert "每日保存文章整理器" not in generated_contract_payload
assert "daily-local-saved-article-organizer" not in generated_contract_payload
assert "local-saved-article-organizer" not in generated_contract_payload
assert "saved-article-organizer" not in generated_contract_payload
```

Extend artifact stems with:

```python
"daily-local-saved-article-organizer",
"local-saved-article-organizer",
"saved-article-organizer",
"daily_local_saved_article_organizer",
"local_saved_article_organizer",
"saved_article_organizer",
```

Add wrapper guard:

```python
def test_stage_371_daily_local_saved_article_organizer_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_saved_article_organizer",
        lambda _organizer: "",
        raising=False,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

- [ ] **Step 4: Run docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_371 or saved_article_organizer or daily_local_saved_article_organizer"
```

Expected: all focused docs/workflow tests pass.

---

### Task 6: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-371-plan-review.md`
- Create: `docs/reviews/opencode-stage-371-plan-review.md`

- [ ] **Step 1: Run Claude Code plan review**

Run:

```bash
claude --print --effort max --dangerously-skip-permissions "Review Stage 371 plan and spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-09-stage-371-daily-local-saved-article-organizer-design.md and docs/superpowers/plans/2026-07-09-stage-371-daily-local-saved-article-organizer-plan.md. Do not edit files. Findings first by severity. Check feasibility, scope, TDD coverage, generated-site-only boundary, app contract/artifact safety, href safety, and whether this advances homepage content organization rather than just links. Keep under 120 lines." > docs/reviews/claude-code-stage-371-plan-review.md
```

If it times out, write a clean timeout artifact and use opencode plus an xhigh Codex reviewer as the usable review gates.

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 --auto "Review Stage 371 plan and spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-09-stage-371-daily-local-saved-article-organizer-design.md and docs/superpowers/plans/2026-07-09-stage-371-daily-local-saved-article-organizer-plan.md. Do not edit files. Findings first by severity. Check feasibility, scope, TDD coverage, generated-site-only boundary, app contract/artifact safety, href safety, and whether this advances homepage content organization rather than just links. Keep under 120 lines." > docs/reviews/opencode-stage-371-plan-review.md
```

- [ ] **Step 3: Fix Critical/Important plan findings**

Apply only valid findings. Re-run focused docs/plan checks if the plan changes.

---

### Task 7: Code Review, Final Gates, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-371-code-review.md`
- Create: `docs/reviews/opencode-stage-371-code-review.md`

- [ ] **Step 1: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_saved_article_organizer.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "daily_local_saved_article_organizer or stage_371 or saved_article_organizer"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/daily_local_saved_article_organizer.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_saved_article_organizer.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
```

- [ ] **Step 2: Full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

- [ ] **Step 3: Run code reviews**

Run:

```bash
claude --print --effort max --dangerously-skip-permissions "Review the staged Stage 371 Daily Local Saved Article Organizer changes in /home/ubuntu/fashion-radar. Use git diff --cached. Do not edit files. Findings first by severity with file/line references. Focus on bugs, href safety, generated-site-only boundary, app contract/artifact leaks, homepage publishing of full articles, tests, and plan compliance. Keep under 120 lines." > docs/reviews/claude-code-stage-371-code-review.md
opencode run -m zhipuai-coding-plan/glm-5.2 --auto "Review the staged Stage 371 Daily Local Saved Article Organizer changes in /home/ubuntu/fashion-radar. Use git diff --cached. Do not edit files. Findings first by severity with file/line references. Focus on bugs, href safety, generated-site-only boundary, app contract/artifact leaks, homepage publishing of full articles, tests, and plan compliance. Keep under 120 lines." > docs/reviews/opencode-stage-371-code-review.md
```

If local Claude Code times out, write a clean timeout artifact and use opencode plus xhigh Codex review as the usable gate.

- [ ] **Step 4: Fix Critical/Important review findings**

Use `superpowers:receiving-code-review`. For each valid finding:

- add or adjust a failing test
- verify RED
- fix implementation
- verify GREEN
- rerun focused and full gates

- [ ] **Step 5: Stage and commit**

Run:

```bash
git add README.md docs/row-one.md docs/reviews/claude-code-stage-371-plan-review.md docs/reviews/opencode-stage-371-plan-review.md docs/reviews/claude-code-stage-371-code-review.md docs/reviews/opencode-stage-371-code-review.md docs/superpowers/specs/2026-07-09-stage-371-daily-local-saved-article-organizer-design.md docs/superpowers/plans/2026-07-09-stage-371-daily-local-saved-article-organizer-plan.md src/fashion_radar/row_one/daily_local_saved_article_organizer.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_saved_article_organizer.py tests/test_row_one_docs.py tests/test_row_one_render.py tests/test_workflows.py
git diff --cached --check
git commit -m "Stage 371: add daily local saved article organizer"
git push origin main
```

- [ ] **Step 6: Handoff Summary**

Report:

- repo status
- commit SHA
- pushed branch
- verified commands and results
- uncommitted files
- next step
