Checking each of the seven specific fix points against the current plan text:

**Singular count assertion (C1):** Task 4 Step 2 line 569 reads `assert "1 local read" in section_html`. Correct singular form. ✓

**Capped signal/source counts (I1):** Data Contract prose (lines 98–99) now says "displayed … capped at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`" for both. Builder code (Task 3 Step 1) sets `signal_count=len(signal_references)` and `source_count=len(source_names)`, both derived from the capped display tuples. Caps test is internally consistent: 4 unique refs → `signal_count == MAX_REFS == len(signal_references)`; 3 unique sources → `source_count == 3 == len(source_names)`. ✓

**Existing import block update (I2):** Task 2 Step 1 reads "Update the existing import block to add:" and lists only the two genuinely new symbols (`RowOneSavedArticleLocalRelatedReadEvidenceBridge`, `build_row_one_saved_article_local_related_read_connection_brief`). No duplicate block. ✓

**No dead dek field:** The Data Contract section (lines 65–79) does not define `dek`. The Task 3 Step 1 implementation code block still includes `dek: LocalizedText` in the dataclass — a discrepancy between spec and implementation snippet. The opencode rereview flags this as **Minor** (m1), not Critical or Important, because the normative Data Contract is the governing spec and an implementer following it would not add the field.

**Explicit renderable_cards assignment (Task 5 Step 2):** Lines 638–644 explicitly assign `renderable_cards = _renderable_saved_article_local_related_read_cards(related_reads.cards)` before passing it to both the brief builder and lane construction. ✓

**Docs-only RED rationale (Task 6 Step 3):** Line 949 reads "Expected: FAIL because the Stage 381 docs paragraphs are not yet present." — docs-only, renderer clause removed. ✓

**Rereview artifact staging (Task 8 Step 6):** `git add … docs/reviews/*stage-381*` glob covers all rereview artifacts (`*-plan-rereview.md`, `*-code-rereview.md`). ✓

The opencode rereview explicitly confirms C1, I1, and I2 are resolved. All remaining findings (m1–m5 in the opencode rereview) are Minor.

No remaining Critical or Important findings.

END_OF_REVIEW
