# Stage 300 ROW ONE Local Article Content Sections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add structured content sections to each saved ROW ONE local article so the website publishes organized local article content, not only a brief plus raw paragraphs.

**Architecture:** Extend `RowOneLocalArticle` sidecars with optional `content_sections` derived from existing saved article paragraphs and `RowOneStory` metadata. Each section contains typed items with localized labels/bodies, optional `RowOneReference` links, and paragraph indices pointing back into the saved body. Render these sections inside the existing local article block, after the Stage 299 brief and before the saved body paragraphs, using the existing language toggle and HTML escaping.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

Stages 297-299 made ROW ONE detail pages save local article paragraphs, render bilingual bodies, and add a four-card scan layer. Stage 300 adds a structured middle layer that makes every saved article feel like a local ROW ONE publishing unit:

- `takeaways`: scannable items from the first saved source paragraphs.
- `entities`: people, brands, designers, and other story refs with paragraph matches.
- `product_signals`: product refs with paragraph matches when available.
- `brand_signals`: tags, heat, source context, regions, and signal context.

The model is intentionally generic. Later social/community connectors can add more refs and paragraphs to the same shape without another sidecar contract redesign.

This is not a new crawler, LLM summarizer, app contract bump, compliance-review feature, recommendation engine, or visual redesign. It does not change `row-one-app/v7`, `data/edition.json`, source extraction, translation services, social connectors, or deployment behavior.

## File Structure

- Modify `src/fashion_radar/row_one/models.py`
  - Move the existing `RowOneReference` class above the local article content models for definition-order clarity.
  - Add `RowOneLocalArticleContentKey`.
  - Add `RowOneLocalArticleContentItem`.
  - Add `RowOneLocalArticleContentSection`.
  - Add `content_sections: list[RowOneLocalArticleContentSection] = Field(default_factory=list)` to `RowOneLocalArticle`.
- Modify `src/fashion_radar/row_one/articles.py`
  - Add `_local_article_content_sections(story, paragraphs, paragraphs_zh)`.
  - Add helper functions for takeaways, paragraph matching, reference sections, and brand signal items.
  - Populate `content_sections` in both extracted and fallback local article paths.
- Modify `src/fashion_radar/row_one/templates.py`
  - Add `_render_local_article_content_sections(article)`.
  - Render content sections between the Stage 299 brief and the saved body paragraphs.
  - Add modest CSS for `.local-article-content-sections`.
- Modify `tests/test_row_one_articles.py`
  - Assert local article sidecars get structured content sections.
  - Assert refs and paragraph indices are preserved.
  - Assert empty optional sections are omitted.
  - Assert backward-compatible default `content_sections == []`.
- Modify `tests/test_row_one_render.py`
  - Assert content sections render with bilingual spans.
  - Assert sidecar JSON includes `content_sections`.
  - Assert section/item/reference values are escaped.
  - Assert local article rendering remains backward-compatible when `content_sections` is empty.

## Task 1: Plan Review Gate

- [ ] Create `docs/reviews/claude-code-stage-300-plan-review-prompt.md` and `docs/reviews/opencode-stage-300-plan-review-prompt.md`.
- [ ] Attempt Claude Code plan review with `--effort max`; if unavailable, record `Verdict: UNAVAILABLE`.
- [ ] Run opencode fallback plan review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- [ ] Fix Critical/Important findings before implementation.

## Task 2: RED Article Builder Tests

- [ ] **Step 1: Import new model dependencies in `tests/test_row_one_articles.py`**

Update the existing model import block:

```python
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)
```

- [ ] **Step 2: Add content-section lookup helpers**

Add below `_assert_local_article_brief_sections(...)`:

```python
def _content_section(article, key: str):
    return next(section for section in article.content_sections if section.key == key)


def _content_item(section, label_en: str):
    return next(item for item in section.items if item.label.en == label_en)
```

- [ ] **Step 3: Assert default constructor compatibility**

Add near the existing model-oriented local article tests:

```python
def test_row_one_local_article_content_sections_default_empty() -> None:
    article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph."],
    )

    assert article.content_sections == []
```

- [ ] **Step 4: Add metadata-rich content-section test**

Add near the other builder tests:

