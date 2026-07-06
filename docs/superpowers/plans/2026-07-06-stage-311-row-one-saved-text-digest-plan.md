# Stage 311 ROW ONE Saved Text Digest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> When spawning Codex subagents for this project, set `reasoning_effort` to `xhigh` as required by `AGENTS.md`.

**Goal:** Add a generated-site detail-page saved text digest that organizes locally saved article content into scan-first cards inside ROW ONE.

**Architecture:** Keep the existing ROW ONE static-site and sidecar architecture. Render the digest from existing `RowOneLocalArticle.paragraphs`, optional aligned `paragraphs_zh`, and existing `content_sections`; do not add model fields, schema fields, or app-payload fields.

**Tech Stack:** Python 3.12, existing Pydantic ROW ONE models, static HTML/CSS template helpers, pytest, ruff, frozen/no-config uv verification.

**Pipeline Gap Closed:** This closes a report-layer presentation gap: the collect and match stages already produce saved local article sidecars and references, while Stage 311 organizes those existing report artifacts into a detail-page reading digest without adding new collection, matching, or scoring.

---

## Non-Goals

- Do not add source collection, scraping, browser automation, platform APIs,
  login/cookie/proxy/CAPTCHA behavior, paywall bypass, LLM calls, translation
  services, image generation, or scheduling.
- Do not add compliance-review product features.
- Do not change `row-one-app/v7`, `data/edition.json`,
  `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, story IDs, detail
  routes, or `#local-article-paragraph-N` anchors.
- Do not add a homepage saved-article coverage index in this stage; that
  broader corpus-level view is a follow-up candidate after the detail-page
  saved text digest lands.
- Do not commit generated `reports/row-one/site/**`.
- Do not rewrite `uv.lock` to mirror URLs.

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
  - Add saved text digest helper functions.
  - Insert digest in `_render_local_article()`.
  - Add a `Digest` / `整理` chip to `_render_local_article_map()` when digest
    exists.
  - Add restrained CSS selectors.
- Modify: `tests/test_row_one_render.py`
  - Add digest rendering, fallback, sanitization, ordering, CSS, and contract
    stability tests.
- Modify: `README.md`, `docs/row-one.md`
  - Document Stage 311 as generated-site detail-page organization only.
- Modify: `tests/test_row_one_docs.py`
  - Pin docs boundary text.
- Existing planning artifacts, created before implementation:
  - `docs/reviews/claude-code-stage-311-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-311-plan-review.md`, if Claude Code is available
  - `docs/reviews/opencode-stage-311-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-311-plan-review.md`

## Task 1: Add Failing Digest Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add structured digest rendering coverage**

Add a focused test near the existing local article render tests:

