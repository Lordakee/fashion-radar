# Stage 166 Plan Review

## Scope Assessment (Q1)

Stage 166 is correctly scoped to local first-run smoke validator hardening. The
only production-adjacent file touched is `scripts/check_first_run_smoke.py`
(a release-check script, not product code), plus its test module. No `src/`
files appear in the Files list. The work is confined to
`validate_community_handoff_check_dir(...)`, which is a pure local payload
validator. This respects the `AGENTS.md` boundary that
`community-handoff-check-dir` must remain a local-only handoff readiness report
with no collection, connectors, imports, or SQLite.

## RED Test Coverage (Q2)

The RED tests correctly prove currently unpinned drift. I verified each target
field against the current validator at `scripts/check_first_run_smoke.py:885-940`:

- Top-level `findings`: not asserted today; the new parametrize tuple is
  genuinely RED.
- `community_signal_lint.directory/input_format/pattern/field_counts/
  source_name_counts/platform_counts`: none are asserted today; all RED.
- `candidate_preview.source_name/as_of/file_count/limit/candidates`: only
  `candidate_count` and `row_count` are asserted today; all new cases are RED.
- `import_dry_run.directory/input_format/pattern/source_name_counts/
  platform_counts`: none asserted today; all RED.

The expected values in Task 2 match the fixture at
`tests/test_first_run_smoke.py:362-433` exactly (as_of windows, counts,
`SOURCE_NAME`, `DIR_PATTERN`, `EXPECTED_SOURCE_COUNTS`,
`EXPECTED_PLATFORM_COUNTS`). The `field_counts` comprehension
`{field: len(EXPECTED_SAMPLE_ROWS) for field in EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS}`
yields `{url: 2, ..., collected_at: 2}`, matching the fixture independent of
key order. The integration call at
`scripts/check_first_run_smoke.py:2660-2665` passes
`expected_directory=str(context.exports_dir)`, so the new nested directory
assertions using `expected_directory` will hold in both direct tests and the
flow test.

## Assertion Granularity (Q3)

The checks are appropriately narrow. The plan does not add a full top-level or
nested key-list equality (unlike `validate_external_tool_workflow`), so
additive schema changes will not break the smoke. Nested `files` and nested
section `findings` lists are deliberately left unpinned, matching the spec's
out-of-scope list and the stated fixture/real-output gap. Pinning
`candidate_preview.candidates` and top-level `findings` to `[]` is in scope
(the latter is not a nested findings list) and is the highest-value empty-list
contract to lock.

## Product Behavior (Q4)

All product behavior under `src/` is unchanged. Confirmed no `src/` path is
listed for modification.

## Process Completeness (Q5)

Task 3 is complete: code-review prompt + run, full release gate (proxy-unset
pytest, smoke, release hygiene, ruff check + format, `UV_NO_CONFIG=1 uv lock
--check`, `git diff --check`, `ghp_` scan, extraheader check), release-review
prompt + run, then commit and push. The gate matches the spec's Verification
section and `docs/REVIEW_PROTOCOL.md`. Review-capture hygiene (temp file,
inspect, copy) is preserved.

## Findings

**Critical:** None.

**Important:** None.

**Minor:**

1. A few newly pinned fields lack a dedicated RED drift case:
   `community_signal_lint.info_count`, `candidate_preview.input_format`,
   `candidate_preview.current_window_start`,
   `candidate_preview.baseline_window_start`, `candidate_preview.current_days`,
   `candidate_preview.baseline_days`. They get `assert_equal` checks but no
   parametrized drift entry proving the assertion is necessary.
   `test_validate_community_handoff_check_dir_accepts_first_run_payload`
   guards the expected values, and each section already has representative
   drift coverage, so this is not blocking; adding one drift case per section
   for these fields would make the TDD motivation exhaustive.

2. Observation (no action required): reusing
   `EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS` to derive `lint.field_counts` is
   sound because both surfaces share the community-signal schema, but the name
   is template-centric. A short inline comment or a schema-named alias would
   make the shared-schema intent self-documenting. Not blocking.

No blocking findings. The plan is acceptable for implementation.
