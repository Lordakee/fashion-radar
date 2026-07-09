# Stage 368 Plan Re-Review — Local Article Body Organizer

**Reviewer:** opencode (GLM 5.2 max), fallback/revision reviewer
**Date:** 2026-07-09
**Scope:** Verify Claude Code's two Important findings were resolved; assess remaining feasibility, generated-site-only boundary, tests, docs, and risks.

## Resolution Of Claude Code's Important Findings

- **Placement order:** Resolved. The updated plan and design say the organizer is inserted between `content_segment_deck` and `local_article_section`. The source order in `templates.py` renders `key_signals` before `content_segment_deck`, so the revised "after Saved Article Key Signals, before the saved body" wording is accurate.
- **Helper duplication:** Resolved with an explicit decision. The plan chooses local helpers that mirror Stage 367 filing inbox validation semantics while keeping ordered tuple output for Stage 368 body-route rendering.

## Critical

None.

## Important

- **Lockfile verification command:** opencode reported that Task 7 used a malformed `uv run lock` command. Controller verification after review found the Stage 368 plan already uses the correct command: `UV_NO_CONFIG=1 uv --no-config lock --check --offline`. No plan command change is required, but the plan now explicitly pins this command to avoid ambiguity.

## Minor

- Add reciprocal sibling comments in both Stage 367 and Stage 368 paragraph-index helpers so future validation changes do not diverge.
- Add PascalCase contract denylist tokens such as `RowOneSavedArticleBodyOrganizer` and `BodyOrganizer`.
- State that `section_position` is derived from `enumerate(local_article.content_sections, start=1)` and must match existing `id="local-article-content-section-N"` anchors.
- Explain in the design that the new body organizer read-first route is intentionally distinct from the existing saved text digest "Read First" card.

## Feasibility / Boundary / Tests / Docs / Risks

- **Feasibility:** Sound. The feature is a pure builder from existing `RowOneStory` and `RowOneLocalArticle`, following the existing builder and renderer pattern.
- **Generated-site-only boundary:** Strong. The plan targets only `articles/<story-id>.html` and does not introduce app JSON, schemas, routes, source collection, fetching, scoring, ranking, LLM, connectors, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
- **Tests:** Comprehensive. Builder, render placement, boundary, CSS, anchor, docs, and workflow guards are specified.
- **Docs:** README, `docs/row-one.md`, and docs tests are covered.
- **Anchor scheme:** Consistent with existing one-based `#local-article-paragraph-N` and `#local-article-content-section-N` anchors.

## Verdict

Approved with changes. Claude Code's Important findings are resolved. The remaining items are plan clarifications and low-risk guardrail additions, now reflected in the updated plan/design before implementation.
