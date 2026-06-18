# Stage 109 Plan Review Prompt

Review the Stage 109 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a section-scoped docs drift guard for `docs/source-boundaries.md`, scoped
only to the `## Quality Boundaries` section, so quality-boundary guidance
remains explicit about heat scores being local metrics, candidate signals
needing review rather than validation, and the dashboard showing a small set of
local diagnostic fields.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-109-source-boundaries-quality-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-109-source-boundaries-quality-docs-plan.md`
- `docs/source-boundaries.md`
- `tests/test_source_boundaries_docs.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_source_boundaries_docs.py`. It will extract `## Quality Boundaries`
and assert:

- `Heat scores are local metrics based on configured sources and imported local signals.`
- `They are not rankings outside that local source set.`
- `Candidate signals are observed phrases from configured sources and imported local signals and need review.`
- `They should not be presented as validated entities.`
- `The dashboard should show:`
- `Source count.`
- `Representative links.`
- `Time window.`
- `Failed source runs.`
- `Missing data warnings.`
- `Whether a source is core, opt-in, or experimental.`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 109 review artifacts

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
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- connectors, scraping, browser automation, platform APIs, monitoring,
  scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime scoring checks, candidate validation
logic, dashboard/report behavior, README parity checks, source collection,
platform search, social monitoring, schema migrations, connector behavior, or
compliance features.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` Quality Boundaries
   section without changing product behavior or docs text?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Quality Boundaries`?
3. Does appending to `tests/test_source_boundaries_docs.py` fit the existing
   source-boundaries docs test pattern?
4. Does the plan avoid overlap with scoring, candidate discovery, dashboard,
   report behavior, package archive checks, and runtime code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
