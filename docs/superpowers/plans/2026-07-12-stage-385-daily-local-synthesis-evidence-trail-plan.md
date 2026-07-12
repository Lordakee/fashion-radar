# Stage 385 Daily Local Synthesis Evidence Trail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only evidence trail inside the existing homepage Daily Local Synthesis Brief so each synthesis card can point readers to concrete saved-article anchors without creating new app contracts, JSON artifacts, or routes.

**Architecture:** Extend the internal `RowOneDailyLocalSynthesisBriefCard` model with capped evidence links derived from the already-built Stage 382 `RowOneLocalArticleSynthesisBrief.anchors`. Keep the evidence trail inside existing `index.html` Daily Local Synthesis Brief cards, using safe same-site `articles/<story-id>.html#local-article-*` links and existing generated local article routes. Do not change source collection, scraping, schemas, app/runtime/manifest payloads, route families, scheduling, analytics, recommendation, personalization, or compliance-review behavior.

**Tech Stack:** Python dataclasses/builders, server-rendered ROW ONE HTML in `templates.py`, pytest, existing ROW ONE render/workflow/docs tests, ruff, uv frozen verification commands.

---

## Product Gap

Stage 383 added a homepage Daily Local Synthesis Brief that explains what the saved local articles add up to. Stage 384 hardened that presentation. The remaining trust gap is that each homepage synthesis card says it is article-backed, but the homepage does not show the concrete saved-body anchors behind the card.

Stage 385 should make the homepage synthesis more useful as an information-organizing tool by adding a compact evidence trail inside each card. Readers should be able to jump from daily synthesis to the saved article section or paragraph that supports it, without exposing full article bodies on the homepage or creating a new data surface.

## Scope Decision

- Add evidence-trail links only inside existing `.daily-local-synthesis-brief-card` elements on `index.html`.
- Reuse Stage 382 `build_row_one_local_article_synthesis_brief(...)` anchors already derived from saved local article content sections and paragraphs.
- Keep builder card `href` as the existing bare article page filename, and store evidence hrefs as bare filename plus safe fragment in the builder; the renderer will convert them to `articles/<story-id>.html#fragment`.
- Do not add standalone `daily-local-synthesis-evidence-trail.html`, `data/daily-local-synthesis-evidence-trail.json`, route families, app fields, schema fields, runtime/manifest fields, article sidecars, source adapters, scraping/fetching/matching/extraction/scoring/ranking behavior, LLM calls, connectors, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review features.
- Do not use or denylist the generic phrase `Evidence Trail` globally because older ROW ONE surfaces already use it legitimately.

## File Map

- Modify `src/fashion_radar/row_one/daily_local_synthesis_brief.py`
  - Add `DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_EVIDENCE_LINKS = 2`.
  - Add `RowOneDailyLocalSynthesisEvidenceLink`.
  - Add `evidence_links` to `RowOneDailyLocalSynthesisBriefCard`.
  - Convert Stage 382 same-page anchor fragments into safe homepage evidence links for each daily synthesis card.
  - Deduplicate evidence links by normalized label first, so repeated section labels do not crowd out the paragraph anchor.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import `RowOneDailyLocalSynthesisEvidenceLink`.
  - Render a compact `.daily-local-synthesis-brief-evidence-trail` block inside each card before the saved-article route when links are present.
  - Add `_render_daily_local_synthesis_evidence_link(...)` and `_safe_daily_local_synthesis_evidence_href(...)`.
  - Add CSS for evidence trail container and links.
- Modify `tests/test_row_one_daily_local_synthesis_brief.py`
  - Add builder tests for evidence link creation, cap/dedupe, and sparse-anchor omission.
- Modify `tests/test_row_one_render.py`
  - Add render tests for evidence link escaping/safe href handling and empty evidence omission.
  - Extend homepage-only site test to assert evidence trail appears only on `index.html` and no Stage 385 artifacts exist.
  - Add CSS assertions for evidence trail selectors.
- Modify `tests/test_workflows.py`
  - Add Stage 385 homepage-only sentinel for `_render_daily_local_synthesis_evidence_link` or equivalent helper with `raising=True`.
  - Add Stage 385 contract/artifact denylist tokens without denying generic `Evidence Trail`.
