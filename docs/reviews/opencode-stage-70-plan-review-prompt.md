# Stage 70 Plan Review Prompt

You are reviewing the Stage 70 spec and implementation plan in
`/home/ubuntu/fashion-radar`.

Do not edit files. Review these artifacts:

- `docs/superpowers/specs/2026-06-17-stage-70-adapter-readiness-command-test-hardening-design.md`
- `docs/superpowers/plans/2026-06-17-stage-70-adapter-readiness-command-test-hardening-plan.md`

## Review Goal

Confirm the plan safely hardens existing tests and first-run smoke validation
for the `external-tool-readiness` command printed in adapter
`recommended_commands`.

## Required Constraints

- No app runtime behavior changes.
- Adapter registry behavior and command output should not change.
- The smoke validator may parse already-printed recommended commands with
  `shlex.split`.
- The plan must explicitly avoid hard-coding user config/data default paths,
  because those vary by environment.
- The plan must add coverage for `--config-dir`, `--data-dir`, malformed shell
  quoting, and missing `--format table`.
- The stage must stay within local-first/free-first project boundaries and must
  not introduce connectors, scraping, browser automation, platform APIs,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance-review product behavior.

## Output Format

Return findings ordered by severity. Use `Critical`, `Important`, or `Minor`.
If there are no Critical/Important issues, state that explicitly. Keep the
review concise and include file/line references where relevant.
