## Verdict

**Approve with Important fixes** — the architecture, scope boundaries, and core clustering logic are sound. Three Critical bugs (two undefined functions, one wrong test assertion) and two Important issues (docs test phrase mismatch, stale paragraph indices) must be resolved before implementation.

---

## Critical Findings

**1. `_format_datetime` is undefined — Task 3, Step 4**
- The provenance renderer calls `_format_datetime(article.extracted_at)` and `_format_datetime(article.published_at)`, but no such helper exists in `templates.py`. The test asserts `"Jul 02, 2026" in detail_html`, implying `"%b %d, %Y"` format.
- Why it matters: `NameError` at runtime; the provenance step cannot pass.
- Fix: Either define `def _format_datetime(dt: datetime) -> str: return dt.strftime("%b %d, %Y")` near the helper, or inline `article.extracted_at.strftime("%b %d, %Y")` throughout.

**2. `_safe_external_href` is undefined — Task 3, Step 4**
- The provenance renderer calls `_safe_external_href(article.url)`. The actual wrapper in `templates.py` (line 3142) is `_safe_external_url(url)`, which delegates to `safe_external_url` from `utils.py`.
- Why it matters: `NameError` at runtime; the safe URL guard never executes.
- Fix: Replace every `_safe_external_href(...)` in the plan with `_safe_external_url(...)`.

**3. Wrong `detail_path` assertion in clustering test — Task 1, Step 2**
- The test asserts `item.detail_path == "details/coach-a-1234567890.html#local-article"`, but `_story_sort_key` sorts by `(-heat_delta, ...)`. `coach-b` has `heat_delta=9` and `coach-a` has `heat_delta=4`, so `coach-b` is processed first and becomes the canonical story. The correct expected value is `"details/coach-b-1234567890.html#local-article"`.
- Why it matters: The test will fail even after a correct implementation, masking real bugs and breaking the TDD flow.
- Fix: Change the assertion to `item.detail_path == "details/coach-b-1234567890.html#local-article"`.

---

## Important Findings

**4. Docs test phrase mismatches — Task 5, Steps 1 and 2**
- Step 1 pins these exact phrases: `"clusters duplicate saved local-article cards"`, `"local article provenance"`, `"does not add source collection"`, `"does not add scoring"`. The docs text in Step 2 uses different wording: `"are clustered"` instead of `"clusters duplicate saved local-article cards"`, `"local article detail pages show compact … provenance"` (no exact `"local article provenance"`), and `"it does not change … collection, matching, scoring"` (no `"does not add source collection"` or `"does not add scoring"`).
- Why it matters: The docs test will fail even after the docs are updated exactly as written, creating a false FAIL loop in Task 5.
- Fix: Rewrite the Step 2 docs paragraphs to embed the exact pinned phrases, or rewrite the Step 1 assertions to match the actual docs text.

**5. Merged paragraph indices across cluster members — Task 2, Step 3**
- `_append_story_article_aggregate` accumulates `paragraph_indices` from every clustered story/article. However, `detail_path` in the resulting item points only to the canonical story's page. Paragraph link hrefs derived from non-canonical articles' indices (e.g., a paragraph index1 that exists in article B but not article A) will produce dead anchors on the canonical detail page.
- Why it matters: Silently produces broken in-page links; `_daily_local_intelligence_paragraph_href` will generate an href pointing to a paragraph anchor that does not exist.
- Fix: In `_append_story_article_aggregate`, skip merging `paragraph_indices` from non-canonical cluster members. In `_story_article_aggregate_item`, use `takeaway.paragraph_indices` directly from the canonical article rather than `aggregate.paragraph_indices`.

---

## Minor Findings

**6. Pydantic attribute mutation in test helper — Task 1, Step 1**
- `_article_with_title` does `article.title = title` on a Pydantic model. This works today because `RowOneLocalArticle` is not `frozen=True`, but it is fragile: any future `frozen=True` config will silently break this helper without a type-checker warning.
- Fix: Use `article.model_copy(update={"title": title})` — idiomatic Pydantic v2 and safe under frozen models.

**7. `rel` attribute inconsistency — Task 3, Step 4**
- The provenance `<a>` tag uses `rel="noopener noreferrer"` while every other external link helper in `templates.py` uses `rel="noopener"` only.
- Fix: Match existing convention (`rel="noopener"`) for consistency, or document the deliberate divergence.

**8. Ambiguous `_edition()` call in render integration test — Task 4, Step 1**
- The test calls `edition = _edition()` with no arguments. In `test_row_one_local_intelligence.py`, `_edition(stories: list[RowOneStory])` requires `stories`. The render test file's `_edition` likely has a different default-args signature, but the plan does not clarify this. The "Adjust exact helper names" hedge is vague.
- Fix: Specify the correct signature or fixture name from `test_row_one_render.py` so the step is unambiguous for the implementer.

---

## Suggested Plan Adjustments

1. **Task 3, Step 4** — Add `def _format_datetime(dt: datetime) -> str: return dt.strftime("%b %d, %Y")` to the helper block, and replace all `_safe_external_href(...)` calls with `_safe_external_url(...)`.

2. **Task 1, Step 2** — Change `item.detail_path == "details/coach-a-1234567890.html#local-article"` → `"details/coach-b-1234567890.html#local-article"`.

3. **Task 5, Steps 1 and 2** — Rewrite the Step 2 docs text so it contains the exact pin phrases used in Step 1, e.g.: *"…clusters duplicate saved local-article cards…local article provenance…does not add source collection…does not add scoring…"*; or rewrite Step 1 assertions to use substring subsets that actually appear in the proposed docs text.

4. **Task 2, Step 3** — Remove the `paragraph_indices` merge loop from `_append_story_article_aggregate`. In `_story_article_aggregate_item`, derive `paragraph_indices` solely from `_article_takeaway(aggregate.canonical_article).paragraph_indices`, ensuring all links point into the canonical article's page.

5. **Task 1, Step 1** — Replace `article.title = title` with `return _article(...).model_copy(update={"title": title})` and drop the mutation line.
