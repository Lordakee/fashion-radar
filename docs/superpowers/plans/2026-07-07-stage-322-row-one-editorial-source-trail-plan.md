# Stage 322 ROW ONE Editorial Source Trail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add compact generated-site-only source trails inside ROW ONE Editorial Brief cards so readers can trace prose back to existing saved local article sections and paragraph anchors.

**Architecture:** Extend the private Stage 321 Editorial Brief render payload with private trail item dataclasses in `templates.py`, build the trails deterministically in `render.py`, and render them only as homepage HTML. Keep all app/runtime/manifest JSON contracts and schemas unchanged.

**Tech Stack:** Python, existing Pydantic `LocalizedText`/ROW ONE models, dataclasses, string-rendered HTML/CSS in `templates.py`, pytest, Ruff, Claude Code review gates.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
  - Add `_EditorialBriefTrailItem`.
  - Add `trail` to `_EditorialBriefItem`.
  - Render trail chips/links inside `_render_editorial_brief_card()`.
  - Reuse `_safe_editorial_brief_href()`.
  - Add CSS selectors.
- Modify: `src/fashion_radar/row_one/render.py`
  - Build per-card trail items in `_editorial_brief_items()`.
  - Add helpers for local article section/paragraph hrefs, labels, cap, and dedupe.
- Modify: `tests/test_row_one_render.py`
  - Add Stage 322 render, omission, link safety, cap/dedupe, and CSS tests.
- Modify: `tests/test_workflows.py`
  - Add generated-site-only HTML/JSON absence assertions.
- Modify: `tests/test_row_one_docs.py`
  - Add Stage 322 docs boundary test.
- Modify: `README.md`
  - Add Stage 322 generated-site-only paragraph.
- Modify: `docs/row-one.md`
  - Add Stage 322 generated-site-only paragraph.
- Create: `docs/reviews/claude-code-stage-322-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-322-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-322-code-review-prompt.md`
- Create after implementation: `docs/reviews/claude-code-stage-322-code-review.md`

## Task 1: Add Failing Render Tests

- [ ] **Step 1: Prepare imports without breaking test collection**

In `tests/test_row_one_render.py`, confirm the standard-library import block already includes `import re`; Stage 321 tests already use it. If it is missing, add it. Do not add `_EditorialBriefTrailItem` or `EDITORIAL_BRIEF_MAX_TRAIL_ITEMS` to the module-level import block during Task 1 because Task 2 creates those symbols. Use local imports inside the new tests that need those not-yet-created symbols so the existing `tests/test_row_one_render.py` module still collects and only the new Stage 322 tests go red for the right reason.

Before adding tests that call `render_index_html(..., editorial_brief=...)`,
confirm the current `render_index_html` signature in
`src/fashion_radar/row_one/templates.py` already accepts the explicit keyword
parameter `editorial_brief: _EditorialBrief | None = None`. Stage 321 already
added it; if it is missing, stop and update the plan before writing those tests.
Also confirm `LocalizedText` is already imported from
`fashion_radar.row_one.models`; Stage 321 tests use it heavily, but add it to
the existing models import block if it is absent.

```python
from fashion_radar.row_one.templates import (
    EDITORIAL_BRIEF_BODY_EXCERPT_CHARS,
    _EditorialBrief,
    _EditorialBriefItem,
    _safe_daily_local_intelligence_href,
    render_detail_html,
    render_index_html,
    row_one_css,
)
```

- [ ] **Step 2: Verify the existing local article fixture supports the test**

Before adding the render test, verify `_signal_briefing_local_article()` still
includes the source/title metadata and section titles that the assertions rely
on. `Vogue Business` comes from `local_article.source_name`; `Signal source
article` comes from `local_article.title`; together they are rendered by
`_editorial_brief_meta(...)` as the existing Stage 321 meta text.

```python
local_article = _signal_briefing_local_article()
assert local_article.source_name == "Vogue Business"
assert local_article.title == "Signal source article"
assert local_article.paragraphs
assert any(paragraph.strip() for paragraph in local_article.paragraphs)

brief_section = next(
    section
    for section in local_article.brief_sections
    if section.key == "what_happened"
)
assert brief_section.title.en == "What Happened"
assert brief_section.title.zh == "发生了什么"

content_section = next(
    section
    for section in local_article.content_sections
    if section.key == "entities"
)
assert content_section.title.en == "People & Brands"
assert content_section.title.zh == "品牌与人物"
```

If the fixture has changed, update only the test fixture setup for this Stage 322
test so it explicitly creates a `what_happened` brief section titled
`What Happened / 发生了什么` and an `entities` content section titled
`People & Brands / 品牌与人物`; also include at least one non-empty paragraph so
the first paragraph anchor assertion is meaningful. Do not rely on unrelated
fixture ordering.

- [ ] **Step 2a: Add Editorial Brief section extraction helper for new tests**

Add this helper near the existing Editorial Brief tests in
`tests/test_row_one_render.py` and use it in all Stage 322 tests that need to
inspect only the Editorial Brief section. Do not use
`index_html.index("</section>", section_start)` in the new Stage 322 tests; that
pattern cuts too early if a future Editorial Brief card contains a nested
`<section>`.

```python
def _editorial_brief_section_html(index_html: str) -> str:
    marker = '<section class="editorial-brief"'
    section_start = index_html.index(marker)
    next_section = re.search(
        r"\n<section class=",
        index_html[section_start + len(marker) :],
    )
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]
```

This helper assumes ROW ONE homepage sections are emitted as top-level
`<section class="...">` blocks starting at column zero, which matches the
current templates. It intentionally ignores indented nested sections.

- [ ] **Step 3: Add source-trail render test**

Add near the Stage 321 Editorial Brief tests:

```python
def test_render_row_one_site_includes_editorial_brief_source_trail(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()
    # Fixture includes an entities content section titled People & Brands / 品牌与人物.

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)

    assert 'class="editorial-brief-trail"' in section_html
    assert "Vogue Business" in section_html
    assert "Signal source article" in section_html
    assert "What Happened" in section_html
    assert "发生了什么" in section_html
    assert "People &amp; Brands" in section_html
    assert "品牌与人物" in section_html
    assert 'class="editorial-brief-meta"' in section_html
    assert section_html.count("Vogue Business") == 2
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert re.search(
        r'href="details/the-row-signal-1234567890.html#local-article-content-section-[1-9][0-9]*"',
        section_html,
    )
    assert '<a class="editorial-brief-card"' not in section_html
    assert '<article class="editorial-brief-card">' in section_html
```

