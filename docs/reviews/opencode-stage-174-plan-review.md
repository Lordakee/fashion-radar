# Stage 174 Plan Review

Objective:

Make first-run documentation accurately describe every external-tool JSON
contract surface that the automated first-run smoke already validates.

## Summary

The Stage 174 plan is a tightly scoped docs/test-only change that closes a real
documentation accuracy gap. I verified the central factual claim against the
runtime smoke script: `scripts/check_first_run_smoke.py` (lines 2432-2500) does
run and validate four external-tool JSON surfaces —
`external-tool-adapters --format json`, then
`external-tool-template`, `external-tool-workflow`, and
`external-tool-readiness` all with `--adapter rednote_mcp --format json` — and
`validate_external_tool_adapters` asserts all eight adapter ids
(`EXPECTED_EXTERNAL_TOOL_ADAPTERS`). The current README (line 351) and
`docs/first-run.md` (line 160) only document the adapter-registry surface, so
the stated gap is genuine and the proposed wording matches the script exactly.

The plan satisfies every `AGENTS.md` boundary rule: runtime smoke logic, CLI
behavior, payloads, adapter/template/workflow/readiness builders, install
hints, and mirror hints are all explicitly out of scope, and the wording keeps
the local command-output / no-platform-collection / no-source-acquisition
framing. The TDD shape (RED docs test, then docs edit, then GREEN) is sound and
the RED expectation is correct.

## Findings

### Critical

None.

### Important

None.

### Minor

- Mild redundancy: after the change, `tests/test_first_run_docs.py` and
  `tests/test_cli_docs.py` both assert the adapter/template/workflow/readiness
  fragments against `docs/first-run.md`. The two differ in scope (section-only
  vs whole-doc) and case handling (`casefold` vs raw), so the overlap is
  defensible and not worth removing, but implementers should keep the two phrase
  sets in mind if wording drifts later.
- The new `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` tuple omits the
  "`external-tool-adapters --format json` across all eight adapters" adapter
  surface from the case-sensitive README/guide guard at the exact-phrase level
  only in the sense that it is present — confirm during GREEN that the README's
  `### Automated First-Run Smoke` subsection (not just `docs/first-run.md`) gets
  the identical replacement so `_normalized_doc_text(README)` substring checks
  pass; the plan already says "apply the replacement in both," so this is just a
  reminder.
- `test_first_run_docs_name_external_tool_smoke_contracts` is scoped to the
  `docs/first-run.md` "Installed-Wheel Smoke" section only; README parity relies
  entirely on `test_cli_docs.py`. That is a reasonable split given the existing
  helper layout, but it means README drift would only be caught by the shared
  CLI docs test.

## Plan Assessment

- Scope and safety: appropriate and safe. Docs/test-only with no runtime, CLI,
  payload, fixture, or boundary-behavior changes.
- Boundary compliance: fully consistent with `AGENTS.md`. The added clause
  ("command-output contract checks only; they do not run adapters or upstream
  external/community tools, do not call platform APIs, and do not perform source
  acquisition") mirrors the script's own boundary constants and the project's
  established "does not run adapters" lexicon for the print-only registry, so it
  does not imply live collection or platform coverage.
- Wording accuracy: verified against the smoke script. Adapter id (`rednote_mcp`),
  command names, `--format json`, and "all eight adapters" all match the
  pinned expectations. The RED phase is meaningful — eight of the nine fragments
  are absent today, so both targeted tests will fail before the docs edit.
- Test utility: focused on the smoke-claim surfaces, uses normalized substring
  matching tied to pinned smoke constants, and is not brittle. Useful without
  being over-broad.
- Verification plan: focused checks, full release gate, code review, release
  review, commit, and push are all present and use the project's
  `uv --no-config run --frozen` and `UV_NO_CONFIG=1 uv lock --check` conventions.
- File list and review artifacts (`opencode-stage-174-...`) align with
  `docs/REVIEW_PROTOCOL.md` naming and capture-hygiene rules.

## Verdict

Approve. The plan is accurate, boundary-compliant, and correctly scoped. Proceed
with implementation after addressing only the minor reminders above (chiefly:
ensure the identical replacement lands in both `README.md` and
`docs/first-run.md`, and run the RED step before editing docs). No critical or
important findings block start.
