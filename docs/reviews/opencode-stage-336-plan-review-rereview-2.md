I'll review Stage 336 by inspecting the design/plan docs and the relevant source files in parallel.
Let me read the remaining key files: content organization, reading paths, the test files, and docs.
Now let me read the test files, docs test, and the relevant docs sections plus the reading paths rendering in templates.
Let me verify the README and row-one.md actually contain the Stage 335 boundary paragraph, and check how reading paths are rendered in templates (for the `../` prefix convention).
Let me verify whether the render test helpers referenced by the plan already exist, and check the reading-paths renderer for the truncation/prefix conventions the plan reuses.
Let me read the Stage 335 render test to see how it builds fixtures, since the plan references reusing Stage 335 helpers.
Let me check the `_signal_briefing_local_article` fixture to confirm it has the sections the theme digest needs, and verify the existing Stage 335 ordering test won't break.
I now have enough to complete the review. Let me verify one final detail — whether the existing Stage 335 ordering test would still pass after inserting the theme digest between hero and signal-index.
## Stage 336 Plan Review

**Verdict: Safe to implement**

### Critical issues
None. The plan mirrors the proven Stage 335 (reading-paths) pattern exactly: same builder structure, same safe-route helpers (`validated_row_one_detail_relative_path`, content-section fragment validation, library detail-path intersection), same render placement strategy, same contract-isolation approach. No app/runtime/manifest/schema/JSON changes; no crawling/extraction/ranking/LLM/connector/scheduling/deployment/compliance behavior.

### Important issues
1. **Task 2 render-test fixture must include a `takeaways` section.** The test asserts `assert "Read First" in html` on `articles/index.html` (plan line 297). The existing `_signal_briefing_local_article()` fixture (`tests/test_row_one_render.py:227`) only has `entities` + `product_signals` sections — **no `takeaways`** — so "Read First" never appears on the library page with that fixture (confirmed: the Stage 335 test at line 3079 asserts "People & Brands"/"Products" but deliberately not "Read First"). The plan's prose ("covering at least takeaways and product_signals", line 281) is correct, but the hedge "unless equivalent Stage 335 helpers already exist" (line 278) is misleading — no equivalent helper exists. **Recommendation:** state explicitly that a *new* fixture with a `takeaways` content section is required; do not reuse `_signal_briefing_local_article()`.

### Minor issues
1. **Third copy of safety helpers.** `_safe_content_section_href` / `_detail_path_key` / `_library_detail_paths` already exist duplicated in `saved_article_reading_paths.py:104-173` (noted in the Stage 335 opencode review). Stage 336 will add a third copy (can't import privates from the reading-paths module; can't import from `templates.py` — circular). Acceptable, but the plan could note the option of extracting the fragment regex into `detail_routes.py` to retire the debt.
2. **Task 1 builder tests reference undefined helpers** `_library_with_safe_story(...)` and `_organization_card(...)` (plan lines 111, 156). The plan says only "patterned after Stage 335 tests." Intent is clear; implementer must define them. Non-blocking.
3. **Task 3 escape test uses `key="brand_momentum"`** (plan line 401), which is not one of the four real theme keys. Harmless at the render layer (renderer doesn't validate keys), just cosmetically odd.

### Verification notes
- Existing Stage 335 ordering test (`test_row_one_render.py:3113-3119`) asserts `hero < signal_index < reading_paths < content_org < grid` — inserting `theme_digest` between hero and signal_index preserves all pairwise orderings, so it stays green. ✓
- Existing Stage 335 docs sentinel (`README.md:256`, `docs/row-one.md:471`) is present and matches the slice anchor the new docs test depends on (`stage 335 adds generated-site only saved article reading paths`). ✓
- The proposed docs paragraph and its docs-test `expected` string are mutually consistent after normalization. ✓
- `_safe_saved_article_content_organization_href` (`templates.py:5059`) and `_prefixed_saved_article_content_organization_href` (`templates.py:5073`) exist and accept content-section fragments; `_local_article_digest_excerpt` (used at `templates.py:4457`) is the existing lead-truncation helper to reuse. ✓
- No circular import: `saved_article_theme_digest.py` imports only from `detail_routes`, `models`, `saved_article_content_organization`, `saved_article_library` — same dependency shape as `saved_article_reading_paths.py`. ✓

### Specific plan changes required before implementation
None strictly required. The one recommended clarification (Important #1): add a sentence to Task 2 Step 1 stating the render-test fixture must contain a `takeaways` content section and that `_signal_briefing_local_article()` cannot be reused as-is for the `"Read First"` assertion.