- [ ] **Step 4: Add content-section trail detail-anchor test**

Add a separate cross-page anchor alignment test near the source-trail render test:

```python
def test_render_row_one_site_editorial_brief_content_section_trail_resolves_to_detail_anchor(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (
        tmp_path / "details" / "the-row-signal-1234567890.html"
    ).read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)
    match = re.search(
        r'href="details/the-row-signal-1234567890.html#(?P<fragment>local-article-content-section-[1-9][0-9]*)"',
        section_html,
    )

    assert match is not None
    assert f'id="{match.group("fragment")}"' in detail_html
```

- [ ] **Step 5: Add omission test**

```python
def test_render_row_one_site_omits_editorial_brief_source_trail_without_local_article(
    tmp_path,
) -> None:
    render_row_one_site(_edition(), tmp_path, local_articles_by_story_id={})

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)

    assert 'class="editorial-brief-trail"' not in section_html
    assert "Editorial Brief" in section_html
    assert "What changed today" in section_html
```

- [ ] **Step 6: Add direct link safety test**

```python
def test_render_index_html_filters_editorial_brief_source_trail_links() -> None:
    from fashion_radar.row_one.detail_routes import (
        validated_row_one_detail_relative_path,
    )
    from fashion_radar.row_one.templates import (
        _EditorialBriefTrailItem,
        _safe_editorial_brief_href,
    )

    for unsafe_path in (
        "../secrets.html",
        "details/../admin.html",
        "details/%2e%2e/admin.html",
        "details/%2E%2E/admin.html",
        "details/%252e%252e/admin.html",
        "details/%2e%2e-1234567890.html",
    ):
        assert validated_row_one_detail_relative_path(unsafe_path) is None

    # Direct validator assertions keep the route trust boundary covered even if
    # _safe_editorial_brief_href changes later.

    for unsafe_href in (
        None,
        "",
        "   ",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "http://evil.example/story",
        "https://evil.example/story",
        "//evil.example/story",
        "../secrets.html",
        "details/../admin.html",
        "details/%2e%2e/admin.html",
        "details/%2E%2E/admin.html",
        "details/%252e%252e/admin.html",
        "details/the-row-signal-1234567890.html#local-article-paragraph-0",
        "details/the-row-signal-1234567890.html#local-article-paragraph--1",
        "details/the-row-signal-1234567890.html#local-article-paragraph-",
        "details/the-row-signal-1234567890.html#local-article-paragraph-abc",
        "details/the-row-signal-1234567890.html#local-article-paragraph-1;drop",
        "details/the-row-signal-1234567890.html#local-article-content-section-0",
        "details/the-row-signal-1234567890.html#local-article-content-section--1",
        "details/the-row-signal-1234567890.html#local-article-content-section-",
        "details/the-row-signal-1234567890.html#local-article-content-section-abc",
        "details/the-row-signal-1234567890.html#local-article-content-section-1;drop",
    ):
        assert _safe_editorial_brief_href(unsafe_href) is None

    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Trail Safety", zh="线索安全"),
                    body=LocalizedText(en="Trail body.", zh="线索正文。"),
                    trail=(
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Safe paragraph", zh="安全段落"),
                            href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Safe section", zh="安全栏目"),
                            href="details/the-row-signal-1234567890.html#local-article-content-section-1",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="External <b>", zh="外链 <b>"),
                            href="https://evil.example/story",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="JavaScript URI", zh="脚本地址"),
                            href="javascript:alert(1)",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Data URI", zh="数据地址"),
                            href="data:text/html,<script>alert(1)</script>",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(
                                en='<script>alert(1)</script> " onmouseover="evil',
                                zh="<script>警告</script>",
                            ),
                            href=None,
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Protocol Relative", zh="协议相对"),
                            href="//evil.example/story",
                        ),
                    ),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Bad Fragment", zh="错误片段"),
                    body=LocalizedText(en="Bad fragment body.", zh="错误片段正文。"),
                    trail=(
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Bad section", zh="错误栏目"),
                            href="details/the-row-signal-1234567890.html#local-article-content-section-0",
                        ),
                    ),
                ),
            )
        ),
    )

    section_html = _editorial_brief_section_html(index_html)

    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-content-section-1"' in section_html
    assert "External &lt;b&gt;" in section_html
    assert "JavaScript URI" in section_html
    assert "Data URI" in section_html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in section_html
    assert "&quot; onmouseover=&quot;evil" in section_html
    assert "Protocol Relative" in section_html
    assert "Bad section" in section_html
    assert "javascript:alert" not in section_html
    assert "data:text/html" not in section_html
    assert "https://evil.example" not in section_html
    assert "//evil.example" not in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-content-section-0"' not in section_html
    assert "<b>" not in section_html
    assert "<script>" not in section_html
```

- [ ] **Step 7: Add cap and dedupe test**

```python
def test_render_index_html_caps_and_dedupes_editorial_brief_source_trail() -> None:
    from fashion_radar.row_one.templates import (
        EDITORIAL_BRIEF_MAX_TRAIL_ITEMS,
        _EditorialBriefTrailItem,
    )

    trail_items = (
        _EditorialBriefTrailItem(
            label=LocalizedText(en="One", zh="一"),
            href="details/the-row-signal-1234567890.html",
        ),
        _EditorialBriefTrailItem(
            label=LocalizedText(en="One", zh="一"),
            href="details/the-row-signal-1234567890.html",
        ),
        _EditorialBriefTrailItem(label=LocalizedText(en="Two", zh="二")),
        _EditorialBriefTrailItem(label=LocalizedText(en="Three", zh="三")),
        _EditorialBriefTrailItem(label=LocalizedText(en="Four", zh="四")),
    )
    assert len(trail_items) > EDITORIAL_BRIEF_MAX_TRAIL_ITEMS

    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Trail Cap", zh="线索上限"),
                    body=LocalizedText(en="Trail body.", zh="线索正文。"),
                    trail=trail_items,
                ),
            )
        ),
    )

    section_html = _editorial_brief_section_html(index_html)

    assert section_html.count("editorial-brief-trail-item") == EDITORIAL_BRIEF_MAX_TRAIL_ITEMS
    assert section_html.count(">One<") == 1
    assert 'href="details/the-row-signal-1234567890.html"' in section_html
    assert ">Two<" in section_html
    assert ">Three<" in section_html
    assert ">Four<" not in section_html
    assert section_html.index(">One<") < section_html.index(">Two<") < section_html.index(">Three<")
```

