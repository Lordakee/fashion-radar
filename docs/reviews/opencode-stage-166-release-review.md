# Stage 166 Release Review

## Summary

Stage 166 hardens the local first-run smoke validator
`validate_community_handoff_check_dir(...)` in
`scripts/check_first_run_smoke.py` by adding exact `assert_equal` checks for
stable, previously-unpinned nested payload fields across four areas: the
top-level `findings` list, `community_signal_lint` identity/provenance details,
`candidate_preview` metadata, and `import_dry_run` provenance maps. The change
is paired with focused one-field-at-a-time drift tests in
`tests/test_first_run_smoke.py`. The working tree contains exactly the nine
listed files (two modified plus seven new docs/review artifacts), with no
`src/` changes and no product behavior change. All independent re-runs
reproduce the stated evidence: focused tests 30 passed / 131 deselected, full
suite 1363 passed, smoke passed, release hygiene passed, ruff check + format
clean, and `uv lock --check` resolved 84 packages. Stage 166 is in scope and
ready to commit and push.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Carried forward from plan and code reviews, non-blocking: the
   `candidate_preview` window fields (`current_window_start`,
   `baseline_window_start`, `current_days`, `baseline_days`) are derived from
   `CandidateDiscoverySettings` defaults plus the fixed `AS_OF` rather than
   independent contract constants. This is the intended drift-catching coupling
   and the smoke confirms the match; flagged only so the dependency is explicit
   if those defaults ever change.

2. Carried forward, non-blocking and cosmetic: reusing
   `EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS` to derive `lint.field_counts` is
   sound since both surfaces share the community-signal schema, but the name is
   template-centric. A schema-named alias or inline comment would make the
   shared-schema intent self-documenting. The dict comprehension is
   order-independent and matches the fixture.

No newly introduced release-level issues. No secrets, tokens, cookies, local
account data, generated reports, SQLite databases, build artifacts, or
CodeGraph DB files entered the working tree. `git diff --check` is clean.
Review artifacts (`opencode-stage-166-plan-review.md`,
`opencode-stage-166-code-review.md`) each contain a single coherent body with
one verdict and no live-capture stubs, tool-status lines, truncation, or
duplicated text, consistent with `docs/REVIEW_PROTOCOL.md`.

## Verification Assessment

Q1 (scope and commit readiness): Met. The diff is confined to
`scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py`; the
remaining seven files are docs/spec/plan/review-prompt/review artifacts. No
`src/` path is modified. Assertions pin top-level `findings` to `[]`,
`candidate_preview.candidates` to `[]`, and scalar/provenance fields, while
deliberately leaving nested `files` lists and nested section `findings` lists
unpinned, matching the stated scope boundaries.

Q2 (review artifacts clean and consistent with REVIEW_PROTOCOL.md): Met. Both
review records are complete, coherent, and contain no critical or important
findings. Minor findings are documented and non-blocking; only critical and
important findings block per `AGENTS.md`. Naming and capture hygiene match the
protocol.

Q3 (release evidence sufficiency): Met. This is a validator-only hardening
stage (additive assertions plus drift tests, no runtime product path change),
and the full release gate was re-run independently and reproduced the stated
results.

Q4 (out-of-scope artifacts/production files/secrets/private data): None
detected. No `src/` changes, no CLI/producer/model changes, no nested
list-exactness, and no new collection/import/SQLite behavior. The `ghp_` scan
found no matches. `http.https://github.com/.extraheader` is not configured.
The token scan of the diff is clean. Working-tree data-file scan shows only the
expected docs/review/spec/plan markdown.

Independent re-run evidence:

- `env -u ...proxy... pytest -q`: 1363 passed in 33.37s.
- `pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir"`:
  30 passed, 131 deselected.
- `python scripts/check_first_run_smoke.py --repo-root .`: First-run sample
  smoke passed.
- `python scripts/check_release_hygiene.py --repo-root .`: Release hygiene
  checks passed.
- `ruff check .`: All checks passed.
- `ruff format --check .`: 144 files already formatted.
- `UV_NO_CONFIG=1 uv lock --check`: Resolved 84 packages in 1ms.
- `git diff --check`: no output, exit 0.
- `rg 'ghp_[A-Za-z0-9]{20,}'`: no matches.
- `git config --get-all http.https://github.com/.extraheader`: not set.

## Verdict

Approve for commit and push. Stage 166 is in scope, the validator hardening is
narrow and fully test-covered, the review artifacts are clean and
protocol-consistent, all release-gate checks reproduce green, and no
out-of-scope code, generated artifact, secret, or local private data entered
the working tree.
