# Stage 174 Release Review

Objective:

Make first-run documentation accurately describe every external-tool JSON
contract surface that the automated first-run smoke already validates.

## Summary

Stage 174 is a tightly scoped, docs/test-only change that closes a genuine
documentation accuracy gap, and it is ready to commit. The central factual
claim, diff surface, and release gate were re-verified.

The four named surfaces in both `README.md` and `docs/first-run.md`
(`external-tool-adapters --format json`, plus `external-tool-template`,
`external-tool-workflow`, and `external-tool-readiness` all with
`--adapter rednote_mcp --format json`) match what
`scripts/check_first_run_smoke.py` runs and validates, and the "all eight
adapters" phrasing matches the smoke script's expected adapter set. The added
boundary clause ("command-output contract checks only; they do not run adapters
or upstream external/community tools, do not call platform APIs, and do not
perform source acquisition") is accurate: the smoke only invokes local CLI
subcommands and asserts JSON contract fields, with no network, platform-API, or
source-acquisition behavior.

Scope is respected. `git diff --stat` shows only the four claimed files
(`README.md`, `docs/first-run.md`, `tests/test_cli_docs.py`,
`tests/test_first_run_docs.py`); no runtime CLI, smoke-script, payload, adapter,
template, workflow, readiness, install-hint, or mirror-hint code was touched.
The README and detailed first-run guide received equivalent replacement text, so
parity holds and is enforced by the shared `test_cli_docs.py` guards plus the
new section-scoped first-run docs test.

## Findings

### Critical

None.

### Important

None.

### Minor

- The two docs test phrase sets use different casing conventions:
  `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` in `tests/test_cli_docs.py` keeps
  original casing (`JSON`, `APIs`) for raw substring matching, while
  `test_first_run_docs_name_external_tool_smoke_contracts` lowercases via
  `_normalized`. Both correctly match their respective doc text today; this is
  consistent but worth noting if wording is edited later.
- Pre-existing overlap between `tests/test_first_run_docs.py` and
  `tests/test_cli_docs.py` (both assert adapter/template/workflow/readiness
  fragments against `docs/first-run.md`) is retained. The split is defensible
  (section-only `casefold` vs whole-doc raw substring) and both guards add
  value, so no action is needed.
- `test_first_run_docs_name_external_tool_smoke_contracts` is scoped to the
  `docs/first-run.md` "Installed-Wheel Smoke" section only; README parity relies
  on `test_cli_docs.py`. This is the intended layout, but future README wording
  edits should remember the shared README guard catches drift.

## Verification Assessment

Release gate evidence was reproduced:

- Full suite (`env -u ...proxy... uv --no-config run --frozen pytest -q`): 1370
  passed.
- Installed smoke (`uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`):
  First-run sample smoke passed.
- Related smoke coverage
  (`uv --no-config run --frozen pytest tests/test_first_run_smoke.py -k "external_tool or deterministic_local_command_sequence" -q`):
  58 passed, 104 deselected.
- Focused docs tests
  (`uv --no-config run --frozen pytest tests/test_first_run_docs.py tests/test_cli_docs.py -q`):
  71 passed.
- Release hygiene
  (`uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`):
  passed.
- `uv --no-config run --frozen ruff check .`: All checks passed.
- `uv --no-config run --frozen ruff format --check .`: 144 files already
  formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`:
  Resolved 84 packages.
- `git diff --check`: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`: no matches, exit 1.
- `git config --get-all http.https://github.com/.extraheader`: not configured,
  exit 1.

The RED/GREEN evidence in the prompt is credible and consistent with the diff:
the prior docs named only the adapter-registry surface, so both targeted tests
necessarily failed before the wording edit, and they pass now. Because no
runtime behavior changed, the unchanged smoke and `test_first_run_smoke.py`
results are expected and consistent with a docs-only node. The plan and code
review artifacts are complete, properly structured, free of stubs/truncation,
and follow `docs/REVIEW_PROTOCOL.md` naming and capture-hygiene rules.

The evidence is sufficient for this docs/test-only stage.

## Verdict

Approve. Stage 174 is in scope and ready to commit and push. The documentation
now accurately names all four external-tool JSON contract surfaces validated by
the automated first-run smoke while preserving the local command-output /
no-upstream-tool / no-platform-API / no-source-acquisition boundary. No
out-of-scope runtime, smoke-script, payload, adapter, template, workflow,
readiness, install-hint, mirror-hint, connector, source-acquisition, ranking, or
compliance-review behavior changed. No critical or important findings block
release.
