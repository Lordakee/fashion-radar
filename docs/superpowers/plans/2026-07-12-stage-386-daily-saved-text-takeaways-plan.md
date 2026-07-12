# Stage 386 Daily Saved Text Takeaways Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only ROW ONE homepage section that organizes short, capped excerpts from existing saved local article bodies so the daily page becomes a useful reading surface rather than only a set of links.

**Architecture:** Build a new internal `RowOneDailyLocalSavedTextTakeaways` model from current-edition stories, existing saved local article sidecars, and existing generated local article page hrefs. Render the section only in `index.html`, grouped into deterministic lanes from already-saved paragraphs and content sections, with links only to existing `articles/<story-id>.html#local-article-*` anchors. Do not add app/runtime/manifest/schema contracts, new route families, JSON artifacts, source collection, scraping/fetching, extraction, scoring/ranking, LLM calls, connectors, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.

**Tech Stack:** Python dataclasses/builders, existing ROW ONE local article models, server-rendered HTML in `templates.py`, pytest, ruff, uv frozen/no-config verification commands.

---

## Product Gap

Stages 382-385 made saved local article bodies easier to synthesize and trace, but the homepage still relies heavily on navigation links. Stage 386 should expose a small, controlled amount of existing saved article text directly on the ROW ONE homepage, grouped for scanning, while still routing deeper reading to the saved local article pages.

This stage is not a new crawler, downloader, summarizer, external search integration, app API, or article publication pipeline. It is a generated-site-only presentation layer over saved local content that already exists in memory during ROW ONE rendering.

## Scope Decision

- Add a new homepage-only section named `Daily Saved Text Takeaways`.
- Render only inside generated `index.html`.
- Reuse current-edition `RowOneStory` items, existing `RowOneLocalArticle` sidecars, existing local article page hrefs, existing saved paragraphs, existing content sections, and existing paragraph/content-section anchors.
- Show short capped snippets from saved local text, not full article bodies.
- Omit the section unless at least two current-edition saved local articles have usable saved text.
- Keep every link same-site and shaped as `articles/<safe-story-id>.html#local-article-content-section-N` or `articles/<safe-story-id>.html#local-article-paragraph-N`.
- Do not create standalone `daily-saved-text-takeaways.html`, `daily-local-saved-text-takeaways.html`, `data/daily-saved-text-takeaways.json`, `data/daily-local-saved-text-takeaways.json`, route families, app fields, schema fields, manifest/runtime fields, article-source sidecars, source adapters, scraping/fetching/matching/extraction/scoring/ranking behavior, LLM calls, connectors, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review features.

## File Map

- Create `src/fashion_radar/row_one/daily_local_saved_text_takeaways.py`
  - Own the Stage 386 dataclasses, constants, safe href validation, lane-building logic, and excerpt caps.
- Modify `src/fashion_radar/row_one/render.py`
  - Build Stage 386 after local article page hrefs are available and pass it into `render_index_html(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import Stage 386 dataclasses.
  - Add a `daily_local_saved_text_takeaways` parameter to `render_index_html(...)`.
  - Render a `.daily-local-saved-text-takeaways` homepage section between Daily Local Synthesis Brief and Daily Local Saved Article Organizer.
  - Add compact editorial CSS for the section, lanes, cards, excerpts, and same-site anchor links.
- Create `tests/test_row_one_daily_local_saved_text_takeaways.py`
  - Builder tests for lane construction, two-article minimum, excerpt caps, safe links, and empty omission.
- Modify `tests/test_row_one_render.py`
  - Render tests for escaping, link filtering, homepage-only placement, CSS selectors, and artifact absence.
- Modify `tests/test_workflows.py`
  - Add a Stage 386 homepage-only sentinel test and contract/artifact denylist tokens.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the generated-site-only boundary and explicit non-goals.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-386-plan-review.md`
  - `opencode-stage-386-plan-review.md`
  - Stage 386 code-review artifacts after implementation.

## Requirements

1. Builder behavior:
   - Return `None` unless at least two current-edition stories have matching saved local articles with usable paragraph or content-section text.
   - Include at most three lanes and at most three cards per lane.
   - Build deterministic lanes:
     - `what_article_says`: first nonblank saved paragraph per article.
     - `brand_product_context`: first usable content-section item per article with brand/person/product-style references or section keys.
     - `inspect_next`: next usable saved paragraph or content section per article that is not already used in the first two lanes.
   - Cap excerpt text to `DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS = 170`.
   - Deduplicate cards per lane by normalized href.
   - Keep article ordering aligned to current edition story order.
   - Preserve source names and localized text fallbacks where available.

