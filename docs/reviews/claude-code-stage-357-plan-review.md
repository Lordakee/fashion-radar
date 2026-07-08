Here is the plan review.

---

## Stage 357 Plan Review

### 1. Product fit

Good. The digest answers a real editorial question — across today's saved local articles, what patterns recur in signals — without being a navigation surface or a link list. Aggregating existing Stage 356 data into compact Why It Matters / Brands / Products / People / Themes groups is a genuine organizing layer that belongs on the homepage and not on article pages. Fits the product goal.

### 2. Non-prohibited behaviors

Clean. The non-goals list in the design is explicit and complete. The builder calls `build_row_one_saved_article_key_signals(...)` on in-memory inputs already available in `render_row_one_site(...)`, performs deduplication and grouping entirely in memory, and passes a view model to the template. No new JSON artifacts, no route families, no schema changes, no fetching, no LLM, no scheduling, no app-contract mutations. The workflow guard additions in Task 4 Step 3 will enforce this boundary testably.

### 3. Scope

Non-duplicative on all three axes:

- **Stage 356** produces per-article key signals on `articles/<story-id>.html`. Stage 357 aggregates across articles on `index.html` — different page, different unit of analysis.
- **Daily Edit / Daily Local Intelligence** (homepage) present source-level or section-level signals per story. Stage 357 presents cross-article signal patterns (recurring brands, themes, why-it-matters) — genuinely orthogonal.
- **Saved Article Briefs** surfaces per-article leads and references. **Saved Article Content Organization** groups articles by content section type. Stage 357 inverts that: it groups signals across articles. No overlap.

### 4. Render ordering

Technically sound. Looking at `templates.py:346-347`, the current homepage template string is:

```
{saved_article_briefs_section}
{saved_article_content_organization_section}
```

Inserting `{daily_local_key_signals_digest_section}` between those two lines is straightforward and consistent with how every other optional section is handled in `render_index_html`. The `render_row_one_site(...)` call at `render.py:184-196` follows the same build-then-pass pattern used by Saved Article Briefs and Saved Article Content Organization. No integration ordering risk.

### 5. Href validation and dedupe/count rules

The test cases are correct and complete — invalid prefixes, unsafe story IDs, bad anchor patterns, paragraph-0 rejection (Stage 356 uses 1-based paragraph hrefs: `index + 1`), and count-before-cap separation. One concrete correction is needed:

---

###⚠️ Concrete correction required before implementation

**The builder must explicitly reconstruct full-path hrefs from Stage 356's fragment-only hrefs.**

Stage 356 emits evidence hrefs as fragment-only strings relative to the article page:

- `_paragraph()` → `href = f"#local-article-paragraph-{index + 1}"`
- `_themes_group()` → `href = f"#local-article-content-section-{section_position}"`

These pass through `RowOneSavedArticleKeySignalEvidence.href` and `RowOneSavedArticleKeySignalTheme.href` as `#...` strings. If the Stage 357 builder passes them through to the renderer unchanged, the renderer's revalidation will correctly reject them (they don't match the `articles/<safe-story-id>.html#...` pattern), silently dropping all evidence and theme links.

**The plan must add an explicit builder responsibility** in Task 1 Step 2:

> When consuming Stage 356 evidence and theme hrefs, the builder must prepend `articles/<safe-story-id>.html` to any fragment-only href (`#local-article-...`) to produce a full site-root-relative path before storing it in the digest view model. Do not pass Stage 356 fragment-only hrefs to the renderer unmodified.

The test added in Task 1 Step 1 should explicitly cover this: a Stage 356 theme href `#local-article-content-section-2` from story `foo-bar` must appear in the digest as `articles/foo-bar.html#local-article-content-section-2`, not as `#local-article-content-section-2`.

Without this fix, href revalidation in the renderer silently passes with no links for evidence/themes, which would only surface as a visual regression rather than a test failure.

---

### 6. Other observations (no blocking changes needed)

- **Cap constants**: The plan defers specific cap values to implementation, which is fine given the existing `MAX_*` constant pattern. The implementer should define named constants in `daily_local_key_signals_digest.py` rather than inline literals.
- **Task 1 Step 1test gap**: Explicitly add a test case that `#local-article-paragraph-1` (fragment-only) is *not* accepted by the renderer — this makes the reconstruction requirement testable independently of the builder.
- **Task 5 ordering**: Plan review is Step 1 of Task 5, after implementation steps. The plan review is being executed now (pre-implementation) which is the correct sequence even if the task numbering implies otherwise. No change needed.

### Summary

The plan is well-scoped, technically sound, and enforces the right boundaries. One concrete fix is required: add an explicit statement in Task 1 Step 2 that the builder reconstructs full `articles/<safe-story-id>.html#fragment` hrefs from Stage 356's fragment-only hrefs, and add a corresponding test case. Everything else is ready for implementation.
