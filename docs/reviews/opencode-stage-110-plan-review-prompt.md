# Stage 110 Plan Review Prompt

Review the Stage 110 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a section-scoped docs drift guard for `docs/source-boundaries.md`, scoped
only to the `## Robots And Fetching` section, so robots/fetching guidance
remains explicit about robots.txt checks before article extraction, skipped URL
reasons, source-specific rate limits, and GDELT metadata/link storage and
backoff boundaries.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-plan.md`
- `docs/source-boundaries.md`
- `tests/test_source_boundaries_docs.py`
- `tests/test_collectors_robots.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_source_boundaries_docs.py`. It will extract `## Robots And Fetching`
and assert:

- `Before fetching an article page for extraction, collectors must check robots.txt.`
- `Default fetch behavior:`
- `Use source-specific rate limits where configured.`
- `Record skipped URLs with reasons.`
- `GDELT fetch behavior:`
- `Use bounded exponential backoff.`
- `Store GDELT-provided metadata and links, not republished article bodies.`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 110 review artifacts

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
- `tests/test_collectors_robots.py`
- `tests/test_cli_docs.py`
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- HTTP client behavior, robots parser behavior, article extraction behavior,
  GDELT runtime behavior, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime collector tests, HTTP/robots policy
changes, GDELT fetching behavior, source collection, platform search, social
monitoring, schema migrations, connector behavior, or compliance features.

This stage intentionally does not freeze the numeric GDELT throttling sentence
(`near 1 request per second`) and avoids generic fetch-policy bullets already
covered more directly by runtime collector tests.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` Robots And Fetching
   section without changing product behavior or docs text?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Robots And Fetching`?
3. Does appending to `tests/test_source_boundaries_docs.py` fit the existing
   source-boundaries docs test pattern?
4. Does the plan avoid overlap with collector runtime tests, HTTP/robots policy,
   GDELT fetching behavior, package archive checks, and runtime code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