```python
def test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="Zendaya", type="celebrity", label="new"),
    ]
    story.product_refs = [
        RowOneReference(name="Margaux", type="product", label="bag"),
    ]
    story.designer_refs = [
        RowOneReference(name="Mary-Kate Olsen", type="designer", label="founder"),
    ]
    story.tags = ["celebrity", "The Row", "quiet luxury", "The Row"]
    story.heat_delta = 7
    story.market_region = "US"
    story.source_region = "Global"

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Structured source",
            text=(
                "First source paragraph frames The Row demand.\n\n"
                "Second source paragraph shows Zendaya styling context around Margaux.\n\n"
                "Third source paragraph mentions Mary-Kate Olsen and a product signal."
            ),
            skipped=False,
        )

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert [section.key for section in article.content_sections] == [
        "takeaways",
        "entities",
        "product_signals",
        "brand_signals",
    ]

    takeaways = _content_section(article, "takeaways")
    assert [item.body.en for item in takeaways.items] == [
        "First source paragraph frames The Row demand.",
        "Second source paragraph shows Zendaya styling context around Margaux.",
        "Third source paragraph mentions Mary-Kate Olsen and a product signal.",
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[0], [1], [2]]

    entities = _content_section(article, "entities")
    the_row = _content_item(entities, "The Row")
    zendaya = _content_item(entities, "Zendaya")
    olsen = _content_item(entities, "Mary-Kate Olsen")
    assert the_row.references == [story.entity_refs[0]]
    assert the_row.paragraph_indices == [0]
    assert zendaya.paragraph_indices == [1]
    assert olsen.paragraph_indices == [2]

    product_signals = _content_section(article, "product_signals")
    margaux = _content_item(product_signals, "Margaux")
    assert margaux.references == [story.product_refs[0]]
    assert margaux.paragraph_indices == [1]

    brand_signals = _content_section(article, "brand_signals")
    assert _content_item(brand_signals, "Heat delta").body.en == "+7"
    assert _content_item(brand_signals, "Tags").body.en == "celebrity, The Row, quiet luxury"
    assert _content_item(brand_signals, "Source").body.en == "Vogue Business"
    assert _content_item(brand_signals, "Market region").body.en == "US"
    assert _content_item(brand_signals, "Source region").body.en == "Global"
```

- [ ] **Step 5: Add fallback content-section test**

Add:

```python
def test_build_row_one_local_articles_content_sections_work_on_fallback() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise RuntimeError("network failed")

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert [section.key for section in article.content_sections] == [
        "takeaways",
        "entities",
        "brand_signals",
    ]
    assert _content_section(article, "takeaways").items[0].body.en == "Summary"
    assert _content_item(_content_section(article, "entities"), "The Row").references == [
        story.entity_refs[0]
    ]
```

- [ ] **Step 6: Add empty-optional-section test**

Add:

```python
def test_build_row_one_local_articles_omits_empty_optional_content_sections() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Plain source",
            text="Plain source paragraph without refs.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert [section.key for section in article.content_sections] == [
        "takeaways",
        "brand_signals",
    ]
    assert "entities" not in [section.key for section in article.content_sections]
    assert "product_signals" not in [section.key for section in article.content_sections]
```

- [ ] **Step 7: Add JSON dump stability test**

Add:

```python
def test_build_row_one_local_articles_content_sections_model_dump_json() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.product_refs = [RowOneReference(name="Margaux", type="product", label="bag")]

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Product source",
            text="The Margaux bag is the product signal to watch.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    dumped = articles["the-row-signal-1234567890"].model_dump(mode="json")
    product_section = next(
        section for section in dumped["content_sections"] if section["key"] == "product_signals"
    )
    assert product_section["items"][0]["label"]["en"] == "Margaux"
    assert product_section["items"][0]["references"] == [
        {"name": "Margaux", "type": "product", "label": "bag"}
    ]
    assert product_section["items"][0]["paragraph_indices"] == [0]
```

- [ ] **Step 8: Run RED article tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_row_one_local_article_content_sections_default_empty \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_content_sections_work_on_fallback \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_omits_empty_optional_content_sections \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_content_sections_model_dump_json \
  -q
