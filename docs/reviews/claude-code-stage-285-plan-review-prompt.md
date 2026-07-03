# Stage 285 Plan Review Request

Please review the Stage 285 implementation plan in `/home/ubuntu/fashion-radar`.

## File To Review

- `docs/superpowers/plans/2026-07-04-stage-285-row-one-card-synthesis-and-detail-map-plan.md`

## Goal

Stage 285 should make ROW ONE expose more organized story information without
creating a new broad contract surface. It enriches existing app card payloads
with already-generated synthesis fields and adds a detail-page information map
from existing story data.

## Proposed Scope

- Add existing `why_it_matters` and `signal_context` fields to `$defs.contentCard`
  and `_content_card_payload`, so `content_sections`, `daily_digest.blocks`, and
  `daily_digest.briefing_topics` cards carry fuller story synthesis.
- Add a detail-page `detail-information-map` after article contents and before
  the existing summary section, derived only from existing `RowOneStory` fields.
- Update schema, tests, and docs.

## Constraints

- No new source collection, scraping, platform APIs, social/community connectors,
  browser automation, account/session/cookie behavior, image generation,
  translation service, LLM calls, deployment, scheduler changes, paid APIs, or
  compliance-review product feature.
- Do not change matching, ranking, scoring, story sorting, story IDs, cleanup,
  server, or schedule behavior.
- Do not infer new people, products, designers, brands, or categories from
  headlines, sections, tags, source names, or URLs.
- Keep the work deterministic and local.
- Keep dependency files unchanged.

## Please Evaluate

1. Is enriching existing content cards plus a detail information map the right
   narrow next step for the user's request to make ROW ONE organize information
   instead of just linking out?
2. Is adding `why_it_matters` and `signal_context` to `contentCard` safer than
   introducing a new `story_intelligence` object at this stage?
3. Are schema updates and tests sufficient for `additionalProperties: false`?
4. Are there risks around duplicating existing fields, app contract versioning,
   or detail-page rendering?
5. Are there missing files, docs risks, or blockers before implementation?

Return:

- APPROVED or NOT APPROVED
- Findings ordered by severity with file/line references
- Required fixes before implementation
- Optional follow-ups
