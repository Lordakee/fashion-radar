Based on a thorough read of the Stage 342 implementation, here is the severity-labeled review.

---

## Stage 342 Code Review — Saved Paragraph Context Cues

### R1 — Correctness: Anchors, Bilingual, Information Panel

**Paragraph anchors** (`id="local-article-paragraph-N"`): Preserved. `_local_article_paragraph_anchor(index)` returns `local-article-paragraph-{index+1}` and is applied as `id=` on the `<p>` tag in both the bilingual path and the plain fallback. Stage 342 inserts context cues *before* the paragraph text inside the same `<p>` — the anchor stays on the tag. ✅

**Content-section anchors** (`#local-article-content-section-N`,1-based): `_local_article_content_section_anchor(position)` called with `enumerate(..., start=1)` throughout. Context cues link to these anchors. ✅

**Bilingual handling**: The bilingual path (`len(paragraphs_zh) == len(paragraphs)`) now calls `_render_local_article_paragraph_context` per paragraph. The **plain fallback path** (lines 8645–8652) is untouched — no context cues are injected inline, and anchor IDs continue to emit as before. Both the inline paragraph context and the information panel excerpt handle misaligned `paragraphs_zh` with the correct `excerpt_zh = excerpt_en` fallback. ✅

**Information panel**: The new context-cues section is placed between the jump-nav and the sections grid. Ordering and aria labeling are clean. ✅

---

### R2 — Test Sufficiency

The 7 new render tests cover the meaningful surface well:

| Test | What it covers |
|---|---|
| `test_render_local_article_page_labels_saved_paragraphs_with_paragraph_context_cues` | Inline cues appear on local article page |
| `test_render_local_article_information_panel_shows_saved_paragraph_context_cues` | Panel cues + unreferenced paragraph exclusion |
| `test_render_row_one_detail_labels_saved_paragraphs_with_paragraph_context_cues` | Inline cues propagate to detail page |
| `test_render_local_article_paragraph_context_filters_invalid_duplicate_indices` | Bool `True`, dupes, negative, out-of-range all rejected |
| `test_render_local_article_paragraph_context_escapes_and_caps_labels` | `<N>` escaping; cap of 4 enforced |
| `test_render_row_one_site_local_article_page_paragraph_context_cues_are_html_only` | Contract files clean; no new `.json` artifact |
| `test_row_one_css_includes_local_article_paragraph_context_styles` | Four required CSS selectors present |

The boundary doc test and `test_workflows.py` lines 527–530 close the contract-safety loop. Coverage is sufficient.

---

### R3 — Contract Safety and Generated-Site-Only

`_local_article_paragraph_contexts` reads only `article.content_sections[*].items[*].paragraph_indices` — no new data fields. Context cues appear only in generated HTML. The site-render test verifies `edition.json`, `manifest.json`, and `runtime.json` are all free of `saved_paragraph_context_cues` / `paragraph_context_cues`, and confirms `data/saved-paragraph-context-cues.json` is not created. ✅

---

### R4 — Issues

**LOW (non-blocking) — Dead field on `_LocalArticleParagraphContextCue.excerpt`**

`_local_article_paragraph_contexts` populates `excerpt` via `_local_article_paragraph_context_excerpt`. However, neither render function consumes it: `_render_local_article_paragraph_context` (inline cue) only uses `entry.label`; `_render_local_article_information_context_cues` (panel) re-derives the excerpt directly from `article.paragraphs[paragraph_index]` at lines 7517–7523. The field is computed but never read.

This is not a correctness issue — the panel renders the correct excerpt — but the dataclass carries a redundant field and redundant computation. Worth noting for a future cleanup pass, not a blocker.

No other issues found. Bool/int coercion guard (`not isinstance(index, int) or isinstance(index, bool)`) is correct. `_esc()` coverage is complete across labels, excerpts, hrefs, and paragraph text. Dedupe key is correctly 5-tuple (section anchor + casefold label pair + casefold item label pair). Cap of 4 cues per paragraph and 5 paragraph links in the panel are consistent with the design.

---

**✅ Stage 342 is approved for commit and push.**
