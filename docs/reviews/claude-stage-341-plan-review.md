## Stage341Plan Review

**Approved with required fixes before coding.**

---

### Critical Issues

**1. `_local_article_body_source_label()` name collision with type mismatch**

The function already exists at `templates.py:7121`, returns `str`, and is actively called by `_render_local_article_provenance()`. The plan's Task 2 Step 3 proposes adding a *new* function with the **exact same name** but returning `LocalizedText` instead of `str`. This will:

- Silently overwrite the existing definition in Python (last-def-wins), breaking `_render_local_article_provenance()`
- Cause ruff to flag a redefinition
- Misalign the existing caller's expected `str` with the new `LocalizedText` return

Also: the existing function returns `"Extracted article text"` (with "text"); the spec and plan say `"Extracted article"`. Minor but the implementation should pick one.

**Fix before coding:** Rename the new bilingual helper — e.g. `_local_article_body_source_label_localized()` — and use it only inside the panel. Leave the existing `str`-returning function untouched.

---

**2. `_strict_valid_local_article_paragraph_indices()` needs `rendered_indices` — the panel can't get it for free**

`_strict_valid_local_article_paragraph_indices(indices, rendered_indices)` requires a `set[int]` of paragraphs that were actually rendered. That set is computed *inside* `_render_local_article()` via `_local_article_rendered_paragraph_indices(article)`, a private call the panel has no access to.

The plan says "use the existing helper" but never says how the panel obtains `rendered_indices`. Two options:

- Call `_local_article_rendered_paragraph_indices(article)` directly from the panel helper (if it's accessible from the same module — it is, since everything is in `templates.py`).
- Compute a simplified version inline from `article.paragraphs` (non-blank check).

**Fix before coding:** The plan must explicitly state that `_render_local_article_information_panel()` calls `_local_article_rendered_paragraph_indices(article)` itself to build its own copy of `rendered_indices`, which it then passes to `_strict_valid_local_article_paragraph_indices()`.

---

### Important Issues

**3. Bool/string paragraph-index test won't exercise the guard**

Task 1 Step 4 proposes `paragraph_indices=[0, True, 0, 99, "1"]`. `RowOneLocalArticleContentItem.paragraph_indices` is typed `list[int]` in a Pydantic model — Pydantic coerces `True → 1` and `"1" → 1` at instantiation time, before any test code runs. The `isinstance(index, bool)` branch in `_strict_valid_local_article_paragraph_indices()` will never fire from a panel test built this way.

This doesn't make the test wrong — it still verifies out-of-range exclusion and dedup at the rendered HTML level — but the comments claiming it tests "bool indices" are misleading. The bool-guard is already covered by `test_strict_valid_local_article_paragraph_evidence_indices_rejects_bool_values` at the unit level.

**Fix:** Update the test comment to note Pydantic coercion. Use `[0, 0, 99]` (no bools/strings) and document that the bool path is tested at the helper unit level. This keeps the test honest.

---

**4. `_html_between()` existence is unconfirmed**

Task 1 Step 2 calls `_html_between(html, ...)`. The plan says "use an existing helper if it exists; otherwise add one." Before coding, confirm whether this helper already exists in `test_row_one_render.py`. If not, define it as a module-level test utility — don't bury it inside a test function.

---

**5. `_signal_briefing_local_article()` fixture is unconfirmed**

This fixture is used across all six panel tests. If it doesn't exist, all tests fail at setup. Confirm it exists or add it to Task 1 before Step 1.

---

### Minor Suggestions

**6. `{information_panel}` insertion point in the template string**

The current template (line 436) has `{local_article_section}` inside `<div class="local-article-page-article">`. The implementation must insert `{information_panel}` between the `<p class="story-source">` line (line 435) and `{local_article_section}`. The plan implies this but doesn't show the exact before/after diff. Showing it in the plan would prevent an implementer from placing the panel outside the article div or after the existing section.

**7. Redundant empty-check on the panel is fine but worth documenting**

`render_local_article_page_html()` already gates on `if not local_article_section: return ""` before the panel is ever called. The panel's own `return ""` when there are no nonblank paragraphs is harmless but redundant. A short comment in the implementation noting the early-return upstream removes confusion.

**8. `...` placeholder in Step 5's contract-stability loop**

Task 1 Step 5 uses `for contract_json in (...):` without stating which variables. The implementer needs to know exactly which JSON strings to check (e.g. the serialized `edition.json`, `manifest.json`, `runtime.json` payloads). Spelling them out prevents accidental omission.

**9. Section-link anchor assumption in the local-anchor test**

`assert 'href="#local-article-content-section-1"' in panel` assumes `_signal_briefing_local_article()` has at least one content section. Verify the fixture has `content_sections` before writing that assertion.

---

### Answers to the Six Review Questions

1. **Technically feasible?** Yes. `render_local_article_page_html()` already has all required inputs (`edition`, `story`, `local_article`; `section_title` is a local variable computed inside it). The template layer is the right place and nothing outside it needs to change.

2. **Right insertion point?** Yes. `render_local_article_page_html()` is the correct and only necessary call site. There is no reason to touch `render.py`.

3. **Scope creep?** None detected. The plan stays inside `templates.py`, `row_one_css()`, tests, and docs. No model fields, JSON artifacts, sidecar files, or app contract changes.

4. **Safety rules sufficient?** The anchor, escaping, dedupe, cap, and index rules are sound. The `_strict_valid_local_article_paragraph_indices()` guard is reused correctly — once the `rendered_indices` dependency (Critical Issue2) is resolved.

5. **Tests sufficient?** Yes, once Critical Issues 2 and 3 are addressed. The CSS selector test, contract-stability extension, and local-anchor test collectively cover the required surface area.

6. **Simpler boundaries?** No simplifications needed. The plan's scope is already minimal. The critical fixes above are naming/wiring corrections, not scope changes.

---

### Recommendation

Fix the two critical issues (rename the bilingual body-source helper; explicitly thread `rendered_indices` through the panel call) before writing any production code. Update the bool-index test comment and confirm `_signal_briefing_local_article()` and `_html_between()`. All other items are straightforward and can be handled inline during implementation. The overall architecture is correct and ready to proceed once those fixes are made.
