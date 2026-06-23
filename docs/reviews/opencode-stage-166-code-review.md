# Stage 166 Code Review

## Summary

Stage 166 tightens `validate_community_handoff_check_dir(...)` in
`scripts/check_first_run_smoke.py` so stable nested payload drift in the
`community-handoff-check-dir` JSON output is caught earlier. The change adds
exact `assert_equal(...)` checks across four areas: the top-level `findings`
list, the `community_signal_lint` identity/provenance details, the
`candidate_preview` metadata, and the `import_dry_run` provenance maps. It is
paired with focused drift tests in `tests/test_first_run_smoke.py`. The
objective is met cleanly with no production-code impact.

## Findings

### Critical

None.

### Important

None.

### Minor

1. The `candidate_preview` window fields (`current_window_start`,
   `baseline_window_start`, `current_days`, `baseline_days`) are derived from
   `CandidateDiscoverySettings` defaults plus the fixed `AS_OF`, not from
   hard-coded contract constants. Pinning them is acceptable because the smoke
   always runs against the default `init` config and the smoke pass confirms
   the match, but if those defaults ever change the smoke will fail here first.
   That is the intended drift-catching behavior; flagged only so the coupling
   is explicit.

2. Carried forward from plan review, non-blocking: reusing
   `EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS` to derive `lint.field_counts` is
   sound since both surfaces share the community-signal schema, but the name is
   template-centric. A schema-named alias or short inline comment would make
   the shared-schema intent self-documenting. The dict-comprehension form
   `{field: len(EXPECTED_SAMPLE_ROWS) for field in ...}` is order-independent
   and matches the fixture exactly, so this is cosmetic only.

## Verification Assessment

Objective (Q1): Met. The validator now pins top-level `findings`, lint
identity/path/info_count/field_counts/source_name_counts/platform_counts,
candidate_preview input_format/as_of/window starts/current_days/baseline_days/
source_name/file_count/limit/candidates, and import_dry_run directory/
input_format/pattern/source_name_counts/platform_counts.

Drift tests (Q2): Focused and sufficient. Each newly pinned field has at least
one dedicated RED drift case. The implementation goes beyond the plan minimum
and also covers the fields the plan review flagged as lacking dedicated cases
(`community_signal_lint.info_count`, `candidate_preview.input_format`,
`current_window_start`, `baseline_window_start`, `current_days`,
`baseline_days`). Mutations are one-field-at-a-time against
`community_handoff_check_dir_payload(...)`, and `match=` strings align with the
validator's assertion labels.

Narrowness (Q3): Maintained. No top-level or nested key-set equality was added,
so additive schema changes will not break the smoke. Nested `files` and nested
section `findings` lists remain deliberately unpinned, matching the spec's
out-of-scope list and the documented fixture/real-output gap. Existing
constants (`DIR_PATTERN`, `SOURCE_NAME`, `EXPECTED_PLATFORM_COUNTS`,
`EXPECTED_SOURCE_COUNTS`, `EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS`,
`EXPECTED_SAMPLE_ROWS`) and the `expected_directory` argument are reused.

Out-of-scope (Q4): None detected. The diff shows only
`scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py`; no
`src/` changes, no CLI/producer/model changes, no nested list exactness, and
no new collection/import/SQLite behavior.

Independent re-runs reproduced the stated evidence:

- `pytest ... -k "community_handoff_check_dir"`: 30 passed, 131 deselected.
- `ruff check`: All checks passed.
- `ruff format --check`: 2 files already formatted.
- `python scripts/check_first_run_smoke.py --repo-root .`: First-run sample
  smoke passed.

## Verdict

Approve for release verification. No critical or important findings. The
validator hardening is narrow, fully test-covered, scope-compliant, and all
focused checks reproduce green. Proceed to the full release gate and Stage 166
release review.
