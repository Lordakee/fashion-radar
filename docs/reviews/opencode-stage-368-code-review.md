## Stage 368 Review — Local Article Body Organizer

### Critical
None.

### Important
None.

### Minor / Informational
- **Redundant null-guard** — `saved_article_body_organizer.py` `_section_row` (review-pack lines 924-927): the first check `if title is None and not item_labels and support is None and not paragraphs: return None` is fully subsumed by the immediately following `if not item_labels and support is None and not paragraphs: return None`. Dead branch; harmless but noisy. Drop the first.
- **Theoretical empty-join** — `templates.py` `_render_local_article_body_organizer` (~line 194): `section_rows = "\n".join(...)` could yield a whitespace-only truthy string if every row rendered empty, gating the `sections` wrapper on whitespace. Cannot occur in practice (builder always emits valid `section_href` + content), so non-blocking. Could guard with `section_rows.strip()`.

### Correctness checks (all pass)
- **Escaping**: every user-derived value (`source_name`, `title`, metric labels, item labels, support text, paragraph label/excerpt, hrefs) flows through `_esc` or `_safe_local_article_body_organizer_href`. Render test confirms `People &amp; &lt;Brands&gt;`, `The Row &lt;signal&gt;`, `Escaped &lt;section&gt; support text.` (templates.py:15208+).
- **Anchors**: paragraph chips → `#local-article-paragraph-N`; section rows → `#local-article-content-section-N`. Both validated by regex fullmatch against `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` / `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE`. Anchors resolve to existing targets (segment deck above, saved body below).
- **Counts**: `saved_paragraph_count` = rendered (non-blank) paragraphs; `filed_paragraph_count` accumulates across all sections (added before per-row cap/dedup, so capped-but-filed indices still count as filed); `unfiled_paragraph_count` = rendered − filed (full count, not display-capped); `organized_section_count` = emitted rows. Test `caps_rows_deterministically` + `keeps_capped_section_paragraphs_unfiled` confirm semantics.
- **Generated-site-only boundary**: render test asserts absence on homepage, library index, detail pages; contract-leak test asserts none of the organizer identifiers appear in edition/manifest/runtime JSON; no standalone `.json`/`.html` artifacts created across `tmp_path`, `articles/`, `data/`; `test_stage_368_..._stays_generated_site_only` monkeypatches renderer to `""` and re-runs full workflow test. Thorough.
- **Bilingual fallback**: `_paragraph_view_model` falls back to `excerpt_en` when `paragraphs_zh` misaligned or blank; `_nonblank_localized_text` cross-fills en↔zh; untitled section falls back to `Section N` / `第 N 节`. Covered by `handles_misaligned_zh` and `uses_bilingual_fallback_section_title`.
- **Index validation**: `_strict_valid_paragraph_indices` rejects bool, non-int, out-of-range, and dedupes. Covered by `filters_invalid_indices_and_blank_paragraphs` (True, "0", -1, 99, repeats all rejected).
- **Prior-review-fix consistency**: href sanitization, None-when-empty contract, strict index typing, and no-contract-leak patterns match Stages 365-367. Doc boundary test's stale-phrase sweep is comprehensive.
- **Template order**: segment-deck → organizer → body, verified by `index()` ordering asserts and the `_local_article_information_html` / `_local_article_content_segment_deck_html` helper rebounds.

### Verdict
**APPROVE.** Ship as-is; optionally drop the redundant first null-check in `_section_row`.

Post-review note: the two Minor / Informational cleanup items above were addressed before commit.
