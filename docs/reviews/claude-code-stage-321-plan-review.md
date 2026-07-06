The review has been written to `docs/reviews/claude-code-stage-321-plan-review.md`.

**Summary of findings:**

**Critical:** None.

**Important (2):**
- I-1: `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS` is missing from the test import block in the plan. The body-length cap test (Task 1 Step 7) uses it directly but the plan never adds it to the `from fashion_radar.row_one.templates import (...)` block. Must be added alongside `_EditorialBrief` and `_EditorialBriefItem` in Task 1 Step 3.
- I-2/I-3: Informational notes on the escaping test's cap-vs-filter ambiguity and the workflow precondition operating on serialized dicts — both are correctly implemented as written, just flagged for implementer awareness.

**Minor (5):** CSS test return-value pattern is correct; duplicate-body test whitespace stripping assumption is safe; no explicit zero-index fragment rejection test (acceptable given existing regex coverage); Task 3 Steps 2 and 3 must not be split; `_lead_story_for_editorial_brief` must check all four localized strings (en+zh for both fields), not just `.en`.

**Recommendation: Approve with changes.** The only required fix before implementation is I-1 (add `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS` to the test import block). Everything else is correct and well-bounded.
``

This is a required mechanical fix before Task 1 Step 7 can pass.

---

### I-2 — Escaping test assertion on item-4 paragraph href is ambiguous without the comment

**Location:** Plan Task 1 Step 3

The assertion:

```python
assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' not in section_html
```

Is documented with an inline comment explaining it is excluded by the 3-item cap, not by link rejection. This is correct behavior, but the test name `test_render_index_html_escapes_editorial_brief_and_filters_links` suggests a link-filtering test. A future reader or reviewer could misread the assertion as proving the fragment is rejected rather than capped.

The **separate** test `test_render_index_html_accepts_editorial_brief_content_section_href` (Task 1 Step 5) does confirm paragraph fragments are accepted when they are within the 3-item cap. So the coverage is complete, but the two tests together can be confusing.

**Recommendation:** Keep the comment exactly as written. The plan already addresses this with the explicit comment. No code change required — this is a heads-up for the implementer to preserve that comment precisely during implementation.

---

### I-3 — Workflow test precondition assertion operates on app payload dict, not `RowOneStory` objects

**Location:** Plan Task 3 Step 1

```python
assert any(
    story.get("editorial_takeaway", {}).get("en") or story.get("summary", {}).get("en")
    for story in edition_payload["stories"]
)
```

`edition_payload["stories"]` is the serialized app payload (list of `dict`), not `RowOneStory` objects. The fields `editorial_takeaway` and `summary` are dicts of the form `{"en": "...", "zh": "..."}`. The `.get("editorial_takeaway", {}).get("en")` pattern is correct for that structure.

However, `_editorial_brief_payload` in `render.py` operates on `RowOneStory` Pydantic objects (via `edition.stories`), not the serialized dict. The precondition in the workflow test confirms the serialized payload has non-empty text, which is a valid proxy — if `editorial_takeaway.en` is non-empty in the app payload dict, the same text is non-empty in the `RowOneStory` object. This is correct and consistent.

No code change required. Calling this out so the implementer does not accidentally switch to accessing `RowOneStory` objects here.

---

## Minor Findings

### M-1 — `render_row_one_site` return value used in CSS test

**Location:** Plan Task 1 Step 10

```python
index_path = render_row_one_site(_edition(), tmp_path).index_path
```

`render_row_one_site` returns `RowOneRenderResult`, which has `index_path: Path`. This is correct and already the established pattern in other tests (e.g., Stage 320 Daily Edit CSS test). No issue — confirming it is intentional.

---

### M-2 — Duplicate-body test uses whitespace-padded body for the second item

**Location:** Plan Task 1 Step 8

```python
body=LocalizedText(en=" Same body. ", zh=" 相同正文。 "),
```

The dedup logic uses `clean_row_one_text(a) == clean_row_one_text(b)`. If `clean_row_one_text` strips whitespace (it does, based on the existing text utilities), then `" Same body. "` and `"Same body."` will compare equal, and the second item is correctly skipped. Verify `clean_row_one_text` normalises leading/trailing whitespace before implementing — this is safe based on the existing `text.py` implementation.

---

### M-3 — No explicit test for fragment index-zero rejection

The regex `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(r"local-article-paragraph-[1-9][0-9]*$")` rejects `local-article-paragraph-0`. The plan does not include a dedicated test for this edge case. Given the regex is already tested in existing Stage 317/319 tests and is reused unchanged, this omission is acceptable. A paranoid assertion could be added to the escaping test, but it is not required.

