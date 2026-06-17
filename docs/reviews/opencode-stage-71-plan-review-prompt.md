# Stage 71 Plan Review Prompt

You are reviewing the Stage 71 spec and implementation plan in
`/home/ubuntu/fashion-radar`.

Do not edit files. Review these artifacts:

- `docs/superpowers/specs/2026-06-17-stage-71-adapter-readiness-docs-guard-design.md`
- `docs/superpowers/plans/2026-06-17-stage-71-adapter-readiness-docs-guard-plan.md`

## Review Goal

Confirm the plan safely adds a focused docs drift guard for the documented
relationship between `external-tool-adapters` and `external-tool-readiness`.

## Required Constraints

- Runtime code must not change.
- Existing docs should not change unless the new test exposes actual drift.
- The guard should pin stable concepts, not exact paragraphs.
- The guard must preserve that `external-tool-adapters` is print-only and does
  not run readiness or perform PATH lookup.
- The guard must preserve that adapter command lists include
  `external-tool-readiness` as an optional local read-only preflight command.
- No connectors, scraping, browser automation, platform APIs, scheduling,
  source acquisition, demand proof, ranking, coverage verification, or
  compliance-review product behavior should be introduced.

## Output Format

Return findings ordered by severity. Use `Critical`, `Important`, or `Minor`.
If there are no Critical/Important issues, state that explicitly. Keep the
review concise and include file/line references where relevant.
