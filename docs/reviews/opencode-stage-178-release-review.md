# Stage 178 Release Review

Objective:

Add focused regression guards for community handoff directory check renderer
count labels and unavailable candidate preview output.

## Summary

Stage 178 is a tightly scoped, test-only hardening stage that closes the three
minor coverage notes carried over from `docs/reviews/opencode-stage-171-code-review.md`.
The change set is confined to `tests/test_community_handoff_check.py` (`+100/-1`):
the existing singular renderer test is renamed to
`..._uses_singular_count_labels` (body byte-for-byte preserved), and two new
renderer-scoped exact-equality tests are appended — a plural count-label guard
and an unavailable candidate-preview guard. No runtime, model, CLI, importer,
candidate-scoring, dependency, or lockfile behavior changed; `git status` shows
the only modified tracked file is the test module, with the expected new
untracked spec/plan/review artifacts alongside.

I independently reproduced the headline release gate. The proxy-stripped full
suite reports `1376 passed`, the first-run smoke and release-hygiene scripts
pass, `ruff check .` is clean, `ruff format --check .` reports 144 files
already formatted, `UV_NO_CONFIG=1 uv lock --check` resolves 84 packages,
`git diff --check` is clean, the `ghp_` token grep returns no matches, and the
GitHub extraheader is not configured. The focused module runs `9 passed` with
`ruff check`/`ruff format --check` clean on the test file. The
`community-handoff-check-dir` scope boundary (local read-only; no source
acquisition, connectors, scraping, browser automation, platform APIs,
monitoring, scheduling, ranking, coverage verification, compliance-review
product feature) is respected.

## Findings

### Critical

None.

### Important

None.

### Minor

1. The perl artifact-cleanliness probe is reported as "no output, exit 0," but
   the command as specified includes a blank-line alternative, so it emits
   approximately 90 blank-line hits across the five Stage 178 markdown files
   (exit 0 is correct; "no output" is not). This is a probe-reporting
   inaccuracy, not an artifact defect: a re-run against only the real red-flag
   alternatives shows zero substantive matches in the review bodies, with the
   sole hit coming from the release-review prompt quoting the command itself.
   The artifacts contain no ANSI escapes, no build-status markers, no read-arrow
   markers, no capture stubs, no duplicated/truncated text, and no tool status
   messages. The plan-review (41 lines) and code-review (145 lines) bodies are
   complete and well-formed. Recommend either dropping the blank-line
   alternative from this probe in future stages or correcting the "no output"
   expectation; it does not block this release.

2. (Awareness, carried from plan/code review, still accurate.) The plural
   test's `model_copy` forces `error_count: 2` while leaving `result.findings`
   empty, so the renderer emits "No community handoff check findings." beside
   "2 errors" lines. This is intentional renderer-grammar coverage and is
   complementary to the singular test; no change needed.

## Verification Assessment

Scope. `git status --short` shows only `tests/test_community_handoff_check.py`
modified (plus the expected untracked spec/plan/prompt/review artifacts).
`git diff tests/test_community_handoff_check.py` shows the singular test rename
(one function-name line changed, body unchanged) followed by two verbatim
additions. No source files, models, CLI, config, dependency manifests, or
`uv.lock` changed. The stage stays within the `community-handoff-check-dir`
boundary and the AGENTS.md test-only-hardening scope.

Exact-line correctness. The three plural assertions (`Lint: 2 files, 2/2
import-ready rows, 2 errors`; `Candidate preview: 2 candidates from 2 rows`;
`Import dry-run: 2/2 valid files, 2 rows, 2 errors`) and the unavailable
assertions (`Candidate preview: unavailable` plus the stable
`candidate_preview_unavailable` finding row) are consistent with the renderer
contract the plan/code reviews traced through
`render_community_handoff_directory_check_table(...)` and
`format_count_label(...)`.

Independent reproduction of the release gate:
- Proxy-stripped full pytest — `1376 passed in 35.46s` (matches prompt).
- `check_first_run_smoke.py` — First-run sample smoke passed.
- `check_release_hygiene.py` — Release hygiene checks passed.
- `ruff check .` — All checks passed.
- `ruff format --check .` — 144 files already formatted (matches prompt).
- `UV_NO_CONFIG=1 uv lock --check` — Resolved 84 packages (matches prompt).
- `git diff --check` — clean, exit 0.
- `rg 'ghp_[A-Za-z0-9]+'` — no matches, exit 1.
- `git config --get-all http.https://github.com/.extraheader` — none, exit 1.

Focused reproduction:
- `pytest tests/test_community_handoff_check.py -q` — 9 passed.
- `ruff check` / `ruff format --check` on the test file — clean / 1 file already
  formatted.

The RED/absence claims are inherent and credible: neither new test name existed
before this stage, and the plural/unavailable renderer branches were only
indirectly exercised previously. The single evidence-reporting discrepancy
(Minor 1) concerns the perl probe's blank-line noise and does not reflect any
artifact-quality problem.

Review-history consistency. Both `opencode-stage-178-plan-review.md` and
`opencode-stage-178-code-review.md` report no critical or important findings
with minor awareness notes only, are internally consistent with each other and
with `docs/REVIEW_PROTOCOL.md`, and trace assertions to concrete renderer source
lines. The plan-review prompt, code-review prompt, and release-review prompt
are present and well-formed.

## Verdict

Approve. Stage 178 is in scope and ready to commit. The implementation is
test-only, matches the approved plan exactly, addresses all three Stage 171
follow-up notes, introduces no runtime/connector/scraping/platform-API/ranking/
coverage-verification/compliance-review/dependency/lockfile behavior, and the
full release gate (1376 passed, smoke and hygiene clean, ruff and lockfile
clean, no tokens or extraheader) is reproduced. The plan/code review artifacts
are clean and protocol-consistent. There are no critical or important findings;
the two minor notes are awareness items and do not block commit and push.
