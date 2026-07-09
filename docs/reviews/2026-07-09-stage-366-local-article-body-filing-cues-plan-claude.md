# Stage 366 Local Article Body Filing Cues Plan Review

Reviewer: Claude Code subagent
Date: 2026-07-09
Scope: `docs/superpowers/specs/2026-07-09-stage-366-local-article-body-filing-cues-design.md`, `docs/superpowers/plans/2026-07-09-stage-366-local-article-body-filing-cues-plan.md`

## Initial Result

Blocking changes required before implementation.

## Findings

- Cover section-level paragraph references explicitly. The plan described section/item paragraph indices in the design but Task 2 only mentioned item paragraph indices.
- Fix the focused pytest command. Multiple `-k` flags in one pytest invocation could skip intended focused tests.
- Clarify the monkeypatch guard. The plan said to monkeypatch `_render_local_article_body_filing_cue` to `""`, which could mean replacing a callable with a string.

## Resolution

- Updated the spec and plan to require mapping both section-level `section.paragraph_indices` and item-level `item.paragraph_indices`.
- Updated label rules: section-level references use section titles; item-level references use item labels and fall back to section titles when labels are blank.
- Replaced the focused test command with one combined `-k` expression across all focused files.
- Clarified that workflow monkeypatching must use a callable: `lambda _entries: ""`.

## Follow-Up

The revised plan should be re-reviewed before implementation.

## Re-Review Result

READY FOR IMPLEMENTATION.

The revised plan resolves the prior blockers:

- Section-level and item-level paragraph references are both covered in the spec, tests, and implementation plan.
- The focused pytest command uses one valid `-k` expression across the focused files.
- The workflow monkeypatch is specified as a callable with the expected one-argument signature: `lambda _entries: ""`.

The implementation remains generated-site-only, article-page-only, render-only, scoped inside `#local-article-body`, and guarded against app contracts, schemas, JSON artifacts, routes, fetching, LLM, and compliance-review behavior.

## Model-Fact Correction

After the re-review, implementation prep verified that `RowOneLocalArticleContentSection` currently has no standalone `paragraph_indices` field. The Stage 366 spec and plan were corrected before implementation:

- Filing contexts are derived from item-level `item.paragraph_indices`.
- Section-level filing semantics come from each cited item's parent section anchor and section title fallback.
- The implementation must not access `section.paragraph_indices`.

This corrected plan needs another review pass before implementation.

## Final Claude Code re-review

READY FOR IMPLEMENTATION

No blockers found.

- `RowOneLocalArticleContentSection` has no `paragraph_indices` field; only `RowOneLocalArticleContentItem` defines `paragraph_indices`.
- The corrected spec and plan derive filing contexts only from `item.paragraph_indices`.
- Section-level semantics are correctly modeled through the cited item’s parent section anchor, with section title used only as the fallback label when the item label is blank.
- The plan remains generated-site-only, article-page-only, render-only, and scoped inside `#local-article-body`.
- The plan preserves the boundary against app contracts, schemas, JSON artifacts, routes, fetching, LLM, and compliance behavior.
