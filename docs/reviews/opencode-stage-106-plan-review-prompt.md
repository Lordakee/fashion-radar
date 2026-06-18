# Stage 106 Plan Review Prompt

Review the Stage 106 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/source-boundaries.md`, scoped only
to the `## Storage Boundaries` section, so source-boundary storage guidance
remains explicit about conservative local storage, source metadata and local
provenance, avoiding full article text/media/comment redistribution by default,
preserving source attribution, and skipping known paywalled extraction unless
permitted metadata is provided.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-106-source-boundaries-storage-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-106-source-boundaries-storage-docs-plan.md`
- `docs/source-boundaries.md`

## Planned Test

The implementation will add `tests/test_source_boundaries_docs.py` with one
docs-only test that extracts `## Storage Boundaries` and asserts:

- `Default storage should be conservative:`
- `` Store source URLs, titles, publication timestamps, source names, optional local `platform` provenance labels for imported rows, short summaries, entity matches, tags, counts, and scores. ``
- `Avoid storing full article text by default.`
- `Avoid storing original images or videos.`
- `Avoid storing user comments as redistributable assets.`
- `Preserve source links so users can read original content on the source site.`
- `Display source attribution beside representative items.`
- `Add attribution footer to generated reports.`
- `Skip extraction for known paywalled domains unless the source itself provides permitted metadata.`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 106 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
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

Do not expand this stage into runtime storage checks, robots/fetching behavior,
source collection, platform search, social monitoring, market rankings,
dashboard logic, report logic, schema migrations, connector behavior, or
compliance features.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` storage boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Storage Boundaries`?
3. Does the plan avoid overlap with robots/fetching behavior, output wording,
   README requirements, architecture source-boundary docs, package archive
   checks, and runtime collector/storage code?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
