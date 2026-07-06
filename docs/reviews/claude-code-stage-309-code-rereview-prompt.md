Re-review the Stage 309 ROW ONE newsroom digest polish implementation after code-review fixes.

Repo: `/home/ubuntu/fashion-radar`
Original code review: `docs/reviews/claude-code-stage-309-code-review.md`

Fixes to verify:
- Removed the dead `_story_article_item` helper from `src/fashion_radar/row_one/local_intelligence.py`.
- Restored `uv.lock` to public PyPI / files.pythonhosted URLs with no tracked lockfile diff.
- Added an implementation note to `docs/superpowers/plans/2026-07-05-stage-309-row-one-newsroom-digest-polish-plan.md` explaining why the final cluster key uses normalized source name plus full saved body rather than the early headline/first-paragraph sketch.

Please verify:
- No callers or tests rely on `_story_article_item`.
- `strongest_reads` and `heat_movers` still use the aggregate item path.
- The implementation note does not contradict the shipped behavior.
- No remaining Critical/Important correctness, safety, schema-contract, or release-hygiene issues are visible in the Stage 309 changed files.

Return only:

## Verdict
Approve, Approve with Important fixes, or Reject.

## Remaining Critical/Important Findings
- Finding, why it matters, concrete fix.

## Minor Findings
- Finding, concrete fix.

Do not modify files.
