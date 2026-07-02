# Claude Code Stage 262 Plan Review

Reviewer: Claude Code (`--effort max`)
Stage: 262 (ROW ONE reader orientation)
Scope: Stage 262 design spec and implementation plan before coding

## Verdict

Accept with fixes.

The stage is a coherent, low-risk presentation-layer increment after Stage 261.
It improves ROW ONE's reader navigation without adding collection, scraping,
platform APIs, translation, LLM calls, deployment, demand proof, platform
coverage verification, or compliance-review product behavior. The plan is
concrete enough to implement after the required plan/spec fixes below.

## Critical Findings

None.

## Important Findings

- The implementation plan's helper sketch uses `LocalizedText` in
  `templates.py` but does not explicitly add it to the import list.
- The planned `_render_story_orientation()` sketch contains long interpolated
  `<span>` lines that are likely to violate the project's 100-character Ruff
  line limit.
- The planned `_section_title_from_key()` duplicates section title literals that
  already exist on `RowOneSection`. The implementation should thread the
  current section title into story-card rendering instead of introducing a
  second title map that can drift from `SECTION_DEFINITIONS`.
- Stage 262 is the third consecutive presentation-only ROW ONE stage. This is
  acceptable because the user's current objective is the ROW ONE web/app
  experience, but the spec/plan should state this rationale explicitly against
  the protocol's general release-track preference for coverage and matching
  quality work.

## Minor Findings

- Keep test expectations behavior-focused and avoid asserting large exact HTML
  fragments.
- Keep the new navigation and metadata additive; do not change existing story
  ranking, story IDs, cleanup, server behavior, or JSON contract shape.

## Required Plan And Spec Fixes Before Coding

- Add `LocalizedText` and `RowOneSection` import guidance for
  `src/fashion_radar/row_one/templates.py`.
- Rewrite the planned story-orientation helper sketch so long strings are built
  from shorter local variables and formatted spans stay under Ruff line length.
- Replace `_section_title_from_key()` with a plan that passes the active
  `RowOneSection.title` into `_render_story_card()` / `_render_story_orientation()`.
- Add a short Stage Direction Rationale section explaining why this
  presentation-only Stage 262 is still the right next increment for the current
  user goal.

## Recommended Next Action

Apply the required plan/spec fixes, then proceed with TDD implementation and the
normal code/release review gates.
