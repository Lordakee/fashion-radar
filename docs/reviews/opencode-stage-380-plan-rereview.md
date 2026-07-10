# Stage 380 Plan Rereview - opencode

## Critical

None.

## Important

None.

The prior Important finding is resolved: Task 3 Step 2 adds `current_article: RowOneLocalArticle` to the `_candidate(...)` signature, and the loop call site passes `current_article=current_article`. All inputs required by `_evidence_bridges(...)` are now available inside `_candidate(...)`: `current_article`, candidate `article`, validated `base_href`, `current_ref_entries_by_key`, candidate `entries`, and `shared_keys`.

The planned render-time href guards are feasible because `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`, `_safe_saved_article_local_related_read_href`, `_esc`, and `local_article_paragraph_anchor` already exist. The dataclass field ordering is valid for both `_Candidate` and `RowOneSavedArticleLocalRelatedReadCard`.

END_OF_REVIEW