- Modify `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`
  - Add Stage 385 generated-site-only boundary paragraph above Stage 384.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-385-plan-review.md`
  - `opencode-stage-385-plan-review.md`
  - code review artifacts after implementation.

## Requirements

1. Builder evidence links:
   - Each `RowOneDailyLocalSynthesisBriefCard` may contain up to `DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_EVIDENCE_LINKS` evidence links.
   - Evidence links must come from the corresponding Stage 382 local article synthesis anchors.
   - Each evidence link must preserve anchor label fallback and support copy where available.
   - Evidence hrefs must be same-site saved-article routes only, shaped as `<story-id>.html#local-article-content-section-N` or `<story-id>.html#local-article-paragraph-N`.
   - Invalid article hrefs, invalid fragments, empty labels, and duplicate labels must be omitted.
   - A card can still render without evidence links; lack of anchors must not drop otherwise valid cards.

2. Homepage rendering:
   - Render evidence links inside `.daily-local-synthesis-brief-card`, after read/adds copy and before `.daily-local-synthesis-brief-route`.
   - Render final hrefs as `articles/<story-id>.html#local-article-content-section-N` or `articles/<story-id>.html#local-article-paragraph-N`.
   - Escape labels and support copy.
   - Omit the evidence-trail block when a card has no renderable evidence links.
   - Keep the existing Daily Local Synthesis Brief placement between Daily Local Article Intelligence Brief and Daily Local Saved Article Organizer.

3. CSS:
   - Add explicit selectors for `.daily-local-synthesis-brief-evidence-trail`, `.daily-local-synthesis-brief-evidence-link`, and `.daily-local-synthesis-brief-evidence-support`.
   - Use existing dark editorial style.
   - Add `overflow-wrap: anywhere;` and `min-width: 0;` where needed for long labels/support text.

4. Generated-site-only boundary:
   - Stage 385 evidence trail must appear only in generated `index.html`.
   - It must not appear in `articles/index.html`, `articles/<story-id>.html`, detail pages, or generated contract payloads (`data/edition.json`, `data/manifest.json`, `data/runtime.json`).
   - Do not create root, `articles/`, or `data/` `.html`/`.json` artifacts for Stage 385 stems.

5. Docs:
   - README and `docs/row-one.md` must state Stage 385 is generated-site-only homepage evidence-trail presentation inside the existing Daily Local Synthesis Brief.
   - Docs must say it reuses existing current-edition stories, saved local article sidecars, generated local article page routes, and Stage 382 synthesis anchors.
   - Docs must say it does not create new JSON artifacts, route families, app/runtime/manifest/schema contracts, article-source sidecars, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connectors, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.

## Tasks

### Task 1: RED builder tests for evidence links

**Files:**
- Modify: `tests/test_row_one_daily_local_synthesis_brief.py`

- [ ] Extend the local `_article(...)` fixture signature so the new RED tests can construct sparse and repeated-anchor articles without a `TypeError`:

```python
def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Runway",
    thesis: str | None = None,
    thesis_zh: str | None = None,
    adds: str | None = None,
    adds_zh: str | None = None,
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    ...
```

Inside the fixture, use the provided `paragraphs`, `paragraphs_zh`, and `content_sections` values when they are not `None`; otherwise keep the current default values.

- [ ] Add `test_build_daily_local_synthesis_brief_adds_evidence_trail_from_article_synthesis_anchors`.

Test shape:

```python
def test_build_daily_local_synthesis_brief_adds_evidence_trail_from_article_synthesis_anchors() -> None:
    first_id = "runway-reset-1111111111"
    second_id = "retail-shift-2222222222"
    stories = [_story(first_id, headline="Runway Reset"), _story(second_id, headline="Retail Shift")]
    local_articles = {
        first_id: _article(
            first_id,
            title="Runway Reset Article",
            adds="Runway Reset article adds merchandising evidence.",
        ),
        second_id: _article(
            second_id,
            title="Retail Shift Article",
            adds="Retail Shift article adds channel evidence.",
        ),
    }

    brief = build_row_one_daily_local_synthesis_brief(
        _edition(stories),
        local_articles,
        _hrefs(first_id, second_id),
    )

    assert brief is not None
    first_links = brief.cards[0].evidence_links
    assert [link.href for link in first_links] == [
        "runway-reset-1111111111.html#local-article-content-section-1",
        "runway-reset-1111111111.html#local-article-paragraph-1",
    ]
    assert first_links[0].label.en == "Article Adds"
    assert "Runway Reset article adds merchandising evidence." in first_links[0].support.en
    assert first_links[1].label.en == "Paragraph 1"
```

