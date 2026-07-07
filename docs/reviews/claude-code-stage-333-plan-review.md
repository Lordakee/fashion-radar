Here is my review of the Stage 333 design and plan.

---

## Stage 333 Plan Review — ROW ONE Saved Article Library Text-Source Map

### 1. Design Coherence and Scope

The design is coherent and correctly scoped. It extends the existing `RowOneSavedArticleLibrary` view-model dataclass (an in-memory, HTML-only object) with a new `body_source` string field on each entry and three aggregate count fields on the library. `RowOneLocalArticle.body_source` already exists in `models.py` as `RowOneLocalArticleBodySource = Literal["extracted", "summary_fallback", "skipped"]` (line 32) and is already populated by Stage 331. No new field, schema, JSON artifact, or sidecar contract is needed.

The boundary list in the design matches the objective and the existing constraint pattern established by Stages 326–332. The decision not to expose `reason` on library cards is sound: detail pages already show it, and repeating it would make the card feel like a diagnostic rather than a reading index.

**Finding: None.**

---

### 2. Technical Feasibility Against Stage 332 Code

The plan is feasible. All dependencies are already in place:

- `RowOneLocalArticle.body_source` defaults to `"extracted"` (models.py:147) — the builder can propagate it trivially.
- `RowOneSavedArticleLibraryEntry` is a `@dataclass(frozen=True)` — adding a required `body_source` field is straightforward.
- `RowOneSavedArticleLibrary` is also a frozen dataclass — adding the three count fields is straightforward.
- `_count_label()` (templates.py:4748) and `_render_saved_article_library_metric()` (templates.py:3924) already exist and can be reused directly for the new metrics.
- `_render_saved_article_library_card()` (templates.py:3957) already has a `<ul class="saved-article-library-card-counts">` list — the chip appends cleanly to it.
- `_local_article_body_source_label()` already exists for detail pages (templates.py:5592). The plan adds a parallel helper for the library context. The slight difference (takes `str` not `RowOneLocalArticle`, omits the `article.skipped` fallback) is acceptable because the library only has `body_source` as a string and `body_source` is the canonical signal post-Stage-331.

One workflow concern worth flagging: Task 1Step 2 adds `body_source: RowOneLocalArticleBodySource` to `RowOneSavedArticleLibraryEntry` **without a default**. This is a required field, so the existing `_saved_article_library_fixture()` in `test_row_one_render.py` (line 184) will raise a `TypeError` the moment the implementation change lands — before the fixture is updated in Task 2 Step 1. The plan doesn't mention these transient regressions, so a developer running the full test suite after Task 1 Step 2 will see many unexpected failures. This won't prevent correct final state, but an implementer should be aware that Task 1 Step 2 intentionally breaks existing tests that Task 2 Step 1 then fixes.

**Finding: Important.** The plan should note that Task 1 Step 2's dataclass change will produce transient regressions in `test_row_one_render.py` until Task 2 Step 1 updates `_saved_article_library_fixture()`. No code change required — just add a warning comment in the plan step so the developer doesn't investigate phantom failures.

---

### 3. Count Semantics Correctness

The count semantics are correct. The plan sums over `entries` — the flat list built after all filtering (safe route, safe story ID, nonblank paragraphs) but before the source-group and per-source caps are applied:

```python
extracted_article_count=sum(1 for entry in entries if entry.body_source == "extracted"),
summary_fallback_article_count=sum(
    1 for entry in entries if entry.body_source == "summary_fallback"
),
skipped_article_count=sum(1 for entry in entries if entry.body_source == "skipped"),
```

This is consistent with the existing `article_count=len(entries)` and `source_count=len(grouped_entries)` semantics — those also count all included entries before display capping. "Included" means "passed all library filters," which is exactly what the design specifies.

The test correctly covers the four-article scenario: one extracted (included, counted), one summary\_fallback (included, counted), one skipped-with-paragraph (included, counted), one skipped-with-blank-paragraph (excluded by the nonblank filter, not counted). The assertion `library.article_count == 3` and `library.skipped_article_count == 1` together confirm that the skipped-with-paragraph case is included in the library and counted.

**Finding: None.**

---

### 4. Test Sufficiency and Brittleness

**Coverage provided:**

| Area | Test | Status |
|---|---|---|
| Builder propagates `body_source` per entry | `test_saved_article_library_tracks_body_source_counts_for_included_articles` | Covered |
| Builder computes extracted / fallback / skipped counts | Same test, explicit assertions | Covered |
| Zero-paragraph skipped excluded from library | Same test (`article_count == 3`) | Covered |
| Metrics render summary\_fallback count and ZH label | `test_render_row_one_site_writes_saved_article_library_page` | Covered |
| Per-card chip renders bilingual label and value | Same test | Covered |
| Chip is not a link | `test_render_saved_article_library_filters_content_organization_links_on_library_page` | Covered |
| JSON contracts don't expose text-source map | Extended existing assertions in the render test | Covered |
| Docs sentinel for Stage 333 boundary | `test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary` | Covered |

**Two gaps worth noting:**

**Gap A (Minor):** No render test verifies the `"extracted"` chip — only `"summary_fallback"` is tested end-to-end in HTML. If `_saved_article_library_body_source_label("extracted")` were broken (e.g., fell through to return `"summary_fallback"`), no test would catch it. The builder test checks the `body_source` value on entries, but does not drive a render to HTML. Consider adding `assert "Extracted article text" in html` to the render test, using a local article with the default `body_source` (no change needed — the test at line 2726 uses the default `"extracted"` but the assertions don't check the chip label).

**Gap B (Minor):** The homepage `home_html` widget also calls `_render_saved_article_library_metrics()` (templates.py:3882) and will therefore display text-source counts. The render test checks `home_html` for many things but does not assert the new counts appear there too. This is low risk (the function is shared), but it means homepage regressions in this area would be missed.

Neither gap is blocking. The test suite as designed would catch all plausible implementation bugs from the plan's code snippets.

The docs sentinel test uses `_normalized()` (whitespace-collapsed, casefold) with exact substring matching, consistent with all previous stage sentinel tests. Not brittle.

**Finding: Minor** for Gap A (missing `extracted` chip render assertion); **None** for the rest.

---

### 5. Critical and Important Issues

**Critical: None.** The plan is safe to implement as written. No contract, schema, JSON artifact, or pipeline behavior is touched.

**Important issues to fix before implementation:**

**I-1 (Important):** Add a note in Task 1 Step 2 that adding the required
`body_source` field to `RowOneSavedArticleLibraryEntry` will intentionally
produce transient render-test fixture failures until Task 2 Step 1 updates
`_saved_article_library_fixture()` and other direct `RowOneSavedArticleLibrary`
constructions. This avoids treating expected intermediate failures as unrelated
regressions.

**Minor follow-ups:**

- Add an end-to-end render assertion for the extracted text-source chip.
- Add a homepage metric assertion if convenient, because the homepage saved
  article library widget reuses `_render_saved_article_library_metrics()`.

**Summary:** Fix I-1 in the plan, then proceed to implementation. No Critical
issues.