```python
def test_render_row_one_detail_includes_saved_text_digest_from_content_sections(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Structured digest source",
        url="https://example.com/digest",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "The Row demand moved through the saved source paragraph.",
            "Zendaya styled the Margaux bag in the second saved paragraph.",
        ],
        paragraphs_zh=[
            "The Row 需求出现在保存正文第一段。",
            "Zendaya 在第二段中搭配 Margaux 包袋。",
        ],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="what_happened",
                title=LocalizedText(en="What Happened", zh="发生了什么"),
                body=LocalizedText(en="Digest brief.", zh="整理简报。"),
            )
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(
                            en="Zendaya styled the Margaux bag in the second saved paragraph.",
                            zh="Zendaya 在第二段中搭配 Margaux 包袋。",
                        ),
                        paragraph_indices=[1],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(en="Entities", zh="相关对象"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ],
                        paragraph_indices=[0],
                    ),
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Zendaya", zh="Zendaya"),
                        references=[
                            RowOneReference(name="Zendaya", type="celebrity", label="new"),
                        ],
                        paragraph_indices=[1],
                    ),
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(en="Product Signals", zh="产品信号"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Margaux", zh="Margaux"),
                        references=[
                            RowOneReference(name="Margaux", type="bag", label="product"),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    edition_json = (tmp_path / "data" / "edition.json").read_text(encoding="utf-8")
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]
    map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert 'class="local-article-digest"' in digest_html
    assert 'aria-label="Saved text digest"' in digest_html
    assert '<span data-lang="en">Saved Text Digest</span>' in digest_html
    assert '<span data-lang="zh">保存正文整理</span>' in digest_html
    assert '<span data-lang="en">Read First</span>' in digest_html
    assert '<span data-lang="zh">先读</span>' in digest_html
    assert "Zendaya styled the Margaux bag in the second saved paragraph." in digest_html
    assert "Zendaya 在第二段中搭配 Margaux 包袋。" in digest_html
    assert 'href="#local-article-paragraph-2"' in digest_html
    assert '<span data-lang="en">People &amp; Brands</span>' in digest_html
    assert '<span data-lang="zh">品牌与人物</span>' in digest_html
    assert "The Row" in digest_html
    assert "Zendaya" in digest_html
    assert '<span data-lang="en">Products</span>' in digest_html
    assert '<span data-lang="zh">产品</span>' in digest_html
    assert "Margaux" in digest_html
    assert '<span data-lang="en">Source Map</span>' in digest_html
    assert '<span data-lang="zh">来源结构</span>' in digest_html
    assert "Vogue Business" in digest_html
    assert "2 saved paragraphs" in digest_html
    assert "3 organized sections" in digest_html
    assert 'href="#local-article-digest"' in map_html
    assert '<span data-lang="en">Digest</span>' in map_html
    assert '<span data-lang="zh">整理</span>' in map_html
    assert detail_html.index('href="#local-article-brief"') < detail_html.index(
        'href="#local-article-digest"'
    )
    assert detail_html.index('href="#local-article-digest"') < detail_html.index(
        'href="#local-article-reader"'
    )
    assert detail_html.index('id="local-article-digest"') < detail_html.index(
        'id="local-article-reader"'
    )
    assert detail_html.index('id="local-article-digest"') < detail_html.index(
        'id="local-article-brief"'
    )
    assert "local-article-digest" not in edition_json
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_includes_saved_text_digest_from_content_sections -q
```

Expected: FAIL because `local-article-digest` does not exist yet.

- [ ] **Step 2: Add plain article digest coverage**

Add:

```python
def test_render_row_one_detail_plain_local_article_gets_digest_without_map(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Plain digest source",
        url="https://example.com/plain-digest",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First saved source paragraph becomes the digest fallback.",
            "Second saved source paragraph stays in the saved text reader.",
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]

    assert 'id="local-article-digest"' in detail_html
    assert "First saved source paragraph becomes the digest fallback." in digest_html
    assert 'href="#local-article-paragraph-1"' in digest_html
    assert "Fashion Desk" in digest_html
    assert "2 saved paragraphs" in digest_html
    assert "0 organized sections" in digest_html
    assert 'class="local-article-map"' not in detail_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_plain_local_article_gets_digest_without_map -q
```

Expected: FAIL until the digest is implemented.

- [ ] **Step 3: Add sanitization, dedupe, index filtering, and truncation coverage**

Add:

```python
def test_render_row_one_detail_digest_escapes_dedupes_filters_and_truncates(
    tmp_path,
) -> None:
    edition = _edition()
    long_text = (
        "The Row paragraph includes <script>alert('x')</script> and a very long "
        "saved source sentence that should be shortened inside the digest card "
        "while the complete saved text remains available through its anchor."
    )
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Escaped digest source",
        url="https://example.com/escaped-digest",
        source_name="Vogue <Business>",
        extracted_at=AS_OF,
        paragraphs=[long_text, "   ", "Final saved paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Unsafe", zh="不安全"),
                        body=LocalizedText(en=long_text, zh=long_text),
                        paragraph_indices=[0, 1, 99],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(en="Entities", zh="相关对象"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(
                                name="<script>Brand</script>",
                                type="brand",
                                label="unsafe",
                            ),
                        ],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]
    reference_html = digest_html[
        digest_html.index('<span data-lang="en">People &amp; Brands</span>') : digest_html.index(
            '<span data-lang="en">Source Map</span>'
        )
    ]
    body_html = detail_html[detail_html.index('id="local-article-body"') :]

    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in digest_html
    assert "&lt;script&gt;Brand&lt;/script&gt;" in digest_html
    assert "<script>" not in digest_html
    assert reference_html.count('class="local-article-digest-chip"') == 2
    assert reference_html.count(">The Row<") == 1
    assert 'href="#local-article-paragraph-1"' in digest_html
    assert 'href="#local-article-paragraph-2"' not in digest_html
    assert 'href="#local-article-paragraph-100"' not in digest_html
    assert "2 saved paragraphs" in digest_html
    assert "3 saved paragraphs" not in digest_html
    assert "complete saved text remains available" not in digest_html
    assert "…" in digest_html
    assert "complete saved text remains available" in body_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_digest_escapes_dedupes_filters_and_truncates -q
```

