**Verdict: Safe to implement**

---

**Critical**

None.

---

**Important**

1. **`_render_saved_article_reading_path` reuses `_safe_saved_article_content_organization_href` and `_prefixed_saved_article_content_organization_href`** — the plan calls these helpers by name but they live in the existing Stage 334 template code. The plan never verifies those helpers accept a `#local-article-content-section-N` fragment (they may currently only accept `#local-article-paragraph-N` evidence anchors). Before Task 2Step 3, confirm both helpers allow content-section fragments or add a dedicated safe-href helper for reading paths.

2. **`_render_saved_article_reading_path_evidence` reconstructs a `RowOneSavedArticleContentOrganizationCard` from step fields and delegates to `_render_saved_article_content_organization_evidence`** — this creates an implicit coupling to the card dataclass constructor. If the card dataclass gains required fields between now and implementation, this will silently fail at runtime, not at test time. Consider either importing the card builder directly or adding a dedicated step-evidence renderer.

3. **`test_saved_article_reading_paths_accepts_any_safe_library_route`** — the test name says "accepts any safe library route" but the two parametrized cases both have at least one *unsafe* route (traversal `../outside.html`) among the three entry paths. The test asserts the step is still rendered because one safe path exists. This is correct behavior per the spec, but the fixture comment and test name should clarify this is a "partial-safe fallback" case, not "any route is accepted." As written it could mislead a future maintainer.

---

**Minor**

1. **`_render_saved_article_reading_path` line length** — the `_render_saved_article_reading_path_step` inner list comprehension is a single very long line. Ruff will flag it; the plan says "Expected: PASS after small syntax/import adjustments" but does not call this out. Fine to fix during implementation, just note it.

2. **CSS `grid-template-columns: repeat(2, ...)` for path grid** — with a cap of 4 paths you can get a single path that renders as a half-width card. Consider `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` for robustness, or explicitly note the2-column layout is intentional for the 2–4 path case.

3. **`test_render_saved_article_library_reading_path_hrefs_match_local_anchor_allowlist`** — the regex `[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}` requires exactly a 10-hex suffix. Confirm the story-id convention in the existing test fixtures matches this exactly; if the suffix length varies, the test would incorrectly pass for some fixtures and fail for others.

4. **`_count_label` helper** — the plan uses it in the path card render but does not define it or confirm it exists. Verify it is already present in `templates.py` from a prior stage.

---

**Required plan changes**

None — the plan is internally consistent with the goal. The Important items above are pre-implementation checks, not structural blockers. No task ordering needs to change.
