# Stage 393 Plan Review - OpenCode Fallback

## Review Context

- Reviewer: local OpenCode fallback after the primary Claude Code attempt timed out without review output
- Model: `zhipuai-coding-plan/glm-5.2`
- Variant: `max`
- Scope: Stage 393 strict ROW ONE ops-check design and implementation plan

## Feasibility

The plan is feasible and minimal. It adds one opt-in flag, one canonical
healthy-status constant and pure predicate, one defensive status allowlist, and
a post-output exit. It adds no dependencies, payload fields, generated files,
or I/O.

## Important Findings And Resolutions

1. `typer.Exit` is an `Exception`, so the strict failure must be raised strictly
   after the existing `try/except Exception` block. Otherwise the generic
   handler would print `ROW ONE ops check failed:` and corrupt the contract.
   The plan now calls out this placement and requires a regression assertion
   that strict failure does not emit that generic error.
2. The payload compatibility promise needs an explicit regression test. The
   plan now requires `--strict --json` and ordinary `--json` to produce
   byte-identical stdout for the same patched payload, with only the process
   exit status differing.

## Minor Findings And Resolutions

- The design now distinguishes the reusable healthy-status constant from the
  CLI predicate and the local-article healthy allowlist.
- The pure predicate test matrix now includes unrecognized strings, missing
  status, and `None`.
- The docs now state that `ok` means diagnostic construction succeeded; strict
  automation must use the process exit code to judge health.
- Documentation additions are isolated from the existing Stage 329 boundary
  slice, and documentation tests remain pure content assertions.
- CLI help tests explicitly require `--strict` and reject an unexpected
  `--no-strict` form.

## Verdict

**APPROVE WITH REVISIONS.** The revised plan is ready for implementation after
the above changes are recorded.