- [ ] Add `test_build_daily_local_synthesis_brief_caps_and_dedupes_evidence_links`.

Test shape:

```python
def test_build_daily_local_synthesis_brief_caps_and_dedupes_evidence_links() -> None:
    first_id = "runway-reset-1111111111"
    second_id = "retail-shift-2222222222"
    article = _article(
        first_id,
        title="Runway Reset Article",
        content_sections=[
            _section("Repeated", "Repeated support text.", key="brand_signals"),
            _section("Repeated", "Repeated support text.", key="product_signals"),
            _section("Third", "Third support text.", key="market_signals"),
        ],
    )

    brief = build_row_one_daily_local_synthesis_brief(
        _edition([_story(first_id), _story(second_id)]),
        {first_id: article, second_id: _article(second_id)},
        _hrefs(first_id, second_id),
    )

    assert brief is not None
    assert len(brief.cards[0].evidence_links) == 2
    assert [link.label.en for link in brief.cards[0].evidence_links] == ["Repeated", "Paragraph 1"]
```

- [ ] Add `test_build_daily_local_synthesis_brief_omits_empty_evidence_trails_without_dropping_cards`.

Test shape:

```python
def test_build_daily_local_synthesis_brief_omits_empty_evidence_trails_without_dropping_cards() -> None:
    first_id = "runway-reset-1111111111"
    second_id = "retail-shift-2222222222"
    first_article = _article(first_id, content_sections=[], paragraphs=[], paragraphs_zh=[])
    second_article = _article(second_id, content_sections=[], paragraphs=[], paragraphs_zh=[])

    brief = build_row_one_daily_local_synthesis_brief(
        _edition([_story(first_id), _story(second_id)]),
        {first_id: first_article, second_id: second_article},
        _hrefs(first_id, second_id),
    )

    assert brief is not None
    assert brief.card_count == 2
    assert all(card.evidence_links == () for card in brief.cards)
```

- [ ] Run RED command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_synthesis_brief.py::test_build_daily_local_synthesis_brief_adds_evidence_trail_from_article_synthesis_anchors \
  tests/test_row_one_daily_local_synthesis_brief.py::test_build_daily_local_synthesis_brief_caps_and_dedupes_evidence_links \
  tests/test_row_one_daily_local_synthesis_brief.py::test_build_daily_local_synthesis_brief_omits_empty_evidence_trails_without_dropping_cards \
  -q
```

Expected: FAIL because `evidence_links` does not exist yet.

### Task 2: Implement builder evidence links

**Files:**
- Modify: `src/fashion_radar/row_one/daily_local_synthesis_brief.py`

- [ ] Import `RowOneLocalArticleSynthesisAnchor` if direct typing is useful.
- [ ] Add constants and dataclass:

```python
DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_EVIDENCE_LINKS = 2


@dataclass(frozen=True)
class RowOneDailyLocalSynthesisEvidenceLink:
    label: LocalizedText
    href: str
    support: LocalizedText | None = None
```

- [ ] Add `evidence_links: tuple[RowOneDailyLocalSynthesisEvidenceLink, ...] = ()` to `RowOneDailyLocalSynthesisBriefCard`. Use a default to minimize fixture churn.
- [ ] When building each card, set:

```python
evidence_links=_evidence_links(
    page_href=page_href,
    anchors=synthesis.anchors,
),
```

- [ ] Add helper:

```python
def _evidence_links(
    *,
    page_href: str,
    anchors: tuple[RowOneLocalArticleSynthesisAnchor, ...],
) -> tuple[RowOneDailyLocalSynthesisEvidenceLink, ...]:
    links: list[RowOneDailyLocalSynthesisEvidenceLink] = []
    seen_labels: set[str] = set()
    for anchor in anchors:
        href = _safe_evidence_href(page_href, anchor.href)
        label = _clean_localized(anchor.label, DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_ADDS_CHARS)
        label_key = _localized_key(label)
        if href is None or not label_key:
            continue
        if label_key in seen_labels:
            continue
        support = (
            _clean_localized(anchor.support, DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_ADDS_CHARS)
            if anchor.support is not None
            else None
        )
        links.append(
            RowOneDailyLocalSynthesisEvidenceLink(
                label=label,
                href=href,
                support=support,
            )
        )
        seen_labels.add(label_key)
        if len(links) >= DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_EVIDENCE_LINKS:
            break
    return tuple(links)
