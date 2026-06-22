# Stage 159 Plan Rereview Prompt

Review the updated Stage 159 design and implementation plan after the first
plan review found C1 and I1.

Files to review:

- `docs/superpowers/specs/2026-06-23-stage-159-review-artifact-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-23-stage-159-review-artifact-hygiene-gate-plan.md`
- First review: `docs/reviews/opencode-stage-159-plan-review.md`

First-review findings to verify:

1. C1: Bare U+2192 substring matching could reject legitimate review prose.
   The updated plan should only flag UI markers when the stripped line starts
   with a status glyph or `build middle-dot`, and should include a RED test
   proving inline arrow prose is accepted.
2. I1: The path regex missed numbered rereviews such as `-rereview-2.md`.
   The updated plan should match `rereview-N` files and include a RED test for
   a numbered rereview artifact.
3. Minor follow-ups: empty-output RED test, prompt-exclusion test selected by
   the focused `-k` filter, direct release-hygiene script in the final release
   gate, release-review artifact before commit, and `chore:` commit prefix.

Review questions:

1. Are C1 and I1 fully resolved?
2. Are the remaining tests and implementation snippets internally consistent?
3. Is the scope still process-only with no product/runtime/social collection,
   scraping, platform API, scheduling, monitoring, or compliance-review product
   behavior?
4. Is the plan safe to implement with no critical or important findings?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
