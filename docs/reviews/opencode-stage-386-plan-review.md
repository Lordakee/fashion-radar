# Stage 386 Plan Review - OpenCode GLM 5.2

Scope/boundary was reviewed for the Stage 386 Daily Saved Text Takeaways plan. The proposed generated-site-only direction is feasible and aligned with the project boundary: homepage presentation over existing saved local article bodies, with no new app/runtime/manifest/schema/route/source/scraping/LLM/scheduling/deployment/compliance-review behavior.

## Findings From Initial Review

### Critical - Fixed in plan
- Test fixtures used invalid ROW ONE model shapes: `RowOneSectionKey.FASHION`, missing required `RowOneStory` fields, `summary` as a plain string, `as_of`, and `sections=[...]`. The plan now mirrors existing fixture patterns with `section_key="top_stories"`, `story_type="tracked_entity"`, localized summary fields, `edition_date`, and no invalid `sections` field.
- Renderer href validation double-prefixed `articles/` and would reject every takeaway href. The plan now validates `path_text` directly with `_safe_daily_local_synthesis_brief_href(...)`, compares `path_text == page_href`, and returns `f"{page_href}#{fragment}"`.

### Important - Fixed or narrowed in plan
- Core lane helpers were underspecified. The plan now defines lane order, lane titles/deks, helper selection behavior, brand/product reference types, source/title fallback behavior, duplicate handling, excerpt truncation, and `inspect_next` non-overlap rules.
- `inspect_next` non-overlap lacked a test. The plan now adds `test_build_daily_local_saved_text_takeaways_inspect_next_avoids_reused_evidence`.
- CSS selectors were under-tested. The plan now requires CSS selector assertions and wrapping protection checks.

## Residual Risks
- Claude Code plan review timed out and produced no actionable final review in this environment.
- Implementation should still follow the plan's RED/GREEN sequence because the plan is large enough that test fixture drift or render placement mistakes could otherwise slip through.