---

### M-4 — Task 3 Step 3 must be performed in the same edit as Step 2

The plan already calls this out explicitly: "This update must happen in the same edit as the Stage 321 README/docs paragraph insertion." Worth emphasising: if Step 2 and Step 3 are applied separately, the Stage 320 docs test will fail between commits (it will find `"Stage 321 adds"` before `"Stage 310 adds"` and the slice endpoint will be wrong). The plan's ordering is correct. The implementer must not split these edits.

---

### M-5 — `_lead_story_for_editorial_brief` selection criteria excludes no-text editions cleanly

The spec says: "return the first story… whose `editorial_takeaway` or `summary` has at least one non-empty localized string after cleanup." `RowOneStory.editorial_takeaway` and `summary` are both non-optional `LocalizedText` fields — they exist on every story, but their string values may be empty. The plan's helper must check `clean_row_one_text(story.editorial_takeaway.en)` or any of the four localized strings (en/zh for both fields), not just `.en`. The plan says "at least one non-empty localized string" which covers this. Make sure the implementation checks all four strings, not just `.en`.

---

## Review of the Five Spec Questions

**1. Scope alignment with "整理信息，而不是只是链接"**

Yes. The feature assembles existing saved local article brief sections and story text into three readable prose paragraphs with safe internal links to detail pages and paragraph anchors. This is a direct narrative upgrade over the current link-and-card layout, without introducing any new data collection or external calls.

**2. Technical feasibility in the current codebase**

Yes. All required building blocks exist:
- `RowOneLocalArticle.brief_sections` (with keys `what_happened`, `why_it_matters`, `signal_context`, `watch_next`)
- `RowOneStory.editorial_takeaway`, `summary`, `why_it_matters`, `signal_context`, `reader_path`
- `clean_row_one_text()` in `text.py`
- `validated_row_one_detail_relative_path()` in `detail_routes.py`
- `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` already in `templates.py`
- The rendered-section pattern (`_render_saved_article_content_organization`, `_render_daily_edit`, etc.) is well-established and directly reusable

The one-way `render.py → templates.py` import graph is preserved. The dataclasses stay private and out of all JSON artifacts.

**3. File boundaries (generated-site-only JSON contract boundary)**

Correct and well-guarded. The plan touches only:
- `render.py` (builder logic, passes `editorial_brief` to `render_index_html`)
- `templates.py` (private dataclasses, render helpers, CSS)
- Test files
- README and docs

No changes to `edition.json`, `manifest.json`, `runtime.json`, schemas, or app payload builders. The workflow test explicitly asserts `'"editorial_brief"' not in generated_contract_payload`, which covers the key contract boundary.

**4. Test sufficiency**

The test plan is comprehensive and covers all required cases:
- Render from local articles (Task 1 Step 1)
- Omission when no usable content (Step 2)
- Escaping and link safety — `javascript:`, external URLs, safe detail href, safe paragraph fragment (Step 3)
- Story-text fallback when no local article (Step 4)
- Content-section fragment href acceptance (Step 5)
- 3-item cap (Step 6)
- Body length cap with `…` truncation (Step 7)
- Duplicate body deduplication (Step 8)
- Empty item omission (Step 9)
- CSS selector and mobile breakpoint (Step 10)
- Ordering: `saved-article-content-organization` < `editorial-brief` < `lead-story` (Step 1)
- Workflow JSON boundary (`'"editorial_brief"'` absent from contract payload) (Task 3 Step 1)
- Docs boundary phrases (Task 3 Step 4)

No gaps identified beyond the minor fragment-zero edge case (M-3), which is covered by the existing regex.

**5. Ambiguity, placeholder work, or risky overreach**

No placeholder work. No risky overreach. One minor ambiguity: the `_lead_story_for_editorial_brief` selection criteria says "at least one non-empty localized string" — the implementation must check all four strings (en+zh for both `editorial_takeaway` and `summary`), not just `.en` (see M-5).

The risk that `templates.py` grows large is acknowledged in both the spec and the plan. Keeping the helpers private and grouped near the Daily Edit / saved article section helpers is the right mitigation.

---

## Final Recommendation

**Approve with changes.**

One required fix before Task 1 Step 7 can pass: add `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS` to the templates import block in the test file (I-1). All other findings are minor or informational. The spec and plan are well-structured, correctly bounded, technically feasible, and have comprehensive test coverage. Proceed to implementation after applying the I-1 fix.
