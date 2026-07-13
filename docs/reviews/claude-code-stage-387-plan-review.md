# Claude Code Stage 387 Plan Review

## Scope

- Design: docs/superpowers/specs/2026-07-13-daily-local-brand-product-people-signal-digest-design.md
- Plan: docs/superpowers/plans/2026-07-13-stage-387-daily-local-brand-product-people-signal-digest-plan.md
- Existing precedent: Stage 386 saved-text-takeaways builder, renderer, templates, and tests.

## Invocation

Claude Code ran before Stage 387 product-code changes with effort max,
read-only plan permissions, no session persistence, and Read/Grep/Glob/LS/Bash
tools.

## Completed Review Output

Verdict: APPROVED. No blockers were found.

The reviewer verified that the planned output types match existing
RowOneLocalArticleContentItem, RowOneReference, and
RowOneLocalArticleContentSection usage; the two-layer local href guard is
appropriate; homepage placement is constrained between Daily Saved Text
Takeaways and Daily Local Saved Article Organizer; first-seen ordering avoids
a coverage ranking; and builder/render/workflow/docs tests cover the important
surface.

Residual risk 1: the plan referenced _valid_article without showing the strict
article.story_id == story.id check. Without that check, a wrong saved sidecar
could silently be accepted.

Residual risk 2: the plan did not name the exact template fragment rule. A
wrong regex could accept a paragraph anchor or reject a valid saved
content-section anchor.

## Disposition

Both residual risks were verified against the Stage 386 implementation and
corrected in the Stage 387 design and plan before implementation:

- _valid_article must reject a missing, unsafe, or mismatched local article,
  and focused tests must include a third mismatched sidecar beside two valid
  contributors.
- the template safe-href helper must use the existing
  _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE and reject the paragraph fragment
  pattern and every other fragment.

No unresolved plan-review finding remains.
