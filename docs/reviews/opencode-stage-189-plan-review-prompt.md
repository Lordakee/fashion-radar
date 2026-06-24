# Stage 189 Plan Review Prompt

Review the Stage 189 design and implementation plan before coding.

Repository: `/home/ubuntu/fashion-radar`

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-189-review-capture-hygiene-coverage-design.md`
- `docs/superpowers/plans/2026-06-24-stage-189-review-capture-hygiene-coverage-plan.md`
- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `docs/REVIEW_PROTOCOL.md`
- `docs/reviews/opencode-full-project-review.md`

Review questions:

1. Does the plan correctly identify real release-hygiene coverage gaps for
   non-stage local opencode review records and timeout-stub staged records?
2. Will the planned RED tests fail before the predicate/timeout changes and
   pass after the planned implementation?
3. Does the planned implementation preserve the Stage 158 legacy exclusion and
   prompt-file exclusion?
4. Is sanitizing `docs/reviews/opencode-full-project-review.md`, replacing the
   Stage 188 code-review timeout record, and adding a Stage 188 release
   rereview sufficient and appropriately scoped?
5. Is it reasonable to treat this as a prerequisite maintenance node before the
   next product node, provided the plan explicitly directs the next node to
   source-liveness diagnostics?
6. Does the plan avoid product runtime changes, new collectors, social
   connectors, or further external/community handoff expansion?

Report findings under:

- Critical
- Important
- Minor

Critical or Important findings must block implementation. If the plan is
acceptable, say it is approved for implementation.

Start the response exactly with:

```text
# Stage 189 Plan Review
```

Do not include process chatter, command logs, ANSI output, or tool-status lines.
