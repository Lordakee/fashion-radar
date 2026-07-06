# opencode Plan Rereview Prompt: Stage 311 Saved Text Digest

Use read-only review. Do not edit files.

Review only these files:

- `docs/superpowers/specs/2026-07-06-stage-311-row-one-saved-text-digest-design.md`
- `docs/superpowers/plans/2026-07-06-stage-311-row-one-saved-text-digest-plan.md`
- `docs/reviews/opencode-stage-311-plan-review.md`

Verify that the plan-review findings have been addressed:

1. Reference digest chips must render escaped reference names only, and the plan
   must say this explicitly.
2. Plain-article Read First fallback must synthesize the first nonblank
   paragraph index and render its existing `#local-article-paragraph-N` link.
3. The plan must keep the takeaway body even when all paragraph indices are
   invalid, rendering no paragraph links for that card.
4. Reference dedupe normalization must be explicit.
5. Stage 310 map-slice updates must clearly cover all existing slices that
   would otherwise include digest/reader markup.

Return:

- Critical
- Important
- Minor
- Verdict

Keep the result under 600 words. If no Critical or Important findings remain,
say the plan is approved for implementation.
