I now have all the information needed to deliver the rereview.

---

## Stage 307Plan Rereview

**Base SHA:** `f774eff`
**Revised plan:** `docs/superpowers/plans/2026-07-05-stage-307-row-one-local-evidence-drilldowns-plan.md`
**Prior review:** `docs/reviews/claude-code-stage-307-plan-review.md`

---

### Verdict: APPROVE_WITH_NOTES

---

### Critical Issues

None.

---

### Important Issues

**1. Task 4 Step 1 code snippet uses undefined variable names — will raise `NameError` at test runtime**

The plan's Step 1 under Task 4 directs the implementer to add:

```python
assert "homepage Daily Local Intelligence cards include local saved-text and paragraph drilldown links" in normalized
assert "data/local-intelligence.json" in text
```

Neither `normalized` nor `text` exists in `test_row_one_docs_describe_daily_local_intelligence()`. The function declares:

```python
readme = _normalized(_read(README))
row_one_docs = _normalized(_read(ROW_ONE_DOC))
```

Both assertions will raise `NameError` as written. The corrected assertions should be:

```python
assert "homepage Daily Local Intelligence cards include local saved-text and paragraph drilldown links" in readme
assert "data/local-intelligence.json" in row_one_docs
```

Note: the second assertion targets `row_one_docs`, not `readme` — `"data/local-intelligence.json" in readme` already passes at line 739 of the existing test. The new docs coverage the plan describes in Step 3 (`docs/row-one.md` generated-files block) belongs in `row_one_docs`.

**Required fix before implementation:** Correct both variable names in the Task 4 Step 1 snippet.

---

### Minor Notes

1. **Prior finding1(CSS) — fully resolved.** Task 2 Step 5 adds all three CSS rules to `row_one_css()`. Task 2 Step 1 adds test assertions that the three class name strings appear in `row_one_css()`. Both remediation paths from the prior finding are present.✓

2. **Prior finding 2 (double-validation) — fully resolved.** The revised `_daily_local_intelligence_paragraph_href()` implementation is exactly the simplified form requested: `path = detail_href.split("#", 1)[0]` with an explanatory comment that `detail_href` is already validated by the caller. ✓

3. **Prior finding 3 (docs test target) — fully resolved.** Task 4 Step 1 explicitly names `test_row_one_docs_describe_daily_local_intelligence()` as the target function. That function is confirmed present at `tests/test_row_one_docs.py:727`. ✓

4. **Prior finding 4 (escaping regression) — fully resolved.** Task 2 Step 7 explicitly runs `test_render_row_one_site_escapes_daily_local_intelligence` after the renderer refactor with an expected-pass result. ✓

5. **`row_one_css` is not yet in the test file's import block.** The current import at `tests/test_row_one_render.py:31–34` imports only `_safe_daily_local_intelligence_href` and `render_index_html` from `templates`. The CSS assertions added in Task 2 Step 1 call `row_one_css()`, so the implementer must also add `row_one_css` to that import. The plan says "importing or using the existing helper" without spelling out the import line; this is low-risk but worth noting to avoid a silent `NameError` on the first red-test run.

6. **Steps 3 and 4 of Task 2 cannot be independently compiled between completion.** Step 3 calls `_render_daily_local_intelligence_segments(item, detail_href=href)` before Step 4 adds the `detail_href` parameter to that helper. The code is not importable between the two steps. This is acceptable because the plan correctly defers test execution to Step 6 (after both steps are complete); an implementer who tries an intermediate import check will see a `TypeError`. No plan change required, but awareness helps.

7. **`test_render_row_one_site_includes_daily_local_intelligence` existing assertion at line 941 stays safe.** The current assertion `'href="details/the-row-signal-1234567890.html#local-article"' in html` will continue to pass after Stage 307 because that href now appears inside the `_render_daily_local_intelligence_actions` anchor rather than the card anchor. The plan's new `'<a class="daily-local-intelligence-card"' not in html` assertion is what turns the test red, which is the correct trigger. ✓

---

### Required Plan Changes Before Implementation

1. In Task 4 Step 1, replace `normalized` with `readme` and replace `text` with `row_one_docs` in the two new assertion lines.

---

REVIEW_COMPLETE