Expected: FAIL until the digest is implemented.

- [ ] **Step 4: Add contract stability coverage**

Add:

```python
def test_render_row_one_detail_digest_keeps_app_contract_stable(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Contract digest source",
        url="https://example.com/contract-digest",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Digest-only local paragraph for contract stability."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    edition_json = json.dumps(edition_payload, ensure_ascii=False)

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    assert "Digest-only local paragraph for contract stability." not in edition_json
    assert "local-article-digest" not in edition_json
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_digest_keeps_app_contract_stable -q
```

Expected: PASS before and after implementation for contract values and body
exclusion; it guards against accidentally moving digest data into
`data/edition.json`.

- [ ] **Step 5: Add takeaway-body coverage when paragraph links are invalid**

Add:

```python
def test_render_row_one_detail_digest_keeps_takeaway_body_without_valid_links(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Invalid link digest source",
        url="https://example.com/invalid-link-digest",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=["Only publishable saved paragraph.", "   "],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(
                            en="Use this organized takeaway even without valid paragraph links.",
                            zh="即使没有有效段落链接，也使用这条整理要点。",
                        ),
                        paragraph_indices=[1, 99],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]

    assert "Use this organized takeaway even without valid paragraph links." in digest_html
    assert "即使没有有效段落链接，也使用这条整理要点。" in digest_html
    assert 'href="#local-article-paragraph-2"' not in digest_html
    assert 'href="#local-article-paragraph-100"' not in digest_html
    assert "1 saved paragraph" in digest_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_digest_keeps_takeaway_body_without_valid_links -q
```

Expected: FAIL until the digest is implemented.

- [ ] **Step 6: Update existing Stage 310 map slices for the new digest block**

When digest is inserted between the local article map and reader, existing
tests that slice map HTML up to `id="local-article-reader"` or
`class="local-article-brief"` must be narrowed so digest/reader markup does not
pollute the map slice.

Update existing local-article map slices in `tests/test_row_one_render.py`:

```python
local_article_map_html = detail_html[
    detail_html.index('class="local-article-map"') : detail_html.index(
        'id="local-article-digest"'
    )
]
```

Use this replacement in structured local article tests where the fixture now
renders the digest. Keep plain local article tests asserting no
`class="local-article-map"`.

At minimum, check and update these existing tests if their map slices would
otherwise include digest or reader markup:

- `test_render_row_one_detail_includes_local_article_content`
- `test_render_row_one_detail_map_handles_brief_only_local_article`
- `test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch`
- `test_render_row_one_detail_escapes_local_article_content`

## Task 2: Implement Digest Template Helpers

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add digest constants**

Near the local article reader constants, add:

```python
LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS = 160
LOCAL_ARTICLE_DIGEST_MAX_REFERENCES = 4
```

- [ ] **Step 2: Add digest rendering helpers**

Add helpers near `_render_local_article_reader()`:

