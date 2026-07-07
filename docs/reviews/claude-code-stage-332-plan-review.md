Here is the Stage 332 plan review.

---

## Stage 332 ROW ONE Saved Article Library Content Groups — Plan Review

### 1. Design coherence and goal alignment

**None.**

The design is coherent and tightly scoped to its stated goal. The gap is real: `articles/index.html` already holds the daily saved article library but shows no content-group organization, while the homepage already renders `RowOneSavedArticleContentOrganization` from `content_sections`. Reusing the existing view model is the minimal correct approach. Placement (hero → optional signal index → content organization → source grid) matches reading order and preserves the existing source-grid as the primary browsing surface.

The three discarded alternatives are correctly evaluated. Alternative 3 is the right choice: no new schema, no new sidecar, no new builder, no new extraction.

### 2. Technical feasibility against current code

**None.**

The wiring is straightforward:

- `render_row_one_site()` (`render.py:109`) already builds `saved_article_content_organization` and stores it in a local variable. It already passes `saved_signal_index` into `_write_saved_article_library_page()`. The Task 2 call-site change is a one-line addition.
- `_write_saved_article_library_page()` (`render.py:236`) and `render_saved_article_library_html()` (`templates.py:265`) both have keyword-only parameter lists; adding `saved_article_content_organization` is backward-compatible.
- `_render_saved_article_content_organization()` (`templates.py:4379`) and its four direct descendants (group, card, chips, evidence — lines 4412–4517) currently accept no `href_prefix`. The plan correctly enumerates all five functions and the `_prefixed_saved_article_content_organization_href` insertion points.
- The test helpers `_saved_article_content_organization_section_html` (line 3794), `_signal_briefing_local_article` (line 217), and `_saved_article_library_fixture` (line 183) all exist in `test_row_one_render.py`. Neither new test needs new fixtures or helpers beyond what is already present.

One implementation step the plan correctly flags as conditional but which is **guaranteed to be required**: `RowOneSavedArticleContentOrganization` (the type) is not imported in `render.py`. Only `build_row_one_saved_article_content_organization` is imported (line 32). The new `_write_saved_article_library_page()` signature needs the type for its annotation. Because `render.py` opens with `from __future__ import annotations` this is not a runtime error, but it is a linting error that `ruff check` will catch in Task 5 if omitted. The plan's wording "if `render.py` does not already import `RowOneSavedArticleContentOrganization`" is correct — it does not, so the import must be added.

### 3. Link-prefix approach and route/fragment safety

**None.**

The prefix is applied correctly:

- `_safe_saved_article_content_organization_href()` (`templates.py:4530`) validates that `detail_path` contains `#local-article-content-section-N` (via `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE`), that the path component passes `validated_row_one_detail_relative_path`, and that the path is a `str`. A path like `"details/the-row-signal-1234567890.html#local-article-paragraph-1"` (wrong fragment type) fails the regex and is filtered. This is correct.
- `_safe_saved_article_content_organization_evidence_href()` (`templates.py:4543`) explicitly guards against `isinstance(paragraph_index, bool)`, `paragraph_index < 0`, and invalid paragraph fragments via `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`. The `bad_index_card` in Task 1 Step 2 (`paragraph_indices=(-1, True)`) correctly tests both guards.
- The prefix `"../"` is hardcoded at the one call site (`render_saved_article_library_html`) and applied only after safety validation. It is never passed through validation. `../details/<story>.html#...` is only safe in the article-library page context after the validated canonical `details/...` path is confirmed — the plan states this explicitly, and the implementation plan honours it.
- Homepage call site passes no `href_prefix` argument; since the parameter defaults to `""` the homepage links remain `details/...` unchanged.

### 4. Test adequacy and brittleness

**None.**

The test suite is well-structured across three layers:

**Integration test (Task 1 Step 1):** Drives `render_row_one_site()` end-to-end, reads `articles/index.html` and `index.html`, asserts content-section and evidence-paragraph links are `../details/...` on the library page and `details/...` on the homepage. Asserts ordering (`saved-signal-index` < `saved-article-content-organization` < `saved-article-library-grid`) by string position. Asserts none of the three JSON contracts (`edition.json`, `manifest.json`, `runtime.json`) contain the section key or CSS class, and that `data/saved-article-content-organization.json` does not exist. This covers the generated-site-only boundary completely.

**Direct renderer safety test (Task 1 Step 2):** Calls `render_saved_article_library_html()` directly with a hand-constructed `RowOneSavedArticleContentOrganization` containing five distinct failure cases:
- `javascript:` href — filtered
- traversal (`../secrets.html`) — filtered by `validated_row_one_detail_relative_path`
- wrong fragment type (`#local-article-paragraph-1` instead of `#local-article-content-section-N`) — filtered by the regex
- negative index (`-1`) — filtered by the evidence validator
- boolean index (`True`) — filtered by `isinstance(paragraph_index, bool)` guard

One minor note: `bad_index_card` has `paragraph_indices=(-1, True)`, which is truthy as a two-element tuple. The chips renderer renders a "2 paragraphs" count chip even though neither index produces a valid evidence link. The test does not assert against this chip, which is correct — the chip is harmless display metadata derived from `len(card.paragraph_indices)`, not a safety concern. The test correctly asserts "Bad index card" IS rendered (card title survives) while the bad-index evidence links are absent.

**Docs sentinel (Task 4Step 1):** Follows the Stage 327/328 pattern — flat `assert expected in normalized` rather than a bounded slice. There is no "Stage 333" marker yet, making a slice approach impossible. The flat match is consistent with recent precedent and sufficient.

No test is brittle: all assertions are against stable CSS class names, bilingual labels, and known story IDs from the fixture.

### 5. Critical or Important issues to fix before implementation

**None.**

There are no Critical or Important findings. The design is coherent, the implementation plan maps cleanly to the existing code structure, safety is preserved end-to-end, and the tests are adequate.

One minor item to act on during Task 2Step 2: add `RowOneSavedArticleContentOrganization` to the import from `fashion_radar.row_one.saved_article_content_organization` in `render.py`. The plan correctly flags this; the condition is true so the import must be added. `ruff check` in Task 5 Step 1 will catch it if forgotten.

**Summary — proceed to implementation.**
