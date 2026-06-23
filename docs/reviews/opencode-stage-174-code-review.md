# Stage 174 Code Review

Objective: Make first-run documentation accurately describe every external-tool
JSON contract surface that the automated first-run smoke already validates.

## Summary

The implementation is a clean, tightly scoped docs/test-only change that closes
a genuine documentation accuracy gap. The central factual claim matches
`scripts/check_first_run_smoke.py`: the smoke runs and validates exactly the four
surfaces now named in the docs: `external-tool-adapters --format json`, plus
`external-tool-template`, `external-tool-workflow`, and
`external-tool-readiness` all with `--adapter rednote_mcp --format json`. The
"all eight adapters" claim matches the smoke script's expected adapter set.

The README (`Automated First-Run Smoke` section) and `docs/first-run.md`
(`Installed-Wheel Smoke` section) received equivalent replacement text, so
parity holds. The added boundary clause ("command-output contract checks only;
they do not run adapters or upstream external/community tools, do not call
platform APIs, and do not perform source acquisition") is accurate and mirrors
the project's local/no-live-collection framing. The TDD shape is sound: two
new/expanded test guards fail before the docs edit and pass after.

Scope is respected: only `README.md`, `docs/first-run.md`,
`tests/test_cli_docs.py`, and `tests/test_first_run_docs.py` changed. No runtime
CLI, smoke-script, payload, adapter, template, workflow, readiness, install-hint,
or mirror-hint code was touched.

## Findings

### Critical

None.

### Important

None.

### Minor

- Pre-existing redundancy acknowledged in the plan review remains:
  `tests/test_first_run_docs.py` and `tests/test_cli_docs.py` both assert
  overlapping adapter/template/workflow/readiness fragments against
  `docs/first-run.md`. The split is defensible (section-only plus `casefold`
  vs whole-doc raw substring) and both guards add value, so no action is needed.
- `test_first_run_docs_name_external_tool_smoke_contracts` is scoped to the
  `docs/first-run.md` section only; README parity relies on `test_cli_docs.py`.
  This is the intended layout and README drift is still caught, but future
  wording edits should remember the shared README guard.
- The two phrase sets use different casing conventions
  (`FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` keeps `JSON`/`APIs`; the first-run
  docs test lowercases via `_normalized`). Both match the actual rendered doc
  text, so this is consistent, just worth noting if wording drifts later.

## Verification Assessment

Focused GREEN commands were reproduced:

- `uv --no-config run --frozen pytest tests/test_first_run_docs.py -q` -> 2
  passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q`
  -> 2 passed.
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -k "external_tool or deterministic_local_command_sequence" -q`
  -> 58 passed, 104 deselected.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  -> First-run sample smoke passed.
- `uv --no-config run --frozen ruff check tests/test_first_run_docs.py tests/test_cli_docs.py`
  -> All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_first_run_docs.py tests/test_cli_docs.py`
  -> 2 files already formatted.

The RED/GREEN evidence in the prompt is credible: the prior docs named only the
adapter-registry surface, so both targeted tests necessarily failed before the
wording edit. The factual basis (four validated surfaces, eight adapters) was
confirmed by reading the smoke script source rather than relying on the prompt's
assertion. No runtime behavior changed, so the unchanged smoke and
`test_first_run_smoke.py` results are expected and consistent with a docs-only
node.

## Verdict

Approve. The implementation fully meets the Stage 174 objective: the README and
detailed first-run guide now accurately name all four external-tool JSON
contract surfaces validated by the smoke (`external-tool-adapters`,
`external-tool-template`, `external-tool-workflow`, and
`external-tool-readiness` with the `rednote_mcp` adapter) while preserving the
local command-output / no-upstream-tool / no-platform-API /
no-source-acquisition boundary. The change is narrowly scoped with no
out-of-scope runtime, smoke-script, payload, adapter, template, workflow,
readiness, install-hint, mirror-hint, connector, source-acquisition, ranking, or
compliance-review behavior. No critical or important findings block release
verification.
