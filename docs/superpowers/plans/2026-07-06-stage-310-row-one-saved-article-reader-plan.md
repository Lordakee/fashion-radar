# Stage 310 ROW ONE Saved Article Reader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site detail-page saved text reader so ROW ONE users can scan locally saved article content in-page instead of relying on outbound source links.

**Architecture:** Keep ROW ONE's existing static-site and sidecar architecture. Implement a template-only reader block from existing `RowOneLocalArticle.paragraphs` and optional aligned `paragraphs_zh`, preserving the current app/manifest/runtime contract versions and existing paragraph anchors.

**Tech Stack:** Python 3.12, existing Pydantic ROW ONE models, static HTML/CSS template helpers, pytest, ruff, frozen/no-config uv verification.

---

## Non-Goals

- Do not add source collection, browser automation, platform APIs, scraping, network fetching, LLM calls, image generation, translation services, or scheduling.
- Do not add compliance-review product features.
- Do not change `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, `data/edition.json`, JSON schemas, story IDs, story detail routes, or paragraph anchor naming.
- Do not redesign ROW ONE visually; add only restrained reader markup/CSS that follows existing local-article styles.
- Do not commit generated `reports/row-one/site/**`.
- Do not rewrite `uv.lock` to mirror URLs.

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
  - Add saved text reader helper functions.
  - Insert the reader in `_render_local_article()`.
  - Add a `Reader` / `阅读` chip to `_render_local_article_map()` when the reader exists.
  - Rename the existing `Full saved text` / `完整保存正文` map label to `Saved text` / `保存正文` without changing `#local-article-body`.
  - Add small CSS selectors for the reader and numbered excerpt list.
- Modify: `tests/test_row_one_render.py`
  - Add focused reader rendering coverage.
  - Extend existing local article assertions where needed.
- Modify: `README.md`, `docs/row-one.md`
  - Document Stage 310 as generated-site detail-page organization only.
- Modify: `tests/test_row_one_docs.py`
  - Pin docs boundary text.
- Create review artifacts:
  - `docs/reviews/claude-code-stage-310-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-310-plan-review.md`
  - Later, code review prompt/result files after implementation.

## Task 1: Add Failing Reader Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Extend the structured local article detail test**

In `test_render_row_one_detail_includes_local_article_content`, after the
existing local article map assertions, add assertions for the new reader block:

```python
    assert 'id="local-article-reader"' in detail_html
    assert 'class="local-article-reader"' in detail_html
    assert '<span data-lang="en">Saved Text Reader</span>' in detail_html
    assert '<span data-lang="zh">保存正文阅读</span>' in detail_html
    assert "2 saved paragraphs from Vogue Business" in detail_html
    assert "来自 Vogue Business 的 2 个保存段落" in detail_html
    assert 'class="local-article-reader-list"' in detail_html
    assert 'aria-label="Saved text paragraphs"' in detail_html
    assert 'href="#local-article-reader"' in detail_html
    assert '<span data-lang="en">Reader</span>' in detail_html
    assert '<span data-lang="zh">阅读</span>' in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-paragraph-2"' in detail_html
    assert '<span class="local-article-reader-number">01</span>' in detail_html
    assert '<span class="local-article-reader-number">02</span>' in detail_html
    assert '<span data-lang="en">First local paragraph about The Row demand.</span>' in detail_html
    assert '<span data-lang="zh">第一段本地正文，关于 The Row 需求。</span>' in detail_html
    assert '<span data-lang="en">Saved text</span>' in detail_html
    assert '<span data-lang="zh">保存正文</span>' in detail_html
    assert "Full saved text" not in detail_html
    assert "完整保存正文" not in detail_html
    assert detail_html.index('class="local-article-map"') < detail_html.index(
        'id="local-article-reader"'
    )
    assert detail_html.index('href="#local-article-brief"') < detail_html.index(
        'href="#local-article-reader"'
    )
    assert detail_html.index('href="#local-article-reader"') < detail_html.index(
        'href="#local-article-content-section-1"'
    )
    assert detail_html.index('id="local-article-reader"') < detail_html.index(
        'class="local-article-brief"'
    )
    assert detail_html.index('id="local-article-reader"') < detail_html.index(
        'id="local-article-body"'
    )
    assert "local-article-reader" not in edition_json
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content -q
```

Expected: FAIL because `local-article-reader` does not exist yet.

- [ ] **Step 2: Add plain local article reader coverage**

Add a focused test after
`test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs`:

```python
def test_render_row_one_detail_plain_local_article_gets_reader_without_map(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Plain source article",
        url="https://example.com/plain",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First saved source paragraph for the local reader.",
            "Second saved source paragraph for the local reader.",
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

    assert 'id="local-article-reader"' in detail_html
    assert "2 saved paragraphs from Fashion Desk" in detail_html
    assert 'class="local-article-reader-list"' in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-paragraph-2"' in detail_html
    assert 'class="local-article-map"' not in detail_html
    assert '<p id="local-article-paragraph-1">First saved source paragraph for the local reader.</p>' in detail_html
    assert '<p id="local-article-paragraph-2">Second saved source paragraph for the local reader.</p>' in detail_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_plain_local_article_gets_reader_without_map -q
```

Expected: FAIL because the reader does not exist yet.

- [ ] **Step 3: Add single-paragraph meta coverage**

Add a focused test after the plain local article reader test:

```python
def test_render_row_one_detail_reader_uses_singular_paragraph_meta(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Single paragraph article",
        url="https://example.com/single",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=["One saved source paragraph for the reader."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert "1 saved paragraph from Fashion Desk" in detail_html
    assert "1 saved paragraphs from Fashion Desk" not in detail_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_reader_uses_singular_paragraph_meta -q
```

Expected: FAIL because the reader does not exist yet.

- [ ] **Step 4: Add aligned blank Chinese paragraph fallback coverage**

Add a focused test after the plain local article reader test:

```python
def test_render_row_one_detail_reader_falls_back_when_aligned_zh_excerpt_is_blank(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Aligned blank zh article",
        url="https://example.com/aligned",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First aligned paragraph for the reader.",
            "Second aligned paragraph falls back when zh is blank.",
        ],
        paragraphs_zh=[
            "第一段用于阅读器。",
            "   ",
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
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert '<span data-lang="zh">第一段用于阅读器。</span>' in reader_html
    assert (
        '<span data-lang="zh">Second aligned paragraph falls back when zh is blank.</span>'
        in reader_html
    )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_reader_falls_back_when_aligned_zh_excerpt_is_blank -q
```

Expected: FAIL because the reader does not exist yet.

- [ ] **Step 5: Add misaligned Chinese paragraph fallback coverage**

Add a focused test after the aligned blank Chinese paragraph fallback test:

```python
def test_render_row_one_detail_reader_uses_plain_excerpt_when_zh_paragraphs_mismatch(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Mismatched zh article",
        url="https://example.com/mismatch",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First source paragraph uses plain reader output.",
            "Second source paragraph also uses plain reader output.",
        ],
        paragraphs_zh=["只有一个中文段落。"],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert "First source paragraph uses plain reader output." in reader_html
    assert "Second source paragraph also uses plain reader output." in reader_html
    assert 'data-lang="zh">只有一个中文段落。' not in reader_html
    assert 'data-lang="en">First source paragraph uses plain reader output.' not in reader_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_reader_uses_plain_excerpt_when_zh_paragraphs_mismatch -q
```

Expected: FAIL because the reader does not exist yet.

- [ ] **Step 6: Add skip/escape/truncate coverage**

Add:

```python
def test_render_row_one_detail_reader_skips_blank_escapes_and_truncates(tmp_path) -> None:
    edition = _edition()
    long_text = (
        "The Row paragraph includes <script>alert('x')</script> and a very long "
        "source sentence that should be shortened inside the reader index while "
        "the existing saved text remains available through the paragraph anchor."
    )
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Escaped reader article",
        url="https://example.com/escaped",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[long_text, "   ", "Final concise paragraph."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert "local-article-paragraph-2" not in reader_html
    assert 'href="#local-article-paragraph-1"' in reader_html
    assert 'href="#local-article-paragraph-3"' in reader_html
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in reader_html
    assert "<script>alert" not in reader_html
    assert "paragraph anchor." not in reader_html
    assert "…" in reader_html
    assert '<p id="local-article-paragraph-3">Final concise paragraph.</p>' in detail_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_reader_skips_blank_escapes_and_truncates -q
```

Expected: FAIL because the reader does not exist yet.

- [ ] **Step 7: Add contract-stability coverage**

Add a focused test near the other ROW ONE local article render tests:

```python
def test_render_row_one_detail_reader_keeps_app_contract_stable(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Contract stable article",
        url="https://example.com/contract",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Reader-only local paragraph for contract stability."],
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
    assert "Reader-only local paragraph for contract stability." not in edition_json
    assert "local-article-reader" not in edition_json
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_reader_keeps_app_contract_stable -q
```

Expected: PASS before and after implementation for contract values and body
exclusion; it becomes a guard against accidentally moving reader data into
`data/edition.json`.

- [ ] **Step 8: Update existing paragraph-link count assertion**

In `test_render_row_one_detail_skips_invalid_local_article_paragraph_links`,
update the existing global count assertion because the reader now contributes
one additional valid link to the rendered paragraph 3 anchor:

```python
    assert detail_html.count('href="#local-article-paragraph-3"') == 3
```

Keep the existing assertions that invalid paragraph 0, 2, and 100 anchors are
not emitted.

Expected: FAIL until Task 2 is complete.

## Task 2: Implement Template Reader Helpers

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add a reader excerpt limit**

Near the local article constants/helpers in `templates.py`, add:

```python
LOCAL_ARTICLE_READER_EXCERPT_CHARS = 120
```

- [ ] **Step 2: Add reader item helpers**

Add helpers near `_render_local_article_map()`:

```python
def _render_local_article_reader(article: RowOneLocalArticle) -> str:
    items = _local_article_reader_items(article)
    if not items:
        return ""
    count = len(items)
    meta_en = f"{count} saved {'paragraph' if count == 1 else 'paragraphs'} from {article.source_name}"
    meta_zh = f"来自 {article.source_name} 的 {count} 个保存段落"
    rendered_items = "\n".join(
        _render_local_article_reader_item(
            position=position,
            paragraph_index=paragraph_index,
            excerpt_en=excerpt_en,
            excerpt_zh=excerpt_zh,
        )
        for position, (paragraph_index, excerpt_en, excerpt_zh) in enumerate(items, start=1)
    )
    return f"""      <div id="local-article-reader" class="local-article-reader">
        <h4>
          <span data-lang="en">Saved Text Reader</span>
          <span data-lang="zh">保存正文阅读</span>
        </h4>
        <p class="local-article-reader-meta">
          <span data-lang="en">{_esc(meta_en)}</span>
          <span data-lang="zh">{_esc(meta_zh)}</span>
        </p>
        <ol class="local-article-reader-list" aria-label="Saved text paragraphs">
{rendered_items}
        </ol>
      </div>"""
```

Then add:

```python
def _local_article_reader_items(article: RowOneLocalArticle) -> list[tuple[int, str, str | None]]:
    aligned_zh = article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    items: list[tuple[int, str, str | None]] = []
    for index, paragraph in enumerate(article.paragraphs):
        if not paragraph.strip():
            continue
        excerpt_en = _local_article_reader_excerpt(paragraph)
        excerpt_zh = None
        if aligned_zh:
            zh = aligned_zh[index]
            excerpt_zh = _local_article_reader_excerpt(zh) if zh.strip() else excerpt_en
        items.append((index, excerpt_en, excerpt_zh))
    return items
```

Add:

```python
def _local_article_reader_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_READER_EXCERPT_CHARS,
    )
```

Add:

```python
def _render_local_article_reader_item(
    *,
    position: int,
    paragraph_index: int,
    excerpt_en: str,
    excerpt_zh: str | None,
) -> str:
    href = f"#{_local_article_paragraph_anchor(paragraph_index)}"
    number = f"{position:02d}"
    if excerpt_zh is None:
        excerpt = _esc(excerpt_en)
    else:
        excerpt = (
            f'<span data-lang="en">{_esc(excerpt_en)}</span>'
            f'<span data-lang="zh">{_esc(excerpt_zh)}</span>'
        )
    return f"""          <li>
            <a href="{_esc(href)}">
              <span class="local-article-reader-number">{_esc(number)}</span>
              <span class="local-article-reader-excerpt">{excerpt}</span>
            </a>
          </li>"""
```

- [ ] **Step 3: Wire reader into `_render_local_article()`**

Update `_render_local_article()` to compute the reader once and pass whether it
exists to the map:

```python
    reader = _render_local_article_reader(article)
    article_map = _render_local_article_map(article, include_reader=bool(reader))
```

Place `{reader}` after `{article_map}` and before `{brief}`. Plain local
articles without `brief_sections` or `content_sections` still render the reader,
but continue to omit the structured local article map.

- [ ] **Step 4: Add the reader map chip**

Change the signature:

```python
def _render_local_article_map(article: RowOneLocalArticle, *, include_reader: bool = False) -> str:
```

After the brief link and before content section links, add:

```python
    if include_reader:
        links.append(
            '<a href="#local-article-reader">'
            '<span data-lang="en">Reader</span>'
            '<span data-lang="zh">阅读</span>'
            "</a>"
        )
```

Keep the existing early return so plain articles still do not render the
structured map when they have no `brief_sections` or `content_sections`.

In the existing final body link, change:

```python
'<span data-lang="en">Full saved text</span>'
'<span data-lang="zh">完整保存正文</span>'
```

to:

```python
'<span data-lang="en">Saved text</span>'
'<span data-lang="zh">保存正文</span>'
```

Do not change the `href="#local-article-body"` target.

- [ ] **Step 5: Add restrained CSS**

Inside `row_one_css()`, near the existing `.local-article-*` CSS, add selectors:

```css
.local-article-reader {
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 14px;
  margin: 14px 0 16px;
}

.local-article-reader h4 {
  margin: 0 0 6px;
  font-size: 0.9rem;
}

.local-article-reader-meta {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 0.82rem;
}

.local-article-reader-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.local-article-reader-list a {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  color: inherit;
  text-decoration: none;
}

.local-article-reader-list a:hover {
  color: var(--accent);
}

.local-article-reader-number {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0;
  text-transform: uppercase;
}

.local-article-reader-excerpt {
  min-width: 0;
}
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content tests/test_row_one_render.py::test_render_row_one_detail_plain_local_article_gets_reader_without_map tests/test_row_one_render.py::test_render_row_one_detail_reader_uses_singular_paragraph_meta tests/test_row_one_render.py::test_render_row_one_detail_reader_falls_back_when_aligned_zh_excerpt_is_blank tests/test_row_one_render.py::test_render_row_one_detail_reader_uses_plain_excerpt_when_zh_paragraphs_mismatch tests/test_row_one_render.py::test_render_row_one_detail_reader_skips_blank_escapes_and_truncates -q
```

Expected: PASS after implementation.

- [ ] **Step 6: Extend CSS selector coverage**

In the existing local article CSS selector test in `tests/test_row_one_render.py`,
assert these selectors/text snippets are present in `row_one_css()`:

```python
    assert ".local-article-reader {" in css_text
    assert ".local-article-reader-list {" in css_text
    assert ".local-article-reader-list a {" in css_text
    assert ".local-article-reader-number {" in css_text
    assert ".local-article-reader-excerpt {" in css_text
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_row_one_css_includes_local_article_map_styles -q
```

Expected: PASS after CSS is added.

## Task 3: Update Docs And Docs Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs assertions**

In `tests/test_row_one_docs.py`, add assertions to the existing ROW ONE docs
test or create a focused Stage 310 test:

```python
def test_row_one_docs_describe_saved_article_reader_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")

    expected_phrases = [
        "saved text reader",
        "detail-page saved text reader",
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
    ]
    for phrase in expected_phrases:
        assert phrase in readme
        assert phrase in docs
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_saved_article_reader_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Update README**

In the ROW ONE generated-site/local article section of `README.md`, add a short
paragraph:

```markdown
Stage 310 adds a generated-site saved text reader on ROW ONE detail pages:
saved local paragraphs are listed as numbered in-page reader segments that link
to the existing paragraph anchors before the existing saved text. This is a
detail-page saved text reader only; it does not change `row-one-app/v7`,
does not change `data/edition.json`, uses existing
`data/articles/<story-id>.json` sidecars, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change
detail routes, does not change paragraph anchors, does not change schemas, does
not add source collection, and does not add scoring.
```

- [ ] **Step 3: Update docs/row-one.md**

In the generated files/local article section, add the same boundary statement
adapted to docs style:

```markdown
Stage 310 adds a generated-site saved text reader on story detail pages. ROW ONE
lists saved local paragraphs as numbered reader segments that link to the
existing `#local-article-paragraph-N` anchors before the existing saved text.
This is a detail-page saved text reader only; it does not change
`row-one-app/v7`, does not change `data/edition.json`, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, uses existing
`data/articles/<story-id>.json` sidecars, does not change detail routes, does
not change paragraph anchors, does not change schemas, does not add source
collection, and does not add scoring.
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_saved_article_reader_boundary -q
```

Expected: PASS.

## Task 4: Review, Verification, Build, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-310-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-310-code-review.md`
- Possibly create rereview artifacts if fixes are needed.

- [ ] **Step 1: Run focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q
```

Expected: PASS.

- [ ] **Step 2: Run full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
```

Expected: all PASS. `uv.lock` must remain unmodified.
The lock check intentionally follows `AGENTS.md`, CI, and existing project
templates: `UV_NO_CONFIG=1 uv lock --check`.

- [ ] **Step 3: Rebuild ignored sample site and check status**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected: `ok: true`, `row-one-app/v7`, `row-one-manifest/v1`,
`row-one-runtime/v1`. Do not stage `reports/row-one/site/**`.

- [ ] **Step 4: Request Claude Code code review**

Create a prompt that includes the Stage 310 goal, plan, changed files, and
verification evidence. Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-310-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-310-code-review.md
```

Fix Critical/Important findings and rerun relevant verification.

- [ ] **Step 5: Stage explicitly**

```bash
git add README.md docs/row-one.md \
  docs/superpowers/specs/2026-07-06-stage-310-row-one-saved-article-reader-design.md \
  docs/superpowers/plans/2026-07-06-stage-310-row-one-saved-article-reader-plan.md \
  docs/reviews/claude-code-stage-310-plan-review-prompt.md \
  docs/reviews/claude-code-stage-310-plan-review.md \
  docs/reviews/claude-code-stage-310-code-review-prompt.md \
  docs/reviews/claude-code-stage-310-code-review.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py tests/test_row_one_docs.py
```

If rereview artifacts are created, add them explicitly. Confirm:

```bash
git diff --cached --name-only -- uv.lock reports/row-one/site
git diff --cached --check
```

Expected: no output.

- [ ] **Step 6: Commit and push**

```bash
git commit -m "Stage 310: add row one saved text reader"
git push origin main
```

- [ ] **Step 7: Handoff Summary**

Report:

- repo status;
- commit SHA;
- verified commands;
- uncommitted files;
- ignored generated site status;
- next recommended stage.