```python
def _render_local_article_digest(article: RowOneLocalArticle) -> str:
    if not _local_article_rendered_paragraph_indices(article):
        return ""
    cards = [
        card
        for card in (
            _render_local_article_digest_read_first(article),
            _render_local_article_digest_references(
                article,
                keys=("entities",),
                title_en="People & Brands",
                title_zh="品牌与人物",
            ),
            _render_local_article_digest_references(
                article,
                keys=("product_signals",),
                title_en="Products",
                title_zh="产品",
            ),
            _render_local_article_digest_source_map(article),
        )
        if card
    ]
    if not cards:
        return ""
    return f"""      <div id="local-article-digest" class="local-article-digest" aria-label="Saved text digest">
        <div class="local-article-digest-header">
          <h4>
            <span data-lang="en">Saved Text Digest</span>
            <span data-lang="zh">保存正文整理</span>
          </h4>
          <p>
            <span data-lang="en">A scan-first organization of the existing saved text.</span>
            <span data-lang="zh">基于现有保存正文的速览整理。</span>
          </p>
        </div>
        <div class="local-article-digest-grid">
{chr(10).join(cards)}
        </div>
      </div>"""
```

Implement these helper responsibilities:

- `_render_local_article_digest_read_first(article)` returns the first takeaway
  item with a nonblank body. Valid paragraph links are rendered when present;
  invalid or blank-paragraph indices are omitted without discarding the takeaway
  body. If no takeaway body exists, it falls back to the first nonblank saved
  paragraph, synthesizes that paragraph's original index, and renders its
  `#local-article-paragraph-N` link.
- `_local_article_digest_takeaway(article)` returns
  `(body_en, body_zh, paragraph_indices)`. It must still return the body with
  an empty `paragraph_indices` list when all supplied paragraph indices are
  invalid or point to blank paragraphs.
- `_render_local_article_digest_references(article, *, keys, title_en, title_zh)`
  dedupes and limits references from matching `content_sections`. Each rendered
  reference chip uses `class="local-article-digest-chip"` and renders the
  escaped reference name only. Deduplication uses
  `normalize_row_one_paragraph(ref.name).casefold()`, stripped casefolded
  `ref.type`, and stripped casefolded `ref.label`, preserving first-seen order.
- `brand_signals` remains available in existing organized content cards and is
  intentionally not duplicated as a digest reference card in this stage.
- `_render_local_article_digest_source_map(article)` renders source name, saved
  paragraph count, and organized section count. Saved paragraph count must be
  nonblank-only, using `_local_article_saved_paragraph_count(article)` or an
  equivalent count.
- `_render_local_article_digest_paragraph_links(indices, rendered_indices)`
  returns compact bilingual anchor links inside
  `class="local-article-digest-link-list"` with the same
  `#local-article-paragraph-N` targets.
- `_local_article_digest_excerpt(text)` must use `_meta_description(...,
  limit=LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS)`.

All rendered text and hrefs must be escaped.

- [ ] **Step 3: Wire digest into `_render_local_article()`**

Update `_render_local_article()`:

```python
digest = _render_local_article_digest(article)
reader = _render_local_article_reader(article)
article_map = _render_local_article_map(
    article,
    include_digest=bool(digest),
    include_reader=bool(reader),
)
```

Place `{digest}` after `{article_map}` and before `{reader}`.

- [ ] **Step 4: Add the digest map chip**

Change `_render_local_article_map()` signature to:

```python
def _render_local_article_map(
    article: RowOneLocalArticle,
    *,
    include_digest: bool = False,
    include_reader: bool = False,
) -> str:
```

Keep the current early return for plain articles:

```python
if not article.brief_sections and not article.content_sections:
    return ""
```

After the brief link and before the reader link, add:

```python
if include_digest:
    links.append(
        '<a href="#local-article-digest">'
        '<span data-lang="en">Digest</span>'
        '<span data-lang="zh">整理</span>'
        "</a>"
    )
```

Run the three failing render tests from Task 1. Expected: PASS after Task 2.

## Task 3: Add CSS Selector Coverage And Styles

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Extend the local article CSS selector test**

In `test_row_one_css_includes_local_article_map_styles`, add:

