
Final Stage 381 plan rereview — verifying remaining Critical/Important status after recorded fixes.

**C1 (singular count assertion):** Task 4 Step 2 asserts `"1 local read"` (singular), matching `_count_label(1, "local read", "local reads")`. Resolved.

**I1 (signal/source count asymmetry):** Data Contract prose states both counters are "displayed ... capped at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`"; builder sets `signal_count = len(signal_references)` and `source_count = len(source_names)`, both derived from capped display tuples. Resolved.

**I2 (duplicate import block):** Task 2 Step 1 reads "Update the existing import block to add:" listing only the two new symbols. Resolved.

**Residual dek field (m1 follow-up):** Both the Data Contract (lines 67–79) and the Task 3 Step 1 implementation dataclass (lines 331–342) omit `dek`. The dead field is removed; data model carries only rendered surfaces (`title`, `lead`) plus metrics. Resolved.

**Supporting Minor fixes already folded in:** Task 5 Step 2 explicitly assigns `renderable_cards = _renderable_saved_article_local_related_read_cards(related_reads.cards)` (m4 addressed); Task 6 Step 3 RED rationale is docs-only (m2 addressed); Task 8 Step 6 glob `docs/reviews/*stage-381*` covers rereview artifacts (m3 addressed). m5 hyphenation drift is cosmetic only and does not affect any test.

No remaining Critical or Important findings.

END_OF_REVIEW
