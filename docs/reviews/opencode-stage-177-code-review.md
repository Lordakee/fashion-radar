# Stage 177 Code Review

Objective: Keep `docs/github-upload-checklist.md` aligned with README and
`docs/first-run.md` by naming every local external-tool JSON contract surface
that the automated first-run smoke already validates.

## Summary

Stage 177 is a tightly scoped docs/test-only change that extends
`test_upload_checklist_documents_first_run_smoke_boundary` to assert every
phrase in the shared `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` tuple, and adds one
paragraph to the checklist Package Smoke section that is verbatim-identical to
the paragraphs already enforced in README and `docs/first-run.md`. The change
meets the objective, the wording accurately reflects what
`scripts/check_first_run_smoke.py` validates, and the shared phrase tuple is a
sound DRY parity guard. No runtime, payload, adapter, smoke-script, lockfile,
install-hint, mirror-hint, dependency, or compliance-review behavior is touched.
No critical or important findings.

## Findings

### Critical

None.

### Important

None.

### Minor

- M1 (advisory, no change required): The checklist paragraph is a verbatim copy
  of the README/`first-run.md` paragraph, which is intentional parity and
  desirable. `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` guards normalized
  substrings rather than full sentence ordering; this is acceptable because the
  tuple covers every load-bearing claim.
- M2 (advisory): Before commit, confirm the Stage 177 review artifacts exist
  alongside the spec/plan/plan-review files. This code review and the subsequent
  release review still need to be recorded before staging per review-capture
  hygiene.

## Verification Assessment

The submitted verification evidence is accurate and independently reproduced.

- RED plausibility: before the docs edit, the checklist lacked the external-tool
  JSON-contract paragraph, so the extended phrase loop would fail on the first
  missing phrase.
- GREEN: `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_upload_checklist_documents_first_run_smoke_boundary -q`
  -> 1 passed.
- GREEN group: `uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "upload_checklist or first_run_smoke"`
  -> 10 passed, 59 deselected.
- Lint: `uv --no-config run --frozen ruff check tests/test_cli_docs.py` -> All
  checks passed; `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
  -> 1 file already formatted.
- Scope: diff shows only `docs/github-upload-checklist.md` and
  `tests/test_cli_docs.py`, with no runtime/code changes.
- Wording accuracy independently confirmed against the smoke script: it runs
  exactly the four named surfaces: `external-tool-adapters --format json`
  across all eight adapters, plus `external-tool-template`,
  `external-tool-workflow`, and `external-tool-readiness` each with
  `--adapter rednote_mcp --format json`.
- Boundary accuracy: the command-output-only clause matches the smoke validators
  and does not imply live collection, adapter execution, or platform coverage.

## Verdict

Approve. The Stage 177 implementation meets the objective, the checklist wording
is verbatim-parity with README and `docs/first-run.md` and accurately names
exactly the four surfaces the first-run smoke validates, and the reused phrase
tuple is a maintainable DRY parity guard. No out-of-scope runtime, smoke-script,
payload, adapter, source-acquisition, ranking, coverage-verification,
install-hint, mirror-hint, dependency, or lockfile behavior slipped in. No
critical or important findings; proceed to release verification.
