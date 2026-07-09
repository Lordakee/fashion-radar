**Stage 371 Plan & Spec Review**

---

## IMPORTANT

**Render-time href validator not implemented in plan.**
Task 4 Step 3 says "Use the Stage 370 href validator shape" but never provides the body of `_safe_daily_local_saved_article_organizer_href`. The spec requires rejecting `N=0`, whitespace, traversal, absolute paths, and protocol URLs at render time. The builder constructs hrefs correctly (`enumerate(..., start=1)`, `index + 1`), but the render-side guard is essential — without it the escaping test for `#local-article-paragraph-0` passes vacuously. Implementer must write this validator from scratch based on the description alone. Recommend adding the function body to Task 4 the way Task 2 provides the full builder.

**`_item_lane_key` silently drops items with unrecognized section keys and reference labels.**
Items whose `section.key` contains neither `"product"` nor `"brand"`/`"people"`, and whose reference labels don't intersect `_PRODUCT_TYPES` or `_PEOPLE_BRAND_TYPES`, are dropped with no fallback. Sections like `"source_signals"`, `"trend_signals"`, or `"market_signals"` with mixed reference types will produce no card in any lane. This may be intentional, but it is undocumented in the spec and untested. Add a test or a spec note clarifying the drop-by-design intent.

---

## MINOR

**TDD gap: aggregate field accuracy untested.**
No test verifies `article_count`, `source_count`, or `reference_count` field values on the returned organizer. The caps test covers `card_count` implicitly but not explicitly. The grouping test asserts `organizer.article_count == 1` — good — but `source_count` and `reference_count` are never asserted directly.

**`source_context` lane uses first paragraph only.**
The spec says this lane explains "where the saved local content came from" using "source-name and body-source oriented cards." The builder's `_source_context_card` always uses the first non-empty paragraph, ignoring content-section bodies with source-oriented references. Low functional impact but diverges from the spec's intent.

**CSS grid hardcodes 4 columns; renders sparse with 1–3 lanes.**
`.daily-local-saved-article-organizer-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }` — with 1 or 2 lanes, empty grid columns appear. Stage 370 may handle this with `auto-fill` or a JS-driven class. If the pattern is consistent with Stage 370, no change needed; if not, consider `repeat(auto-fill, minmax(240px, 1fr))`.

**Article title not localized.**
`_article_title` returns `LocalizedText(en=title, zh=title)` using the English headline for both language slots. Cards always show the English title in the zh view. Acceptable if consistent with prior stages, but worth noting for future i18n consistency.

**Lane cap test covers `products` only.**
`test_build_daily_local_saved_article_organizer_caps_and_dedupes` verifies the cap on the `products` lane but not `people_brands`, `read_first`, or `source_context`. A single overloaded article with many brief sections would not be caught by the existing cap test.

---

## PASSES

- Feasibility: builder uses only existing models and helpers; no new data sources, LLM calls, or external I/O.
- Scope: boundary paragraph matches docs boundary; artifact and contract denylists are comprehensive.
- Generated-site-only boundary: no new JSON, no new HTML routes, no article/detail page mutations; wrapper guard test is sound.
- App contract safety: workflow guard covers all naming variants including zh string.
- Content organization: excerpt-first cards with reference chips and editorial lane grouping clearly advance content depth over link-only navigation.
- href safety in builder: `_safe_article_page_href` correctly rejects traversal, absolute paths, mismatched story IDs, and whitespace.
- TDD structure: RED→GREEN flow with focused lint gates is correctly ordered; docs and workflow guard tests are well-specified.
