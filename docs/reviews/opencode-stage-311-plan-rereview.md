# Stage 311 Plan Rereview (opencode)

Verified the opencode plan-review findings against the current spec and plan.

## Finding Resolution

1. **Reference chips render name only (was I1): Resolved.** Task 2 Step 2 now
   states each chip renders the escaped reference name only with
   `class="local-article-digest-chip"`, matching the `>The Row<` assertion in
   Task 1 Step 3.

2. **Read First fallback synthesizes paragraph index (was I2): Resolved.** Task
   2 Step 2 specifies the fallback synthesizes that paragraph's original index
   and renders its `#local-article-paragraph-N` link, satisfying the
   plain-article `paragraph-1` assertion.

3. **Takeaway body retained with all-invalid indices (was M3): Resolved.** Task
   2 Step 2 requires `_local_article_digest_takeaway` to still return the body
   with an empty `paragraph_indices` list when all supplied paragraph indices
   are invalid or point to blank paragraphs. Task 1 Step 5 enforces this.

4. **Dedupe normalization explicit (was M2): Resolved.** Task 2 Step 2 defines
   the key as `normalize_row_one_paragraph(ref.name).casefold()`, stripped
   casefolded `type`, and stripped casefolded `label`, preserving first-seen
   order.

5. **Map-slice coverage (was M1): Resolved.** Task 1 Step 6 states the general
   rule that slices bounded by `id="local-article-reader"` or
   `class="local-article-brief"` must be narrowed, while plain-article tests
   keep the no-map assertion.

## Critical

None.

## Important

None.

## Minor

**m1 - Digest placement relative to brief is under-locked.** Spec requires the
digest section to appear before `#local-article-brief`. The plan should include
a test assertion for `id="local-article-digest"` before
`id="local-article-brief"`.

**m2 - No dedicated test for the 4-chip reference cap.** The constant
`LOCAL_ARTICLE_DIGEST_MAX_REFERENCES = 4` is planned but no fixture supplies
more than four references to exercise the cap. This is a minor coverage gap.

**m3 - Saved-paragraph count helper name is not pinned.** The plan allows
`_local_article_saved_paragraph_count(article)` or an equivalent count. This is
acceptable if the chosen helper returns a nonblank-only count consistent with
`_local_article_rendered_paragraph_indices`.

## Test-Assertion Soundness

Rechecked brittle assertions: truncation, invalid-index filtering, dedupe count,
map chip ordering, and contract stability all remain sound.

## Verdict

Approved for implementation. All Critical and Important plan-review findings
are addressed. Remaining items are minor clarifications or coverage nits that
can be handled during implementation without blocking.