2. Link safety:
   - Builder stores final same-site hrefs as `articles/<page>.html#local-article-*`.
   - Reject unsafe article hrefs, mismatched story IDs, `index.html`, prefixed traversal, absolute paths, URLs, queries, missing fragments, unknown fragments, `0`, `01`, whitespace, and malformed suffixes.
   - Only content-section and paragraph anchors are allowed.

3. Homepage rendering:
   - Render the section only when a valid `RowOneDailyLocalSavedTextTakeaways` object is passed.
   - Place the section after `.daily-local-synthesis-brief` and before `.daily-local-saved-article-organizer`.
   - Render a bilingual title/dek, metric line, lane titles, short excerpts, source/story labels, and safe same-site links.
   - Escape all text.
   - Omit cards that have unsafe hrefs or blank excerpts.
   - Do not render full saved article bodies on the homepage.

4. Generated-site-only boundary:
   - The section must appear only in generated `index.html`.
   - It must not appear in `articles/index.html`, `articles/<story-id>.html`, detail pages, or generated contract payloads (`data/edition.json`, `data/manifest.json`, `data/runtime.json`, `data/articles/*.json`).
   - Do not create root, `articles/`, or `data/` `.html` or `.json` artifacts for Stage 386 stems.

5. Docs:
   - README and `docs/row-one.md` must state that Stage 386 is generated-site-only homepage presentation inside the existing ROW ONE site.
   - Docs must say it reuses current-edition stories, saved local article sidecars, generated local article page routes, saved paragraphs, and content-section anchors.
   - Docs must say it does not create new JSON artifacts, route families, app/runtime/manifest/schema contracts, article-source sidecars, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connectors, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.

## Tasks

### Task 1: RED builder tests for saved text takeaways

**Files:**
- Create: `tests/test_row_one_daily_local_saved_text_takeaways.py`

- [ ] Create fixtures for two current-edition stories, matching `RowOneLocalArticle` sidecars, one mismatched sidecar, and safe article hrefs:

```python
from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_saved_text_takeaways import (
    build_row_one_daily_local_saved_text_takeaways,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 12, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _story(story_id: str, headline: str = "The Row signal") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline,
        summary=_lt("Saved text summary."),
        why_it_matters=_lt("Saved local text adds context."),
        editorial_takeaway=_lt("The saved article adds a concrete daily signal."),
        signal_context=_lt("The signal context stays grounded in saved text."),
        reader_path=_lt("Read through the saved local article body."),
        source_name="Vogue Business",
        source_url="https://example.com/story",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _edition(stories: list[RowOneStory]) -> RowOneEdition:
    return RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=_lt("Daily ROW ONE summary."),
        stories=stories,
    )


def _article(
    story_id: str,
    *,
    title: str = "Saved source article",
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url="https://example.com/local",
        source_name=source_name,
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=paragraphs
        if paragraphs is not None
        else [
            "The saved article explains why the item is gaining attention in stores.",
            "A second saved paragraph shows what the reader should inspect next.",
        ],
        paragraphs_zh=paragraphs_zh
        if paragraphs_zh is not None
        else [
            "保存正文解释该单品为何在门店获得关注。",
            "第二段保存正文提示读者接下来要观察什么。",
        ],
        content_sections=content_sections
        if content_sections is not None
        else [
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(en="Products", zh="单品"),
                body=LocalizedText(en="Product context from saved text.", zh="保存正文中的单品语境。"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Margaux bag", zh="Margaux 手袋"),
                        body=LocalizedText(
                            en="Margaux bag evidence appears in saved local text.",
                            zh="Margaux 手袋证据出现在保存本地正文中。",
                        ),
                        references=[
                            RowOneReference(
                                name="Margaux bag",
                                type="bag",
                                label="product",
                            )
                        ],
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )
```

- [ ] Add `test_build_daily_local_saved_text_takeaways_groups_existing_saved_text`.

Expected assertions:

