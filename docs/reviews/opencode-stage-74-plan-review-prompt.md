# Stage 74 Plan Review Prompt

Review the Stage 74 design and implementation plan in
`/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-18-stage-74-adapter-registry-parity-design.md`
- `docs/superpowers/plans/2026-06-18-stage-74-adapter-registry-parity-plan.md`

Use a planning/code-review stance. Lead with Critical or Important findings if
present; include Minor notes after. Do not propose adding scraping, connectors,
browser automation, platform APIs, login/cookie/session/token/proxy behavior,
CAPTCHA handling, media download, monitoring/scheduling, source acquisition,
demand proof, ranking, coverage verification, or compliance-review product
behavior.

For this stage, the user explicitly directed local review through
`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`; this
stage-local review path does not change broader repository review protocol
documents.

## Goal

Add a direct parity test proving
`tests/test_first_run_smoke.py::external_tool_adapters_payload()` matches the
real `build_external_tool_adapter_registry(...).model_dump_json()` output for
deterministic local inputs.

## Planned Scope

- Modify only `tests/test_first_run_smoke.py`.
- Keep runtime CLI and adapter registry code unchanged.
- Make the first-run smoke adapter fixture full-fidelity with the runtime
  registry JSON.
- Preserve Stage 73 adapter contract negative tests and first-run flow sequence.

## Review Questions

1. Is this parity-test scope safe and useful after Stage 73?
2. Does the plan correctly anticipate fixture drift in `description`,
   `upstream_tool_examples`, `field_mappings`, and `boundaries`?
3. Does the plan avoid runtime behavior changes and external platform behavior?
4. Are there any Critical or Important issues to fix before implementation?
