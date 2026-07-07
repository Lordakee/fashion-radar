## Verdict: Needs revision (one blocker)

## Critical issues
None — after verifying Python 3.13's `PurePosixPath` collapses `.` segments, the canonicalization test (Task 2 Step 4) works as written: `validated_row_one_detail_relative_path("details/./the-row-…html")` returns a 2-part path and the `./` never reaches output.

## Important issues
**B1 — CSS selector regex will not match `.saved-article-library-snippet-evidence` (Task 2 Step 5).** The existing test helper asserts `re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)` (`tests/test_row_one_render.py:5991`). The planned CSS only emits that class inside the compound selector `.saved-article-library-snippet-evidence a { … }`, so after the class token comes ` a `, not `{` or `,`. The regex fails and `test_row_one_css_includes_saved_article_library_styles` goes red even with a correct implementation. Fix: either add a standalone `.saved-article-library-snippet-evidence { … }` rule, or drop that selector from the test list.

## Minor issues
- **M1 Mapping import** — plan already adds `from collections.abc import Mapping, Sequence` (Task 1 Step 3); resolved.
- **M2 "People & Brands" label** — the current plan asserts `People &amp; Brands` / `品牌与人物` (Task 1 Step 1), matching the inline `entities` fixture and existing content-org builder; resolved.
- **M3 evidence double-wrap** — `_render_saved_article_content_organization_evidence` returns `<span class="saved-article-content-organization-evidence">…` (with `display: contents`), then the snippet wraps it in `<span class="saved-article-library-snippet-evidence">`. Benign layout-wise, but `.saved-article-library-snippet-evidence a` (specificity 0,1,1) overrides `.saved-article-content-organization-evidence-link` (0,1,0) inside cards — verify that is the intended visual.
- **M4 redundant per-card cap** — harmless.
- **M5 entry-with-no-valid-paths** — Task 2 Step 3 (`test_render_saved_article_library_omits_snippets_for_unsafe_entry_paths`) covers this; resolved.

## Required plan changes before implementation
1. Fix B1: in Task 2 Step 5, add a standalone `.saved-article-library-snippet-evidence { … }` rule (recommended, since the HTML emits that class) **or** remove `.saved-article-library-snippet-evidence` from the selector assertion list.

No other plan changes required; the design, contract boundaries, lookup/matching safety logic, docs boundary approach, and review/verification tasks are sound and within the Stage 334 generated-site-only scope.
