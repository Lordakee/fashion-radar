Re-review the revised Stage 337 plan for Fashion Radar / ROW ONE.

Goal: confirm the prior plan-review issues are resolved before implementation.

Files to inspect:
- docs/superpowers/specs/2026-07-08-stage-337-row-one-saved-article-reference-atlas-design.md
- docs/superpowers/plans/2026-07-08-stage-337-row-one-saved-article-reference-atlas-plan.md
- docs/reviews/claude-code-stage-337-plan-review.md
- docs/reviews/opencode-stage-337-plan-review.md
- tests/test_row_one_render.py

Specific checks:
1. The plan no longer relies on ambiguous `_theme_digest_local_article()` behavior and explicitly uses `_reference_atlas_local_article()`.
2. The plan includes a CSS selector sentinel test for saved article reference atlas selectors.
3. The plan defines the plural `_library_with_safe_stories(*story_ids)` helper expectation.
4. The spec/plan clearly state canonical bucket order and first-seen tie-breaks.
5. No generated-site-only / JSON contract / source collection / fetching / extraction / scoring / ranking / LLM / connector / scheduling / deployment / compliance boundaries were weakened.

Return Critical / Important / Minor findings. If no Critical or Important findings remain, say Safe to implement.
