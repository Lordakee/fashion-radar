# Stage 99 Plan Review Prompt

Review the Stage 99 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/manual-signal-import.md`, scoped only
to the `## Privacy Boundary` section, so manual import remains documented as
limited to conservative local metadata and away from private or sensitive
material.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-plan.md`
- `docs/manual-signal-import.md`

## Planned Test

The implementation will add `tests/test_manual_signal_import_docs.py` with one
docs-only test that extracts `## Privacy Boundary` and asserts:

- `do not import private comments`
- `account ids`
- `cookies`
- `author profiles`
- `follower lists`
- `images, videos`
- `private or sensitive material`
- `keep imported rows limited to conservative metadata`
- `allowed to process and review locally`

## Scope Constraints

Allowed changes:

- `tests/test_manual_signal_import_docs.py`
- Stage 99 review artifacts

Disallowed changes:

- `docs/manual-signal-import.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime manual import tests
- data-retention, dashboard, architecture/source-boundary, source-pack,
  entity-pack, entity-pack-quality, candidate-discovery, or imported-candidate
  behavior

Do not expand this stage into manual import workflow text, local input path
claims, connector/platform-collector claims, source-acquisition guide claims,
candidate review semantics, dashboard/report wording, privacy-compliance
features, audit/legal review, or runtime validation changes.

## Review Questions

1. Does the plan protect a real manual-signal-import privacy docs boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/manual-signal-import.md` and scoped
   narrowly enough to `## Privacy Boundary`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially
   architecture/source boundaries and candidate discovery?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
