# Opencode Stage 62 Plan Review

Reviewer: local `opencode`
Model: `zhipuai-coding-plan/glm-5.2`

## Verdict: CHANGES REQUIRED

The design and plan stay within the Stage 62 objective: print-only metadata
registry, no connectors, scraping, APIs, schema changes, or new dependencies.
The CLI signature matches existing patterns, generated command templates match
real command signatures, and the Pydantic model style matches existing handoff
modules. The plan is internally inconsistent in a way that would fail its own
verification gate.

## Critical

None.

## Important

1. `AGENTS.md` is omitted from Task 4 and Task 5, but the planned docs-drift
   test requires it. The test checks `AGENTS.md` for the new phrases
   "external social/community tool adapter registry" and
   "local producer-discovery registry". Add an `AGENTS.md` update step and add
   `AGENTS.md` to the commit file list.
2. Task 4 does not explicitly require the two new phrases in
   `docs/community-signal-import.md`, `docs/community-signal-quality.md`,
   `docs/source-boundaries.md`, and `docs/architecture.md`. Make Task 4 require
   both phrases in all four docs so the docs-drift test is directly
   satisfiable.

## Minor

1. The first-run smoke plan should say to run the CLI command first, then pass
   stdout to `validate_json_output(...)`; that helper only parses JSON.
2. The planned implementation imports `datetime` and `parse_datetime_utc`.
   Either explicitly parse/normalize `as_of`, or remove the unused imports.
3. The plan should explicitly source field-mapping required flags and allowed
   fields from `build_community_signal_profile()` so the registry cannot drift
   from the community signal contract.
