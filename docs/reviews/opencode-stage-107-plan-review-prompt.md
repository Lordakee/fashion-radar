# Stage 107 Plan Review Prompt

Review the Stage 107 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a section-scoped docs drift guard for `docs/source-boundaries.md`, scoped
only to the `## README Requirements` section, so public README boundary
obligations remain explicit about no full social-platform coverage, user
responsibility for source/robots/API terms, avoiding account-based default
collection, manual import as a local input path rather than a platform connector,
and community handoff check directory reports as local-only readiness reports.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-107-source-boundaries-readme-requirements-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-107-source-boundaries-readme-requirements-docs-plan.md`
- `docs/source-boundaries.md`
- `tests/test_source_boundaries_docs.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_source_boundaries_docs.py`. It will extract `## README Requirements`
and assert:

- `The public README must explain:`
- `The project does not provide full social-platform coverage.`
- `Users are responsible for respecting source terms, robots rules, and API terms.`
- `The default workflow avoids account-based collection and access-control bypasses.`
- `Manual signal import is a local input path, not a platform connector or instructions for obtaining platform exports.`
- `Community handoff check directory reports are local-only handoff readiness reports.`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 107 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `README.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- collector, robots/fetching, storage schema, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into README parity checks, runtime storage checks,
robots/fetching behavior, source collection, platform search, social monitoring,
market rankings, dashboard logic, report logic, schema migrations, connector
behavior, or compliance features.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` README Requirements
   boundary without changing product behavior or README text?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## README Requirements`?
3. Does appending to `tests/test_source_boundaries_docs.py` fit the Stage 106
   file pattern better than creating a second source-boundaries docs test file?
4. Does the plan avoid overlap with full README parity, CLI docs broad boundary
   checks, architecture source-boundary docs, robots/fetching behavior, package
   archive checks, and runtime collector/storage code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
