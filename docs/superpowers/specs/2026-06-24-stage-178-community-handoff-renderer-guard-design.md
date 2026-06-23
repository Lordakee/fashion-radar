# Stage 178 Community Handoff Renderer Guard Design

## Objective

Add focused regression guards for community handoff directory check renderer
count labels and unavailable candidate preview output.

## Background

Stage 171 introduced singular count-label coverage for
`render_community_handoff_directory_check_table`, and the local code review
recorded two follow-up coverage notes:

- plural summary lines are exercised indirectly but not pinned by exact
  equality assertions;
- the `candidate_preview is None` renderer branch is behaviorally preserved but
  lacks an exact assertion for the rendered `unavailable` text.

This stage closes those coverage notes without changing runtime behavior.

## Scope

In scope:

- Add an exact plural-count renderer assertion for the three summary lines:
  `Lint: ...`, `Candidate preview: ...`, and `Import dry-run: ...`.
- Add an exact renderer assertion for `Candidate preview: unavailable` when the
  candidate preview cannot be built.
- Optionally rename the existing singular renderer test so the test name
  describes all count labels it covers, not only the error label.
- Add Stage 178 plan/review artifacts.

Out of scope:

- Runtime behavior changes unless a new test exposes an actual defect.
- CLI output changes beyond what existing renderer behavior already produces.
- Community signal parsing, candidate scoring, import dry-run behavior, source
  acquisition, connector integration, scraping, browser automation, platform
  APIs, monitoring, scheduling, ranking, coverage verification features,
  compliance-review product features, dependencies, and `uv.lock`.

## Technical Approach

Use existing fixtures and result models in `tests/test_community_handoff_check.py`.
Create deterministic renderer inputs by building the normal two-file handoff
result and using `model_copy` to pin the exact plural values to assert. Reuse
the existing invalid CSV scenario for the unavailable candidate preview path and
assert the renderer emits the exact summary line plus the stable finding row.

## Acceptance Criteria

- The plural renderer test asserts exact lines:
  - `Lint: 2 files, 2/2 import-ready rows, 2 errors`
  - `Candidate preview: 2 candidates from 2 rows`
  - `Import dry-run: 2/2 valid files, 2 rows, 2 errors`
- The unavailable renderer test asserts exact line:
  - `Candidate preview: unavailable`
- The unavailable renderer test also asserts the stable candidate-preview finding
  row is rendered.
- Focused community handoff tests pass.
- `ruff check` and `ruff format --check` pass for the touched test file.
- Full release gate remains clean before commit.
