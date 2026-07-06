# Stage 316 Design and Implementation Plan Review

Based on thorough review of both documents against the codebase patterns, here are the findings ordered by severity:

## ✅ No Critical or Important Issues

The Stage 316 scope is technically sound, preserves all boundaries, and aligns with the progression from "links only" toward locally organized article content.

## Minor Issues

### 1. Stage 315 docs test boundary will silently expand (Minor)

**Issue:** The plan inserts Stage 316 docs between Stage 315 and Stage 310, but doesn't update the existing `test_row_one_docs_describe_article_readiness_boundary()` function.

**Current Stage 315 test:**
```python
readme_stage_315 = readme[
    readme.index("Stage 315 adds ROW ONE article readiness diagnostics") : readme.index("Stage 310 adds")
]
```

**After Stage 316 insertion:** This slice will now span both Stage 315 and Stage 316 text. The test still passes (Stage 316's text doesn't contain any of Stage 315's forbidden phrases), but the test's precision is undermined.

**Fix:** In Task 3, update the Stage 315 test to use:
```python
readme_stage_315 = readme[
    readme.index("Stage 315 adds ROW ONE article readiness diagnostics") : readme.index("Stage 316 adds")
]
```

**Location:** `tests/test_row_one_docs.py:275-327`

---

### 2. `paragraph_indices` sourcing logic underspecified (Minor)

**Issue:** The design says cards carry "valid paragraph indices" from content section items, but doesn't specify the aggregation logic when a content section has multiple items.

**Current ambiguity:** Does the builder:
- Aggregate all `paragraph_indices` from all items in the section?
- Use only the first item's indices?
- Use only the lead item's indices?

**Recommendation:** The builder should aggregate and deduplicate all `paragraph_indices` from items within the selected content section, preserving order. This matches the reference deduplication pattern in `saved_article_briefs.py:114-136`.

**Test gap:** Task 1 test list doesn't explicitly cover multi-item sections with distinct paragraph index sets.

---

### 3. Content section anchor index N underspecified (Minor)

**Issue:** The design says cards link to `details/...html#local-article-content-section-N` but doesn't explicitly define how N is computed.

**Clarification needed:** N is the zero-based position of the content section in `article.content_sections` (e.g., if `takeaways` is at index 0, N=0).

**Evidence from templates.py:** Function `_local_article_content_section_anchor(position: int)` at line 3590 returns `f"local-article-content-section-{position}"`, confirming N is the list position.

**Recommendation:** Add a note in the builder docstring that anchor indices correspond to `enumerate(article.content_sections)` positions.

---

### 4. Group-level `dek` strings not specified (Nit)

**Issue:** `RowOneSavedArticleContentOrganizationGroup` has a `dek: LocalizedText` field, but the design only specifies the top-level section dek (for "Saved Article Content Organization"). Individual group deks (for "Read First", "People & Brands", etc.) aren't specified.

**Recommendation:** The builder can use concise generic deks like:
- Read First: `{zh: "关键要点", en: "Key takeaways from saved articles"}`
- People & Brands: `{zh: "品牌与人物", en: "Brands and people mentioned"}`
- Products: `{zh: "产品信号", en: "Product signals"}`
- Source Structure: `{zh: "来源结构", en: "Source structure signals"}`

Not blocking—sensible defaults are acceptable.

---

### 5. `section_label` vs `section_title` field naming (Nit)

**Issue:** The card dataclass has both `section_title` (edition section title, e.g. "Top Stories") and `section_label` (content section title, e.g. "Takeaways"). The naming could be clearer.

**Context:** This follows the existing pattern of carrying both story-level and content-level metadata, but `section_label` for what is actually "content section title" is slightly non-obvious.

**Recommendation:** Add a docstring or comment clarifying:
- `section_title`: Edition section (from `edition.sections`)
- `section_label`: Content section type (from `RowOneLocalArticleContentSection.title`)

Not blocking—the distinction is inferable from usage.

---

### 6. Missing `"does not write a new json artifact"` in Stage 316 docs phrases (Nit)

**Issue:** Stages 312 and 313 docs tests include `"does not write a new json artifact"` in their expected phrases. Stage 316's expected phrases list doesn't include this, though the workflow test explicitly guards the JSON contract boundaries.

**Recommendation:** Add `"does not write a new json artifact"` to the Stage 316 expected docs phrases in Task 3 Step 1, after `"does not change schemas"`.

Not blocking—the workflow test already enforces the boundary.

---

## Evaluation Summary

### 1. **Is the Stage 316 scope technically sound?**
✅ **Yes.** The scope directly addresses organizing existing saved local article `content_sections` into a homepage presentation layer. Architecture is sound: pure builder module → `render_row_one_site()` → `render_index_html()`.

### 2. **Does the plan preserve boundaries?**
✅ **Yes.** All contracts preserved:
- ✅ `row-one-app/v7` unchanged
- ✅ `data/edition.json`, `data/manifest.json`, `data/runtime.json` unchanged
- ✅ Schemas unchanged
- ✅ No source collection, extraction, scoring, LLM calls, connectors, or compliance-review
- ✅ Detail routes and paragraph anchors untouched

Task 2 workflow test explicitly guards all JSON contracts (lines 125-129).

### 3. **Are builder semantics deterministic and safe?**
✅ **Yes.** Filtering logic mirrors `saved_article_briefs.py`:
- Current edition stories only
- `article.story_id == story.id` check
- `safe_local_article_story_id()` validation
- `is_safe_row_one_detail_path()` validation
- Nonblank paragraph requirement
- Deterministic group order and card caps

### 4. **Are tests sufficient?**
✅ **Mostly yes.** Tests cover:
- ✅ Stale sidecar exclusion
- ✅ Mismatched `article.story_id`
- ✅ Unsafe paths and invalid IDs
- ✅ Blank paragraph exclusion
- ✅ Contract creep (JSON artifact guards)

**Minor gap:** No explicit test for multi-item content sections with distinct paragraph index sets.

### 5. **Is the homepage rendering insertion point appropriate?**
✅ **Yes.** Placement after saved article briefs (Task 2 Step 3, line 156) maintains the homepage narrative: coverage → briefs → content organization → sections.

### 6. **Are there blocking issues?**
✅ **No blocking issues.** All 6 minor issues can be addressed during implementation without redesign.

---

## Recommendation

**Proceed with implementation.** Address Minor Issues #1-2 before Task 3 commit. Issues #3-6 are cosmetic and can be resolved during Task 1-2 implementation or left as-is with clarifying comments.
