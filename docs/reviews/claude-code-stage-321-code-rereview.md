---

## Stage 321Re-Review — Post-Fix Assessment

### Previous Critical/Important Findings — Resolved

**1. Duplicate deduplication across render/template boundary — RESOLVED.**
`_deduped_editorial_brief_items()` is entirely in `render.py`. The template's `has_body` guard in `_render_editorial_brief()` is a lightweight safety filter, not a body-key dedup. The separation is now correct.

**2. Triple truncation and unclear `_EditorialBriefItem.body` invariant — RESOLVED.**
The builder calls `clean_row_one_text()` on body strings during dedup and stores the result as the item body — cleaned, not truncated. Single truncation happens at render time in `_editorial_brief_body_excerpt()`. The invariant is clear.

**3. Misleading link-filter test — RESOLVED.**
Replaced by three explicit tests: paragraph-fragment accept, content-section-fragment accept, and unknown-fragment reject. The negative assertion that was driven by the cap is gone.

**No Critical issues. No Important issues.**

---

### Minor Issues

**M1 — `_editorial_brief_paragraph_href` anchors to paragraph-1 without verifying `paragraphs[0]` is non-empty.**

```python
# render.py
if not any(paragraph.strip() for paragraph in local_article.paragraphs):
    return None
return f"{detail_href}#local-article-paragraph-1"
```

`any(...)` confirms at least one paragraph is non-empty but does not confirm `paragraphs[0]` is. If `paragraphs[0]` is empty and `paragraphs[2]` is not, the anchor points to an empty element. In practice the first paragraph is rarely empty, but the guard doesn't enforce it. A tighter fix would be:

```python
first = next((p for p in local_article.paragraphs if p.strip()), None)
if first is None:
    return None
idx = local_article.paragraphs.index(first) + 1  # anchor is1-based
return f"{detail_href}#local-article-paragraph-{idx}"
```

Or simply `if local_article.paragraphs and local_article.paragraphs[0].strip()`.

---

**M2 — Emptiness gate inconsistency between builder and template.**

The builder gates items on `_story_localized_text_has_content(body)`, which calls `clean_row_one_text()`. The template re-gates in `_render_editorial_brief()` using `normalize_row_one_paragraph()`. These are different functions (line 5375–5378 of `templates.py` shows `normalize_row_one_paragraph` goes through sentence splitting and additional cleanup on top of `clean_row_one_text`). An item the builder considers non-empty could in theory be silently dropped by the template.

This is defensive-coding in the safe direction, but it contradicts the spec's stated single-dedup-at-builder invariant. Since the builder already guarantees non-empty bodies when items reach the template, the `has_body` re-check in the template could just be removed — or clearly documented as a belt-and-suspenders guard. As-is it's slightly confusing but not a functional regression.

---

**M3 — Fallback test covers presence but not structure.**

`test_render_row_one_site_editorial_brief_falls_back_to_story_text` only checks:

```python
assert 'class="editorial-brief"' in index_html
assert "The Row is today&#x27;s priority signal." in index_html
assert "This signal belongs in Top Stories." in index_html
```

It does not assert the three section labels ("What changed today", "Why it matters", "What to read locally") are present in the no-local-article path, even though the builder always constructs all three items from story fields when no local article is available. The test is sufficient to confirm the section renders, but a follow-up pass could add one label assertion to complete the structural check.

---

### Generated-Site-Only Boundary — Intact

- `_EditorialBrief` / `_EditorialBriefItem` are private `templates.py` types, never serialised.
- `render_index_html()` accepts `editorial_brief: _EditorialBrief | None` — not wired into any JSON builder.
- `test_workflows.py` asserts `'"editorial_brief"' not in generated_contract_payload` and the pre-existing `'"daily_information_layer"' not in generated_contract_payload` assertion is still present.
- Import graph is one-way: `render.py → templates.py`. No reverse import introduced.

### XSS / Link Safety — Clean

- All display strings go through `_esc()` (html.escape) before insertion.
- `_safe_editorial_brief_href()` delegates path validation to `validated_row_one_detail_relative_path()`, which returns `None` for external URLs, `javascript:`, and path traversal. Fragment validation uses two explicit regexes. The composed href is additionally `_esc()`-ed at the call site. No injection vector found.
