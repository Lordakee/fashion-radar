# Opencode Stage 58 Plan Review Prompt

You are reviewing the Stage 58 design and implementation plan for
`/home/ubuntu/fashion-radar`.

Review model requested by the project owner:
`zhipuai-coding-plan/glm-5.2`.

Do not edit files. Review only these planning artifacts:

- `docs/superpowers/specs/2026-06-17-stage-58-imported-heat-review-workflow-design.md`
- `docs/superpowers/plans/2026-06-17-stage-58-imported-heat-review-workflow-plan.md`

## Objective

Stage 58 should extend the existing print-only `imported-review-workflow` with
one final local read-only `heat-movers` review step so sanitized external or
community tool outputs have a clear post-import path into heat/trend review.

## Required Boundaries

The stage must not add:

- new platform/social/source connectors
- scraping, crawling, platform APIs, browser automation
- accounts, cookies, sessions, or login handling
- monitoring, watching, scheduling, or source acquisition
- schema/migration changes
- dependency or lockfile changes
- daily report/digest/dashboard writes
- new compliance/legal/authorization/safety-review features
- changes to producer-facing community handoff/profile/manifest/check-dir
  behavior

## Review Questions

Please verify:

1. The design is scoped to a single small feature and does not duplicate
   existing community handoff behavior.
2. The implementation plan follows TDD and lists concrete files, tests,
   commands, and expected failures.
3. The plan keeps `imported-review-workflow` print-only and does not make the
   workflow execute `heat-movers`.
4. The new heat review step uses existing `heat-movers` CLI behavior and does
   not add new DB reads/writes inside the workflow builder.
5. The plan has enough test coverage for direct builder output, CLI JSON/table
   output, docs drift, no source-name leakage into `heat-movers`, and no
   artifact/data-dir creation from the workflow command.
6. Docs requirements preserve local-only/no demand proof/no platform coverage
   verification wording.
7. Release checks include full tests, ruff, lockfile/mirror checks,
   release-hygiene, first-run smoke, installed-wheel smoke, and opencode
   release review.

## Output Format

Return:

- Critical findings
- Important findings
- Minor findings
- Final verdict

If there are no Critical or Important findings, include this exact approval
line:

```text
APPROVED FOR STAGE 58 PLAN
```
