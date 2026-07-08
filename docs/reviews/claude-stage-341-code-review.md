**Approved**

**Critical findings:** None.

**Important findings:**

1. `_local_article_body_source_label_localized()` is a brand-new private function (lines 269–274) returning `LocalizedText`. The pre-existing `_local_article_body_source_label(article) -> str` is untouched — zero collision, zero redefinition. Naming and return types are distinct.

2. `_render_local_article_information_panel` early-returns `""` when `_local_article_rendered_paragraph_indices(article)` returns an empty set, so articles with no renderable paragraphs produce no panel at all. Correct guard.

3. `_render_local_article_information_paragraph_links` passes `indices` through `_strict_valid_local_article_paragraph_indices(indices, rendered_indices)` before slicing. The invalid-index test (`[0, 0, 99]` with only 3 paragraphs) confirms deduplication and out-of-range filtering both hold.

4. Every href in the panel is a `#local-article-*` fragment. The test explicitly asserts `'href="http' not in panel` and `'href="../details/' not in panel`. Jump links also use only internal anchors (`#local-article`, `#local-article-reader`, `#local-article-digest`, `#local-article-paragraph-evidence`, `#local-article-content-section-N`, `#local-article-paragraph-N`).

5. All user-controlled strings (source_name, section titles, item labels, body text, ref names/types/labels, dek text) pass through `_esc()`. The XSS test (`<script>` in every user field) verifies no raw `<script>` survives into the panel.

6. Ref deduplication uses a `casefold()` triple-key `(name, type, label)` and caps at `LOCAL_ARTICLE_INFORMATION_MAX_REFS = 6`. Test asserts `<= 6` refs and only one "The Row" entry.

7. No schema, model, render.py, JSON artifact, or contract drift. Workflow tests add negative assertions against `local_article_reading_improvements` and `local-article-reading-improvements.json` in the contract payload and output directory. The `render_local_article_page_html` integration test also asserts those keys are absent from every JSON contract file.

8. Panel is inserted at the correct position in `render_local_article_page_html`: after `<p class="story-source">` and before the `{local_article_section}` block, and the test verifies `information` index< `id="local-article"` index.

**Minor findings:**

1. `_local_article_information_referenced_paragraph_indices` falls back to `sorted(rendered_indices)` when no section-level paragraph indices are valid. This means jump links for paragraphs may show the full rendered set (up to `LOCAL_ARTICLE_INFORMATION_MAX_PARAGRAPH_LINKS = 5`). Behaviour is reasonable but not directly tested by the filtering test — it's covered only indirectly by the jumps-inclusion test. Not a defect, just an observation.

2. `section_count` in the metrics uses `len(article.content_sections)` (total sections), while the card grid only renders up to `LOCAL_ARTICLE_INFORMATION_MAX_SECTIONS = 4`. So the count metric can say "6 organized sections" while only 4 cards appear. Intentional or cosmetic inconsistency — not a bug, but worth noting.

3. `_local_article_information_excerpt` calls `normalize_row_one_paragraph` then `_meta_description`. `section.body.zh` is excerpted even when only `section.body.en.strip()` is checked for truthiness — if `.en` is non-empty but `.zh` is empty the excerpt will be an empty span. Harmless but asymmetric.

**Recommended fixes before commit:** None required. All three minor items are cosmetic or intentional design choices and do not affect correctness, contracts, or test pass/fail state.
