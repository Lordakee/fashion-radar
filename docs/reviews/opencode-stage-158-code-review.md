## Stage 158 Code Review

**No blocking findings.** The implementation is correct, tests pass (`138 passed`), ruff is clean, and the live `scripts/check_first_run_smoke.py` smoke passes end-to-end.

### Against the review questions

**1. Validates useful readiness fields without overfitting? - Yes.**
`validate_community_handoff_check_dir` (scripts/check_first_run_smoke.py:885) pins the high-value readiness/boundary signals:
- `execution_mode == "local_read_only"` (the Pydantic `Literal["local_read_only"]` boundary)
- `ok == True`, `failed_check_count == 0`, `warning_count == 0`
- runtime echoes: `directory`, `config_dir`, `input_format`, `pattern`, `as_of`, `source_name`, `strict`, `limit`
- nested *count summaries* only (lint/candidate/import-dry-run file/row/error counts)

It deliberately does **not** pin full nested schemas (`field_counts`, `source_name_counts`, `files`, `findings`, window timestamps). This is the right smoke-contract level - catches readiness regressions without being brittle.

**2. Fixture mirrors real model shapes? - Yes.**
`community_handoff_check_dir_payload` (tests/test_first_run_smoke.py:362) matches the field order and shapes of `CommunityHandoffDirectoryCheckResult` (community_handoff_check.py:47) and its nested `CommunitySignalDirectoryLintResult` / `CommunityCandidateDirectoryPreview` / `ManualSignalDirectoryDryRunResult`. Additionally the e2e `run_first_run_flow` validates **real** CLI JSON output, which is stronger than a fixture-only guard.

**3. Preserves local-only, read-only behavior? - Yes.**
Validator pins `execution_mode == "local_read_only"`. The flow calls `community-handoff-check-dir` (read-only) then `import-signals-dir --dry-run` (read-only). No write-capable import runs in the first-run flow.

**4. RED/GREEN tests sufficient? - Yes, with minor gaps.**
GREEN acceptance + parametrized top-level drift (execution_mode/ok/failed_check_count/warning_count/strict) + one nested count drift (`lint row_count`). `test_run_first_run_flow_uses_deterministic_local_command_sequence` wires the validator to run against the fake JSON and asserts the new `--format json` argv.

**5. Critical/important issues? - None.**

### Minor (non-blocking) observations

- **M1.** No RED test for `directory`/`config_dir` runtime-echo drift *on this validator*, and nested drift is only tested for `community_signal_lint.row_count` (not `candidate_preview` or `import_dry_run` counts). The e2e smoke covers the real output, so coverage is adequate, but extending the parametrize would mirror the rigor of the workflow validators.
- **M2.** No standalone `*_payload_matches_real_check` unit test like the pure-builder payloads enjoy. This is justified - `check_community_handoff_directory` does file I/O rather than being a pure builder - so noting only for completeness.
- **M3.** `limit == 50` and `as_of == "...+00:00"` are correct given the CLI defaults and the `Z` to `+00:00` normalization through `parse_datetime_utc().isoformat()`; consistent with `EXPECTED_WORKFLOW_AS_OF`. No action needed.

Stage 158 is clear for release-gate verification and commit.
