All 85 tests pass. Here is the complete Stage 301 code review.

---

## Stage 301 Code Review

**Verdict: APPROVE_WITH_NOTES**

All tests pass (85 passed). No critical or blocking issues. One important coverage gap and several minor notes.

---

### Review Scope

All changed files were read in full. Tests were executed via `pytest tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py -q` —85 passed, 0 failed.

---

### Review Objective Checklist

**Does Stage 301 correctly add a homepage Daily Local Intelligence section derived from saved local article sidecars?**
Yes. `build_row_one_local_article_intelligence` builds the four-section structure from `edition.stories` × `local_articles_by_story_id`, and `render_index_html` places `{daily_local_intelligence}` after `{signal_synthesis}` and before the lead story block. The HTML section and bilingual header are confirmed by `test_render_row_one_site_includes_daily_local_intelligence`.

**Is `data/local-intelligence.json` written only when there is saved local article intelligence?**
Yes. `_write_local_article_intelligence_file` returns early when `writable_sections` is empty. The render test `test_render_row_one_site_omits_daily_local_intelligence_without_saved_articles` confirms the file is absent without saved articles.

**Do `data/edition.json` and `row-one-app/v7` remain unchanged?**
Yes. The builder result is not passed to `build_row_one_app_payload`. `edition.json` does not contain `local_article_intelligence`. Confirmed by direct assertion in the render test.

**Does rendering escape all local article-derived text and safely accept only valid detail links plus the exact `#local-article` fragment?**
Yes, with one coverage note (see Important Issues).

- `_render_daily_local_intelligence_item` calls `_esc` on `item.title.en`, `item.title.zh`, `item.body.en`, `item.body.zh`, and all meta values before interpolating them into HTML.
- `_safe_daily_local_intelligence_href` correctly:
  - Rejects `None` and non-strings.
  - Accepts bare detail paths via `_validated_detail_relative_path`.
  - For paths containing `#`: splits on the first `#` only (via `split("#", 1)`), rejects any fragment that is not exactly `"local-article"`, and validates the base path separately.
  - A path like `details/foo.html#local-article#extra` produces `fragment = "local-article#extra"`≠ `"local-article"`, so it is correctly rejected.
- `test_render_row_one_site_escapes_daily_local_intelligence` covers body (`<script>`) and entity name (`<The Row>`) escaping.

**Is the aggregation logic deterministic, source-grounded, and compatible with existing generated-site cleanup?**
Yes.

- **Source-grounded**: only stories present in `edition.stories` are processed (stale article test confirms this). Only articles with at least one non-empty paragraph (`_has_publishable_paragraphs`) are included.
- **Deterministic**: body text uses the first-seen story in edition order (first `aggregate["body"] is None` check); `_append_unique` deduplicates sources in first-seen order; references deduplicated by `(normalized_name, type)`; sort key is `(story_count desc, article_count desc, heat_delta desc, name asc)`.
- **Cleanup compatible**: `data/local-intelligence.json` lives under `data/`, which is already a member of `GENERATED_CHILDREN`. No new cleanup logic needed.

**Do tests provide meaningful coverage? What gaps could hide real bugs?**
Coverage is solid for the primary paths. See Important and Minor sections below.

---

### Critical Issues

None.

---

### Important Issues

**I1. `_safe_daily_local_intelligence_href` has no unit test for fragment rejection**

`_safe_daily_local_intelligence_href` is the only function guarding arbitrary-fragment injection in the new section. It is exercised only via integration through `test_render_row_one_site_includes_daily_local_intelligence`, which confirms the happy path (`#local-article` is accepted). There is no test that:

- a `#xss-fragment` path is rejected (returns `None`),
- a bare `.html` path without a fragment is accepted,
- a non-string input returns `None`,
- a path with a valid base but an invalid fragment returns `None`.

Given that `_safe_signal_detail_href` (the older sibling) is also untested at unit level, this is consistent with existing practice — but the new function is strictly more complex because of the fragment handling. If a future edit introduces a bug in the `fragment != "local-article"` branch, no test will catch it.

**Recommendation**: Add a small parametrized unit test in `test_row_one_local_intelligence.py` or a dedicated test module covering the accept/reject cases of `_safe_daily_local_intelligence_href`. This does not need to be done before merge, but should be filed as a follow-up.

---

### Minor Notes

**n1. Aggregate `detail_path` is set but untested**

`_reference_watch_section` sets `aggregate["detail_path"]` to the first-seen story's `#local-article` path. The `brand_watch` and `product_watch` items therefore carry a `detail_path`. The test `test_build_row_one_local_article_intelligence_aggregates_references_by_name` does not assert this field, so the first-seen-story selection rule for aggregate links is implicitly trusted. Low risk given the builder test fixture is deterministic, but the behavior is undocumented by a test.

**n2. `_daily_local_intelligence_meta` rendering is not directly tested**

The meta line content (source names, article count, story count, evidence count, heat delta formatting) is rendered but no test checks the exact output string. The integration test only confirms the section is present in HTML. If the meta format is changed (e.g., swapping order of article/story counts), no test will fail. This is a low-risk gap for display-only metadata.

**n3. Source name escaping in meta is correct but the escape test does not cover it**

`_daily_local_intelligence_meta` joins `item.source_names` and passes the result through `_esc`. The escape test uses `source_name="<Vogue>"` in the article fixture, but the test only asserts that `&lt;The Row&gt;` appears (entity name) and `&lt;script&gt;…` appears (body). It does not assert that `&lt;Vogue&gt;` appears in the meta line. The code is correct (`_esc` is called), but the test does not prove it.

**n4. `story.headline` is used verbatim for `title.zh` in strongest_reads and heat_movers items**

`_story_article_item` sets `title = LocalizedText(zh=story.headline, en=story.headline)`. Headlines in this system are English-only, so both language slots get the English string. This is consistent with existing story card rendering where zh and en headlines are the same. No behavioral issue, but readers of the builder code may find it surprising without a comment.

**n5. Aggregate dict uses `dict[str, object]` with `type: ignore` casts throughout `_reference_watch_section` and `_aggregate_item`**

The 12+ `type: ignore[arg-type]` and `type: ignore[union-attr]` annotations are necessary because the intermediate dict is typed loosely. A `@dataclass` or `TypedDict` for the intermediate aggregate state would eliminate the annotations and make the data flow clearer. Not a correctness issue.

**n6. `scroll-margin-top` for `#local-article` not addressed (carried from plan note n6)**

Fragment jumps from `details/…html#local-article` links on the homepage land at the `id="local-article"` anchor in the detail page. If the detail page uses a sticky header, the anchor target may be hidden beneath it. The plan reviewer (opencode rereview) noted this as still-open minor note n6. The fix belongs in the detail-page CSS (`#local-article { scroll-margin-top: …}`), not in this stage's new CSS selectors.

---

### Summary

The implementation faithfully executes the approved plan. All six architecture properties from the review objective are satisfied: the Daily Local Intelligence section is rendered from saved article sidecars, `local-intelligence.json` is conditional, `edition.json` and `row-one-app/v7` are untouched, all text is escaped, the href validator accepts only `#local-article`, aggregation is deterministic and source-grounded, and the new artifact coexists with existing site cleanup. The important issue (I1) is a test coverage gap for a security-sensitive helper, not a runtime defect — the function itself is correct. Safe to merge.
