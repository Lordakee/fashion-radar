# Stage 199 Plan Rereview Prompt

Rereview the revised Stage 199 plan:

`docs/superpowers/plans/2026-06-25-stage-199-aggregate-match-evidence-report-plan.md`

Previous review artifact:

`docs/reviews/opencode-stage-199-plan-review.md`

## What Changed Since First Review

The plan was revised to address all required plan changes:

- First-run smoke instructions now explicitly update `tests/test_first_run_smoke.py::report_payload()` entity fixtures with full 9-key `match_evidence` objects.
- First-run smoke validator instructions now require `match_evidence` key presence, exact 9-key shape, non-negative integer `matched_items` for every expected entity, and `matched_items >= 1` only for `The Row`.
- Task 2 now includes duplicate tie-break coverage with equal confidence and lexicographic reason ordering.
- Task 2 now includes a sub-threshold confidence row at `confidence=0.3`.
- Docs placement now says to insert `## Match Evidence` after `## Formula` and before `## Labels`.
- Markdown rendering now explicitly keeps the range form when `min_confidence == max_confidence`, e.g. `confidence 1.00-1.00 avg 1.00`.
- Review capture snippets now use `sed -n '1,400p'`.
- The evidence helper now explicitly filters by both `entity_name` and `entity_type`.
- The model test now uses the `EntityMatchEvidence` import via `isinstance(...)`, avoiding an unused import.

## Review Questions

1. Are the previous required plan changes fully resolved?
2. Is filtering evidence by both `entity_name` and `entity_type` correct and sufficient?
3. Are the revised tests still practical and not over-brittle?
4. Are there any new Critical or Important blockers before implementation?

Start the response exactly with:

```markdown
# Stage 199 Plan Rereview
```

Then include:

- Verdict
- Critical findings
- Important findings
- Minor findings
- Resolution status for previous required changes
- Required plan changes before implementation

Do not include tool-status chatter, live command transcripts, duplicated drafts, or process narration.
