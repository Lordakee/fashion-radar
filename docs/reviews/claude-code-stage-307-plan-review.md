I now have all the information needed for a complete review. Here is the structured assessment.

---

## Stage 307 Plan Review

**Base SHA:** `f774eff`
**Plan:** `docs/superpowers/plans/2026-07-05-stage-307-row-one-local-evidence-drilldowns-plan.md`

---

### Verdict: APPROVE_WITH_NOTES

---

### Critical Issues

None.

---

### Important Issues

**1. New CSS classes have no rules in `row_one_css()`**

The plan introduces three new CSS class names used on rendered HTML elements:
- `.daily-local-intelligence-actions` (wrapping div)
- `.daily-local-intelligence-action` (the "Open saved text" / "Open paragraph N" anchor)
- `.daily-local-intelligence-paragraph-link` (inline paragraph anchor in segment meta)

None of these have corresponding rules in `row_one_css()` in `templates.py`. The existing `.daily-local-intelligence-card` CSS includes `text-decoration: none` because it was an anchor; that's harmless on a div after the change. But the new action and paragraph-link anchors will render with default browser link styling (blue underline) which is inconsistent with every other link in the site. The plan says "no visual redesign" but adding navigable anchors with no CSS is a presentation regression.

**Required fix:** Either add minimal CSS rules for the new classes in `row_one_css()` before committing, or explicitly document in the plan that default browser styling is accepted and add a test assertion that the new CSS class names are at least present in the rendered CSS string.

**2. `_daily_local_intelligence_paragraph_href` double-validates an already-validated href**

In the proposed implementation, `_render_daily_local_intelligence_actions` and `_render_daily_local_intelligence_segment_meta` call `_daily_local_intelligence_paragraph_href(detail_href, index)` where `detail_href` is already the output of `_safe_daily_local_intelligence_href(item.detail_path)`.

Inside `_daily_local_intelligence_paragraph_href`, the code calls `_safe_daily_local_intelligence_href(detail_href)` again. The only real effect of this second call is to extract the path before `#` for fragment replacement. This works, but it is opaque: a reader cannot tell whether the second call is for validation or for path extraction. If the validator is tightened in a future stage, this could silently suppress paragraph links.

The simpler and clearer implementation is:
```python
def _daily_local_intelligence_paragraph_href(detail_href: str, index: int) -> str | None:
    if index < 0:
        return None
    path = detail_href.split("#", 1)[0]
    return f"{path}#local-article-paragraph-{index + 1}"
```
Since `detail_href` is already validated by the caller, the second `_safe_daily_local_intelligence_href` call is redundant. The plan should either simplify this or add a comment explaining the intent.

---

### Minor Notes

1. **Task ordering (2before 3) is safe.** `_daily_local_intelligence_paragraph_href` constructs paragraph hrefs programmatically and does not pass the result back through `_safe_daily_local_intelligence_href` before writing it to HTML. Task 3 (expanding the validator) is only required for the validator unit tests, not for Task 2's render logic. The ordering will not cause green tests to go red in between tasks.

2. **Task 1 fix is minimal and correct.** Moving `aggregate.detail_path = _local_article_detail_path(story.detail_path)` inside the `if aggregate.body is None or segment_match_score > aggregate.segment_match_score:` block, with the `elif aggregate.detail_path is None:` fallback, correctly covers both the upgrade path and the first-story-sets-path-only path. The existing code at `local_intelligence.py:136-143` confirms this is the exact block to change.

3. **The regex `[1-9][0-9]*$` correctly rejects paragraph-0.** The test case `("details/..html#local-article-paragraph-0", None)` is correctly handled.✓

4. **Task 4 docs test phrasing needs a target function.** The plan says "Add assertions to the relevant ROW ONE docs test" but does not name the function. The most natural target is the existing `test_row_one_docs_describe_daily_local_intelligence()` in `tests/test_row_one_docs.py`. The plan should name this explicitly to avoid ambiguity for the implementer.

5. **`test_render_row_one_site_includes_daily_local_intelligence` red step will work.** The current test at line 941 asserts `'href="details/the-row-signal-1234567890.html#local-article"' in html`, which passes today because the card itself is an anchor. After Stage 307 removes the card anchor and introduces action links, the href still appears (inside the action link), so this old assertion continues to pass. The new assertion `'<a class="daily-local-intelligence-card"' not in html` is what turns the test red, which is the correct trigger. ✓

6. **`test_render_row_one_site_escapes_daily_local_intelligence` is not mentioned in Task 2.** The existing escape test (`test_render_row_one_site_escapes_daily_local_intelligence`) verifies that `<script>` and `onerror` patterns cannot appear in the rendered HTML. After Task 2's renderer refactor, this test should still pass because `_esc()` is applied consistently. The plan does not mention verifying this; the Task
