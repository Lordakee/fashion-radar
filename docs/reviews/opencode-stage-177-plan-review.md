# Stage 177 Plan Review

Objective: Keep `docs/github-upload-checklist.md` aligned with README and
`docs/first-run.md` by naming every local external-tool JSON contract surface
that the automated first-run smoke already validates.

## Summary

Stage 177 is a narrow docs/test-only change that extends the existing
upload-checklist smoke docs guard to require the same external-tool JSON
contract phrases already enforced for README and `docs/first-run.md`, then adds
one concise paragraph to the checklist Package Smoke section that mirrors the
verified README/first-run wording. The plan is well-scoped, boundary-clean, and
accurately reflects what `scripts/check_first_run_smoke.py` already validates.
No runtime, payload, adapter, smoke-script, lockfile, install-hint, mirror-hint,
or compliance-review behavior is touched. No critical or important findings.

## Findings

### Critical

None.

### Important

None.

### Minor

- M1 (advisory, no change required): The plan's proposed paragraph is a
  verbatim copy of the README/`first-run.md` paragraph. This is intentional
  parity and desirable, but if those surfaces ever diverge in the future, the
  shared `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` tuple guards normalized
  substrings rather than full sentence ordering. The current design is
  acceptable because the phrase tuple covers every load-bearing claim.
- M2 (advisory): Task 3 Step 5 stages review prompt and review record files
  that are created during Task 3 itself. The ordering is correct, so no action
  is needed; just confirm those files exist before `git add`.

## Plan Assessment

**Q1 - Appropriately scoped and safe?** Yes. The change touches only
`tests/test_cli_docs.py` and `docs/github-upload-checklist.md`. No runtime code,
CLI behavior, smoke logic, fixtures, payloads, or packaging changes. Risk is
limited to a docs wording mismatch, which the RED/GREEN TDD steps catch
immediately.

**Q2 - Satisfies `AGENTS.md` boundary rules?** Yes. The stage is explicitly
docs/test-only. The proposed wording reiterates the command-output-contract-only
boundary and lists exactly the prohibited behaviors the smoke does not do: no
adapter execution, no upstream tool execution, no platform APIs, no source
acquisition. It adds no connectors, scraping, browser automation, monitoring,
scheduling, demand proof, ranking, coverage verification, or compliance-review
product feature.

**Q3 - Is reusing `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` the right test design?**
Yes. Reusing the existing phrase tuple is the correct DRY choice. It already
guards README and the detailed first-run guide, so extending it to the upload
checklist keeps all three first-run-smoke documentation surfaces in lockstep.

**Q4 - Does the proposed wording accurately match the smoke script and avoid
implying live collection or platform coverage?** Yes. The smoke script invokes
and validates exactly the four named surfaces:
`external-tool-adapters --format json` over all eight adapters in
`EXPECTED_EXTERNAL_TOOL_ADAPTERS`, plus
`external-tool-template --adapter rednote_mcp --format json`,
`external-tool-workflow --adapter rednote_mcp --format json`, and
`external-tool-readiness --adapter rednote_mcp --format json`. The paragraph
explicitly states these are command-output contract checks only and enumerates
what they do not do, so it cannot be read as implying live collection, adapter
execution, or platform coverage.

**Q5 - Did any out-of-scope behavior slip into the plan?** No. The design,
implementation plan, proposed test diff, and proposed checklist paragraph do
not touch runtime smoke logic, first-run smoke fixture behavior, CLI behavior,
payload shapes, external-tool adapter/template/workflow/readiness runtime
behavior, install hints, mirror hints, dependency manifests, or `uv.lock`.

**Q6 - Any critical or important planning findings before implementation?** No.
The RED step is achievable because the current checklist omits the external-tool
paragraph, so the extended assertion will fail as predicted. The GREEN step
will pass once the paragraph is inserted, because every phrase in
`FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` is a substring of the normalized
paragraph text. Insertion point after the existing "directory handoff dry-run
counts" sentence is correct and contextually appropriate.

## Verdict

Approve. The Stage 177 plan is correctly scoped, boundary-compliant, and
accurately reflects the existing first-run smoke contract. The TDD ordering
(RED test, GREEN docs, then review/release/commit) is sound, the phrase-tuple
reuse is the right design, and the proposed wording matches the smoke script
without overstating coverage. Proceed with implementation; no changes required
before starting Task 1.