- [ ] **Step 8: Add saved-paragraph fallback trail test**

Add this fallback test near the source-trail render tests. It covers the only
named Stage 322 trail chip that appears only when `watch_next` is absent:

```python
def test_render_row_one_site_editorial_brief_source_trail_uses_saved_paragraph_without_watch_next(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    base_article = _signal_briefing_local_article()
    local_article = base_article.model_copy(
        update={
            "brief_sections": [
                section
                for section in base_article.brief_sections
                if section.key != "watch_next"
            ]
        }
    )
    assert all(section.key != "watch_next" for section in local_article.brief_sections)
    assert local_article.paragraphs

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)
    title_start = section_html.index("What to read locally")
    card_start = section_html.rfind('<article class="editorial-brief-card">', 0, title_start)
    assert card_start != -1
    card_end = section_html.index("</article>", title_start) + len("</article>")
    card_html = section_html[card_start:card_end]

    assert 'class="editorial-brief-trail"' in card_html
    assert "Saved paragraph 1" in card_html
    assert "保存段落 1" in card_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in card_html
```

- [ ] **Step 9: Add double-absent fallback omission test**

Add this test near the saved-paragraph fallback test. It verifies the
`watch_next`-absent path gracefully omits the fallback trail when no saved
paragraph exists:

```python
def test_render_row_one_site_editorial_brief_source_trail_omits_saved_paragraph_without_text(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    base_article = _signal_briefing_local_article()
    local_article = base_article.model_copy(
        update={
            "paragraphs": (),
            "paragraphs_zh": (),
            "brief_sections": [
                section
                for section in base_article.brief_sections
                if section.key != "watch_next"
            ],
        }
    )
    assert all(section.key != "watch_next" for section in local_article.brief_sections)
    assert not local_article.paragraphs

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)
    title_start = section_html.index("What to read locally")
    card_start = section_html.rfind('<article class="editorial-brief-card">', 0, title_start)
    assert card_start != -1
    card_end = section_html.index("</article>", title_start) + len("</article>")
    card_html = section_html[card_start:card_end]

    assert "Saved paragraph 1" not in card_html
    assert "保存段落 1" not in card_html
    assert "#local-article-paragraph-1" not in card_html
```

- [ ] **Step 10: Add item dedupe trail preservation test**

Add this test near `test_editorial_brief_payload_deduplicates_bodies()`:

This test is intentionally lower-level than `_editorial_brief_payload(...)` so
it can prove `_deduped_editorial_brief_items(...)` preserves trail data before
the new Stage 322 trail builders and card call sites are wired.

```python
def test_editorial_brief_item_dedupe_preserves_trail() -> None:
    from fashion_radar.row_one.render import _deduped_editorial_brief_items
    from fashion_radar.row_one.templates import _EditorialBriefTrailItem

    trail = (
        _EditorialBriefTrailItem(
            label=LocalizedText(en="Saved paragraph 1", zh="保存段落 1"),
            href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
    )

    deduped = _deduped_editorial_brief_items(
        (
            _EditorialBriefItem(
                title=LocalizedText(en="Title", zh="标题"),
                body=LocalizedText(en="Same body.", zh="相同正文。"),
                trail=trail,
            ),
            _EditorialBriefItem(
                title=LocalizedText(en="Duplicate", zh="重复"),
                body=LocalizedText(en="Same body.", zh="相同正文。"),
            ),
        )
    )

    assert len(deduped) == 1
    assert deduped[0].trail == trail
```

- [ ] **Step 11: Add CSS selector test**

Extend `test_row_one_css_includes_daily_edit_styles` or add a new adjacent test:

Before writing this test, confirm an existing Stage 320/321 CSS test reads the
stylesheet from `render_row_one_site(...).index_path.parent / "assets" /
"row-one.css"`. Use that same path; if the existing test uses a different
stylesheet location, follow the current repository pattern instead.

```python
def test_row_one_css_includes_editorial_brief_source_trail_styles(tmp_path) -> None:
    index_path = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (index_path.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".editorial-brief-trail",
        ".editorial-brief-trail-item",
        ".editorial-brief-trail a",
        ".editorial-brief-link",
    ):
        assert selector in css_text
```

This follows the existing Stage 320/321 CSS test pattern: `render_row_one_site(...)`
returns `RowOneRenderResult`, and `.index_path` is the generated `index.html` path.

- [ ] **Step 12: Run tests to verify red**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_editorial_brief_source_trail \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_content_section_trail_resolves_to_detail_anchor \
  tests/test_row_one_render.py::test_render_row_one_site_omits_editorial_brief_source_trail_without_local_article \
  tests/test_row_one_render.py::test_render_index_html_filters_editorial_brief_source_trail_links \
  tests/test_row_one_render.py::test_render_index_html_caps_and_dedupes_editorial_brief_source_trail \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_source_trail_uses_saved_paragraph_without_watch_next \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_source_trail_omits_saved_paragraph_without_text \
  tests/test_row_one_render.py::test_editorial_brief_item_dedupe_preserves_trail \
  tests/test_row_one_render.py::test_row_one_css_includes_editorial_brief_source_trail_styles -q
```

Expected: fails because `_EditorialBriefTrailItem`, trail rendering, and builder
trail payloads do not exist yet. The content-section href assertion is
intentionally part of the red suite so Task 2 cannot accidentally ship plain
non-link chips for safe local section anchors even though the underlying
content-section href allowlist is already expected to exist.

## Task 2: Implement Template Trail Rendering

- [ ] **Step 1: Add constants and dataclass**

In `src/fashion_radar/row_one/templates.py`, near the Editorial Brief constants and dataclasses:

```python
EDITORIAL_BRIEF_MAX_TRAIL_ITEMS = 3


