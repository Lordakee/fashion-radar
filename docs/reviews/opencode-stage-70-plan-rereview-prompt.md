# Stage 70 Plan Rereview Prompt

You are rereviewing the Stage 70 spec and implementation plan in
`/home/ubuntu/fashion-radar` after the first plan review found a Critical test
conflict.

Do not edit files. Review these artifacts:

- `docs/superpowers/specs/2026-06-17-stage-70-adapter-readiness-command-test-hardening-design.md`
- `docs/superpowers/plans/2026-06-17-stage-70-adapter-readiness-command-test-hardening-plan.md`
- `docs/reviews/opencode-stage-70-plan-review.md`

## Prior Critical Finding

The original plan kept the existing `missing_token` negative test as a heavily
truncated readiness command. The new parser would report `--directory` missing
before `--input-format`, so the existing pytest `match="--input-format"` would
fail.

## Rereview Goal

Confirm the plan now resolves that conflict by changing `missing_token` to omit
only `--input-format`. Also review the added CLI token-level assertion scope.

## Required Constraints

- No app runtime behavior changes.
- Adapter registry behavior and command output should not change.
- The smoke validator may parse already-printed recommended commands with
  `shlex.split`.
- The plan must avoid hard-coding user config/data default paths.
- The plan must add coverage for `--config-dir`, `--data-dir`, malformed shell
  quoting, and missing `--format table`.
- The added CLI test hardening must stay token-based, not exact-string brittle.

## Output Format

Return findings ordered by severity. Use `Critical`, `Important`, or `Minor`.
If there are no Critical/Important issues, state that explicitly. Keep the
review concise and include file/line references where relevant.
