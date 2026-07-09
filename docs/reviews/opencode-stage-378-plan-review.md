## Stage 378 Plan Review (opencode)

**Critical**

No remaining Critical findings. The prior C1 (`_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` undefined in the builder) is genuinely resolved: the updated `_related_read_lane_key` does only `normalize_row_one_paragraph(...).casefold()` text matching, and the File Map explicitly forbids any href-validation layer in the builder. The reason strings produced by `_reason` classify cleanly: shared-signal uses ASCII/fullwidth colons that `normalize_row_one_paragraph` preserves, so all three reason types map to a lane today. No unsafe href can reach output because lane cards still route through `_render_saved_article_local_related_read_card` -> `_safe_saved_article_local_related_read_href`. Existing render tests should continue to hold: the default-card test switches to the lane path but its assertions still hold; the escape/mismatched tests fall back to the flat grid through unknown or unsafe reasons.

**Important**

**I1: Lane classification is a parallel string-parsing layer over `_reason`, with silent card-loss on drift.**
`_related_read_lane_key` re-derives the lane by prefix/exact-matching the human-readable `_reason` text. If `_reason` and `_related_read_lane_key` ever drift, affected cards return `None` and could be omitted from lanes. Because a partial drift can hide cards unless the renderer detects incomplete lane coverage, the plan should explicitly fall back to the flat grid whenever any renderable card is not represented by a lane.

**I2: Artifact-stem denylist is not updated with lane stems.**
Stage 377 added saved/local/related-read artifact stems to the generated-artifact loop. The Stage 378 docs paragraph claims it does not create lane JSON/HTML artifacts, but the plan only extends the contract-payload denylist. Add `saved-local-article-related-read-lanes`, `local-article-related-read-lanes`, `related-read-lanes`, and their snake-case forms to the artifact-stem loop.

**Minor**

**m1: `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS_PER_LANE = 3` is non-truncating for the current single caller.** Upstream `build_row_one_saved_article_local_related_reads` already caps total cards at 3, so no lane can hold more than 3 today. This is defensible as a pure-function guard for direct fixtures or future callers.

**m2: Render integration snippet leaves f-string reassembly implicit.** Task 4 Step 3 shows `body_html` computation but not the full f-string with correct leading whitespace, nor an explicit instruction to keep the existing `if not cards: return ""` guard before computing lanes. Spell out the reassembly and guard preservation.

**m3: Stage 378 docs test lacks an ordering assertion.** Mirror the Stage 377 pattern by asserting the Stage 378 paragraph appears before Stage 377 in both docs.

**m4: File Map promises a Stage 378 generated-site-only workflow monkeypatch test that Task 5 never adds.** The existing Stage 377 test already monkeypatches `_render_saved_article_local_related_reads`, which neutralizes the entire section including lanes. Either add a separate builder-level monkeypatch test or trim the File Map claim.

**m5: Fourth copy of the lane-grouping idiom.** The cards-by-lane pattern already exists in several ROW ONE modules. This is acceptable because it does not duplicate an existing ROW ONE section or contract/route/schema surface.

**Boundary confirmation:** Generated-site-only scope is sound. Rendering stays inside the existing `saved-article-local-related-reads` section on `articles/<story-id>.html`, no new JSON/HTML/route/schema/contract field is added, safe sibling-href handling is preserved end-to-end, and the feature does not duplicate any existing ROW ONE section or lane surface.

END_OF_REVIEW
