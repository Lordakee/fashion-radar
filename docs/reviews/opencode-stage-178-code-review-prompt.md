# Stage 178 Code Review Prompt

Review the Stage 178 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree.
Start the response exactly with:

# Stage 178 Code Review

Objective:

Add focused regression guards for community handoff directory check renderer
count labels and unavailable candidate preview output.

Changed files:

- `tests/test_community_handoff_check.py`
  - Renames the singular renderer test to
    `test_render_community_handoff_directory_check_table_uses_singular_count_labels`.
  - Adds
    `test_render_community_handoff_directory_check_table_uses_plural_count_labels`.
  - Adds
    `test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview`.
- Stage 178 spec, plan, plan-review prompt, and plan-review artifact.

Review context:

- `docs/superpowers/plans/2026-06-24-stage-178-community-handoff-renderer-guard-plan.md`
- `docs/reviews/opencode-stage-178-plan-review.md`
- `src/fashion_radar/community_handoff_check.py`
- `docs/reviews/opencode-stage-171-code-review.md`

Scope boundaries:

- Test-only hardening.
- No runtime behavior changes.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification
  features, compliance-review product features, dependency changes, or
  `uv.lock` changes.

Expected implementation:

- The singular renderer test was renamed only; it still asserts exact singular
  lines for lint, candidate preview, and import dry-run.
- The plural renderer guard asserts these exact renderer lines:
  - `Lint: 2 files, 2/2 import-ready rows, 2 errors`
  - `Candidate preview: 2 candidates from 2 rows`
  - `Import dry-run: 2/2 valid files, 2 rows, 2 errors`
- The plural renderer guard remains renderer-scoped and deterministic: it uses
  the existing fixture flow, asserts `result.candidate_preview is not None`, and
  uses `model_copy` only to force plural counts. The semantic decoupling between
  forced counts and `result.findings` is intentional for this count-label guard.
- The unavailable candidate-preview renderer guard uses the deterministic
  invalid `bad.csv` scenario, asserts `result.candidate_preview is None`, asserts
  exactly `Candidate preview: unavailable`, and pins the expected
  `candidate_preview_unavailable` finding row.
- The new tests should not overcouple to candidate scoring internals; they
  should validate rendered summary output and the stable unavailable-preview
  finding only.
- Existing community handoff tests should not be weakened or deleted.

Verification evidence:

- RED/absence:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_plural_count_labels -q`
  - Result before adding test: no matching test collected.
- RED/absence:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview -q`
  - Result before adding test: no matching test collected.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_count_labels tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_plural_count_labels -q`
  - Result: 2 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview -q`
  - Result: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q`
  - Result: 9 passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_community_handoff_check.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_community_handoff_check.py`
  - Result: 1 file already formatted.

Review questions:

1. Does the implementation match the approved Stage 178 plan?
2. Are the exact renderer assertions correct and useful?
3. Did any runtime, source acquisition, connector, scraping, platform API,
   ranking, coverage-verification feature, compliance-review product feature,
   dependency, or lockfile behavior slip in?
4. Are the focused verification commands sufficient before release gate?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
