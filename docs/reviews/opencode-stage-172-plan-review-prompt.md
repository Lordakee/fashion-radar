# Stage 172 Plan Review Prompt

Review the Stage 172 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 172 Plan Review

Objective:

Make the first-run smoke readiness parity test fail loudly if
`fashion_radar.external_tool_readiness` is missing or broken, instead of
silently skipping behind a stale Stage 66 fallback.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-172-first-run-readiness-import-hardening-design.md`
- `docs/superpowers/plans/2026-06-23-stage-172-first-run-readiness-import-hardening-plan.md`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_readiness.py`
- `tests/test_external_tool_readiness.py`

Scope boundaries:

- Test-hygiene only.
- Remove the stale optional import fallback and `skipif` around the
  external-tool-readiness first-run smoke parity test.
- Keep runtime source, first-run smoke script behavior, adapter metadata,
  payload shapes, command order, boundaries, and install hints unchanged.
- No changes to `src/fashion_radar/external_tool_readiness.py`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Planned implementation:

1. Add a RED meta test in `tests/test_first_run_smoke.py` that asserts
   `test_external_tool_readiness_payload_matches_real_rednote_readiness` does
   not carry a `skipif` mark.
2. Run that meta test before implementation and confirm it fails because the
   current parity test still has the stale `skipif` mark.
3. Replace the optional import fallback with a direct import:
   `from fashion_radar.external_tool_readiness import build_external_tool_readiness`.
4. Remove the stale `@pytest.mark.skipif(...)` decorator and redundant
   `assert build_external_tool_readiness is not None`.
5. Run focused tests/checks, code review, full release gate, release review,
   commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Is the meta test a useful RED guard for this stale skip removal?
4. Is it appropriate for the first-run smoke parity test to fail at import or
   collection time if `external_tool_readiness` is missing?
5. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
