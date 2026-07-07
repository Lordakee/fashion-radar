## Stage 336 Plan Review

**Verdict: Needs revision** (two localized plan defects; no architectural blockers)

### Critical issues
None. The stage stays generated-site-only, reuses existing validated route helpers, adds no JSON/schema/contract output, and adds no collection/extraction/LLM/connector/scheduling/deployment/compliance behavior — consistent with Stages 326–335 and the AGENTS.md scope boundaries. Source counts are descriptive (not ranking/demand-proof); theme order follows organization-group order, not heat.

### Important issues

1. **`reading_paths` parameter is accepted but never used.** The spec (design §"Chosen Approach"/"Data Flow") lists `RowOneSavedArticleReadingPaths` as a builder input and `render.py:126` builds it, but the plan's Task 1 Step 3 algorithm only consumes `library` (allowed paths) and `organization` (cards). The safety/dedupe tests pass `None` for it and still expect full behavior. Either drop the parameter (cleanest — organization cards already carry lead/references/detail_path/section info) and update the data-flow + first test, or specify how reading-path steps contribute items. As written, a reviewer will flag dead coupling.

2. **Task 3 Step 1 test references helpers that don't exist in `tests/test_row_one_render.py`.** The plan's `test_render_saved_article_library_html_escapes_and_truncates_theme_digest` calls `_story(...)`, `_edition(_story(...))`, and `_saved_article_library_for_story(...)` — but that file defines `_edition()` with **no args** (`test_row_one_render.py:85`), `_edition_with_stories(*stories)` (`:183`), and `_saved_article_library_fixture()` (**no args**, `:189`). There is no `_story` or `_saved_article_library_for_story` there. The test will error at collection/run, breaking the TDD "verify failure → verify pass" loop. Rewrite to `_edition()` + `_saved_article_library_fixture()` (the digest detail_path need not match the fixture story — the renderer validates syntax only), or explicitly instruct creating the helpers.

### Minor issues

- **Theme title/dek table not pinned in the algorithm.** The render test asserts `"Brand Momentum"` and `"Product Heat"`; the design names all four ("Brand Momentum, Product Heat, People / Designers, Source Structure / Market Context") but Task 1 Step 3 only gives the *key* mapping. Add the bilingual title/dek table to the builder spec so the implementer doesn't infer from tests. (Note: `_signal_briefing_local_article` lacks a `takeaways` section, so the new `_row_one_edition_with_local_article_sections` helper *is* genuinely needed — that part of the plan is correct.)
- **Caps not directly exercised.** The cap test collapses to 1 via dedupe before the 3-item cap bites; add a case with ≥4 distinct leads/paths to actually verify `MAX … 3 items per theme` and the 4-theme cap.
- **Make safety-helper reuse explicit.** Say whether to import `_safe_content_section_href`/`_detail_path_key`/`_library_detail_paths` from `saved_article_reading_paths.py` (promote to a shared module if the leading underscore bothers you) or re-implement, to avoid duplicating/diverging the content-section fragment guard. On the render side, mandate reuse of `_safe_saved_article_content_organization_href` + `_prefixed_saved_article_content_organization_href` (`templates.py:5059`, `:5073`) — these already accept exactly `local-article-content-section-N`.

### Specific plan changes required before implementation
1. Resolve issue 1: drop `reading_paths` from `build_row_one_saved_article_theme_digest(...)` (and the data-flow/first-test), or define its contribution.
2. Resolve issue 2: rewrite the Task 3 Step 1 test to use `_edition()` + `_saved_article_library_fixture()` (or explicitly add the new helpers to the plan's file list).

Both are small edits; once applied the plan is safe to implement.
