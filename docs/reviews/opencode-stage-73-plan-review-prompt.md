# Stage 73 Plan Review Prompt

Review the Stage 73 design and implementation plan in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-18-stage-73-adapter-smoke-contract-design.md`
- `docs/superpowers/plans/2026-06-18-stage-73-adapter-smoke-contract-plan.md`

Use a planning/code-review stance. Lead with Critical or Important findings if
present; include Minor notes after. Do not propose adding scraping, connectors,
browser automation, platform APIs, login/cookie/session/token/proxy behavior,
CAPTCHA handling, media download, monitoring/scheduling, source acquisition,
demand proof, ranking, coverage verification, or compliance-review product
behavior.

## Goal

Extend first-run smoke validation of `external-tool-adapters --format json` so
the release smoke path covers all seven adapters, not only `adapters[0]`.

## Planned Scope

- Modify `scripts/check_first_run_smoke.py::validate_external_tool_adapters`.
- Modify `tests/test_first_run_smoke.py::external_tool_adapters_payload`.
- Keep runtime CLI and adapter registry code unchanged.
- Validate static JSON contract and parse readiness command strings only.

## Review Questions

1. Is the expected adapter map correct and consistent with the current registry?
2. Does the plan avoid broadening runtime behavior?
3. Are the proposed error messages and test mutations clear enough to prove
   later adapters are validated?
4. Are there any Critical or Important issues to fix before implementation?
