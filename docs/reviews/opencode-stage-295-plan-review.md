# opencode Stage 295 Plan Review

Fallback review since Claude Code timed out
(`docs/reviews/claude-code-stage-295-plan-review.md`). GLM 5.2 max variant.
No files edited.

## Findings

### Important

**I-1. Task 2 Step 3 under-specifies the existing list-equality update.**
`tests/test_row_one_app_contract.py` asserts `brief["summary_points"] == [...]`
as a strict list equality. The plan says to include the heat-watch point after
the briefing-topic point and that the topic-mix point "may also appear" if the
test only has a brand topic. Given the fixture has one explicit `The Row` brand
reference, the topic-mix point will be emitted and must be specified. The plan
also needs to state the exact insertion order.

Fix: replace Task 2 Step 3 with the full updated expected list in order.

### Minor

**M-1. Task 4 Step 4/5 test-name inconsistency.** Step 4 offers updating the
existing Stage 286 docs test or adding a new Stage 295 docs test, but Step 5
hard-codes the new Stage 295 test name. Pick one path and align the focused
command.

**M-2. RED framing for `tests/test_row_one_briefing_topics.py` is inaccurate.**
The new unit test is regression coverage for previously untested
`briefing_topics_payload`, not a RED test.

**M-3. No explicit omission-path test.** The branches where stories exist but
`heat_delta <= 0`, or stories exist but no explicit references, are covered only
indirectly. Consider one explicit absence test.

**M-4. `_edition_brief_heat_watch_point` boolean edge case.** The planned
`isinstance(value, int)` check would admit `True` because `bool` subclasses
`int`. `_story_payload` emits int-or-None today, but the defensive form should
exclude bool.

**M-5. Task 5 Step 3 grep exit code.** `rg` exits 1 when the day's local data
has no topic refs or positive deltas. Use `|| true` or note that exit 1 is
acceptable on sparse-data days.

## Review Questions

**Q1: Is keeping `row-one-app/v7` technically reasonable?** Yes.
`schemas/row-one-app.schema.json` types `summary_points` as an array of
localized text with no `maxItems` or string enum. Appending more localized text
entries is fully in-contract. No contract bump is warranted.

**Q2: Are helper boundaries appropriately narrow?** Yes. The planned
`_edition_brief_topic_mix_point(...)` and `_edition_brief_heat_watch_point(...)`
helpers are pure, local to `render.py`, and reuse existing summary point
rendering.

**Q3: Are RED tests sufficient and correctly scoped?** Mostly yes. Positive
app-payload and static-render paths are covered, and the new direct
`briefing_topics_payload` unit test fills a real gap. I-1 needs to be resolved
because the existing strict list equality must be updated exactly.

**Q4: Are docs/test updates enough for a GitHub-ready node?** Yes once I-1 and
M-1 are resolved. The plan keeps generated reports ignored, uses frozen uv
commands, and avoids scraping, platform APIs, app UI, and compliance-review
features.

## Verdict

The plan is implementable after fixing I-1. The minor findings can be handled
during the same plan revision or implementation.