```

Expected before implementation: tests fail because `RowOneLocalArticle` has no `content_sections` field and no content-section models/helpers exist.

## Task 3: GREEN Article Builder Implementation

- [ ] **Step 1: Move `RowOneReference` and add content-section models**

In `src/fashion_radar/row_one/models.py`, move the existing `RowOneReference`
class so it sits immediately after `RowOneLink`. The module can resolve forward
annotations today, so this move is for definition-order clarity while adding
`RowOneLocalArticleContentItem.references`.

```python
class RowOneReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    label: str
```

Delete the old lower copy of `RowOneReference` after `RowOneStoryDisplay`.

Then add near the existing local article aliases:

```python
RowOneLocalArticleContentKey = Literal[
    "takeaways",
    "entities",
    "product_signals",
    "brand_signals",
]
```

Add after `RowOneLocalArticleBriefSection`:

```python
class RowOneLocalArticleContentItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: LocalizedText
    body: LocalizedText | None = None
    references: list[RowOneReference] = Field(default_factory=list)
    paragraph_indices: list[int] = Field(default_factory=list)


class RowOneLocalArticleContentSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: RowOneLocalArticleContentKey
    title: LocalizedText
    body: LocalizedText | None = None
    items: list[RowOneLocalArticleContentItem] = Field(default_factory=list)
```

Add to `RowOneLocalArticle`:

```python
content_sections: list[RowOneLocalArticleContentSection] = Field(default_factory=list)
```

- [ ] **Step 2: Import model types in `src/fashion_radar/row_one/articles.py`**

Add:

```python
RowOneLocalArticleContentKey,
RowOneLocalArticleContentItem,
RowOneLocalArticleContentSection,
RowOneReference,
```

- [ ] **Step 3: Add paragraph matching and label helpers**

Add after `_local_article_brief_sections(...)`:

```python
def _localized_content_item(
    *,
    label_en: str,
    label_zh: str | None = None,
    body_en: str | None = None,
    body_zh: str | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=LocalizedText(en=label_en, zh=label_zh or label_en),
        body=(
            LocalizedText(en=body_en, zh=body_zh if body_zh is not None else body_en)
            if body_en is not None
            else None
        ),
        references=list(references or []),
        paragraph_indices=list(paragraph_indices or []),
    )


def _local_article_paragraph_indices(
    paragraphs: list[str],
    terms: list[str],
    *,
    limit: int = 3,
) -> list[int]:
    normalized_terms = [
        normalize_row_one_paragraph(term).casefold()
        for term in terms
        if len(normalize_row_one_paragraph(term)) >= 3
    ]
    if not normalized_terms:
        return []
    indices: list[int] = []
    for index, paragraph in enumerate(paragraphs):
        paragraph_key = paragraph.casefold()
        if any(term in paragraph_key for term in normalized_terms):
            indices.append(index)
            if len(indices) >= limit:
                break
    return indices