```

- [ ] Add helper:

```python
def _safe_evidence_href(page_href: str, fragment_href: object) -> str | None:
    if not isinstance(fragment_href, str):
        return None
    if fragment_href != fragment_href.strip() or not fragment_href.startswith("#"):
        return None
    fragment = fragment_href[1:]
    if not fragment or any(character.isspace() for character in fragment):
        return None
    if fragment.startswith("local-article-content-section-"):
        suffix = fragment.removeprefix("local-article-content-section-")
    elif fragment.startswith("local-article-paragraph-"):
        suffix = fragment.removeprefix("local-article-paragraph-")
    else:
        return None
    if not suffix.isdigit() or suffix != str(int(suffix)) or int(suffix) < 1:
        return None
    if _safe_article_page_href(page_href.removesuffix(".html"), page_href) is None:
        return None
    return f"{page_href}#{fragment}"
```

- [ ] Add unsafe fragment coverage:

```python
def test_build_daily_local_synthesis_brief_filters_unsafe_evidence_hrefs() -> None:
    safe_page = "runway-reset-1111111111.html"
    unsafe_fragments = (
        "#local-article-paragraph-0",
        "#local-article-paragraph-01",
        "#local-article-content-section-0",
        "#local-article-content-section-01",
        "#local-article-unknown-1",
        "#local-article-paragraph-1 ",
        "local-article-paragraph-1",
    )

    assert _safe_evidence_href(safe_page, "#local-article-paragraph-1") == (
        "runway-reset-1111111111.html#local-article-paragraph-1"
    )
    assert _safe_evidence_href(safe_page, "#local-article-content-section-1") == (
        "runway-reset-1111111111.html#local-article-content-section-1"
    )
    for fragment in unsafe_fragments:
        assert _safe_evidence_href(safe_page, fragment) is None
```

- [ ] Run builder tests from Task 1 again.

Expected: PASS.

### Task 3: RED render tests for evidence trail

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Import `RowOneDailyLocalSynthesisEvidenceLink`.
- [ ] Do not change `_daily_local_synthesis_brief_fixture(...)` defaults. Add evidence links only in the new evidence-specific tests with local `replace(...)` calls, so existing render tests do not pick up unrelated evidence markup.
- [ ] Add `test_render_daily_local_synthesis_brief_evidence_trail_links_to_saved_articles`.

Test shape:

```python
def test_render_daily_local_synthesis_brief_evidence_trail_links_to_saved_articles() -> None:
    long_support = "Evidence <support> " + ("verylongtoken" * 12)
    card = replace(
        _daily_local_synthesis_brief_fixture().cards[0],
        evidence_links=(
            RowOneDailyLocalSynthesisEvidenceLink(
                label=LocalizedText(en="Brand <Signals>", zh="品牌 <信号>"),
                href="the-row-signal-1234567890.html#local-article-content-section-1",
                support=LocalizedText(en=long_support, zh="支持 <文本>"),
            ),
            RowOneDailyLocalSynthesisEvidenceLink(
                label=LocalizedText(en="Paragraph 1", zh="第 1 段"),
                href="the-row-signal-1234567890.html#local-article-paragraph-1",
            ),
        ),
    )
    brief = replace(_daily_local_synthesis_brief_fixture(), cards=(card,))

    html = render_index_html(_edition(), daily_local_synthesis_brief=brief)
    section_html = _daily_local_synthesis_brief_section_html(html)

    assert 'class="daily-local-synthesis-brief-evidence-trail"' in section_html
    assert "Evidence Trail" in section_html
    assert "证据线索" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-content-section-1"' in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert "Brand &lt;Signals&gt;" in section_html
    assert "Evidence &lt;support&gt;" in section_html
    assert "支持 &lt;文本&gt;" in section_html
    assert section_html.index('class="daily-local-synthesis-brief-evidence-trail"') < section_html.index(
        'class="daily-local-synthesis-brief-route"'
    )
