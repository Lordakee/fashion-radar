## Stage 328 Plan Review

### Critical

1. **Index bounds safety in `_paragraph_excerpt()`** (Plan lines 273-281)

   The `_paragraph_excerpt()` function accesses `article.paragraphs[index]` and `article.paragraphs_zh[index]` directly without type or bounds checking:
   
   ```python
   en = article.paragraphs[index] if index < len(article.paragraphs) else ""
   zh = article.paragraphs_zh[index] if index < len(article.paragraphs_zh) else ""
   ```
   
   However, this function receives `paragraph_indices` from `_referenced_paragraph_indices()` which returns `tuple[object, ...]` - containing bools, strings, negative ints, etc. The function iterates these raw values without the type filtering that `_strict_valid_saved_signal_paragraph_indices()` provides.
   
   **Issue**: If `index` is `True`, `"2"`, or a negative int, the bounds check `index < len(article.paragraphs)` will fail or behave incorrectly (bools are ints in Python, strings will raise TypeError).
   
   **Fix**: Add type checking before bounds checking:
   ```python
   for index in paragraph_indices:
       if isinstance(index, bool) or not isinstance(index, int):
           continue
       if index < 0 or index >= len(article.paragraphs):
           continue
       # ... rest of logic
   ```

2. **Missing test coverage for whitespace-only item bodies** (Task 1)

   The test suite includes tests for missing item bodies (fallback to paragraph) but doesn't test what happens when an item has a body that is only whitespace after normalization. According to the design, `normalize_row_one_paragraph()` would strip this to empty string, and `_localized_excerpt()` checks `if not en_text and not zh_text: return None`.
   
   **Issue**: The behavior is correct but untested. A hostile or malformed item with `body=LocalizedText(en="   ", zh="   ")` should fall back to paragraph excerpts, not return None.
   
   **Fix**: Add test case:
   ```python
   def test_saved_signal_index_support_excerpt_falls_back_from_blank_body() -> None:
       story = _story("blank-body-1234567890", "Blank body signal")
       index = build_row_one_saved_signal_index(
           _edition(story),
           {
               story.id: _article(
                   story.id,
                   paragraphs=["Fallback paragraph."],
                   content_sections=[
                       _section(
                           "entities",
                           "People & Brands",
                           items=[
                               _item(
                                   "The Row",
                                   body="   ",
                                   body_zh="  ",
                                   paragraph_indices=[0],
                                   references=[_signal_ref("The Row")],
                               )
                           ],
                       )
                   ],
               )
           },
       )
       
       assert index is not None
       support = index.entries[0].supports[0]
       assert support.excerpt is not None
       assert support.excerpt.en == "Fallback paragraph."
   ```

### Important

1. **Render test doesn't verify None excerpt handling** (Task 2, Step 1)

   The render test verifies that excerpts appear and are escaped, but doesn't verify that when `support.excerpt is None`, no empty `<p class="saved-signal-index-support-excerpt">` element is rendered.
   
   **Issue**: The implementation uses early return `if excerpt is None: return ""`, but this isn't tested. A regression could render empty paragraphs.
   
   **Fix**: Add assertion in render test or new test case:
   ```python
   # Build index with a support that has no excerpt
   # Assert "saved-signal-index-support-excerpt" not in rendered HTML for that support
   ```

2. **Documentation stage ordering assumption** (Task 3, Step 3)

   The docs test verifies that Stage 328 description appears and contains expected wording, then checks the text between Stage 328 and Stage 327 for drift phrases. This assumes Stage 328 appears BEFORE Stage 327 in document order.
   
   **Issue**: The test uses:
   ```python
   stage = normalized[
       normalized.index("stage 328 adds generated-site only evidence excerpts") :
       normalized.index("stage 327 adds a generated-site only row one")
   ]
   ```
   
   If Stage 328 is accidentally placed AFTER Stage 327 (wrong chronological order), this will capture the wrong text or raise ValueError.
   
   **Fix**: Add explicit ordering assertion:
   ```python
   stage_328_pos = normalized.index("stage 328 adds generated-site only evidence excerpts")
   stage_327_pos = normalized.index("stage 327 adds a generated-site only row one")
   assert stage_328_pos < stage_327_pos, "Stage 328 must appear before Stage 327"
   ```

3. **Workflow contract test doesn't verify positive case** (Task 2, Step 1)

   The workflow test verifies excerpts DON'T appear in JSON contracts and DON'T create new artifacts, but doesn't verify they DO appear in rendered `articles/index.html`.
   
   **Issue**: A regression could remove excerpt rendering entirely while still passing the contract tests.
   
   **Fix**: Add positive assertion in `test_workflows.py`:
   ```python
   articles_html_path = output_dir / "articles" / "index.html"
   if articles_html_path.exists():
       articles_html = articles_html_path.read_text(encoding="utf-8")
       # If there are saved signals with bodies/paragraphs, verify excerpt appears
       if "saved-signal-index-support-row" in articles_html:
           assert "saved-signal-index-support-excerpt" in articles_html
   ```

### Medium

