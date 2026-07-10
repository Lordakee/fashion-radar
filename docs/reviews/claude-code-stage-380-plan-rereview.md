**Narrow Re-Review — Stage 380 Saved Local Article Related-Read Evidence Bridge Plan**

---

## Critical

None.

## Important

None.

**Disposition of opencode rereview finding:**
The one Important finding from `docs/reviews/opencode-stage-380-plan-rereview.md` — that `current_article: RowOneLocalArticle` was absent from the updated `_candidate(...)` signature — has been resolved in the current plan. Task 3 Step 2 (lines 418–429 of the plan) explicitly includes `current_article: RowOneLocalArticle` as a keyword-only parameter, and the call site in `build_row_one_saved_article_local_related_reads(...)` passes `current_article=current_article`. No gap remains.

The rest of the plan is consistent with the existing source:
- `_Candidate` extension, `_card` passthrough, and `build_row_one_saved_article_local_related_reads` loop all integrate without conflict.
- `_evidence_bridges` bridge-cap against `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`, dual-side paragraph validation, and fallback-to-no-bridge behavior are all correctly specified.
- Existing scoring, sort order, lane routing, and excluded-story logic are untouched.

END_OF_REVIEW