```

- [ ] Add `test_render_daily_local_synthesis_brief_omits_empty_or_unsafe_evidence_trail`.

Test shape:

```python
def test_render_daily_local_synthesis_brief_omits_empty_or_unsafe_evidence_trail() -> None:
    unsafe_links = (
        RowOneDailyLocalSynthesisEvidenceLink(label=LocalizedText(en="External", zh="外链"), href="https://example.com"),
        RowOneDailyLocalSynthesisEvidenceLink(label=LocalizedText(en="Prefixed", zh="前缀"), href="articles/the-row-signal-1234567890.html#local-article-paragraph-1"),
        RowOneDailyLocalSynthesisEvidenceLink(label=LocalizedText(en="Query", zh="查询"), href="the-row-signal-1234567890.html?x=1#local-article-paragraph-1"),
        RowOneDailyLocalSynthesisEvidenceLink(label=LocalizedText(en="", zh=""), href="the-row-signal-1234567890.html#local-article-paragraph-1"),
    )
    card = replace(_daily_local_synthesis_brief_fixture().cards[0], evidence_links=unsafe_links)
    brief = replace(_daily_local_synthesis_brief_fixture(), cards=(card,))

    html = render_index_html(_edition(), daily_local_synthesis_brief=brief)
    section_html = _daily_local_synthesis_brief_section_html(html)

    assert 'class="daily-local-synthesis-brief-card"' in section_html
    assert 'class="daily-local-synthesis-brief-evidence-trail"' not in section_html
    assert "https://example.com" not in section_html
    assert "?x=1" not in section_html
```

- [ ] Extend `test_row_one_css_includes_daily_local_synthesis_brief_styles` to assert:

```python
    for selector in (
        ".daily-local-synthesis-brief-evidence-trail",
        ".daily-local-synthesis-brief-evidence-link",
        ".daily-local-synthesis-brief-evidence-support",
    ):
        assert selector in css
    assert re.search(
        r"\.daily-local-synthesis-brief-evidence-trail\s*\{[^}]*min-width:\s*0",
        css,
    )
    assert re.search(
        r"\.daily-local-synthesis-brief-evidence-link\s*\{[^}]*overflow-wrap:\s*anywhere",
        css,
    )
    assert re.search(
        r"\.daily-local-synthesis-brief-evidence-support\s*\{[^}]*overflow-wrap:\s*anywhere",
        css,
    )
```

- [ ] Run RED command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_daily_local_synthesis_brief_evidence_trail_links_to_saved_articles \
  tests/test_row_one_render.py::test_render_daily_local_synthesis_brief_omits_empty_or_unsafe_evidence_trail \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_local_synthesis_brief_styles \
  -q
```

Expected: FAIL because rendering/CSS is not implemented yet.

### Task 4: Implement evidence trail rendering and CSS

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] Import `RowOneDailyLocalSynthesisEvidenceLink`.
- [ ] Add `_render_daily_local_synthesis_evidence_link(...)`:

```python
def _render_daily_local_synthesis_evidence_link(
    link: RowOneDailyLocalSynthesisEvidenceLink,
) -> str:
    href = _safe_daily_local_synthesis_evidence_href(link.href)
    label_en = normalize_row_one_paragraph(link.label.en)
    label_zh = normalize_row_one_paragraph(link.label.zh)
    if href is None or not (label_en or label_zh):
        return ""
    support_en = normalize_row_one_paragraph(link.support.en) if link.support else ""
    support_zh = normalize_row_one_paragraph(link.support.zh) if link.support else ""
    support_html = (
        f'''        <span class="daily-local-synthesis-brief-evidence-support">
          <span data-lang="en">{_esc(support_en or support_zh)}</span>
          <span data-lang="zh">{_esc(support_zh or support_en)}</span>
        </span>
'''
        if support_en or support_zh
        else ""
    )
    return f'''      <a class="daily-local-synthesis-brief-evidence-link" href="{_esc(href)}">
        <span class="daily-local-synthesis-brief-evidence-label">
          <span data-lang="en">{_esc(label_en or label_zh)}</span>
          <span data-lang="zh">{_esc(label_zh or label_en)}</span>
        </span>
{support_html}      </a>
'''
```

- [ ] Add `_safe_daily_local_synthesis_evidence_href(...)`:

```python
def _safe_daily_local_synthesis_evidence_href(href: object) -> str | None:
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
    if (
        _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None
        and _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None
    ):
        return None
    return f"{page_href}#{fragment}"
```

