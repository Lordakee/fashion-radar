## Stage 333 Plan Rereview

### I-1 (Important) — Resolved

The fix is correctly placed and complete. Task 1 Step 2 now reads:

> "This required dataclass field will intentionally create transient failures in direct render-test fixtures such as `_saved_article_library_fixture()` until Task 2 Step 1 adds the matching fixture values. Do not investigate those intermediate `TypeError` failures as unrelated regressions; complete Task 2 Step 1 before running broad render tests."

This addresses all three requirements of the original finding: it is in the right step, names the specific fixture, explains the failure type (`TypeError`), and gives the implementer clear direction (finish Task 2 Step 1 before running broad render tests). **I-1 is closed.**

---

### Remaining Findings

**Critical: None.** No contracts, schemas, or pipeline behavior are touched. The plan remains safe to implement.

**Important: None.** I-1 is the only Important finding from the original review; it is resolved. No new Important issues are introduced by the fix or anywhere else in the plan.

**Minor — Gap A (unchanged):** No render test asserts the `"extracted"` chip label end-to-end. `_saved_article_library_body_source_label("extracted")` is only exercised indirectly through the builder test, which checks the `body_source` string on entries but does not drive HTML rendering. A broken `"extracted"` branch in the label helper would not be caught. The suggestion from the original review still applies: add `assert "Extracted article text" in html` to the render test (the existing test at line 2726 uses the default `body_source="extracted"` article, so no fixture change is needed).

**Minor — Gap B (unchanged):** The homepage widget also calls `_render_saved_article_library_metrics()` and will display the new text-source counts, but no assertion covers that path. Low risk since the function is shared, but a homepage regression in this area would be silent.

---

### Verdict

The plan is ready to implement. The one blocking issue (I-1) is resolved. Both remaining gaps are Minor and non-blocking — the test suite as written will catch all plausible implementation bugs from the plan's code snippets.