@dataclass(frozen=True)
class _EditorialBriefTrailItem:
    label: LocalizedText
    href: str | None = None
```

Then update `_EditorialBriefItem`:

```python
@dataclass(frozen=True)
class _EditorialBriefItem:
    title: LocalizedText
    body: LocalizedText
    meta: LocalizedText | None = None
    href: str | None = None
    trail: tuple[_EditorialBriefTrailItem, ...] = ()
```

- [ ] **Step 2: Confirm Editorial Brief href allowlist accepts content-section fragments**

Before adding trail render helpers, read `_safe_editorial_brief_href(...)` and
the related fragment regexes in `src/fashion_radar/row_one/templates.py`.
Verify, do not modify: `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` is already
present from Stage 319 and `_safe_editorial_brief_href(...)` already accepts all
three supported forms: bare `details/<slug>.html`, paragraph fragments
`details/<slug>.html#local-article-paragraph-N`, and content-section fragments
`details/<slug>.html#local-article-content-section-N`.

The Task 1 direct link safety test must prove the href below renders as an
anchor rather than degrading to a plain chip:

```python
"details/the-row-signal-1234567890.html#local-article-content-section-1"
```

Also confirm `_safe_editorial_brief_href(None)` returns `None` rather than
raising; trail items allow `href: str | None`.

The allowlist is positive and local-route-only: `_safe_editorial_brief_href(...)`
may return a string only when `validated_row_one_detail_relative_path(path)`
accepts the path and the optional fragment is one of
`local-article-paragraph-N` or `local-article-content-section-N` with one-based
positive `N`. It must reject empty/whitespace input, every URL scheme, every
protocol-relative URL, path traversal, and unknown fragments.
The `N` segment for both supported fragment families must match exactly
`[1-9][0-9]*`; zero, negative values, empty values, non-numeric values, and
suffix-injection values such as `1;drop` must be rejected.
Validation must use full-match/anchored semantics, either via
`re.fullmatch(r"[1-9][0-9]*", n)` after extracting `N` or an equivalent
anchored pattern such as `^[1-9][0-9]*$`. Do not use unanchored `re.search(...)`
or prefix-only matching for fragment numbers.
This is a syntax and route-safety allowlist; it does not verify that the target
detail page actually contains paragraph/content-section number `N`. Builder
helpers must generate hrefs only from existing local article paragraphs and
content-section positions so normal generated output resolves to existing
anchors.

- [ ] **Step 3: Add trail render helpers**

`src/fashion_radar/row_one/templates.py` already imports `Sequence` from
`collections.abc` and already has the Stage 321 `_editorial_brief_display_text(...)`
helper. Confirm both before adding the helper below; if either is missing, add it
before continuing. Also confirm `_editorial_brief_display_text(...)` only
normalizes short display text and does not apply
`EDITORIAL_BRIEF_BODY_EXCERPT_CHARS`; label truncation is not part of Stage 322.

Add immediately above `_render_editorial_brief_card()` so the helper order
matches the surrounding template style and the card renderer never references a
helper that appears later in the file:

```python
def _render_editorial_brief_trail_item(label: LocalizedText, href: str | None) -> str:
    body = (
        f'<span data-lang="en">{_esc(label.en)}</span>'
        f'<span data-lang="zh">{_esc(label.zh)}</span>'
    )
    if href is None:
        return f'        <span class="editorial-brief-trail-item">{body}</span>'
    return f'        <a class="editorial-brief-trail-item" href="{_esc(href)}">{body}</a>'
```

ROW ONE templates are string-rendered HTML, not an auto-escaped template engine.
Every trail label and href emitted by these helpers must pass through `_esc(...)`;
the unsafe-label test asserts raw `<script>` never appears in the section HTML.
Confirm `_esc(...)` quote-escapes for attribute context, equivalent to
`html.escape(..., quote=True)`, before using it for trail href attributes.
There is no Jinja/Markup/safe-filter handoff in this render path:
`render_index_html(...)` returns the assembled Python f-string HTML directly, so
manual `_esc(...)` output is the final escaping layer and is not auto-escaped a
second time.

```python
def _render_editorial_brief_trail(
    items: Sequence[_EditorialBriefTrailItem],
) -> str:
    rendered_items: list[str] = []
    seen: set[tuple[str, str, str | None]] = set()
    for item in items:
        label = LocalizedText(
            en=_editorial_brief_display_text(item.label.en),
            zh=_editorial_brief_display_text(item.label.zh),
        )
        if not (label.en or label.zh):
            continue
        href = _safe_editorial_brief_href(item.href)
        key = (label.en.casefold(), label.zh.casefold(), href)
        if key in seen:
            continue
        seen.add(key)
        rendered_items.append(_render_editorial_brief_trail_item(label, href))
        if len(rendered_items) >= EDITORIAL_BRIEF_MAX_TRAIL_ITEMS:
            break
    if not rendered_items:
        return ""
    items_html = "\n".join(rendered_items)
    return f"""
      <div class="editorial-brief-trail" aria-label="Editorial source trail / 编辑来源线索">
{items_html}
      </div>"""
```

This helper preserves input order: normalize and dedupe items in the order they
are received, then truncate after `EDITORIAL_BRIEF_MAX_TRAIL_ITEMS`. Do not sort
trail chips alphabetically or by href.
`EDITORIAL_BRIEF_MAX_TRAIL_ITEMS` is the new Stage 322 template constant with
the fixed value `3`. Trail dedupe keys are the normalized English label,
normalized Chinese label, and safe href together. Same-href/different-label
items remain distinct unless the normalized bilingual labels also match.
For this template safety-net dedupe pass, normalized labels are
`_editorial_brief_display_text(...)` output compared with `.casefold()`;
that gives whitespace-normalized, case-insensitive matching.
Items with no rendered English or Chinese label are skipped before key
construction, so empty-label chips never collapse unrelated trail items.

- [ ] **Step 4: Wire trail into card HTML without nested links**

Before editing `_render_editorial_brief_card()`, read the top of the current
function in `src/fashion_radar/row_one/templates.py` and confirm these local
variables are bound before the existing `href = _safe_editorial_brief_href(...)`
line:

```python
    title = LocalizedText(
        en=_editorial_brief_display_text(item.title.en),
        zh=_editorial_brief_display_text(item.title.zh),
    )
    body = LocalizedText(
        en=_editorial_brief_body_excerpt(item.body.en),
        zh=_editorial_brief_body_excerpt(item.body.zh),
    )
    meta_block = ""
```

If `title`, `body`, or `meta_block` are not already bound in the current
function, add those bindings exactly as shown above before applying the unified
card template. Do not reference any of those locals in the replacement template
until this preamble exists.

In `_render_editorial_brief_card()`, after `meta_block`, compute:

```python
    trail_block = _render_editorial_brief_trail(item.trail)
```

Then replace the linked-card branch so the card itself is always a non-anchor `<article>`. The primary href becomes a standalone action link after the trail, avoiding invalid nested anchors when trail chips are also links.

This is an intentional Stage 322 design change for all Editorial Brief cards,
including cards without trails. The old Stage 321 full-card click target is
replaced by the explicit `.editorial-brief-link` action so the markup remains
consistent and no card can accidentally contain nested anchors in future
render paths:

Replace the existing `href = _safe_editorial_brief_href(item.href)` assignment
and the entire conditional block below it in `_render_editorial_brief_card()`,
including both current return branches:

- the `href is None` plain `<article class="editorial-brief-card">` branch
- the href-present `<a class="editorial-brief-card" ...>` branch

with the single unified `<article>` template below. Do not keep the old
plain-article branch as an earlier return; doing so would bypass the new
`trail_block` and standalone `.editorial-brief-link` action.

```python
    action_block = ""
    href = _safe_editorial_brief_href(item.href)
    if href is not None:
        action_block = f"""
      <a class="editorial-brief-link" href="{_esc(href)}">
        <span data-lang="en">Read locally</span>
        <span data-lang="zh">本地阅读</span>
      </a>"""
    body_html = f"""      <h3>
        <span data-lang="en">{_esc(title.en)}</span>
        <span data-lang="zh">{_esc(title.zh)}</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(body.en)}</span>
        <span data-lang="zh">{_esc(body.zh)}</span>
      </p>{meta_block}{trail_block}{action_block}"""
    return f"""    <article class="editorial-brief-card">
{body_html}
    </article>"""
```

Remove the old branch that returned:

```python
return f"""    <a class="editorial-brief-card" href="{_esc(href)}">
...
    </a>"""
```

The resulting HTML must not contain an `<a>` nested inside another `<a>`.

- [ ] **Step 5: Update existing Editorial Brief card tests after card restructure**

Search for existing tests that assume the Editorial Brief card itself is an anchor:

```bash
rg -n "editorial-brief-card" tests/
```

Update any such assertions to expect `<article class="editorial-brief-card">` plus a separate `<a class="editorial-brief-link" href="...">`.
For example, an old assertion against
`<a class="editorial-brief-card" href="details/the-row-signal-1234567890.html">`
should become assertions for both `<article class="editorial-brief-card">` and
`<a class="editorial-brief-link" href="details/the-row-signal-1234567890.html">`
so the test still proves the specific detail href is present.