```python
first_id = "the-row-signal-1111111111"
second_id = "alaia-flats-2222222222"
takeaways = build_row_one_daily_local_saved_text_takeaways(
    _edition([_story(first_id), _story(second_id, headline="Alaia flats signal")]),
    {first_id: _article(first_id), second_id: _article(second_id, source_name="WWD")},
    {first_id: f"{first_id}.html", second_id: f"{second_id}.html"},
)

assert takeaways is not None
assert takeaways.article_count == 2
assert takeaways.source_count == 2
assert [lane.key for lane in takeaways.lanes] == [
    "what_article_says",
    "brand_product_context",
    "inspect_next",
]
assert takeaways.lanes[0].cards[0].href == (
    "articles/the-row-signal-1111111111.html#local-article-paragraph-1"
)
assert takeaways.lanes[1].cards[0].href == (
    "articles/the-row-signal-1111111111.html#local-article-content-section-1"
)
assert "gaining attention" in takeaways.lanes[0].cards[0].excerpt.en
assert takeaways.lanes[1].cards[0].label.en == "Margaux bag"
```

- [ ] Add `test_build_daily_local_saved_text_takeaways_requires_two_articles`.

Expected assertions:

```python
story_id = "single-signal-1111111111"
assert (
    build_row_one_daily_local_saved_text_takeaways(
        _edition([_story(story_id)]),
        {story_id: _article(story_id)},
        {story_id: f"{story_id}.html"},
    )
    is None
)
```

- [ ] Add `test_build_daily_local_saved_text_takeaways_caps_excerpts_and_filters_hrefs`.

Expected assertions:

```python
first_id = "the-row-signal-1111111111"
second_id = "alaia-flats-2222222222"
long_text = "Lead sentence. " + ("detail " * 80) + "TAIL_MARKER"
takeaways = build_row_one_daily_local_saved_text_takeaways(
    _edition([_story(first_id), _story(second_id)]),
    {
        first_id: _article(first_id, paragraphs=[long_text], paragraphs_zh=[long_text]),
        second_id: _article(second_id),
    },
    {
        first_id: f"{first_id}.html",
        second_id: "https://example.com/unsafe.html",
    },
)

assert takeaways is None
```

Then add a safe second href and assert `TAIL_MARKER` is omitted from the rendered excerpt.

- [ ] Add `test_build_daily_local_saved_text_takeaways_inspect_next_avoids_reused_evidence`.

Expected assertions:

```python
first_id = "the-row-signal-1111111111"
second_id = "alaia-flats-2222222222"
takeaways = build_row_one_daily_local_saved_text_takeaways(
    _edition([_story(first_id), _story(second_id)]),
    {first_id: _article(first_id), second_id: _article(second_id)},
    {first_id: f"{first_id}.html", second_id: f"{second_id}.html"},
)

assert takeaways is not None
first_article_hrefs = [
    lane.cards[0].href
    for lane in takeaways.lanes
    if lane.cards and "the-row-signal-1111111111" in lane.cards[0].href
]
assert first_article_hrefs == [
    "articles/the-row-signal-1111111111.html#local-article-paragraph-1",
    "articles/the-row-signal-1111111111.html#local-article-content-section-1",
    "articles/the-row-signal-1111111111.html#local-article-paragraph-2",
]
assert len(first_article_hrefs) == len(set(first_article_hrefs))
```

