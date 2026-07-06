# Stage 312 Plan Review (opencode fallback, GLM 5.2 max)

Claude Code returned a 524 timeout; this is the recorded fallback review per
`docs/REVIEW_PROTOCOL.md`. Reviewed only the pasted design and plan.

## Critical Findings

None.

## Important Findings

1. **Escaping test mutates a story field directly** (Task 3, Step 2).

   `story.headline = '<script>...'` assumes `RowOneStory` is mutable. If the
   Pydantic model is frozen, this raises at runtime and the escaping check never
   runs. Prefer rebuilding the story via `model_copy(update={...})` or
   constructing a fresh fixture. Without confirming mutability from `models.py`,
   this is a real risk and the test could fail before exercising the escape
   path.

2. **Metrics describe the full corpus while only 4 cards render.**

   The builder sums `saved_paragraph_count` and `organized_section_count` over
   all `story_articles` but slices `items[:4]`. This is internally consistent,
   but the plan never states that metrics are corpus totals while the grid is a
   capped read queue. Add one line to the design and one assertion that
   `article_count` can exceed `len(items)` so future readers do not "fix" this
   as a bug.

3. **CSS test location is unspecified.**

   Task 3 Step 3 says "In `test_row_one_css_includes_local_article_map_styles`
   or a new CSS test". Pick one. Splitting selector assertions across two tests
   makes the failure message ambiguous and weakens the contract the plan is
   supposed to lock in.

## Minor Findings

4. Source ordering in Task 1 Step 4 relies on Python dict insertion order plus
   exact parity. The assertion is correct but brittle; a note about first-seen
   order would prevent regressions looking like fixes.

5. `_section_title` fallback branch is untested. Either add a unit test or drop
   the fallback.

6. Task 5 docs test asserts many exact lowercase phrases. It is acceptable for
   this repository's boundary tests, but keep the prose phrase list stable.

## Coverage Of Reviewer Tasks

1. Feasible/consistent: Yes. Builder -> `render_row_one_site()` ->
   `render_index_html()` mirrors existing `local_article_intelligence` wiring.
2. Scope/boundaries: Plan stays inside stated fences. No app-facing Pydantic
   model changes, no manifest/runtime/schema/route/anchor changes, no new JSON
   artifact, no collection/scoring/LLM.
3. Tests: Adequate for builder, rendering, omission, escaping, CSS, docs, and
   contract stability once the Important findings are fixed.

## Verdict

Plan is approved with the three Important findings addressed before
implementation starts. No Critical blockers.
