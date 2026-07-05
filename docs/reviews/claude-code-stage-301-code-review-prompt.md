# Claude Code Stage 301 Code Review Prompt

You are reviewing the Stage 301 implementation in `/home/ubuntu/fashion-radar`.

Plan:
- `docs/superpowers/plans/2026-07-05-stage-301-row-one-daily-local-intelligence-plan.md`

Relevant review artifacts:
- `docs/reviews/claude-code-stage-301-plan-review.md`
- `docs/reviews/opencode-stage-301-plan-review.md`
- `docs/reviews/opencode-stage-301-plan-rereview.md`

Changed implementation/test/docs files:
- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/local_intelligence.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_local_intelligence.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`

Review objective:
- Check whether Stage 301 correctly adds a homepage Daily Local Intelligence section derived from saved local article sidecars.
- Check whether `data/local-intelligence.json` is written only when there is saved local article intelligence.
- Check whether `data/edition.json` and `row-one-app/v7` remain unchanged by the new local intelligence layer.
- Check whether rendering escapes all local article-derived text and safely accepts only valid detail links plus the exact `#local-article` fragment.
- Check whether the aggregation logic is deterministic, source-grounded, and compatible with existing generated-site cleanup.
- Check tests for meaningful coverage and identify gaps that could hide real bugs.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