1. **Excerpt capping edge case not tested** (Task 1, Step 1)

   The test `test_saved_signal_index_support_excerpt_is_capped()` uses a body with 80 repetitions of "The Row signal" (14 chars each = 1120 chars), which will definitely trigger capping. But it doesn't test the edge case where text is exactly 220 chars (no truncation) vs 221 chars (triggers "..." appending).
   
   **Issue**: The capping logic is `if len(normalized) <= SAVED_SIGNAL_INDEX_EXCERPT_CHARS: return normalized`. An off-by-one error could cause 220-char excerpts to be truncated.
   
   **Fix**: Add test with exactly 220 and 221 characters:
   ```python
   def test_saved_signal_index_support_excerpt_capping_edge_cases() -> None:
       story = _story("edge-1234567890", "Edge")
       # Exactly 220 chars - should NOT be capped
       body_220 = "a" * 220
       index_220 = build_row_one_saved_signal_index(...)
       assert len(index_220.entries[0].supports[0].excerpt.en) == 220
       assert not index_220.entries[0].supports[0].excerpt.en.endswith("...")
       
       # 221 chars - should be capped to 217 + "..."
       body_221 = "a" * 221
       index_221 = build_row_one_saved_signal_index(...)
       assert len(index_221.entries[0].supports[0].excerpt.en) == 220
       assert index_221.entries[0].supports[0].excerpt.en.endswith("...")
   ```

2. **CSS placement vague** (Task 2, Step 3)

   The plan says "Add CSS near the existing `.saved-signal-index-*` rules" but doesn't specify the exact insertion point. The grep output shows multiple saved-signal-index rules spanning lines 1251-1364.
   
   **Issue**: "Near" is ambiguous. Should be after `.saved-signal-index-support-meta` for logical grouping.
   
   **Fix**: Change instruction to:
   ```markdown
   Add CSS immediately after the `.saved-signal-index-support-meta` rule (around line 1356):
   ```

3. **Item body iteration stops at first match** (Plan line 261-268)

   The `_item_body_excerpt()` function returns the first item with a non-None body that produces a valid excerpt. This is reasonable, but the design doc doesn't explicitly state this "first match" behavior for multiple items supporting the same signal.
   
   **Issue**: If the first item has an item body and the second item has a better/longer body, the second is ignored. This is probably fine (simpler logic), but should be tested/documented.
   
   **Fix**: Add test case:
   ```python
   def test_saved_signal_index_support_excerpt_uses_first_matching_item_body() -> None:
       story = _story("multi-item-1234567890", "Multi-item")
       index = build_row_one_saved_signal_index(
           _edition(story),
           {
               story.id: _article(
                   story.id,
                   paragraphs=["Paragraph."],
                   content_sections=[
                       _section(
                           "entities",
                           "People & Brands",
                           items=[
                               _item("First", body="First body wins.", paragraph_indices=[0], references=[_signal_ref("The Row")]),
                               _item("Second", body="Second body ignored.", paragraph_indices=[0], references=[_signal_ref("The Row")]),
                           ],
                       )
                   ],
               )
           },
       )
       
       assert index.entries[0].supports[0].excerpt.en == "First body wins."
   ```

### Minor

1. **Review output limit may truncate** (Task 4, Step 3)

   The plan uses `sed -n '1,500p'` to limit review output to 500 lines. For a comprehensive code review, this might be insufficient.
   
   **Recommendation**: Increase to 1000 lines or add a note about checking the full tempfile if needed.

2. **Commit message could be more specific** (Task 4, Step 5)

   The commit message "Stage 328: add row one saved signal evidence excerpts" is good but could clarify the location: "add row one saved signal evidence excerpts to saved signal index".
   
   **Recommendation**: Update commit message for precision.

3. **Test helper location** (Task 1, Step 1)

   The test uses `_story()`, `_edition()`, `_article()`, `_section()`, `_item()`, and `_signal_ref()` helpers. These exist in the current test file (verified from reading test_row_one_saved_signal_index.py), so this is fine. But the plan doesn't mention they're already defined.
   
   **Recommendation**: No change needed, but for clarity could note "using existing test helpers" in Step 1.

4. **Chinese fallback test name mismatch** (Plan line 132)

   Test function name is `test_saved_signal_index_support_excerpt_uses_english_when_zh_missing` but it tests paragraph-level Chinese fallback, not item body Chinese fallback.
   
   **Recommendation**: This is fine - the behavior applies to both sources. No change needed.

### Summary

**Feasibility**: The plan is feasible with the current architecture. The dataclass extension and template modification points are correct.

**TDD Completeness**: The RED/GREEN pattern is sound, but Critical findings #1 and #2 identify gaps in bounds checking and whitespace handling that could cause runtime errors.

**Contract Safety**: Well-protected. The plan explicitly tests for absence of new JSON keys and artifacts.

**Frozen Surface Safety**: Excellent. The plan correctly avoids all prohibited changes (schemas, contracts, new pages, LLM calls, etc.).

**Recommendation**: Address Critical findings before implementation. Important and Medium findings should be fixed but won't block basic functionality.
