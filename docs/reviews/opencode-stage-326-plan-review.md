### Critical

None.

The plan is technically feasible with the existing render pipeline. The builder/page/template split mirrors `saved_article_coverage.py` / `saved_article_briefs.py` / `saved_article_content_organization.py` exactly (private frozen dataclasses, `build_*()` taking `edition` + `local_articles_by_story_id`, reusing `safe_local_article_story_id` and `is_safe_row_one_detail_path`, no disk reads). The render wiring mirrors the existing `saved_article_coverage` flow into `render_index_html()`. Path safety is sound: the dataclass stores `details/<id>.html#fragment` validated form, the homepage uses it directly via the existing `safe_row_one_detail_fragment_href` pattern, and the library page prepends a fixed `../`. Adding `"articles"` to `GENERATED_CHILDREN` preserves the marker guard because `clean_row_one_site_children` uses `any(child.exists() ...)` and `rmtree` for directories — `articles/` behaves identically to `details/`, `assets/`, `data/`. The workflow boundary test pattern (deny Stage 326 keys in `edition`/`manifest`/`runtime` JSON) matches the existing Stage 312–324 contract-drift assertions.

### Important

1. **Generated Files docs inventory drift.** `docs/row-one.md:301` "Generated Files" section enumerates the cleaned-up generated children (`index.html`, `details/`, `assets/row-one.css`, `assets/row-one.js`, `data/edition.json`, `data/runtime.json`, `data/local-intelligence.json`, `.row-one-site` marker). Stage 326 adds `articles/` to `GENERATED_CHILDREN`, which `latest_only=True` will now `rmtree`, but the plan only adds a Stage 326 boundary note and does not update the "Generated Files" inventory. The existing `test_row_one_docs_describe_generated_files_and_cleanup_boundary` will not fail (it only asserts presence), but the inventory is now incomplete and users reading the cleanup docs will not see `articles/index.html` listed as a removed generated child. Fix: update the "Generated Files" section to list `articles/index.html` (conditionally, like `data/local-intelligence.json`), and add a docs-test assertion for `` `articles/` `` or `` `articles/index.html` `` in that section.

### Minor

1. **CSS presence test missing.** Existing stages ship `test_row_one_css_includes_saved_article_coverage_styles` and `test_row_one_css_includes_saved_article_briefs_styles` (tests/test_row_one_render.py:5100, 5115). The spec lists 13 `.saved-article-library-*` selectors but Task 2 adds no equivalent CSS assertion; without it the selectors could be omitted and only the HTML tests would notice. Add `test_row_one_css_includes_saved_article_library_styles`.

2. **Per-group entry cap (8) is untested.** The caps test uses 12 distinct `source_name` values, so every group has exactly one entry; `MAX ... entries per source group == 8` is never exercised. Add a case where ≥9 stories share one source.

3. **Paragraph anchor 1-indexing convention is implicit.** The dataclass constant `LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph"` and the `paragraph_indices=[0, 1] → #local-article-paragraph-1` test encode the existing `paragraph_index + 1` convention used in `saved_article_content_organization._safe_saved_article_content_organization_evidence_href`, but neither spec nor plan states it. Worth a one-line note to keep the builder aligned with the existing fragment regex `local-article-paragraph-[1-9][0-9]*$`.

4. **Invalid paragraph-index filtering is untested at the builder level.** Spec requires rejecting booleans, negatives, and out-of-range indices against nonblank paragraphs; the filter test only covers whitespace-only paragraphs and unsafe detail paths. Mirror the negative/non-int/out-of-range case from `saved_article_content_organization` tests.

5. **`organized_section_count` semantics ambiguous.** Spec says "non-empty content sections" but `saved_article_coverage` uses `len(article.content_sections)` (all sections). The builder test has one section per article so both interpretations pass. State whether to count all `content_sections` or only sections with usable items, and align with or explicitly diverge from the coverage module.

6. **Homepage insertion order not restated in Task 2 Step 3.** Spec says "after saved article coverage and before saved article briefs"; the plan's render-integration bullets don't repeat the position, so implementers must cross-reference the spec. Minor clarity.

7. **`articles/` vs `data/articles/` naming overlap.** No functional conflict (different paths), but the near-identical names could confuse maintainers; a one-line comment in `render.py` or a distinct directory name (`library/`) would help. Not a blocker.

### Assessment

Implementation may proceed after addressing the Important finding: update the "Generated Files" section of `docs/row-one.md` (and its docs test) so `articles/index.html`/`articles/` is listed as a generated child that `latest_only=True` removes. The Minor items are polish and should be picked up during TDD (CSS test, per-group cap test, invalid-index test, anchor-indexing note, `organized_section_count` disambiguation); none block the stage. The plan correctly stays in-memory, reuses the existing safe-route helpers, does not touch `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, or JSON artifacts, and does not duplicate source collection, fetching, scoring, LLM, connector, scheduling, deployment, or compliance-review behavior.
