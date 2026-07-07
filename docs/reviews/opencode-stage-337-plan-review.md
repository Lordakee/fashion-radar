## Stage 337 Plan Review — Saved Article Reference Atlas

I inspected the spec, plan, `render.py`, `saved_article_content_organization.py`, `saved_article_theme_digest.py`, both test files, and verified every helper/fixture name the plan depends on.

### Checklist verification

| # | Check | Result |
|---|-------|--------|
| 1 | Generated-site-only | ✅ Pure Python view model → HTML in `articles/index.html` only; homepage excluded; no JSON artifact |
| 2 | No app/runtime/manifest/schema/JSON contract changes | ✅ Explicitly asserted (contract vocab + `data/saved-article-reference-atlas.json` absence) |
| 3 | No collection/fetch/extract/score/rank/LLM/connector/schedule/deploy/social/compliance | ✅ Only re-aggregates existing `RowOneReference` chips already produced upstream |
| 4 | Builder inputs sufficient, not dead-coupled | ✅ `(library, organization)` signature mirrors theme digest |
| 5 | Bucketing/dedupe/counts/caps/safe-route filtering coherent | ✅ Reuses `safe_row_one_detail_fragment_href` + `validated_row_one_detail_relative_path` + content-section fragment rules identical to `saved_article_theme_digest.py:205` |
| 6 | Render ordering & tests consistent with 326–336 | ✅ Ordering chain `hero < theme-digest < reference-atlas < saved-signal-index < reading-paths < content-org < grid` matches spec; one gap (see Minor 1) |
| 7 | Helper/fixture names & assumptions compatible | ✅ `_edition()`, `_theme_digest_local_article()`, `_saved_article_library_fixture()`, `_saved_article_theme_digest_section_html()` all exist; `_theme_digest_local_article()` (`test_row_one_render.py:332`) carries the `The Row`(brand) + `Alaia flats`(shoe) refs + `paragraph_indices=[0]` the render test asserts; all 6 template helpers named in the plan exist in `templates.py` |

Bucket arithmetic spot-check on the positive builder fixture (`entities`=section-1, `product_signals`=section-2): yields buckets `[brands, people, products]`, 3 refs, 3 supports, support detail_path `...#local-article-content-section-1` — matches the plan's assertions.

### Findings

**Critical:** None.
**Important:** None.

**Minor:**
1. **No CSS-selector presence test.** Stage 336 added `test_row_one_css_includes_saved_article_theme_digest_styles` (`test_row_one_render.py:6886`); the plan adds 19 selectors to `row_one_css()` but no parallel test. If the implementer wires the HTML class names but forgets the CSS block, nothing fails. Recommend adding `test_row_one_css_includes_saved_article_reference_atlas_styles` mirroring the 336 regex pattern.
2. **`_library_with_safe_stories` (plural) helper** is used in the new builder test snippets but not defined in the plan — implementer must generalize the singular `_library_with_safe_story` to N story ids (straightforward).
3. **Bucket ordering is mildly ambiguous** — the plan lists a canonical order (brands→people→products→source_context) but also says "first-seen order". The positive test passes under either; stating one explicitly would remove implementer guesswork.

### Verdict

**Safe to implement.** All three findings are Minor and non-blocking; the missing CSS test (Minor 1) is the only one I'd fold in before the code-review gate since it's a direct consistency gap with Stage 336.
