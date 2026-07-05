I've now read all relevant files. Here is the full Stage 304 code review.

---

## Stage 304 Code Review

**Verdict: APPROVE**

---

### Critical Issues

None.

---

### Important Issues

None.

---

### Minor Notes

**1. `_local_article_reference_body` zh-fallback branch is implicit but safe**

At `articles.py:306`, the final `return body_en, body_zh or body_en` silently falls back to English if `body_zh` normalizes to an empty string. The behavior is correct and defensive, but it silently absorbs a case that could otherwise surface a bad zh paragraph (e.g., whitespace-only). There is currently no test that sends a whitespace-only zh paragraph through this path. The risk is low because `text_to_local_article_paragraphs` already strips empty paragraphs before they enter the model, but a brief inline comment would make the intent explicit to a future reader.

**2. No test for a ref name shorter than 3 characters**

`_local_article_paragraph_indices` skips terms with `len(normalized) < 3`. A ref with a 1–2 character name (e.g., `name="NY"`) would yield empty `excerpt_indices`, triggering the `type / label` fallback silently. This is correct behavior, but it is not explicitly tested. Given the domain (brand/designer/product names are virtually always ≥ 3 characters), this is acceptable for the current scope.

**3. Render test body is a manual fixture, not builder-generated**

`test_render_row_one_detail_includes_local_article_content` uses a hand-constructed `RowOneLocalArticleContentItem` with body `"Source-backed reference excerpt for The Row demand."`. This is the correct pattern for a render layer test — it verifies that the renderer faithfully emits whatever body the model holds, independent of the builder. The JSON sidecar assertion at line 548–551 is the strongest proof of the publish contract. No issue; just noting the test is correctly scoped to the render layer only.

**4. `aligned_zh` can equal `paragraphs` when zh paragraphs are missing**

When `paragraphs_zh` is empty or mismatched, `_align_local_article_language_paragraphs` fills the gap with English paragraphs. This means `body_zh` will equal `body_en` in that case, which is correct. The generator tests cover this indirectly (English-only extractor fixtures yield `body.zh == body.en`). The render test in Task 2 covers a genuine zh≠ en case. Combined coverage is adequate.

**5. Review artifacts are clean**

Both plan reviews (`claude-code-stage-304-plan-review.md`, `opencode-stage-304-plan-review.md`) are coherent, free of tool-status noise, and consistent with the implementation that was actually delivered. The opencode `APPROVE_WITH_NOTES` note about `_normalized()` usage in docs tests was correctly applied — the test uses the existing `_normalized(_read(ROW_ONE_DOC))` pattern.

---

### Assessment Against Each Review Objective

**Matched entity/designer/product reference cards use saved local paragraph excerpts as `RowOneLocalArticleContentItem.body`**
Confirmed. `_local_article_reference_section` now computes `excerpt_indices` from `[ref.name]` (limit=1) and calls `_local_article_reference_body`, which picks the first name-matched paragraph. `test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs` asserts the correct excerpt text for The Row, Zendaya, Mary-Kate Olsen, and Margaux.

**Excerpt body matching is reference-name-only; no generic labels**
Confirmed. `excerpt_indices = _local_article_paragraph_indices(paragraphs, [ref.name], limit=1)` uses only `ref.name`. `test_build_row_one_local_articles_reference_excerpt_requires_name_match` proves that a paragraph containing only "bag" (the label) does not produce a misleading excerpt body — `margaux.body.en == "product / bag"` — even though `margaux.paragraph_indices == [0]` (badge still links).

**Broad `paragraph_indices` badge matching still uses name+label**
Confirmed. `paragraph_indices = _local_article_paragraph_indices(paragraphs, [ref.name, ref.label])` is unchanged. Stage 303 anchor behavior is preserved.

**Unmatched or generic-label-only references retain deterministic `type / label` fallback**
Confirmed. `_local_article_reference_body` returns `f"{ref.type} / {ref.label}"` when `_local_article_reference_excerpt` returns `None`. Both `test_build_row_one_local_articles_content_sections_work_on_fallback` and the name-match guard test verify this.

**Detail page HTML and `data/articles/<story-id>.json` publish source-backed reference excerpt bodies; `data/edition.json` and `row-one-app/v7` remain unchanged**
Confirmed. The render test checks both the HTML span and the JSON sidecar body field. It also explicitly asserts `"The Row demand moved." not in edition_json` and `"First local paragraph about The Row demand." not in edition_json`, proving local article content is not leaked into the app contract payload.

**Homepage Daily Local Intelligence behavior remains structurally stable**
Confirmed. The `_local_article_for_daily_intelligence` fixture in render tests is unchanged. No new homepage paragraph links or new schema keys are introduced. Daily Local Intelligence continues to project from `content_sections` bodies as before, and now receives richer values rather than a structural change.

**No app contract, dependency, source acquisition, scraping, social connector, scheduler, image, demand proof, platform coverage verification, or compliance-review behavior added**
Confirmed. `articles.py` adds only two pure Python helpers and modifies one function signature. No imports added. No new model classes. No `row-one-app/v7` fields. The `uv.lock` check passed.

**Tests catch metadata-only body regression, generic-label misleading excerpt regression, paragraph-index regression, and ambiguous detail-page render regression**
Confirmed. Body assertions in the main content-sections test fail immediately if any matched body reverts to `brand / tracked` or similar. The generic-label guard test fails if name-only matching is accidentally replaced with name+label for excerpt selection. Paragraph-index assertions are unchanged from Stage 303. The render test catches both HTML and JSON sidecar regressions in one pass.

**Review artifacts are coherent and free of live-capture/tool-status noise**
Confirmed. Both plan reviews are well-formed markdown with no terminal output fragments or tool status lines. Verdicts, structure, and minor-note content are consistent with the implementation.