```

- [ ] **Step 4: Add section builders**

Add:

```python
def _local_article_takeaway_section(
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> RowOneLocalArticleContentSection | None:
    aligned_zh = _align_local_article_language_paragraphs(paragraphs, paragraphs_zh)
    items: list[RowOneLocalArticleContentItem] = []
    for index, (paragraph_en, paragraph_zh) in enumerate(
        zip(paragraphs[:3], aligned_zh[:3], strict=True)
    ):
        if not paragraph_en.strip():
            continue
        label_en = "Source lead" if index == 0 else f"Source point {index + 1}"
        label_zh = "来源导语" if index == 0 else f"来源要点 {index + 1}"
        items.append(
            _localized_content_item(
                label_en=label_en,
                label_zh=label_zh,
                body_en=paragraph_en,
                body_zh=paragraph_zh if paragraph_zh.strip() else paragraph_en,
                paragraph_indices=[index],
            )
        )
    if not items:
        return None
    return RowOneLocalArticleContentSection(
        key="takeaways",
        title=LocalizedText(en="Takeaways", zh="要点"),
        body=LocalizedText(
            en="The saved source text points to these immediate reads.",
            zh="本地保存的来源正文首先指向这些要点。",
        ),
        items=items,
    )


def _local_article_reference_section(
    *,
    key: RowOneLocalArticleContentKey,
    title: LocalizedText,
    refs: list[RowOneReference],
    paragraphs: list[str],
) -> RowOneLocalArticleContentSection | None:
    items: list[RowOneLocalArticleContentItem] = []
    seen: set[tuple[str, str, str]] = set()
    for ref in refs:
        identity = (ref.name, ref.type, ref.label)
        if identity in seen:
            continue
        seen.add(identity)
        body = f"{ref.type} / {ref.label}"
        items.append(
            _localized_content_item(
                label_en=ref.name,
                body_en=body,
                body_zh=body,
                references=[ref],
                paragraph_indices=_local_article_paragraph_indices(
                    paragraphs,
                    [ref.name, ref.label],
                ),
            )
        )
    if not items:
        return None
    return RowOneLocalArticleContentSection(key=key, title=title, items=items)
```

- [ ] **Step 5: Add brand-signal helpers**

Add:

```python
def _unique_local_article_tags(tags: list[str], *, limit: int = 4) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        normalized = normalize_row_one_paragraph(tag)
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(normalized)
        if len(unique) >= limit:
            break
    return unique


def _local_article_brand_signal_section(story: RowOneStory) -> RowOneLocalArticleContentSection:
    items: list[RowOneLocalArticleContentItem] = []
    if story.signal_context.en.strip() or story.signal_context.zh.strip():
        items.append(
            RowOneLocalArticleContentItem(
                label=LocalizedText(en="Signal context", zh="信号背景"),
                body=story.signal_context,
            )
        )
    if story.heat_delta is not None:
        sign = "+" if story.heat_delta > 0 else ""
        items.append(
            _localized_content_item(
                label_en="Heat delta",
                label_zh="热度变化",
                body_en=f"{sign}{story.heat_delta}",
                body_zh=f"{sign}{story.heat_delta}",
            )
        )
    tags = _unique_local_article_tags(story.tags)
    if tags:
        tag_text = ", ".join(tags)
        items.append(
            _localized_content_item(
                label_en="Tags",
                label_zh="标签",
                body_en=tag_text,
                body_zh=tag_text,
            )
        )
    if story.market_region:
        items.append(
            _localized_content_item(
                label_en="Market region",
                label_zh="市场区域",
                body_en=story.market_region,
                body_zh=story.market_region,
            )
        )
    if story.source_region:
        items.append(
            _localized_content_item(
                label_en="Source region",
                label_zh="来源区域",
                body_en=story.source_region,
                body_zh=story.source_region,
            )
        )
    items.append(
        _localized_content_item(
            label_en="Source",
            label_zh="来源",
            body_en=story.source_name,
            body_zh=story.source_name,
        )
    )
    return RowOneLocalArticleContentSection(
        key="brand_signals",
        title=LocalizedText(en="Brand Signals", zh="品牌信号"),
        body=LocalizedText(
            en="ROW ONE tracks the metadata around this story for follow-up.",
            zh="ROW ONE 会继续追踪这条内容背后的元数据。",
        ),
        items=items,
    )
```

- [ ] **Step 6: Add `_local_article_content_sections(...)`**

Add:

```python
def _local_article_content_sections(
    story: RowOneStory,
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> list[RowOneLocalArticleContentSection]:
    sections: list[RowOneLocalArticleContentSection] = []
    takeaway_section = _local_article_takeaway_section(paragraphs, paragraphs_zh)
    if takeaway_section is not None:
        sections.append(takeaway_section)
    entity_refs = [*story.entity_refs, *story.designer_refs]
    entity_section = _local_article_reference_section(
        key="entities",
        title=LocalizedText(en="Entities", zh="相关对象"),
        refs=entity_refs,
        paragraphs=paragraphs,
    )
    if entity_section is not None:
        sections.append(entity_section)
    product_section = _local_article_reference_section(
        key="product_signals",
        title=LocalizedText(en="Product Signals", zh="产品信号"),
        refs=story.product_refs,
        paragraphs=paragraphs,
    )
    if product_section is not None:
        sections.append(product_section)
    sections.append(_local_article_brand_signal_section(story))
    return sections
```

- [ ] **Step 7: Populate extracted and fallback articles**

In both `RowOneLocalArticle(...)` constructors inside `src/fashion_radar/row_one/articles.py`, add:

```python
content_sections=_local_article_content_sections(story, paragraphs, paragraphs_zh),
```

- [ ] **Step 8: Run GREEN article tests**

Run the command from Task 2 Step 8. Expected: selected tests pass.

## Task 4: RED Render Tests

- [ ] **Step 1: Import content-section models**

In `tests/test_row_one_render.py`, import:

```python
RowOneLocalArticleContentItem,
RowOneLocalArticleContentSection,
```

`RowOneReference` is already imported in this file; do not add it twice.

- [ ] **Step 2: Add content sections to the main local article render fixture**

In `test_render_row_one_detail_includes_local_article_content`, add to the `RowOneLocalArticle(...)` fixture:

```python
content_sections=[
    RowOneLocalArticleContentSection(
        key="takeaways",
        title=LocalizedText(en="Takeaways", zh="要点"),
        body=LocalizedText(en="Saved source reads.", zh="本地来源要点。"),
        items=[
            RowOneLocalArticleContentItem(
                label=LocalizedText(en="Source lead", zh="来源导语"),
                body=LocalizedText(en="The Row demand moved.", zh="The Row 需求变化。"),
                paragraph_indices=[0],
            )
        ],
    ),
    RowOneLocalArticleContentSection(
        key="entities",
        title=LocalizedText(en="Entities", zh="相关对象"),
        items=[
            RowOneLocalArticleContentItem(
                label=LocalizedText(en="The Row", zh="The Row"),
                body=LocalizedText(en="brand / tracked", zh="brand / tracked"),
                references=[
                    RowOneReference(name="The Row", type="brand", label="tracked"),
                ],
                paragraph_indices=[0],
            )
        ],
    ),
],
```

- [ ] **Step 3: Assert content sections render and serialize**

In the same test add:

```python
assert 'class="local-article-content-sections"' in detail_html
assert '<span data-lang="en">Takeaways</span>' in detail_html
assert '<span data-lang="zh">要点</span>' in detail_html
assert '<span data-lang="en">Source lead</span>' in detail_html
assert '<span data-lang="zh">来源导语</span>' in detail_html
assert '<span data-lang="en">The Row demand moved.</span>' in detail_html
assert '<span data-lang="zh">The Row 需求变化。</span>' in detail_html
assert "Paragraph 1" in detail_html
assert "段落 1" in detail_html
assert "Refs: The Row (brand / tracked)" in detail_html
assert "引用：The Row（brand / tracked）" in detail_html
assert detail_html.index('class="local-article-brief"') < detail_html.index(
    'class="local-article-content-sections"'
)
assert detail_html.index('class="local-article-content-sections"') < detail_html.index(
    'class="local-article-body"'
)
assert [section["key"] for section in article_json["content_sections"]] == [
    "takeaways",
    "entities",
]
assert article_json["content_sections"][1]["items"][0]["references"] == [
    {"name": "The Row", "type": "brand", "label": "tracked"}
]
assert "The Row demand moved." not in edition_json
```

- [ ] **Step 4: Assert legacy articles remain backward-compatible**

In `test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs`, add:

```python
assert 'class="local-article-content-sections"' not in detail_html
assert 'href="#local-article"' in detail_html
```

- [ ] **Step 5: Assert mismatched body language still allows bilingual content sections**

In `test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch`, add a bilingual content section to the fixture:

```python
content_sections=[
    RowOneLocalArticleContentSection(
        key="takeaways",
        title=LocalizedText(en="Takeaways", zh="要点"),
        items=[
            RowOneLocalArticleContentItem(
                label=LocalizedText(en="Source lead", zh="来源导语"),
                body=LocalizedText(en="Structured English.", zh="结构化中文。"),
                paragraph_indices=[0],
            )
        ],
    )
],
```

Then assert:

```python
assert '<span data-lang="en">Structured English.</span>' in detail_html
assert '<span data-lang="zh">结构化中文。</span>' in detail_html
assert "<p>One source paragraph.</p>" in detail_html
assert '<span data-lang="zh">一段中文。</span>' not in detail_html
```

- [ ] **Step 6: Add escaping coverage**

In `test_render_row_one_detail_escapes_local_article_content`, add a malicious content section:

```python
content_sections=[
    RowOneLocalArticleContentSection(
        key="takeaways",
        title=LocalizedText(en="<script>Section</script>", zh="章节<script>"),
        body=LocalizedText(
            en='<img src=x onerror="alert(4)"> & body',
            zh='<img src=x onerror="alert(5)"> 中文 & body',
        ),
        items=[
            RowOneLocalArticleContentItem(
                label=LocalizedText(en="<script>Item</script>", zh="条目<script>"),
                body=LocalizedText(
                    en='<img src=x onerror="alert(6)"> & item',
                    zh='<img src=x onerror="alert(7)"> 中文 & item',
                ),
                references=[
                    RowOneReference(name="<script>Ref</script>", type="brand", label="tracked")
                ],
                paragraph_indices=[0],
            )
        ],
    )
],
```

Assert escaped section title, body, item label, item body, and reference strings appear, and raw `<script>`, `<img`, and `onerror="alert` do not.

Use explicit assertions:

```python
assert "&lt;script&gt;Section&lt;/script&gt;" in detail_html
assert "&lt;img src=x onerror=&quot;alert(4)&quot;&gt; &amp; body" in detail_html
assert "&lt;img src=x onerror=&quot;alert(5)&quot;&gt; 中文 &amp; body" in detail_html
assert "&lt;script&gt;Item&lt;/script&gt;" in detail_html
assert "&lt;img src=x onerror=&quot;alert(6)&quot;&gt; &amp; item" in detail_html
assert "&lt;img src=x onerror=&quot;alert(7)&quot;&gt; 中文 &amp; item" in detail_html
assert "&lt;script&gt;Ref&lt;/script&gt;" in detail_html
assert "<script>" not in detail_html
assert "<img" not in detail_html
assert 'onerror="alert' not in detail_html
```

- [ ] **Step 7: Add no-body gate test**

Add:

```python
def test_render_row_one_detail_omits_local_article_content_sections_without_body_paragraphs(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(en="Structured English.", zh="结构化中文。"),
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'id="local-article"' not in detail_html
    assert 'href="#local-article"' not in detail_html
    assert not (tmp_path / "data" / "articles").exists()
```

- [ ] **Step 8: Run RED render tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs \
  tests/test_row_one_render.py::test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch \
  tests/test_row_one_render.py::test_render_row_one_detail_escapes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_omits_local_article_content_sections_without_body_paragraphs \
  -q
```

Expected before implementation: tests fail because the model and renderer do not support `content_sections`.

## Task 5: GREEN Render Implementation

- [ ] **Step 1: Render content sections**

In `src/fashion_radar/row_one/templates.py`, inside `_render_local_article(...)`, add:

```python
content_sections = _render_local_article_content_sections(article)
```

and include `{content_sections}` between `{brief}` and `<div class="local-article-body">`.

- [ ] **Step 2: Add content-section render helpers**

Add below `_render_local_article_brief(...)`:

```python
def _render_local_article_content_sections(article: RowOneLocalArticle) -> str:
    rendered_sections = []
    for section in article.content_sections:
        rendered_items = "\n".join(
            _render_local_article_content_item(item) for item in section.items
        )
        items = f"""          <ul class="local-article-content-items">
{rendered_items}
          </ul>""" if rendered_items else ""
        body = (
            f"""          <p>
            <span data-lang="en">{_esc(section.body.en)}</span>
            <span data-lang="zh">{_esc(section.body.zh)}</span>
          </p>"""
            if section.body is not None
            else ""
        )
        rendered_sections.append(
            f"""        <article class="local-article-content-card">
          <h4>
            <span data-lang="en">{_esc(section.title.en)}</span>
            <span data-lang="zh">{_esc(section.title.zh)}</span>
          </h4>
{body}
{items}
        </article>"""
        )
    if not rendered_sections:
        return ""
    rendered = "\n".join(rendered_sections)
    return f"""      <div class="local-article-content-sections" aria-label="ROW ONE local article content">
{rendered}
      </div>"""


def _render_local_article_content_item(item: RowOneLocalArticleContentItem) -> str:
    body = (
        f"""              <p>
                <span data-lang="en">{_esc(item.body.en)}</span>
                <span data-lang="zh">{_esc(item.body.zh)}</span>
              </p>"""
        if item.body is not None
        else ""
    )
    paragraphs = _render_local_article_paragraph_indices(item.paragraph_indices)
    refs = _render_local_article_content_references(item.references)
    return f"""            <li>
              <strong>
                <span data-lang="en">{_esc(item.label.en)}</span>
                <span data-lang="zh">{_esc(item.label.zh)}</span>
              </strong>
{body}
{paragraphs}
{refs}
            </li>"""
```

- [ ] **Step 3: Add paragraph-index and reference render helpers**

Add:

```python
def _render_local_article_paragraph_indices(indices: list[int]) -> str:
    if not indices:
        return ""
    en = ", ".join(f"Paragraph {index + 1}" for index in indices)
    zh = "、".join(f"段落 {index + 1}" for index in indices)
    return f"""              <p class="local-article-content-meta">
                <span data-lang="en">{_esc(en)}</span>
                <span data-lang="zh">{_esc(zh)}</span>
              </p>"""


def _render_local_article_content_references(references: list[RowOneReference]) -> str:
    if not references:
        return ""
    en_refs = ", ".join(
        f"{ref.name} ({ref.type} / {ref.label})" for ref in references
    )
    zh_refs = "，".join(
        f"{ref.name}（{ref.type} / {ref.label}）" for ref in references
    )
    return f"""              <p class="local-article-content-meta">
                <span data-lang="en">Refs: {_esc(en_refs)}</span>
                <span data-lang="zh">引用：{_esc(zh_refs)}</span>
              </p>"""
```

Also import `RowOneLocalArticleContentItem` and `RowOneReference` from `fashion_radar.row_one.models` if the template module does not already have them.

- [ ] **Step 4: Add content-section CSS**

Add near the `.local-article-brief` styles:

```css
.local-article-content-sections {
  display: grid;
  gap: 14px;
  margin: 0 0 24px;
}
.local-article-content-card {
  border-left: 2px solid var(--ink);
  padding: 0 0 0 16px;
}
.local-article-content-card h4 {
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-content-card p {
  color: var(--ink);
  line-height: 1.55;
  margin: 0 0 10px;
}
.local-article-content-items {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-content-items li {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
.local-article-content-items strong {
  display: block;
  font-size: 0.82rem;
  margin-bottom: 4px;
}
.local-article-content-meta {
  color: var(--muted);
  font-size: 0.78rem;
  margin: 4px 0 0;
}
```

- [ ] **Step 5: Run GREEN render tests**

Run the command from Task 4 Step 8. Expected: selected tests pass.

## Task 6: Verification And Site Proof

- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
```

- [ ] Run release gate:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv lock --check
```

- [ ] Rebuild today's site:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
```

- [ ] Run proof script verifying:
  - `story_count == 18`
  - `data/articles/*.json == 18`
  - `details/*.html == 18`
  - every sidecar has `content_sections`
  - every sidecar has `takeaways`
  - every sidecar has `brand_signals`
  - optional `entities` and `product_signals` sections are omitted when empty
  - every `takeaways` section has at least one item with a paragraph index
  - every `brand_signals` section has a `Source` item
  - every detail page with `id="local-article"` includes `class="local-article-content-sections"`
  - `data/edition.json` still does not contain local article sidecar-only structures such as `paragraph_indices` or `local-article-content-sections`; note that `edition.json` already has an app-level `content_sections` field for ROW ONE page sections

## Task 7: Code Review, Commit, Push

- [ ] Create `docs/reviews/claude-code-stage-300-code-review-prompt.md` and `docs/reviews/opencode-stage-300-code-review-prompt.md`.
- [ ] Attempt Claude Code with `--effort max`; record `Verdict: UNAVAILABLE` if it does not produce a completed body.
- [ ] Run opencode code review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- [ ] Fix Critical/Important findings.
- [ ] Commit and push:

```bash
git add src/fashion_radar/row_one/models.py \
  src/fashion_radar/row_one/articles.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_articles.py \
  tests/test_row_one_render.py \
  docs/superpowers/plans/2026-07-05-stage-300-row-one-local-article-content-sections-plan.md \
  docs/reviews/claude-code-stage-300-*.md \
  docs/reviews/opencode-stage-300-*.md
git diff --cached --check
git commit -m "Stage 300: add row one local article content sections"
git push origin main
```

## Handoff Summary Template

```markdown
**Handoff Summary**
- Repo: `/home/ubuntu/fashion-radar`
- Branch/commit: `main` at `<sha>`, pushed to `origin/main`
- Verified commands: focused article/render tests, full suite, ruff, release hygiene, uv lock, today site rebuild content-section proof
- Uncommitted files: `<git status --short>`
- Generated site: `reports/row-one/site` rebuilt but ignored
- Next step: continue local content depth or move to presentation polish.
```