Run the existing Editorial Brief tests after the migration:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k editorial_brief -q
```

If the `rg` search finds `editorial-brief-card` assertions outside
`tests/test_row_one_render.py`, update those assertions in the same Task 2
migration before continuing to Task 3. Do not defer `test_workflows.py`,
`test_row_one_docs.py`, or any other affected file to a later task if the search
shows it still expects `<a class="editorial-brief-card">`. Also run the affected
test files before continuing, rather than relying only on the focused
`test_row_one_render.py -k editorial_brief` subset.

Expected: tests unrelated to the not-yet-implemented source trail keep passing;
source-trail tests from Task 1 remain red until Task 3 is implemented.

- [ ] **Step 6: Add CSS**

Before editing CSS, run:

```bash
rg -n "\\.editorial-brief-link" src/fashion_radar/row_one/templates.py
```

Confirm whether a Stage 321 `.editorial-brief-link` rule already exists. If it
exists, replace the full existing block with the merged block below rather than
appending a duplicate selector. If it does not exist, add the block below near
the existing Editorial Brief styles. Add the new trail selectors near the
existing Editorial Brief styles:

The current Stage 321 block to replace is:

```css
.editorial-brief-link {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
}
```

Replace it with this merged Stage 322 block plus the new trail selectors:

```css
.editorial-brief-trail {
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-top: 12px;
}
.editorial-brief-trail-item,
.editorial-brief-trail a {
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 4px;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief-trail a:hover,
.editorial-brief-trail a:focus-visible,
.editorial-brief-link:hover,
.editorial-brief-link:focus-visible {
  opacity: 0.75;
}
.editorial-brief-link {
  align-items: center;
  color: var(--accent);
  display: inline-flex;
  font-size: 0.74rem;
  font-weight: 800;
  gap: 6px;
  letter-spacing: 0.12em;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief-link::after {
  content: "↗";
}
```

- [ ] **Step 7: Run direct template tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_filters_editorial_brief_source_trail_links \
  tests/test_row_one_render.py::test_render_index_html_caps_and_dedupes_editorial_brief_source_trail \
  tests/test_row_one_render.py::test_row_one_css_includes_editorial_brief_source_trail_styles -q
```

Expected: pass.

## Task 3: Implement Render Builder Trail Payload

- [ ] **Step 1: Import trail dataclass**

In `src/fashion_radar/row_one/render.py`, extend the templates import:

```python
from fashion_radar.row_one.templates import (
    EDITORIAL_BRIEF_MAX_ITEMS,
    _EditorialBrief,
    _EditorialBriefItem,
    _EditorialBriefTrailItem,
    _validated_detail_relative_path,
    render_detail_html,
    render_index_html,
    row_one_css,
    row_one_js,
)
```

Also confirm the existing imports already include `Sequence` from
`collections.abc` and `clean_row_one_text` from
`fashion_radar.row_one.text`. Stage 321 already added both; add them if either
is missing. This project targets Python versions with standard-library
`typing.Literal`; add a normal top-level `from typing import Literal` import
only if `Literal` is not already imported. Do not use a runtime conditional
import or `try/except ImportError`.
`RowOneLocalArticleContentSection` is required for the new helper annotation and
is currently absent from the models import block; add it before defining
`_first_local_article_content_section(...)`:

```python
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceSection,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentSection,
    RowOneSection,
    RowOneStory,
    RowOneStoryDisplay,
    RowOneStoryImage,
)
```

- [ ] **Step 2: Verify detail content-section anchor alignment**

Before wiring source-trail content-section links, read the detail renderer in
`src/fashion_radar/row_one/templates.py` and verify `_render_local_article_content_sections(...)`
emits section IDs using the same one-based positional scheme as
`_editorial_brief_content_section_href(...)`.

The current Stage 319 detail implementation uses:

```python
for position, section in enumerate(article.content_sections, start=1):
    anchor = _local_article_content_section_anchor(position)
```

and:

```python
def _local_article_content_section_anchor(position: int) -> str:
    return f"local-article-content-section-{position}"
```

If that renderer ever changes to filter, reorder, skip, or key-name anchors
before assigning IDs, `_editorial_brief_content_section_href(...)` must mirror
the renderer exactly before Task 3 continues.

Paragraph trail anchors must continue to come from the existing
`_editorial_brief_paragraph_href(...)` helper. Do not hand-code a separate
paragraph anchor format in `_editorial_brief_source_trail(...)`; the fallback
tests assert `#local-article-paragraph-1` because that is the current helper
output for the first non-empty saved paragraph.

- [ ] **Step 3: Preserve trail through existing item dedupe**

Update `_deduped_editorial_brief_items(...)` so the existing item-level dedupe
preserves trail data before any new source-trail builder call sites are wired.
Otherwise `_EditorialBriefItem.trail` will be built and then silently reset to
the dataclass default `()` during body deduplication.

```python
def _deduped_editorial_brief_items(
    items: Sequence[_EditorialBriefItem],
) -> list[_EditorialBriefItem]:
    deduped: list[_EditorialBriefItem] = []
    seen_bodies: set[tuple[str, str]] = set()
    for item in items:
        body = LocalizedText(
            en=clean_row_one_text(item.body.en),
            zh=clean_row_one_text(item.body.zh),
        )
        if not _story_localized_text_has_content(body):
            continue
        body_key = (body.en, body.zh)
        if body_key in seen_bodies:
            continue
        seen_bodies.add(body_key)
        deduped.append(
            _EditorialBriefItem(
                title=item.title,
                body=body,
                meta=item.meta,
                href=item.href,
                trail=item.trail,
            )
        )
    return deduped
```

After applying the patch, re-run this focused preservation test before
proceeding to helper wiring:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_editorial_brief_item_dedupe_preserves_trail -q
```

Expected: pass. If it is still red, the `trail=item.trail` pass-through was not
applied correctly, and Task 3 must not proceed to source-trail builder helpers.

- [ ] **Step 4: Add trail helper functions**

Before writing the helpers below, verify the Stage 321 helper functions this
task reuses are present with the expected signatures:

```bash
rg -n "def (_local_article_brief_section|_editorial_brief_detail_href|_editorial_brief_paragraph_href)\\(" \
  src/fashion_radar/row_one/render.py
```

Expected: all three definitions are present in `render.py`. If any helper is
missing or has an incompatible signature, stop and update this plan before
continuing.

Add near the existing Editorial Brief helpers:

```python
def _editorial_brief_source_trail(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
    *,
    brief_key: str | None = None,
    brief_href_target: Literal["paragraph_or_detail", "detail"] = "paragraph_or_detail",
    content_keys: tuple[str, ...] = (),
    include_first_paragraph: bool = False,
) -> tuple[_EditorialBriefTrailItem, ...]:
    """Build stable pre-deduped trail payloads; template dedupe is a safety net."""
    if local_article is None:
        return ()
    items: list[_EditorialBriefTrailItem] = []
    if brief_key is not None:
        section = _local_article_brief_section(local_article, brief_key)
        if section is not None:
            brief_href = _editorial_brief_detail_href(story)
            if brief_href_target == "paragraph_or_detail":
                brief_href = (
                    _editorial_brief_paragraph_href(story, local_article)
                    or brief_href
                )
            elif brief_href_target == "detail":
                pass
            items.append(
                _EditorialBriefTrailItem(
                    label=section.title,
                    href=brief_href,
                )
            )
    content_section = _first_local_article_content_section(local_article, content_keys)
    if content_section is not None:
        position, section = content_section
        content_href = _editorial_brief_content_section_href(story, position)
        if content_href is not None:
            items.append(_EditorialBriefTrailItem(label=section.title, href=content_href))
    if include_first_paragraph:
        paragraph_href = _editorial_brief_paragraph_href(story, local_article)
        existing_hrefs = {item.href for item in items if item.href is not None}
        if paragraph_href is not None and paragraph_href not in existing_hrefs:
            items.append(
                _EditorialBriefTrailItem(
                    label=LocalizedText(en="Saved paragraph 1", zh="保存段落 1"),
                    href=paragraph_href,
                )
            )
    return _deduped_editorial_brief_trail(items)
```

This helper intentionally reuses the Stage 321 `_local_article_brief_section(...)`, `_editorial_brief_detail_href(...)`, and `_editorial_brief_paragraph_href(...)` helpers already present in `render.py`.

Do not add a source/title trail chip. Stage 321 already renders source/title context in `_editorial_brief_meta(...)`; duplicating it in the trail makes the card noisy. The trail should add provenance links such as brief-section labels, content-section labels, and paragraph anchors.

Content-section trail chips are link-only by design: if a detail href cannot be
validated, skip the content-section chip instead of rendering a plain unlinked
content-section label.

```python
def _first_local_article_content_section(
    local_article: RowOneLocalArticle | None,
    keys: tuple[str, ...],
) -> tuple[int, RowOneLocalArticleContentSection] | None:
    if local_article is None:
        return None
    for key in keys:
        for position, section in enumerate(local_article.content_sections, start=1):
            if section.key == key:
                return (position, section)
    return None
```

```python
def _editorial_brief_content_section_href(
    story: RowOneStory,
    position: int,
) -> str | None:
    detail_href = _editorial_brief_detail_href(story)
    if detail_href is None or position < 1:
        return None
    return f"{detail_href}#local-article-content-section-{position}"
```

```python
def _deduped_editorial_brief_trail(
    items: Sequence[_EditorialBriefTrailItem],
) -> tuple[_EditorialBriefTrailItem, ...]:
    # Builder-side cleanup keeps generated trail payloads stable; templates
    # validate hrefs and run a second dedupe pass against the safe href value.
    # Builder hrefs come from internal helpers, so raw href keys are expected.
    # clean_row_one_text and _editorial_brief_display_text are equivalent for
    # short section-title labels; both strip and normalize whitespace.
    deduped: list[_EditorialBriefTrailItem] = []
    seen: set[tuple[str, str, str | None]] = set()
    for item in items:
        label = LocalizedText(
            en=clean_row_one_text(item.label.en),
            zh=clean_row_one_text(item.label.zh),
        )
        if not (label.en or label.zh):
            continue
        key = (label.en.casefold(), label.zh.casefold(), item.href)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(_EditorialBriefTrailItem(label=label, href=item.href))
    return tuple(deduped)
```

- [ ] **Step 5: Attach trails to cards**

Update `_editorial_brief_items()`:

```python
        _EditorialBriefItem(
            title=LocalizedText(en="What changed today", zh="今日变化"),
            body=_combined_editorial_body(
                story.editorial_takeaway
                if _story_localized_text_has_content(story.editorial_takeaway)
                else story.summary,
                what_happened.body if what_happened is not None else None,
            ),
            meta=_editorial_brief_meta(local_article),
            href=detail_href,
            trail=_editorial_brief_source_trail(
                story,
                local_article,
                brief_key="what_happened",
                brief_href_target="paragraph_or_detail",
                content_keys=(),
                include_first_paragraph=False,
            ),
        ),
```

```python
        _EditorialBriefItem(
            title=LocalizedText(en="Why it matters", zh="为什么重要"),
            body=_combined_editorial_body(
                story.why_it_matters
                if _story_localized_text_has_content(story.why_it_matters)
                else story.signal_context,
                why_it_matters.body if why_it_matters is not None else None,
            ),
            href=detail_href,
            trail=_editorial_brief_source_trail(
                story,
                local_article,
                brief_key="why_it_matters",
                brief_href_target="detail",
                content_keys=("entities", "brand_signals", "takeaways"),
                include_first_paragraph=False,
            ),
        ),
```

```python
        _EditorialBriefItem(
            title=LocalizedText(en="What to read locally", zh="本地阅读路径"),
            body=_combined_editorial_body(
                watch_next.body if watch_next is not None else story.reader_path,
                None,
            ),
            href=_editorial_brief_paragraph_href(story, local_article) or detail_href,
            trail=_editorial_brief_source_trail(
                story,
                local_article,
                brief_key="watch_next",
                brief_href_target="paragraph_or_detail",
                content_keys=("takeaways",),
                include_first_paragraph=watch_next is None,
            ),
        ),
```

For `What to read locally`, include a bare `Saved paragraph 1 / 保存段落 1`
trail chip only when `watch_next` is missing. When `watch_next` exists, its
brief-section trail item already links to the first paragraph when available,
so the extra paragraph chip stays omitted to avoid duplicate trail chips.
When `watch_next` is missing and the card primary href also points to the first
paragraph, the `Saved paragraph 1 / 保存段落 1` trail chip intentionally shares
that destination with the standalone `Read locally / 本地阅读` action: the action
is navigation, while the chip labels the local evidence trail.

- [ ] **Step 6: Run builder render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_editorial_brief_source_trail \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_content_section_trail_resolves_to_detail_anchor \
  tests/test_row_one_render.py::test_render_row_one_site_omits_editorial_brief_source_trail_without_local_article \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_source_trail_uses_saved_paragraph_without_watch_next \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_source_trail_omits_saved_paragraph_without_text \
  tests/test_row_one_render.py::test_editorial_brief_item_dedupe_preserves_trail -q
```

Expected: pass.

## Task 4: Workflow And Docs Boundary

- [ ] **Step 1: Add workflow boundary assertions**

In `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`, add after the Stage 321 Editorial Brief assertions:

Before adding the trail assertion, confirm the test fixture's local article
includes enough data to generate a trail: at minimum one non-empty paragraph and
one local article `brief_sections` entry whose key is used by
`_editorial_brief_source_trail(...)`, such as `what_happened`,
`why_it_matters`, or `watch_next`. If the fixture is too minimal, enrich only
that fixture with a `what_happened` or `why_it_matters` brief section and at
least one non-empty paragraph; do not change the workflow contract or any
generated JSON schema.

Use an explicit preflight in the workflow test before asserting trail HTML:

```python
assert local_article.paragraphs
assert any(paragraph.strip() for paragraph in local_article.paragraphs)
assert any(
    section.key in {"what_happened", "why_it_matters", "watch_next"}
    and (section.body.en.strip() or section.body.zh.strip())
    for section in local_article.brief_sections
)
```

```python
    assert "Local article paragraph for the ROW ONE detail page." in index_html
    assert 'class="editorial-brief-trail"' in index_html
```

If the local paragraph assertion already exists in the test, leave the existing
assertion in place and add only the `editorial-brief-trail` assertion.

Then add these generated-contract absence assertions after `generated_contract_payload` is constructed:

```python
    assert "Editorial Source Trail" not in generated_contract_payload
    assert '"editorial_source_trail"' not in generated_contract_payload
    assert '"source_trail"' not in generated_contract_payload
```

Do not add duplicate assertions for existing Stage 321 keys.

- [ ] **Step 2: Add docs text**

In both `README.md` and `docs/row-one.md`, add immediately before the Stage 321 paragraph so the newest generated-site stage remains isolated by the next Stage 321 heading in docs tests:

```markdown
Stage 322 adds Editorial Source Trail to the existing homepage Editorial Brief
cards. It is generated-site only and turns existing saved local article source
names, existing saved article titles, existing brief sections, existing content
sections, existing `data/articles/<story-id>.json` sidecars, and existing
paragraph/content-section anchors into compact bilingual provenance chips with
safe internal links. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not add `editorial_source_trail`, does not add
`source_trail`, does not change `row-one-manifest/v1`, does not change
`row-one-runtime/v1`, does not change schemas, does not write a new json
artifact, does not add source collection, does not fetch article pages, does not
add scoring, does not add llm calls, does not add connectors, and is not a
compliance review feature.
```

- [ ] **Step 3: Add docs boundary test**

In `tests/test_row_one_docs.py`, add after the Stage 321 docs test:

Before writing the test, confirm the existing `_normalized(...)` helper only
collapses whitespace and case-folds text, preserving punctuation and markdown
backticks. The current helper is:

```python
def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()
```

```python
def test_row_one_docs_describe_editorial_source_trail_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_322 = readme[
        readme.index("Stage 322 adds Editorial Source Trail") : readme.index("Stage 321 adds")
    ]
    docs_stage_322 = docs[
        docs.index("Stage 322 adds Editorial Source Trail") : docs.index("Stage 321 adds")
    ]
    readme_stage_322_normalized = _normalized(readme_stage_322)
    docs_stage_322_normalized = _normalized(docs_stage_322)

    expected_phrases = [
        "editorial source trail",
        "existing homepage editorial brief cards",
        "generated-site only",
        "existing saved local article source names",
        "existing saved article titles",
        "existing brief sections",
        "existing content sections",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing paragraph/content-section anchors",
        "compact bilingual provenance chips",
        "safe internal links",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not add `editorial_source_trail`",
        "does not add `source_trail`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_322_normalized
        assert phrase in docs_stage_322_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_322_normalized
        assert phrase not in docs_stage_322_normalized
```

- [ ] **Step 4: Run focused workflow/docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_editorial_source_trail_boundary -q
```

Expected: pass.

## Task 5: Focused Verification, Plan Review Artifacts, And Code Review

- [ ] **Step 1: Run combined focused Stage 322 suite**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_editorial_brief_source_trail \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_content_section_trail_resolves_to_detail_anchor \
  tests/test_row_one_render.py::test_render_row_one_site_omits_editorial_brief_source_trail_without_local_article \
  tests/test_row_one_render.py::test_render_index_html_filters_editorial_brief_source_trail_links \
  tests/test_row_one_render.py::test_render_index_html_caps_and_dedupes_editorial_brief_source_trail \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_source_trail_uses_saved_paragraph_without_watch_next \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_source_trail_omits_saved_paragraph_without_text \
  tests/test_row_one_render.py::test_editorial_brief_item_dedupe_preserves_trail \
  tests/test_row_one_render.py::test_row_one_css_includes_editorial_brief_source_trail_styles \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_editorial_source_trail_boundary -q
```

Expected: pass.

- [ ] **Step 2: Run formatting and lint**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --fix \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
git diff --check
```

Expected: all commands pass.

- [ ] **Step 3: Create code review prompt**

Create `docs/reviews/claude-code-stage-322-code-review-prompt.md` with:

```markdown
You are reviewing Stage 322 of Fashion Radar / ROW ONE.

Objective:
- Add a generated-site-only Editorial Source Trail inside existing ROW ONE homepage Editorial Brief cards.
- The trail uses existing saved local article source names, titles, brief sections, content sections, paragraph anchors, and safe detail routes.
- This must not add JSON contract fields, schema changes, source collection, fetching, scoring, LLM calls, connectors, image generation, deployment behavior, or compliance-review product features.

Review the current working tree diff against HEAD. Focus on:
1. Generated-site-only boundary: no new app/runtime/manifest JSON fields or schemas.
2. Correctness of trail labels, caps, dedupe, omission, and bilingual rendering.
3. Link safety: all hrefs must go through existing safe detail/paragraph/content-section allowlists.
4. XSS safety: all displayed text must be escaped.
5. Test coverage: render, omission, unsafe links, cap/dedupe, workflow boundary, docs, CSS.
6. Scope creep or duplicated homepage content.

Commands already run:
- Stage 322 focused pytest suite.
- Ruff check/format.
- Full Ruff check and `git diff --check`.

Return findings grouped by Critical, Important, Minor. If no Critical/Important issues remain, say so explicitly.
```

- [ ] **Step 4: Run Claude Code code review**

Run:

```bash
claude --bare --effort max --permission-mode plan --no-session-persistence --print \
  "$(cat docs/reviews/claude-code-stage-322-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-322-code-review.md
```

Expected: review file is written.

- [ ] **Step 5: Fix Critical and Important findings**

If Claude Code reports Critical or Important findings, apply targeted fixes, rerun the focused suite and lint commands, and append a rereview prompt only if the fix changes behavior materially.

Expected: no unresolved Critical or Important findings.

## Task 6: Final Verification And Commit

- [ ] **Step 1: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git status --short --branch
```

The full pytest run must include
`tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_content_section_trail_resolves_to_detail_anchor`
as part of the complete suite; do not treat earlier focused runs as a
substitute for this final verification.

Expected:
- full pytest passes
- lock check passes
- release hygiene passes
- only intended Stage 322 files are modified/untracked

- [ ] **Step 2: Commit**

Run:

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-322-plan-review-prompt.md \
  docs/reviews/claude-code-stage-322-plan-review.md \
  docs/reviews/claude-code-stage-322-code-review-prompt.md \
  docs/reviews/claude-code-stage-322-code-review.md \
  docs/superpowers/plans/2026-07-07-stage-322-row-one-editorial-source-trail-plan.md \
  docs/superpowers/specs/2026-07-07-stage-322-row-one-editorial-source-trail-design.md \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py
git commit -m "Stage 322: add row one editorial source trail"
```

Expected: commit succeeds.

- [ ] **Step 3: Push**

Run:

```bash
git push origin main
git status --short --branch
```

Expected: push succeeds and worktree is clean.

## Self-Review

- Spec coverage: the plan covers render payload, template rendering, CSS, workflow JSON absence, docs, review, full verification, commit, and push.
- Placeholder scan: no unfinished markers, open-ended implementation placeholders, or ellipsis placeholders remain.
- Scope check: the node is one generated-site-only feature inside existing Editorial Brief cards.
- Boundary check: the plan explicitly avoids JSON contract, schema, collector, source, scoring, LLM, connector, deployment, image generation, and compliance changes.
- Type consistency: `_EditorialBriefTrailItem`, `_EditorialBriefItem.trail`, and helper return types are consistent across render, template, and tests.
