# Stage 181 Release Review

## Summary

Stage 181 is a docs/test-only parity node that (a) adds a runtime-derived
`Known adapter ids` table to `docs/community-signal-import.md` and
`docs/community-signal-quality.md`, and (b) adds a drift guard in
`tests/test_external_tool_contract_parity.py` that rebuilds every row from the
live `ExternalToolAdapter` registry. The change set is exactly 2 docs + 1 test
(82 insertions, 0 deletions) plus the 9 untracked review/spec/plan/prompt
artifacts. No runtime, CLI, connector, source-acquisition, scraping, browser,
platform-API, ranking, compliance-review, dependency, lockfile, package,
source-pack, or entity-pack behavior is present. Approved for commit and push.

## Question Answers

1. In scope and ready to commit. Scope is docs/test-only by design. The table
   block is byte-identical to the already-approved wording in `README.md` and
   `docs/cli-reference.md` and states the labels are "advisory local provenance
   label guidance ... not a schema enum, not a linter restriction, not platform
   coverage, and not demand proof." No connectors, no scraping, no browser
   automation, no platform APIs, no monitoring/scheduling, no source
   acquisition, no demand proof, no ranking, no coverage verification, no
   compliance-review product. Honors all `AGENTS.md` community-tool boundaries.

2. Artifacts complete, clean, and consistent. `opencode-stage-181-plan-review.md`,
   `-code-review.md`, and `-code-rereview.md` are all present, non-stub, and
   each carries explicit Critical/Important/Minor sections. The plan review
   confirmed RED-before-GREEN and anchor validity; the code review confirmed
   runtime-derived rows and byte-exact doc values with an independent
   RED/GREEN experiment; the rereview closed the first review's M1 by adding a
   standalone header-string assertion and removing a trailing fence. Prompt
   files for each stage are also present.

3. Verification sufficient. Full suite (1378 passed), first-run smoke, release
   hygiene, ruff check, ruff format --check (144 files), `uv lock --check`
   (84 packages), `git diff --check`, secret scan (`ghp_`), and git extraheader
   are all clean. Independently re-ran
   `pytest tests/test_external_tool_contract_parity.py tests/test_cli_docs.py`
   -> 76 passed. The guard is a genuine drift trap: any future registry
   addition forces a doc update in both files.

4. No drift. Independent diff confirms only `docs/community-signal-import.md`,
   `docs/community-signal-quality.md`, and
   `tests/test_external_tool_contract_parity.py` changed. All 8 registry rows
   (`src/fashion_radar/external_tool_adapters.py:108-251`) match both doc
   tables exactly on id / display_name / platform_label / format / pattern.
   `pyproject.toml`, `uv.lock`, and all `src/` runtime modules are untouched.

5. No Critical or Important findings.

## Critical

None.

## Important

None.

## Minor

- M1 (non-blocking, `tests/test_external_tool_contract_parity.py:123-131`).
  The guard asserts each registry row is present as a substring and asserts the
  header, but it does not assert row order or the absence of extra rows, so a
  stale-but-valid row left behind after a registry removal could go undetected
  until the removed adapter's row is also dropped. The substring form plus the
  header check is adequate for current parity purposes; optional future
  hardening could assert the full normalized table block per doc.
- M2 (non-blocking, advisory wording repetition). The explanatory paragraph is
  duplicated verbatim across the two community docs (and README/cli-reference).
  This is intentional parity and matches the existing pattern, so no action is
  needed; flagged only for awareness.

Stage 181 is approved for commit and push.
