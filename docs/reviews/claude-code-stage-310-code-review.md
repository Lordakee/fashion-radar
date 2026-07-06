## Stage 310 Code Review

---

### Critical

None.

---

### Important

None.

---

### Minor

**1. `test_render_row_one_detail_includes_local_article_content` — fragile `reader_html` slice boundary**
`tests/test_row_one_render.py:511–515`

```python
reader_html = detail_html[
    detail_html.index('id="local-article-reader"') : detail_html.index(
        'class="local-article-brief"'
    )
]
```

The end boundary relies on `class="local-article-brief"` being present, which holds for this specific fixture (it has `brief_sections`). If the fixture is ever refactored to remove brief sections without updating the slice, `str.index` will raise and the test fails with a `ValueError` instead of an assertion. The other reader tests correctly use `id="local-article-body"` as the end boundary (`test_render_row_one_detail_reader_skips_blank_escapes_and_truncates:914`), which is always present. No current correctness problem; low future-maintenance risk.

---

**2. `_local_article_reader_items` — `excerpt_zh` type when blank zh falls back**
`src/fashion_radar/row_one/templates.py:2668–2671`

```python
if aligned_zh:
    zh = aligned_zh[index]
    excerpt_zh = _local_article_reader_excerpt(zh) if zh.strip() else excerpt_en
```

When zh is blank, `excerpt_zh` is set to `excerpt_en` (a `str`), so `_render_local_article_reader_item` takes the bilingual path and produces:

```html
<span data-lang="en">Second aligned paragraph…</span>
<span data-lang="zh">Second aligned paragraph…</span>
```

Both language slots render the same English text. This is the specified fallback behaviour and is tested in `test_render_row_one_detail_reader_falls_back_when_aligned_zh_excerpt_is_blank`. Worth noting in a comment near the assignment that this is intentional, since the bilingual path with identical text can look surprising.

---

**3. `_render_local_article_map` silent drop when `include_reader=True` but no structure**
`src/fashion_radar/row_one/templates.py:2711`

```python
if not article.brief_sections and not article.content_sections:
    return ""
```

The early return fires regardless of `include_reader`, so a plain article (no brief or content sections) gets no map even if `include_reader=True`. The caller (`_render_local_article`) passes `include_reader=bool(reader)`, but the Reader chip is silently dropped in this code path. This is correct by design (plain articles intentionally get a reader but no map), and `test_render_row_one_detail_plain_local_article_gets_reader_without_map` pins it. However, the early return predates the `include_reader` parameter, and the parameter name now suggests it will always be honoured. A brief comment like `# Map is only shown for structured articles; plain-only reader is rendered without a map` at the early-return site would clarify the intent.

---

### Verdict

No Critical or Important findings. The implementation is correct across all reviewed axes:

- Reader renders from nonblank paragraphs; blank paragraphs skipped; blank aligned zh excerpt falls back to EN; misaligned zh uses plain monolingual excerpts — all verified in code and tests.
- Reader chip appears in the correct map order (Brief → Reader → content sections → Saved text) for every article shape tested.
- Body chip wording is `Saved text` / `保存正文` as required (`templates.py:2737–2741`).
- Excerpts are escaped via `_esc()` and truncated to 120 chars via `_meta_description`.
- Reader links use `#local-article-paragraph-{index+1}` — the same anchor formula as the body paragraphs.
- `data/edition.json` contains no reader content; contract versions `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1` are unchanged.
- No model, schema, or sidecar-field changes.
- Documentation wording uses "saved text reader" / "detail-page saved text reader" throughout; no wording implying full republication.
- Docs boundary test (`test_row_one_docs_describe_saved_article_reader_boundary`) pins all required contract-stability phrases in both README and `docs/row-one.md`.

**Approved to commit.**