- [ ] In `_render_daily_local_synthesis_brief_card(...)`, render evidence links before route:

```python
    evidence_links = [
        link_html
        for link in card.evidence_links
        if (link_html := _render_daily_local_synthesis_evidence_link(link))
    ]
    evidence_html = (
        f'''      <div class="daily-local-synthesis-brief-evidence-trail">
        <p>
          <span data-lang="en">Evidence Trail</span>
          <span data-lang="zh">证据线索</span>
        </p>
{"".join(evidence_links)}      </div>
'''
        if evidence_links
        else ""
    )
```

- [ ] Insert `{evidence_html}` before `<a class="daily-local-synthesis-brief-route" ...>`.
- [ ] Add CSS:

```css
.daily-local-synthesis-brief-evidence-trail {
  border-top: 1px solid rgba(244, 246, 248, 0.14);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding-top: 10px;
}
.daily-local-synthesis-brief-evidence-trail p {
  color: var(--chrome);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  margin: 0;
  text-transform: uppercase;
}
.daily-local-synthesis-brief-evidence-link {
  color: var(--panel);
  display: grid;
  gap: 3px;
  line-height: 1.3;
  overflow-wrap: anywhere;
  text-decoration-color: rgba(244, 246, 248, 0.26);
  text-underline-offset: 3px;
}
.daily-local-synthesis-brief-evidence-support {
  color: var(--steel);
  font-size: 0.82rem;
  overflow-wrap: anywhere;
}
```

- [ ] Run render tests from Task 3 again.

Expected: PASS.

### Task 5: Homepage-only and artifact boundary tests

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`

- [ ] Extend `test_render_row_one_site_writes_daily_local_synthesis_brief_homepage_only`:
  - Assert homepage section contains `daily-local-synthesis-brief-evidence-trail`.
  - Assert rendered evidence trail class attributes are absent from library, article pages, and detail pages by checking `class="daily-local-synthesis-brief-evidence-trail"` rather than the raw selector token, because global CSS may legitimately contain selector text.
  - Assert Stage 385 tokens are absent from `generated_contract_payload`.
  - Assert no artifact stems exist for:

```python
(
    "daily-local-synthesis-evidence-trail",
    "local-synthesis-evidence-trail",
    "daily-synthesis-evidence-trail",
    "synthesis-evidence-trail",
    "daily_local_synthesis_evidence_trail",
    "local_synthesis_evidence_trail",
    "daily_synthesis_evidence_trail",
    "synthesis_evidence_trail",
)
```

- [ ] Add `test_stage_385_daily_local_synthesis_evidence_trail_stays_homepage_only` in `tests/test_workflows.py`.

Test shape:

```python
def test_stage_385_daily_local_synthesis_evidence_trail_stays_homepage_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    sentinel = "STAGE_385_DAILY_LOCAL_SYNTHESIS_EVIDENCE_TRAIL_SENTINEL"
    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_synthesis_evidence_link",
        lambda _link: sentinel,
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
    assert sentinel not in generated_payloads.get("articles/index.html", "")
    assert all(
        sentinel not in payload
        for relative_path, payload in generated_payloads.items()
        if relative_path.startswith("articles/")
        and relative_path.endswith(".html")
        and relative_path != "articles/index.html"
    )
    assert all(
        sentinel not in payload
        for relative_path, payload in generated_payloads.items()
        if relative_path.startswith("details/") and relative_path.endswith(".html")
    )
    assert sentinel not in generated_payloads["data/edition.json"]
    assert sentinel not in generated_payloads["data/manifest.json"]
    assert sentinel not in generated_payloads["data/runtime.json"]
    for relative_path, payload in generated_payloads.items():
        if relative_path.startswith("data/articles/") and relative_path.endswith(".json"):
            assert sentinel not in payload
```

- [ ] Extend contract/artifact denylist tests around current Stage 383 entries with Stage 385 tokens:

```python
"daily_local_synthesis_evidence_trail",
"local_synthesis_evidence_trail",
"daily_synthesis_evidence_trail",
"synthesis_evidence_trail",
"Daily Local Synthesis Evidence Trail",
"daily-local-synthesis-evidence-trail",
"local-synthesis-evidence-trail",
"daily-synthesis-evidence-trail",
"synthesis-evidence-trail",
```

- [ ] Run focused boundary tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_synthesis_brief_homepage_only \
  tests/test_workflows.py::test_stage_385_daily_local_synthesis_evidence_trail_stays_homepage_only \
  -q
```

