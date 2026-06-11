# Claude Code Stage 4 Plan Re-Review 2 Prompt

You are Claude Code re-reviewing the Stage 4 plan after the final scoring
formula fixes.

Repository: `/home/ubuntu/fashion-radar`

Prior reviews:

- `docs/reviews/claude-code-stage-4-plan-review.md`
- `docs/reviews/claude-code-stage-4-plan-rereview.md`

Updated plan file:

- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

Please verify that the remaining findings from the previous re-review are fixed:

1. `heat_score` formula is explicit and reproducible.
2. `growth_ratio = current_rate / baseline_rate` is defined.
3. `items.collected_at` is specified as first-seen and preserved on re-upsert.
4. Zero-current-mention entities are not mislabeled as `stable`.
5. Tests are planned for the heat score components and collected-at preservation.

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 4 implementation
- Approved after fixes
- Do not proceed
