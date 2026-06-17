# Stage 69 Code Review Prompt

You are reviewing the current uncommitted Stage 69 workspace in
`/home/ubuntu/fashion-radar`.

Do not edit files. Review for correctness, regression risk, missing tests, and
scope drift.

## Stage Goal

Refactor the first-run smoke command-capture test so detailed assertions for
unique commands use helper-based lookup instead of brittle numeric
`captured[...]` positions, while preserving the exact deterministic command
order assertion.

## Required Semantics

- Runtime code must not change.
- The first-run command sequence must not change.
- The exact ordered command-name assertion in
  `test_run_first_run_flow_uses_deterministic_local_command_sequence` must
  remain present.
- The test should no longer use numeric `captured[...]` references for unique
  command detail assertions.
- Unique command detail assertions must preserve the same checks as before.
- Duplicate `import-signals` handling must not be weakened; do not require
  `single_command("import-signals")`.
- This remains a local-first/free-first test-maintenance cleanup and must not
  introduce connectors, scraping, browser automation, platform APIs,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance-review product behavior.

## Files In Scope

- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-17-stage-69-first-run-smoke-command-lookup-design.md`
- `docs/superpowers/plans/2026-06-17-stage-69-first-run-smoke-command-lookup-plan.md`
- `docs/reviews/opencode-stage-69-plan-review-prompt.md`
- `docs/reviews/opencode-stage-69-plan-review.md`
- `docs/reviews/opencode-stage-69-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-69-plan-rereview.md`

## Verification Already Run

- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q`
  - passed before implementation: `1 passed`
  - passed after implementation: `1 passed`
- `rg -n "captured\\[" tests/test_first_run_smoke.py`
  - no matches
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q`
  - `52 passed`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - passed
- `uv --no-config run --frozen ruff check tests/test_first_run_smoke.py`
  - passed
- `uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py`
  - passed
- `uv --no-config run --frozen python scripts/check_release_hygiene.py`
  - passed
- `git diff --check`
  - passed
- `uv --no-config run --frozen pytest`
  - `1099 passed`

## Review Output Format

Return:

1. Findings ordered by severity.
2. For each finding, include file path, line number, severity (`Critical`,
   `Important`, or `Minor`), and concrete impact.
3. If no Critical/Important issues exist, state that explicitly.
4. Mention residual risk or test gaps.

Do not paste large diffs or long logs.
