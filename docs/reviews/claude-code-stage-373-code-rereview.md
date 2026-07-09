No Critical or Important issues remain.

The implementation is correct across all reviewed surfaces:

**Builder (`local_article_body_section_markers.py`)**
- Story/article ID guard, rendered-index validation, `used_paragraph_indices` dedup, sort-then-cap order, and fallback title are all spec-compliant.
- `_strict_valid_paragraph_indices` correctly rejects bools before the `isinstance(int)` check (Python bools are ints), negative/out-of-range indices, and within-item duplicates.
- `_support_text` returning `None` (no text anywhere) correctly causes the whole section to be skipped rather than emitting an empty marker.
- `_paragraph_support` bounds-checks `paragraph_index` before array access, preventing IndexError on short articles.

**Renderer interaction (`templates.py`)**
- `markers_by_index` is gated on `include_body_filing_cues=True`, which is the only caller path that also passes markers. Functionally correct; the coupling is intentional per spec ("coexist by surface").
- The suppress condition `if include_body_filing_cues and index not in markers_by_index` is correct: marker paragraphs lose the inline cue, non-marker paragraphs keep it.
- `rendered.extend(markers_by_index.get(index, []))` before the `<p>` append is the right insertion order.
- `_safe_local_article_body_section_marker_href` reuses the existing `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` / `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` as required, and the `href != href.strip()` + `any(isspace)` pair covers all whitespace forms including internal.

**Updated Stage 366 body filing cue tests**
- The count change from 3 to 2 filing cues is correct: paragraph 1 now carries a section marker, suppressing its cue. Paragraphs 2 and 3 still have cues. The per-paragraph assertions (`not in paragraph_one_html`, `in paragraph_two_html`, `in paragraph_three_html`) precisely document the suppression boundary.
- The `href="#local-article-content-section-1"` count in `filing_links_html` dropping from 2 to 1 is correct: that link now lives in the marker for paragraph 1, not in a filing cue, so the filing-cue-link regex no longer captures it. The link still exists in the page (confirmed by the marker render tests).
- `test_render_row_one_site_writes_body_filing_cues_only_on_local_article_pages` correctly pivots from asserting `Filed under` (which is now a marker paragraph) to asserting `Unfiled saved paragraph` (which is still a filing cue paragraph) plus the marker class.

**Escape and href filter tests**
- `javascript:alert(1)#local-article-content-section-1`: rejected because it does not start with `#`.
- `../secret.html#local-article-paragraph-1`: rejected because it does not start with `#`.
- `#local-article-paragraph-0`: rejected by existing paragraph fragment regex (`N >= 1`).
- `#local-article-content-section-01`: rejected by existing section fragment regex because it uses a leading-zero numeral.
