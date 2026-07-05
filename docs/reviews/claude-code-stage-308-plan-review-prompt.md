You are reviewing the Stage 308 implementation plan for the `fashion-radar` repo.

Repo: `/home/ubuntu/fashion-radar`
Plan file: `docs/superpowers/plans/2026-07-05-stage-308-row-one-site-integrity-plan.md`

Context:
- The project is building ROW ONE, a daily local fashion intelligence website.
- The current node should improve generated-site reliability, especially local saved article/detail content and preflight checks.
- Do not add compliance-review product features.
- Do not change source collection, ranking, matching, scoring, sorting, story IDs, schemas, or `row-one-app/v7`.
- The plan must keep `row-one status` read-only: no rebuild, no writes, no server startup, no external network probes.
- Dependencies and lockfile should remain frozen; public `uv.lock` must not be rewritten to local mirror URLs.

Please review the plan for:
1. Feasibility and correctness against the current codebase.
2. Whether the scope is tight enough for a single node.
3. Whether any planned checks are brittle, flaky, over-scoped, or likely to fail legitimate generated sites.
4. Whether the first-run HTTP smoke design is safe and not too flaky.
5. Whether the test plan is sufficient and not duplicative.
6. Whether docs language correctly says CLI-only preflight and no schema/app contract change.

Return findings in this format:

## Verdict
Approve, Approve with Important fixes, or Reject.

## Critical Findings
- File/step reference, issue, why it matters, concrete fix.

## Important Findings
- File/step reference, issue, why it matters, concrete fix.

## Minor Findings
- File/step reference, issue, why it matters, concrete fix.

## Suggested Plan Adjustments
- Concrete edits to the plan if needed.

Do not modify files.