```python
        ".local-article-digest {",
        ".local-article-digest-header {",
        ".local-article-digest-grid {",
        ".local-article-digest-card {",
        ".local-article-digest-card h4 {",
        ".local-article-digest-list {",
        ".local-article-digest-link-list {",
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_row_one_css_includes_local_article_map_styles -q
```

Expected: FAIL until CSS is added.

- [ ] **Step 2: Add restrained CSS**

Inside `row_one_css()`, near existing `.local-article-reader` styles, add small
selectors for digest layout:

```css
.local-article-digest {
  border: 1px solid var(--line);
  border-radius: 4px;
  margin: 14px 0 16px;
  padding: 14px;
}
.local-article-digest-header {
  display: grid;
  gap: 6px;
  margin: 0 0 12px;
}
.local-article-digest-header h4,
.local-article-digest-header p {
  margin: 0;
}
.local-article-digest-header h4 {
  font-size: 0.9rem;
}
.local-article-digest-header p {
  color: var(--muted);
  font-size: 0.82rem;
}
.local-article-digest-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.local-article-digest-card {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
.local-article-digest-card h4 {
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-digest-card p {
  line-height: 1.45;
  margin: 0 0 8px;
}
.local-article-digest-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-digest-link-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-digest-chip,
.local-article-digest-link-list a {
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 6px 8px;
  text-decoration: none;
}
```

Run the CSS selector test again. Expected: PASS.

## Task 4: Update Docs And Docs Tests

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add docs boundary test**

Add:

```python
def test_row_one_docs_describe_saved_text_digest_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")

    expected_phrases = [
        "saved text digest",
        "detail-page saved text digest",
        "uses existing `data/articles/<story-id>.json` sidecars",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not add source collection",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme
        assert phrase in docs
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_saved_text_digest_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Update README and docs**

Add a short Stage 311 paragraph to both README and `docs/row-one.md`. Keep the
required phrases physically contiguous on one line where the test expects exact
phrases:

```markdown
Stage 311 adds a generated-site saved text digest on ROW ONE detail pages:
existing saved local paragraphs and existing organized sidecar sections are
presented as scan-first cards for read-first context, people/brands, products,
and source structure. This is a detail-page saved text digest only; it does not
change `row-one-app/v7`, does not change `data/edition.json`, uses existing `data/articles/<story-id>.json` sidecars, does not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change detail routes, does not change paragraph anchors, does not change schemas, does not add source collection, does not add scoring, and does not add llm calls.
```

Run the docs test again. Expected: PASS.

## Task 5: Verification, Code Review, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-311-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-311-code-review.md`
- Possibly create rereview artifacts if fixes are needed.

- [ ] **Step 1: Focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q
```

Expected: PASS.

- [ ] **Step 2: Full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
```

Expected: all PASS.

- [ ] **Step 3: Build ignored sample site and check status**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected: `ok: true`, app `row-one-app/v7`, manifest
`row-one-manifest/v1`, runtime `row-one-runtime/v1`.

- [ ] **Step 4: Request Claude Code code review**

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-311-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-311-code-review.md
```

Fix Critical/Important findings and rerun relevant verification.

- [ ] **Step 5: Confirm this is a normal stage push, not release upload**

This stage may be committed and pushed to the already configured `origin/main`
after code review and verification because the user has already authorized
stage pushes to this remote. It is not a release/GitHub-upload node. Do not
claim release readiness from this stage alone, and do not create release-review
artifacts unless the user explicitly requests a release/upload review.

- [ ] **Step 6: Stage explicitly**

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-311-code-review-prompt.md \
  docs/reviews/claude-code-stage-311-code-review.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py tests/test_row_one_docs.py
git diff --cached --name-only -- uv.lock reports/row-one/site
git diff --cached --check
```

Expected: no output from the `uv.lock` / generated-site check and no diff check
errors.

- [ ] **Step 7: Commit and push**

```bash
git commit -m "Stage 311: add row one saved text digest"
git push origin main
```

- [ ] **Step 8: Handoff Summary**

Report repo status, commit SHA, verified commands, uncommitted files, ignored
generated site status, and next recommended stage.
