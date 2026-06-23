# Stage 177 Release Review

Objective:

Keep `docs/github-upload-checklist.md` aligned with README and
`docs/first-run.md` by naming every local external-tool JSON contract surface
that the automated first-run smoke already validates.

## Summary

Stage 177 is a tightly scoped docs/test-only change. It extends
`test_upload_checklist_documents_first_run_smoke_boundary` to assert every phrase
in the shared `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` tuple, and adds one
8-line paragraph to the Package Smoke section of
`docs/github-upload-checklist.md` that names exactly the four contract surfaces
the automated first-run smoke validates. The diff is minimal (+10 lines across
two files), boundary-clean, and accurately mirrors the verified README and
`docs/first-run.md` wording verbatim. No runtime, payload, adapter,
smoke-script, lockfile, install-hint, mirror-hint, dependency, or
compliance-review behavior is touched. The plan and code review artifacts are
clean and consistent with `docs/REVIEW_PROTOCOL.md`. No critical or important
findings.

## Findings

### Critical

None.

### Important

None.

### Minor

- M1 (advisory, no change required): `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES`
  guards normalized substrings rather than full sentence ordering across the
  three first-run-smoke documentation surfaces (README, `docs/first-run.md`,
  upload checklist). This is the same accepted tradeoff recorded in the Stage 177
  plan and code reviews; the tuple still covers every load-bearing claim, so
  parity holds. No action needed.
- M2 (advisory): Before staging the commit, file this release review record at
  `docs/reviews/opencode-stage-177-release-review.md` per review-capture
  hygiene. The plan-review and code-review artifacts already exist with
  complete, non-stubbed bodies.

## Verification Assessment

The submitted evidence is accurate and was independently reproduced.

- Scope (Q1, Q4): `git diff --name-only` confirms exactly two changed files:
  `docs/github-upload-checklist.md` (+8) and `tests/test_cli_docs.py` (+2). The
  test diff adds the phrase-tuple loop only; the docs diff adds the single
  external-tool JSON-contract paragraph after the existing "directory handoff
  dry-run counts" sentence. No runtime CLI, smoke script
  (`scripts/check_first_run_smoke.py`), `tests/test_first_run_smoke.py`,
  payload, adapter, template, workflow, readiness builder, install-hint,
  mirror-hint, dependency manifest, or `uv.lock` changes were introduced.
- Parity (objective): all nine `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` entries
  are present in the normalized text of README, `docs/first-run.md`, and
  `docs/github-upload-checklist.md`, confirming verbatim-parity with the
  pre-existing enforced surfaces.
- Accuracy against smoke: `scripts/check_first_run_smoke.py` validates exactly
  the named surfaces — `external-tool-adapters --format json` over all eight
  adapters in `EXPECTED_EXTERNAL_TOOL_ADAPTERS`, plus the three
  `--adapter rednote_mcp --format json` invocations for `external-tool-template`,
  `external-tool-workflow`, and `external-tool-readiness`. The new paragraph's
  "command-output contract checks only" clause and its "do not run adapters ...
  do not call platform APIs ... do not perform source acquisition" boundary
  match the smoke validators and cannot be read as implying live collection,
  adapter execution, or platform coverage (Q4, scope boundaries).
- Boundary compliance (Q4): no source acquisition, connectors, scraping,
  browser automation, platform APIs, MCP execution, login, cookies, monitoring,
  scheduling, demand proof, ranking, coverage verification, or compliance-review
  product feature was added.
- RED/GREEN: the pre-edit checklist omitted the paragraph, so the extended
  assertion would have failed on the first missing phrase; after the docs edit,
  `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_upload_checklist_documents_first_run_smoke_boundary -q`
  -> 1 passed (independently reproduced).
- Test group: `uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "upload_checklist or first_run_smoke"`
  -> 10 passed, 59 deselected (independently reproduced).
- Lint: `uv --no-config run --frozen ruff check tests/test_cli_docs.py` -> All
  checks passed; `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
  -> 1 file already formatted (independently reproduced).
- Release gates (Q3, Q5): the reported full-suite 1374 passed, first-run smoke
  pass, release hygiene pass, repo-wide ruff check/format, `uv lock --check`
  (84 packages), `git diff --check` (clean, exit 0, independently reproduced),
  `rg 'ghp_...'` (no matches, exit 1, independently reproduced), and absent
  GitHub extraheader (exit 1, independently reproduced) are consistent with a
  docs/test-only stage and sufficient for this change class. The verification
  evidence is sufficient; no out-of-scope runtime, smoke-script, payload,
  adapter, source-acquisition, ranking, coverage-verification, install-hint,
  mirror-hint, dependency, or lockfile behavior slipped in (Q4).
- Review artifacts (Q2): `docs/reviews/opencode-stage-177-plan-review.md` and
  `docs/reviews/opencode-stage-177-code-review.md` are complete, non-stubbed,
  single-verdict records with no live tool status lines, duplicated text, or
  truncated output. Both record no critical or important findings and only the
  same minor notes carried forward here. Naming and structure are consistent
  with `docs/REVIEW_PROTOCOL.md`.

## Verdict

Approve. Stage 177 is in scope, boundary-compliant, and ready to commit and
push. The checklist wording is verbatim-parity with README and
`docs/first-run.md`, names exactly the four contract surfaces the automated
first-run smoke validates, and the shared phrase tuple is a sound DRY parity
guard. No critical or important findings; file this release review record, then
proceed to commit and push.
