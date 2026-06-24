# Stage 188 Plan Review Prompt

Review the Stage 188 plan for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 188 Plan Review
```

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-design.md`
- `docs/superpowers/plans/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-plan.md`
- `tests/test_collectors_runner.py`
- `tests/test_workflows.py`
- `src/fashion_radar/collectors/runner.py`
- `src/fashion_radar/workflows.py`
- `docs/PROJECT_BRIEF.md`
- `README.md`
- `docs/architecture.md`
- `docs/REVIEW_PROTOCOL.md`
- `CHANGELOG.md`
- `docs/reviews/opencode-full-project-review.md`

Review questions:

1. Does the plan take the smallest sound path to fix proxy-sensitive test
   isolation without broadening product behavior, and does it correctly keep
   the fix test-side only?
2. Is the RED/GREEN approach meaningful for the collector/workflow proxy issue?
3. Are the proposed roadmap/documentation corrections scoped appropriately and
   aligned with the full-project review?
4. Does the plan correctly redirect the next-stage priority toward source
   coverage, source-health diagnostics, matching quality, and optional
   summarization?
5. Does the plan avoid adding new external/community handoff features or other
   out-of-scope product behavior?

Report findings under Critical, Important, and Minor. Critical or Important
findings must include exact file/line references and concrete fixes. If the plan
is acceptable, say it is approved for implementation.
