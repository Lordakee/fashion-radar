# Stage 72 Plan Review Prompt

Review the Stage 72 design and implementation plan in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-18-stage-72-adapter-json-contract-design.md`
- `docs/superpowers/plans/2026-06-18-stage-72-adapter-json-contract-plan.md`

Use a code-review/planning-review stance. Lead with Critical or Important
findings if present; include Minor notes after. Do not propose adding scraping,
connectors, browser automation, platform APIs, login/cookie/session/token/proxy
behavior, CAPTCHA handling, media download, monitoring/scheduling, source
acquisition, demand proof, ranking, coverage verification, or
compliance-review product behavior.

## Goal

Broaden the `external-tool-adapters --format json` CLI contract test so it
validates all seven adapters, not only the first adapter.

## Planned Scope

- Modify `tests/test_cli.py::test_external_tool_adapters_command_prints_json`.
- Keep runtime code unchanged unless the broader test reveals true drift.
- Assert all adapter ids, stable metadata, field mappings, command sequence,
  and adapter-specific `external-tool-readiness` command flags.

## Review Questions

1. Is the plan test-only and appropriately scoped?
2. Are the expected adapter values and command sequence consistent with the
   current implementation?
3. Is the proposed nested `flag_value` helper valid inside the per-adapter loop,
   or should it be refactored to accept `readiness_parts` as an argument?
4. Are there Critical or Important issues to fix before implementation?
