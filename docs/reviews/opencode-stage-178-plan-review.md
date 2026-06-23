# Stage 178 Plan Review

## Summary

The Stage 178 plan is a tightly scoped, test-only hardening stage that directly closes the three minor coverage notes recorded in `docs/reviews/opencode-stage-171-code-review.md`. It adds two new renderer-scoped regression tests (plural count labels and unavailable candidate preview), renames the existing singular renderer test to match what it actually asserts, and adds no runtime changes. I traced every proposed exact-line assertion through `render_community_handoff_directory_check_table(...)` in `src/fashion_radar/community_handoff_check.py:169` and the `format_count_label(count, singular, plural)` contract in `src/fashion_radar/lint_formatting.py:4`; all six asserted strings reproduce the current renderer output exactly. The stage boundaries (no source acquisition, connectors, scraping, platform APIs, monitoring, scheduling, ranking, coverage verification, compliance-review product features, dependency changes, or `uv.lock` changes) are respected. No critical or important issues were found; implementation may proceed.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Inherent model_copy semantic decoupling in the plural test (accepted pattern, awareness note only). Task 1 Step 3 builds a real two-file result with an empty findings list and `ok=True`, then uses `model_copy` to force `error_count: 2` on `community_signal_lint` and `import_dry_run`. Because `result.findings` is not overridden, the renderer will still emit "No community handoff check findings." while the Lint/Import dry-run lines say "2 errors". This is the identical pattern already approved in Stage 171's singular test at `tests/test_community_handoff_check.py:335` and is appropriate for a count-label guard, since the test's purpose is rendering grammar, not end-to-end finding consistency. No change required; the implementer should simply not be alarmed by the decoupling.

2. The unavailable candidate-preview test (Task 2 Step 2) relies on the same `bad.csv` scenario already proven deterministic by `test_check_community_handoff_directory_preserves_lint_and_dry_run_on_candidate_failure` at `tests/test_community_handoff_check.py:114`, which asserts `result.candidate_preview is None` for this exact input. The new test additionally pins the exact `Candidate preview: unavailable` line and the stable finding row, both of which I confirmed against the renderer's `candidate_preview_text = "unavailable"` fallback at `src/fashion_radar/community_handoff_check.py:175` and the finding rendering at `src/fashion_radar/community_handoff_check.py:218`. This is solid and deterministic. Note that this scenario also produces `community_signal_lint` and `import_dry_run` findings, but the test correctly scopes its assertions to the candidate-preview outputs only.

3. The singular-test rename in Task 1 Step 2 is safe and useful. `..._uses_singular_error_label` is a private pytest function with no external callers; the only references to the old name are in the historical Stage 171 review artifacts, which the scope rules require leaving as prior context. The new name `..._uses_singular_count_labels` accurately reflects that the test pins file, import-ready row, candidate, row, valid file, and error singular labels. No grep is needed beyond the test module itself.

## Verification Guidance

The implementer should, at minimum:

- Run Task 1 Step 1's absence probe to confirm the plural test does not already exist before adding it.
- After Task 1, run the combined singular+plural invocation in Step 4 to confirm both names resolve and pass.
- After Task 2, run the unavailable-preview test in isolation; if it fails, inspect whether renderer output or the finding message string changed before touching runtime code, per the plan's explicit "only update runtime if a real regression" guidance.
- In Task 3, run the focused module pytest plus `ruff check` and `ruff format --check` on `tests/test_community_handoff_check.py`.
- In Task 4, run the full release gate including the proxy-stripped full pytest, the smoke and hygiene scripts, the `UV_NO_CONFIG=1 uv lock --check`, the `git diff --check`, the token absence grep, and the extraheader absence check. The two absence checks correctly expect exit 1 with no output.
- Confirm the plural test's three asserted lines exactly match the renderer, which I verified during this review:
  - `Lint: 2 files, 2/2 import-ready rows, 2 errors`
  - `Candidate preview: 2 candidates from 2 rows`
  - `Import dry-run: 2/2 valid files, 2 rows, 2 errors`

## Verdict

Approve. The plan fully addresses all three Stage 171 follow-up notes (singular test rename, exact plural-line guard, exact unavailable candidate-preview guard), the proposed tests are deterministic and renderer-scoped rather than coupled to candidate scoring internals, the singular rename is safe and improves intent alignment, and the verification/code-review/release-review/commit/push sequence matches `docs/REVIEW_PROTOCOL.md` and `AGENTS.md`. There are no critical or important findings; the three minor notes are awareness items and do not block implementation.
