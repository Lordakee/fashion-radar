I'll review whether the two Minor findings are addressed. Let me read the relevant files in parallel.
Let me verify there are no lingering references to the old function form and confirm the tests reference the new constant correctly.
Let me run the parity test to confirm it passes as verification.
## Findings
- **Minor 1 (registry/spec parity)**: Closed. `_upstream_command_check` now wraps the spec lookup in `try/except KeyError` and re-raises as a friendly `ValueError` (`external_tool_readiness.py:254-257`), matching the error style for unknown adapters. A new parity test `test_readiness_command_specs_cover_adapter_registry` (`tests/test_external_tool_readiness.py:411-430`) iterates every adapter in the registry and builds readiness for each, so a future adapter lacking a spec fails the suite rather than silently breaking at runtime.
- **Minor 2 (module-level constant)**: Closed. The parameterless `_upstream_command_specs()` function is replaced by the `_UPSTREAM_COMMAND_SPECS` module-level constant (`external_tool_readiness.py:43-92`), referenced via direct dict lookup at `external_tool_readiness.py:255`. No per-call reconstruction remains; only one reference site exists.

Verification: all 18 tests in `tests/test_external_tool_readiness.py` pass.

## Verdict
Both Minor findings from `docs/reviews/opencode-stage-66-code-review.md` are closed. No new Critical or Important findings.