Expected: PASS.

### Task 6: Docs boundary paragraph and docs test

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] Add paragraph above Stage 384 in both docs:

```text
Stage 385 adds a generated-site-only Daily Local Synthesis Evidence Trail inside the existing Daily Local Synthesis Brief cards on the ROW ONE homepage; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, and Stage 382 local article synthesis anchors to connect each homepage synthesis card to concrete saved-article sections or paragraphs without changing app-facing contracts; it does not create `data/daily-local-synthesis-evidence-trail.json`, does not create `data/local-synthesis-evidence-trail.json`, does not create `data/daily-synthesis-evidence-trail.json`, does not create `data/synthesis-evidence-trail.json`, does not create `daily-local-synthesis-evidence-trail.html`, does not create `local-synthesis-evidence-trail.html`, does not create `daily-synthesis-evidence-trail.html`, does not create `synthesis-evidence-trail.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles or raw paragraphs on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
```

- [ ] Add `test_row_one_docs_describe_stage_385_daily_local_synthesis_evidence_trail_boundary`.
- [ ] Assert the paragraph appears in README and `docs/row-one.md`.
- [ ] Assert it appears before Stage 384.
- [ ] In the Stage 385 slice only, deny stale phrases for both creates/writes variants of the JSON/HTML artifacts above plus standard new routes/contracts/schemas/source/scraping/LLM/scheduling/analytics/recommendation/compliance-review behavior.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_385_daily_local_synthesis_evidence_trail_boundary -q
```

Expected: PASS.

### Task 7: Focused and related verification

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_synthesis_brief.py \
  tests/test_row_one_render.py -k "daily_local_synthesis_brief" \
  tests/test_workflows.py::test_stage_385_daily_local_synthesis_evidence_trail_stays_homepage_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_385_daily_local_synthesis_evidence_trail_boundary \
  -q
```

Expected: PASS.

Then run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_synthesis_brief.py \
  tests/test_row_one_local_article_synthesis_brief.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  -q
```

Expected: PASS.

### Task 8: Code review and final gates

- [ ] Build `/tmp/stage385-code-review-prompt.md` from the plan summary and `git diff --stat`.
- [ ] Run code reviews:

```bash
claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash -p "$(cat /tmp/stage385-code-review-prompt.md)" > docs/reviews/claude-code-stage-385-code-review.md
NO_COLOR=1 opencode run --model zhipuai-coding-plan/glm-5.2 --variant max "$(cat /tmp/stage385-code-review-prompt.md)" > docs/reviews/opencode-stage-385-code-review.md
```

If Claude times out, write a non-empty timeout note. Clean opencode chatter before release hygiene.

- [ ] Fix every Critical/Important review finding, with rereview artifacts if needed.
- [ ] Run final gates:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --cached --check
```

Expected: all pass.

### Task 9: Commit and push

- [ ] Stage files:

```bash
git add README.md docs/row-one.md docs/reviews docs/superpowers/plans/2026-07-12-stage-385-daily-local-synthesis-evidence-trail-plan.md \
  src/fashion_radar/row_one/daily_local_synthesis_brief.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_daily_local_synthesis_brief.py \
  tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
```

- [ ] Commit and push:

```bash
git commit -m "Stage 385: add daily local synthesis evidence trail"
git push origin main
```

- [ ] Handoff summary must include repo status, verified commands, uncommitted files, and next step.

## Acceptance Criteria

- `RowOneDailyLocalSynthesisBriefCard` carries capped, safe, deduped evidence links derived from Stage 382 local article synthesis anchors.
- `index.html` Daily Local Synthesis Brief cards render evidence trails when valid links exist.
- Empty or unsafe evidence links are omitted without dropping otherwise valid cards.
- Stage 385 does not create new JSON/HTML artifact families and does not alter app/runtime/manifest/schema contracts.
- Stage 385 evidence trail is homepage-only and absent from article library, article pages, detail pages, and generated contract payloads.
- README and `docs/row-one.md` document the Stage 385 boundary above Stage 384.
- Plan review, code review, focused tests, related tests, full pytest, ruff, format check, release hygiene, lock check, and diff whitespace checks pass before push.
