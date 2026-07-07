## Verdict: Ready

Stage 336 implementation is correct, safe, and respects all contract boundaries. No critical or important issues.

**Verification performed (all green):**
- Full suite: 2264 passed
- Builder unit tests: 5/5 passed (including unsafe-path rejection, dedupe, caps, source-union counting)
- Render + CSS + contract tests passed
- `ruff check` + `ruff format --check` clean on all 6 touched files
- Docs boundary test passes; both `README.md:256` and `docs/row-one.md:471` carry the Stage 336 paragraph, correctly ordered above Stage 335

**Boundary compliance (verified by tests, not just inspection):**
- No JSON contract leakage — `edition.json`/`manifest.json`/`runtime.json` scanned for `theme_digest`/`saved-article-theme-digest`/local lead text; none present
- No `data/saved-article-theme-digest.json` generated
- No outbound article URLs in the digest section (asserted in `test_render_row_one_site...`)
- No app/runtime/manifest/schema changes
- Render order: hero → theme-digest → signal-index → reading-paths → content-organization → grid (asserted by index comparison)

**Safety is sound:**
- Builder intersects org-card detail paths against the library's allowed set (`_library_detail_paths`), re-validates fragments via `validated_row_one_detail_relative_path`, rejects traversal/wrong-fragment/unmatched paths
- Dedupe key `(theme_key, detail_path, lead.en, lead.zh)`; caps 4 themes / 3 items; `source_count` is the global union, not the per-theme sum (explicitly tested in `test_..._counts_source_union`)
- Template re-validates hrefs (defense in depth) and escapes all dynamic text via `_esc`; leads truncated via existing `_local_article_digest_excerpt`
- Optional paragraph evidence derived only from validated `paragraph_indices`, rendered through the shared `_render_saved_article_content_organization_evidence` helper

**Minor issues (non-blocking, optional polish):**
1. `templates.py:4644` and `:4625-4628` — when evidence links exist, two sibling `<div class="saved-article-theme-digest-actions">` elements are emitted (one for the "Open theme section" CTA, one wrapping evidence). Valid HTML, but a distinct class for the evidence wrapper would read more cleanly.
2. Lead truncation uses `LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS = 160`, not the plan's "~180". This is the right call — it keeps the digest visually consistent with the Stage 334 excerpts that share the helper.
3. Plan named new test helpers `_row_one_edition_with_local_article_sections`/`_local_articles_with_theme_digest_signals`; implementation reuses the existing `_edition()` + `_theme_digest_local_article()` fixtures instead. Benign deviation — the existing fixtures already supply `takeaways` + `product_signals` sections.

**Required fixes before commit:** none.
