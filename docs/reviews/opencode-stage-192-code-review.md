# Stage 192 Code Review

## Critical

None. The change is confined to the report builder/renderer layer
(`src/fashion_radar/reports.py`) and review documentation. No public model
shape changes, no new CLI command, no source acquisition, no
platform/social connector, no monitoring/scheduling, no demand proof, no
coverage verification, no compliance-review feature, no LLM summarization, and
no trend/heat/dashboard contract mutation. Source attribution is preserved.

## Important

None. The Stage 192 plan review caught the real Task 2 wording/test mismatch,
the rereview confirmed it was resolved, and the implementation plus tests now
match the reconciled wording exactly.

Verified scope items:

- Error capping in `_brief_item_for_source_health(...)` and
  `_brief_item_for_recent_run(...)` now routes through the existing
  `report_safe_snippet(...)` policy.
- `_source_caveat_items(...)` de-duplicates failed recent-run caveats when a
  source-health caveat already represents the same casefolded
  `(source_name, source_type)` source key.
- `_render_daily_brief(...)` uses `- No items in this section.` for empty
  sections inside a partially populated brief while preserving the global
  `- No daily brief items available.` fallback for fully empty briefs.
- `docs/reviews/opencode-full-project-review.md` was updated only in
  `## Current Follow-Up Status`; historical findings remain untouched.

## Minor

1. No focused test covers the `Last error:` omission path when the error field
   is empty or `None`. The branch is simple and non-blocking.
2. A capped snippet ending with `...` followed by the sentence period renders
   as `....` in Markdown. Harmless and consistent with the report-safe policy.
3. Two failed recent runs for the same source with no health row would still
   both appear. This is outside the Stage 192 de-dup scope and is only noted
   for awareness.

## Verdict

Approved. The implementation follows the Stage 192 spec/plan, stays within
scope, is covered by focused RED->GREEN tests, and passes the full verification
suite.
