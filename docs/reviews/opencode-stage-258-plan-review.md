# Stage 258 Plan Review

**Reviewer:** opencode (GLM 5.2 max) — fallback per `docs/REVIEW_PROTOCOL.md`
(Claude Code plan review timed out after 180 s; see
`docs/reviews/claude-code-stage-258-plan-review.md`).

## Verdict

Approve with revisions. The plan is well-scoped, minimal,
AGENTS.md/REVIEW_PROTOCOL compliant, and the core implementation in Task 1 is
correct. Two important issues around test-guard strength and scope
acknowledgment should be fixed before implementation.

## Critical Issues

None.

## Important Issues

1. **Task 2 Step 2's "verify they fail" claim is inaccurate for the README guard.**
   The plan instructs adding `reports/fashion-radar-2026-06-13.html` to
   assertion tuples in `tests/test_cli_docs.py`. Those tests use `assert term in
   text` over the whole document, and README already contains that HTML path in
   other sections. A new assertion would pass immediately and would not drive
   the intended edit to the README sentence that still says temporary dated
   reports such as `.md` and `.json`. Pin the specific smoke-description
   sentence with a normalized substring assertion, or explicitly mark that README
   edit as unguarded editorial cleanup.

2. **Plan omits `docs/daily-digest.md` / `tests/test_daily_digest_docs.py`, which
   pins "reads only the markdown and json report files".** This is likely
   correctly out of scope because digest packaging consumes the MD/JSON pair, a
   separate concern from generated report-output hygiene. Add a Scope Out note
   declaring daily digest intentionally excluded so coverage parity is
   unambiguous.

## Optional Nits

- The default-artifact guard test additions are redundant with the generic
  `rglob` in `snapshot_default_artifacts`, which already detects any file under
  `reports/`, including `.html`. This is still acceptable as explicit parity
  coverage.
- The reset-command guard in `tests/test_cli_docs.py` is a contiguous expected
  literal. The implementation should rewrite the whole expected string, not just
  append a separate HTML deletion assertion.
- `report_paths` has exactly two consumers: the smoke script's
  `run_first_run_flow` and the report-path test. Both are covered by the plan.
- Stage 3 should confirm during the gate that `scripts/check_release_hygiene.py`
  has no MD/JSON-pinned generated report checks requiring changes.
- README and first-run already mention HTML report creation elsewhere; only the
  specific smoke-description and cleanup/reset lines need edits.
