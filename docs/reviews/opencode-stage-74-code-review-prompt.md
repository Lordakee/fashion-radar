# Stage 74 Code Review Prompt

Review the Stage 74 implementation in `/home/ubuntu/fashion-radar`.

Use a code-review stance. Lead with Critical or Important findings if present,
then Minor notes. Focus on correctness, regression risk, test coverage, and
whether the implementation stays inside the intended test-only/static fixture
parity scope. Do not propose adding scraping, connectors, browser automation,
platform APIs, login/cookie/session/token/proxy behavior, CAPTCHA handling,
media download, monitoring/scheduling, source acquisition, demand proof,
ranking, coverage verification, or compliance-review product behavior.

For this stage, the user explicitly directed local review through
`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`; this
stage-local review path does not change broader repository review protocol
documents.

## Goal

Add a direct parity test proving
`tests/test_first_run_smoke.py::external_tool_adapters_payload()` matches the
real `build_external_tool_adapter_registry(...).model_dump_json()` output for
deterministic local inputs.

## Touched Files

- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-18-stage-74-adapter-registry-parity-design.md`
- `docs/superpowers/plans/2026-06-18-stage-74-adapter-registry-parity-plan.md`
- `docs/reviews/opencode-stage-74-plan-review-prompt.md`
- `docs/reviews/opencode-stage-74-plan-review.md`
- `docs/reviews/opencode-stage-74-code-review-prompt.md`

## Implementation Summary

- Imported `build_external_tool_adapter_registry` in
  `tests/test_first_run_smoke.py` for test parity only.
- Added `test_external_tool_adapters_payload_matches_real_registry` next to the
  existing external-tool template/workflow/readiness parity tests.
- Kept `external_tool_adapters_payload()` as a static hand-built fixture, not a
  wrapper around the runtime builder.
- Updated the static fixture to match the runtime registry exactly for adapter
  descriptions, upstream tool examples, field mapping notes, and required flags.
- Preserved Stage 73 adapter contract negative tests and deterministic
  first-run command sequence behavior.
- Runtime/source files are unchanged.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Latest broad verification result: full pytest collected 1100 tests and all
passed.

## Review Questions

1. Does the new parity test compare the static fixture to the real registry
   using the intended deterministic inputs?
2. Does `external_tool_adapters_payload()` remain static rather than delegating
   to the runtime builder?
3. Did the fixture fidelity changes preserve Stage 73 adapter contract negatives
   and first-run flow sequence behavior?
4. Did the implementation accidentally alter runtime adapter behavior or
   external platform behavior?
5. Are there any Critical or Important issues to fix before commit?
