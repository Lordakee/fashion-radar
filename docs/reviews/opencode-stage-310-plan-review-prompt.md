Review the Stage 310 ROW ONE saved text reader design and plan after Claude Code approval.

Repo: `/home/ubuntu/fashion-radar`
Design: `docs/superpowers/specs/2026-07-06-stage-310-row-one-saved-article-reader-design.md`
Plan: `docs/superpowers/plans/2026-07-06-stage-310-row-one-saved-article-reader-plan.md`
Claude review: `docs/reviews/claude-code-stage-310-plan-review.md`
Claude rereview: `docs/reviews/claude-code-stage-310-plan-rereview.md`

Check whether the plan is technically reasonable and ready for implementation.

Key constraints:
- Template/static-site only.
- Use existing `RowOneLocalArticle` fields and generated sidecars.
- Do not change source collection, extraction, schemas, `data/edition.json`, story IDs, detail routes, paragraph anchors, `row-one-app/v7`, `row-one-manifest/v1`, or `row-one-runtime/v1`.
- Avoid wording that implies full external article republication.
- Keep frozen/no-config uv verification and public `uv.lock` hygiene.

Return only:

## Verdict
Approve, Approve with Important fixes, or Reject.

## Critical Findings
- Finding, why it matters, concrete fix.

## Important Findings
- Finding, why it matters, concrete fix.

## Minor Findings
- Finding, concrete fix.

If a section has no findings, write `None.`. Do not modify files.