- [ ] Run RED command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_saved_text_takeaways.py -q
```

Expected: FAIL because `fashion_radar.row_one.daily_local_saved_text_takeaways` does not exist yet.

### Task 2: Implement builder model and safe links

**Files:**
- Create: `src/fashion_radar/row_one/daily_local_saved_text_takeaways.py`
- Modify: `tests/test_row_one_daily_local_saved_text_takeaways.py`

- [ ] Add constants:

```python
DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_LANES = 3
DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_CARDS_PER_LANE = 3
DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS = 170
```

- [ ] Add dataclasses:

```python
@dataclass(frozen=True)
class RowOneDailyLocalSavedTextTakeawayCard:
    title: LocalizedText
    source_name: str
    label: LocalizedText
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalSavedTextTakeawayLane:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: tuple[RowOneDailyLocalSavedTextTakeawayCard, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneDailyLocalSavedTextTakeaways:
    title: LocalizedText
    dek: LocalizedText
    article_count: int
    source_count: int
    card_count: int
    lanes: tuple[RowOneDailyLocalSavedTextTakeawayLane, ...]
```

- [ ] Implement `build_row_one_daily_local_saved_text_takeaways(...)`:

```python
def build_row_one_daily_local_saved_text_takeaways(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalSavedTextTakeaways | None:
    cards_by_lane: dict[str, list[RowOneDailyLocalSavedTextTakeawayCard]] = {
        key: [] for key in _LANE_ORDER
    }
    totals = {key: 0 for key in _LANE_ORDER}
    seen_hrefs = {key: set[str]() for key in _LANE_ORDER}
    contributing_story_ids: set[str] = set()
    contributing_sources: set[str] = set()

    for story in edition.stories:
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue
        title = _article_title(story.headline, article.title, story.id)
        source_name = _source_name(article, story.source_name)
        emitted_for_story = False
        for lane_key, card in (
            ("what_article_says", _what_article_says_card(article, title, source_name, page_href)),
            (
                "brand_product_context",
                _brand_product_context_card(article, title, source_name, page_href),
            ),
            ("inspect_next", _inspect_next_card(article, title, source_name, page_href)),
        ):
            if card is None:
                continue
            if _add_card(cards_by_lane, totals, seen_hrefs, lane_key, card):
                emitted_for_story = True
        if emitted_for_story:
            contributing_story_ids.add(story.id)
            if source_name:
                contributing_sources.add(source_name.casefold())

    if len(contributing_story_ids) < 2:
        return None
    lanes = tuple(
        RowOneDailyLocalSavedTextTakeawayLane(
            key=lane_key,
            title=_LANE_TITLES[lane_key],
            dek=_LANE_DEKS[lane_key],
            cards=tuple(cards_by_lane[lane_key]),
            total_count=totals[lane_key],
        )
        for lane_key in _LANE_ORDER
        if cards_by_lane[lane_key]
    )[:DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_LANES]
    if not lanes:
        return None
    return RowOneDailyLocalSavedTextTakeaways(
        title=LocalizedText(en="Daily Saved Text Takeaways", zh="每日保存正文要点"),
        dek=LocalizedText(
            en="Short saved-text excerpts grouped for fast homepage reading.",
            zh="把保存正文短摘按阅读意图整理到首页。",
        ),
        article_count=len(contributing_story_ids),
        source_count=len(contributing_sources),
        card_count=sum(len(lane.cards) for lane in lanes),
        lanes=lanes,
    )
```

Implementation rules:
- Iterate `edition.stories` in order.
- Skip invalid story IDs, missing articles, mismatched `article.story_id`, and unsafe page hrefs.
- Build lane cards with helpers `_what_article_says_card(...)`, `_brand_product_context_card(...)`, and `_inspect_next_card(...)`.
- Define `_LANE_ORDER = ("what_article_says", "brand_product_context", "inspect_next")`.
- Define `_LANE_TITLES` and `_LANE_DEKS` with bilingual `LocalizedText` values for the three lanes:
  - `what_article_says`: `What the article says` / `文章说了什么`
  - `brand_product_context`: `Brand / product context` / `品牌与单品语境`
  - `inspect_next`: `Inspect next` / `接下来检查`
- Implement `_what_article_says_card(...)` by selecting the first nonblank paragraph from `article.paragraphs`, labeling it `What the article says`, and linking to `articles/<page>.html#local-article-paragraph-1`.
- Implement `_brand_product_context_card(...)` by scanning `article.content_sections` in order and selecting the first section item that has a nonblank `item.body` or section body and either:
  - a reference type in `{"brand", "celebrity", "creative_director", "designer", "founder", "people", "person", "product", "bag", "shoe", "shoes", "sneaker", "flat", "accessory", "apparel", "watch", "jewelry"}`, or
  - a section key of `"entities"`, `"brand_signals"`, or `"product_signals"`.
- Use the selected item label as the card label; use item body first, then section body, as the excerpt; link to the selected section position with `#local-article-content-section-N`.
- Implement `_inspect_next_card(...)` by selecting the first nonblank paragraph after paragraph index `0`; if none exists, select the first content section not already used by `_brand_product_context_card(...)`; never reuse the same href as another lane card for the same article.
- Implement `_article_title(...)` by using normalized story headline first, then normalized article title, then the story id.
- Implement `_source_name(...)` by using normalized article source first, then normalized story source, then `"Saved local source"`.
- Implement `_add_card(...)` to reject duplicate hrefs per lane and stop appending after `DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_CARDS_PER_LANE`.
- Implement `_truncate(...)` as a simple character cap that strips trailing whitespace and appends `...` only when text exceeds the cap.
- Track articles that contributed at least one card.
- Return `None` if fewer than two articles contributed.
- Build lanes in this order: `what_article_says`, `brand_product_context`, `inspect_next`.

- [ ] Implement safe helpers:

```python
def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if (
        "://" in href
        or "//" in href
        or "?" in href
        or "#" in href
        or href.startswith((".", "/", "//"))
    ):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..", "index.html")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return path.name


def _paragraph_href(page_href: str, paragraph_index: int) -> str:
    return f"articles/{page_href}#local-article-paragraph-{paragraph_index + 1}"


def _content_section_href(page_href: str, section_position: int) -> str:
    return f"articles/{page_href}#local-article-content-section-{section_position}"
```

Use the same `PurePosixPath` and `safe_local_article_story_id(...)` pattern as adjacent daily local builders.

- [ ] Implement text helpers:

```python
def _clean_localized(text: LocalizedText | None, limit: int) -> LocalizedText:
    if text is None:
        return LocalizedText(en="", zh="")
    en = _truncate(normalize_row_one_paragraph(text.en), limit)
    zh = _truncate(normalize_row_one_paragraph(text.zh), limit)
    if not zh:
        zh = en
    if not en:
        en = zh
    return LocalizedText(en=en, zh=zh)


def _excerpt_from_paragraph(article: RowOneLocalArticle, paragraph_index: int) -> LocalizedText | None:
    if paragraph_index < 0 or paragraph_index >= len(article.paragraphs):
        return None
    en = normalize_row_one_paragraph(article.paragraphs[paragraph_index])
    if not en:
        return None
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    zh = (
        normalize_row_one_paragraph(article.paragraphs_zh[paragraph_index])
        if aligned_zh and paragraph_index < len(article.paragraphs_zh)
        else ""
    )
    return _clean_localized(
        LocalizedText(en=en, zh=zh or en),
        DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS,
    )
```

Use `normalize_row_one_paragraph(...)`, truncate by character cap, and preserve zh fallback.

- [ ] Run GREEN command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_saved_text_takeaways.py -q
```

Expected: PASS.

### Task 3: Render homepage section

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] Add render tests:

```python
def test_render_index_html_includes_daily_local_saved_text_takeaways() -> None:
    card = RowOneDailyLocalSavedTextTakeawayCard(
        title=LocalizedText(en="The Row signal", zh="The Row 信号"),
        source_name="Vogue Business",
        label=LocalizedText(en="What the article says", zh="文章说了什么"),
        excerpt=LocalizedText(
            en="The saved local text explains the retail signal.",
            zh="保存本地正文解释零售信号。",
        ),
        href="articles/the-row-signal-1234567890.html#local-article-paragraph-1",
    )
    takeaways = RowOneDailyLocalSavedTextTakeaways(
        title=LocalizedText(en="Daily Saved Text Takeaways", zh="每日保存正文要点"),
        dek=LocalizedText(en="Saved text grouped for reading.", zh="保存正文按阅读意图整理。"),
        article_count=2,
        source_count=1,
        card_count=1,
        lanes=(
            RowOneDailyLocalSavedTextTakeawayLane(
                key="what_article_says",
                title=LocalizedText(en="What the article says", zh="文章说了什么"),
                dek=LocalizedText(en="A direct saved-text read.", zh="直接读取保存正文。"),
                cards=(card,),
                total_count=1,
            ),
        ),
    )
    html = render_index_html(_edition(), daily_local_saved_text_takeaways=takeaways)
    section_html = _daily_local_saved_text_takeaways_section_html(html)
    assert "Daily Saved Text Takeaways" in section_html
    assert "每日保存正文要点" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert "TAIL_MARKER" not in section_html
```

```python
def test_render_daily_local_saved_text_takeaways_escapes_and_filters_hrefs() -> None:
    safe_card = RowOneDailyLocalSavedTextTakeawayCard(
        title=LocalizedText(en="<script>Signal</script>", zh="<script>信号</script>"),
        source_name="Vogue <Business>",
        label=LocalizedText(en="Safe label", zh="安全标签"),
        excerpt=LocalizedText(en="Saved <text> excerpt.", zh="保存 <正文> 摘录。"),
        href="articles/the-row-signal-1234567890.html#local-article-paragraph-1",
    )
    unsafe_card = RowOneDailyLocalSavedTextTakeawayCard(
        title=LocalizedText(en="Unsafe", zh="不安全"),
        source_name="Bad Source",
        label=LocalizedText(en="Unsafe label", zh="不安全标签"),
        excerpt=LocalizedText(en="Should not render.", zh="不应渲染。"),
        href="https://example.com/story#local-article-paragraph-1",
    )
    takeaways = RowOneDailyLocalSavedTextTakeaways(
        title=LocalizedText(en="Daily Saved Text Takeaways", zh="每日保存正文要点"),
        dek=LocalizedText(en="Saved text grouped for reading.", zh="保存正文按阅读意图整理。"),
        article_count=2,
        source_count=1,
        card_count=2,
        lanes=(
            RowOneDailyLocalSavedTextTakeawayLane(
                key="what_article_says",
                title=LocalizedText(en="What the article says", zh="文章说了什么"),
                dek=LocalizedText(en="A direct saved-text read.", zh="直接读取保存正文。"),
                cards=(safe_card, unsafe_card),
                total_count=2,
            ),
        ),
    )
    html = render_index_html(_edition(), daily_local_saved_text_takeaways=takeaways)
    section_html = _daily_local_saved_text_takeaways_section_html(html)
    assert "&lt;script&gt;" in section_html
    assert "https://example.com" not in section_html
    assert "../" not in section_html
```

```python
def test_render_row_one_site_writes_daily_local_saved_text_takeaways_homepage_only(tmp_path) -> None:
    render_row_one_site(edition, tmp_path, local_articles_by_story_id=local_articles)
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    article_html = (tmp_path / "articles" / f"{story_id}.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / f"{story_id}.html").read_text(encoding="utf-8")
    assert 'class="daily-local-saved-text-takeaways"' in homepage_html
    assert 'class="daily-local-saved-text-takeaways"' not in library_html
    assert 'class="daily-local-saved-text-takeaways"' not in article_html
    assert 'class="daily-local-saved-text-takeaways"' not in detail_html
```

- [ ] Run RED render tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_saved_text_takeaways \
  tests/test_row_one_render.py::test_render_daily_local_saved_text_takeaways_escapes_and_filters_hrefs \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_saved_text_takeaways_homepage_only \
  -q
```

Expected: FAIL before renderer implementation.

- [ ] Import and build Stage 386 in `render.py`:

```python
from fashion_radar.row_one.daily_local_saved_text_takeaways import (
    build_row_one_daily_local_saved_text_takeaways,
)

daily_local_saved_text_takeaways = build_row_one_daily_local_saved_text_takeaways(
    edition,
    local_articles_by_story_id,
    local_article_page_hrefs_by_story_id,
)
```

Pass it into `render_index_html(...)`.

- [ ] Add `daily_local_saved_text_takeaways` parameter to `render_index_html(...)`.

- [ ] Add renderer helpers:

```python
def _render_daily_local_saved_text_takeaways(
    takeaways: RowOneDailyLocalSavedTextTakeaways | None,
) -> str:
    if takeaways is None or not takeaways.lanes:
        return ""
    lanes = "".join(
        lane_html
        for lane in takeaways.lanes
        if (lane_html := _render_daily_local_saved_text_takeaway_lane(lane))
    )
    if not lanes:
        return ""
    return f"""<section class="daily-local-saved-text-takeaways" aria-labelledby="daily-local-saved-text-takeaways-title">
  <div class="daily-local-saved-text-takeaways-header">
    <p class="section-kicker">
      <span data-lang="en">Saved local text</span>
      <span data-lang="zh">保存本地正文</span>
    </p>
    <h2 id="daily-local-saved-text-takeaways-title">
      <span data-lang="en">{_esc(takeaways.title.en)}</span>
      <span data-lang="zh">{_esc(takeaways.title.zh or takeaways.title.en)}</span>
    </h2>
    <p>
      <span data-lang="en">{_esc(takeaways.dek.en)}</span>
      <span data-lang="zh">{_esc(takeaways.dek.zh or takeaways.dek.en)}</span>
    </p>
  </div>
  <div class="daily-local-saved-text-takeaways-grid">
{lanes}  </div>
</section>
"""


def _render_daily_local_saved_text_takeaway_lane(
    lane: RowOneDailyLocalSavedTextTakeawayLane,
) -> str:
    cards = "".join(
        card_html
        for card in lane.cards
        if (card_html := _render_daily_local_saved_text_takeaway_card(card))
    )
    if not cards:
        return ""
    return f"""    <section class="daily-local-saved-text-takeaways-lane">
      <h3>
        <span data-lang="en">{_esc(lane.title.en)}</span>
        <span data-lang="zh">{_esc(lane.title.zh or lane.title.en)}</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(lane.dek.en)}</span>
        <span data-lang="zh">{_esc(lane.dek.zh or lane.dek.en)}</span>
      </p>
{cards}    </section>
"""


def _render_daily_local_saved_text_takeaway_card(
    card: RowOneDailyLocalSavedTextTakeawayCard,
) -> str:
    href = _safe_daily_local_saved_text_takeaway_href(card.href)
    excerpt_en = normalize_row_one_paragraph(card.excerpt.en)
    excerpt_zh = normalize_row_one_paragraph(card.excerpt.zh)
    if href is None or not (excerpt_en or excerpt_zh):
        return ""
    return f"""      <article class="daily-local-saved-text-takeaways-card">
        <p class="daily-local-saved-text-takeaways-meta">{_esc(card.source_name)}</p>
        <h4>
          <span data-lang="en">{_esc(card.label.en or card.title.en)}</span>
          <span data-lang="zh">{_esc(card.label.zh or card.label.en or card.title.en)}</span>
        </h4>
        <p>
          <span data-lang="en">{_esc(excerpt_en or excerpt_zh)}</span>
          <span data-lang="zh">{_esc(excerpt_zh or excerpt_en)}</span>
        </p>
        <a class="daily-local-saved-text-takeaways-link" href="{_esc(href)}">
          <span data-lang="en">Open saved text</span>
          <span data-lang="zh">打开保存正文</span>
        </a>
      </article>
"""


def _safe_daily_local_saved_text_takeaway_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or "//" in href or "?" in href or href.startswith((".", "/", "//")):
        return None
    path_text, separator, fragment = href.partition("#")
    if separator != "#":
        return None
    page_href = _safe_daily_local_synthesis_brief_href(path_text)
    if page_href is None:
        return None
    if path_text != page_href:
        return None
    if (
        _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None
        and _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None
    ):
        return None
    return f"{page_href}#{fragment}"
```

Use fragment regexes already present in `templates.py` for paragraph/content-section suffix validation.

- [ ] Insert the section after `{daily_local_synthesis_brief_section}` and before `{daily_local_saved_article_organizer_section}`.

- [ ] Add CSS selectors:
  - `.daily-local-saved-text-takeaways`
  - `.daily-local-saved-text-takeaways-header`
  - `.daily-local-saved-text-takeaways-grid`
  - `.daily-local-saved-text-takeaways-lane`
  - `.daily-local-saved-text-takeaways-card`
  - `.daily-local-saved-text-takeaways-link`

- [ ] Extend `test_row_one_css_includes_daily_local_synthesis_brief_styles` or add a new CSS test that asserts the Stage 386 selectors above exist and that card/link text uses `overflow-wrap: anywhere` or equivalent wrapping protection.

- [ ] Run GREEN render tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_saved_text_takeaways \
  tests/test_row_one_render.py::test_render_daily_local_saved_text_takeaways_escapes_and_filters_hrefs \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_saved_text_takeaways_homepage_only \
  -q
```

Expected: PASS.

### Task 4: Workflow and docs boundary tests

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] Add workflow denylist tokens to the existing generated contract payload checks:

```python
assert "daily_local_saved_text_takeaways" not in generated_contract_payload
assert "daily_saved_text_takeaways" not in generated_contract_payload
assert "saved_text_takeaways" not in generated_contract_payload
assert "Daily Saved Text Takeaways" not in generated_contract_payload
assert "daily-local-saved-text-takeaways" not in generated_contract_payload
assert "daily-saved-text-takeaways" not in generated_contract_payload
assert "saved-text-takeaways" not in generated_contract_payload
```

- [ ] Add Stage 386 artifact stems to root/articles/data artifact-denylist checks:

```python
"daily-local-saved-text-takeaways",
"daily-saved-text-takeaways",
"saved-text-takeaways",
"daily_local_saved_text_takeaways",
"daily_saved_text_takeaways",
"saved_text_takeaways",
```

- [ ] Add homepage-only sentinel test:

```python
def test_stage_386_daily_local_saved_text_takeaways_stays_homepage_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    sentinel = "STAGE_386_DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_SENTINEL"
    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_saved_text_takeaways",
        lambda _takeaways: sentinel,
        raising=True,
    )

    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
    output_dir = tmp_path / "row-one"
    generated_payloads = {
        path.relative_to(output_dir).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(output_dir.rglob("*"))
        if path.suffix in {".html", ".json"}
    }
    sentinel_paths = [
        relative_path
        for relative_path, payload in generated_payloads.items()
        if sentinel in payload
    ]
    assert sentinel_paths == ["index.html"]
```

Check absence from `articles/index.html`, `articles/*.html`, `details/*.html`, `data/edition.json`, `data/manifest.json`, `data/runtime.json`, and `data/articles/*.json`.

- [ ] Add README and `docs/row-one.md` Stage 386 paragraph above Stage 385:

```text
Stage 386 adds a generated-site-only Daily Saved Text Takeaways section on the ROW ONE homepage in `index.html`; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, saved paragraphs, content sections, and local article anchors to show short capped saved-text snippets grouped for reading without changing app-facing contracts; it does not create `data/daily-local-saved-text-takeaways.json`, does not create `data/daily-saved-text-takeaways.json`, does not create `daily-local-saved-text-takeaways.html`, does not create `daily-saved-text-takeaways.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, detail pages, `data/edition.json`, `data/manifest.json`, or `data/runtime.json`, does not publish full article bodies on the homepage, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
```

- [ ] Add docs test that asserts the paragraph appears in README and `docs/row-one.md`, appears before Stage 385, and does not include stale phrases such as `creates data/daily-local-saved-text-takeaways.json`, `adds routes`, `changes scraping`, or `adds compliance-review behavior`.

- [ ] Run focused workflow/docs tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_stage_386_daily_local_saved_text_takeaways_stays_homepage_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_386_daily_saved_text_takeaways_boundary \
  -q
```

Expected: PASS after implementation.

### Task 5: Reviews and verification gates

**Files:**
- Create: `docs/reviews/claude-code-stage-386-plan-review.md`
- Create: `docs/reviews/opencode-stage-386-plan-review.md`
- Create: `docs/reviews/claude-code-stage-386-code-review.md`
- Create: `docs/reviews/opencode-stage-386-code-review.md`

- [ ] Request Claude Code plan review before implementation:

```bash
printf '%s\n' "Review docs/superpowers/plans/2026-07-12-stage-386-daily-saved-text-takeaways-plan.md for feasibility, technical fit, scope boundaries, and test coverage. Use --effort max. Do not edit files." \
  | claude --print --effort max --add-dir /home/ubuntu/fashion-radar \
  > docs/reviews/claude-code-stage-386-plan-review.md
```

- [ ] If Claude Code times out, write a concise timeout attempt note instead of keeping empty or live-capture output.

- [ ] Request opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 "Review docs/superpowers/plans/2026-07-12-stage-386-daily-saved-text-takeaways-plan.md for feasibility, technical fit, scope boundaries, and test coverage. Do not edit files." \
  > docs/reviews/opencode-stage-386-plan-review.md
```

- [ ] If opencode times out or only emits live-capture chatter, replace it with a concise timeout attempt note.

- [ ] After implementation, run Claude Code and opencode code reviews with the same clean-artifact policy.

- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_saved_text_takeaways.py \
  tests/test_row_one_render.py -k 'daily_local_saved_text_takeaways or saved_text_takeaways' \
  tests/test_workflows.py::test_stage_386_daily_local_saved_text_takeaways_stays_homepage_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_386_daily_saved_text_takeaways_boundary \
  -q
```

- [ ] Run related suite:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_saved_text_takeaways.py \
  tests/test_row_one_daily_local_synthesis_brief.py \
  tests/test_row_one_local_article_synthesis_brief.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  -q
```

- [ ] Run full gates:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --cached --check
```

- [ ] Commit and push:

```bash
git add README.md docs/row-one.md src/fashion_radar/row_one/daily_local_saved_text_takeaways.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_saved_text_takeaways.py tests/test_row_one_docs.py tests/test_row_one_render.py tests/test_workflows.py docs/reviews/claude-code-stage-386-plan-review.md docs/reviews/opencode-stage-386-plan-review.md docs/reviews/claude-code-stage-386-code-review.md docs/reviews/opencode-stage-386-code-review.md docs/superpowers/plans/2026-07-12-stage-386-daily-saved-text-takeaways-plan.md
git commit -m "Stage 386: add daily saved text takeaways"
git push origin main
```

## Definition of Done

- Stage 386 appears on the generated ROW ONE homepage only.
- Homepage shows short saved-text excerpts grouped into deterministic reading lanes.
- Every link points to existing local article paragraph or content-section anchors.
- No new JSON/app/runtime/manifest/schema/route/source/scraping/LLM/scheduling/deployment/compliance behavior is added.
- All focused, related, and full verification gates pass.
- Plan review, code review attempts/results, commit, push, and Handoff Summary are complete.
