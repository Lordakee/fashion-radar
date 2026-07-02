# Claude Code Stage 262 Plan Rereview

Reviewer: Claude Code (`--effort max`)
Stage: 262 (ROW ONE reader orientation)
Scope: Stage 262 design spec and implementation plan after initial plan-review fixes

## Verdict

Accept with fixes.

The stage remains contract-safe and presentation-only. It stays inside `templates.py`, tests, and ROW ONE documentation, while leaving collection, matching, ranking, scoring, story IDs, JSON payload shape, server behavior, cleanup behavior, deployment, external tools, and imported/community workflows out of scope. The fixes below are required before coding to avoid visual duplication and tighten the tests around the actual new UI fragments.

## Critical Findings

None.

## Important Findings

- The planned story card metadata would show `source_name` twice: once in the existing `.story-meta` line and again in `.story-orientation`. Since Stage 262 is about scannability, the card should fold source into the orientation row and remove the standalone source meta line from the card header.
- Several planned tests assert strings that already appear elsewhere on the page, such as section titles and source names. The tests should scope nav and orientation assertions to the actual `.edition-nav` and `.story-orientation` fragments.
- The planned test coverage checks the plural evidence case but not the common one-link production case. It also does not exercise the `published_at is None` branch.
- The plan should explicitly state the direction decision: Stage 262 is allowed because the user's current priority is ROW ONE web/app experience; Stage 263 should move to app-facing JSON contract only if still requested, otherwise the broader release track should return to coverage/matching work.

## Minor Findings

- Avoid locale-sensitive English date assertions where possible; also assert the locale-stable Chinese date.
- Move `RowOneSection` import guidance into the task where `_render_edition_nav` first uses it.
- Fix the Task 4 prose/code mismatch around `_render_story_orientation(story, section_title)`.
- Clarify that the Reader Orientation docs section should be inserted after the Editorial Synthesis section and before Generated Files.
- Include a formatting write step before the final `ruff format --check .` gate.

## Required Plan And Spec Fixes Before Coding

- Update spec/plan so story-card orientation replaces the standalone source meta line rather than duplicating source.
- Scope nav/orientation tests to their rendered fragments.
- Add tests for `1 evidence link` / `1 条线索` and `Undated` / `时间未标注`.
- Add the direction note that Stage 262 is presentation-only by explicit user priority and that subsequent stages should rebalance toward coverage/matching unless the user continues the ROW ONE app/site track.
- Move `RowOneSection` import guidance to the nav task, fix the orientation helper prose mismatch, clarify docs insertion, and include a format step.

## Recommended Next Action

Apply these plan/spec fixes, then proceed with TDD implementation.
