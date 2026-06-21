# Stage 156 Plan Review

## Verdict

**No blocking issues.** The plan is sound, correctly scoped, and faithful to the
path-exactness pattern already established for `validate_community_handoff_workflow`
and `validate_imported_review_workflow`.

## Findings by Review Question

### 1. RED tests isolate coordinated top-level path drift

Yes. The proposed `rewrite_external_tool_payload_paths` helper rewrites the
three top-level fields directly and rewrites nested command argv via exact
`shlex` token equality (`exports` / `configs` / `data`). Those literals appear
only as path values, not as flag names, adapter ids, or substrings of other
tokens. The parametrized drift over `directory`, `config_dir`, and `data_dir`
will surface field-specific `SmokeError` checks because the design places
top-level assertions before nested command synthesis.

### 2. Validator signatures and `run_first_run_flow(context)` threading

Yes. The proposed keyword-only expected path parameters match the existing
community-handoff shape, with defaults adapted to the external-tool static
fixtures (`exports`, `configs`, `data`). The runtime call-site threading mirrors
the existing community-handoff and imported-review validators.

### 3. Deterministic flow test context-path payloads

Yes, this is required. Once `run_first_run_flow` passes temp paths into the
validators, static fixtures with `directory="exports"` would fail. The plan
correctly keeps default fixtures for builder parity tests and adds rewritten
context-path helpers only for the deterministic first-run flow test.

### 4. `shlex.split()` / `shlex.join()` command rewriting

Yes. Token-based rewriting is safer than raw substring replacement, and the
validator already parses commands with `shlex.split`, so quoting normalization is
consistent.

### 5. Runtime builders remain unchanged

Yes. Both builders stringify `directory`, `config_dir`, and `data_dir` once and
thread the same values into top-level fields and generated steps. No builder
change is warranted.

### 6. Verification commands

Yes. Focused RED/GREEN selection, deterministic flow test, full first-run smoke
module, real smoke script, ruff, diff check, full release gate, lock check, and
token/header hygiene are sufficient.

## Minor Non-Blocking Notes

- Task 3 Steps 2/4 should remove the old non-empty-only path loops and the
  payload-derived `directory = str(payload["directory"])` style bindings. Nested
  command synthesis should use `expected_directory`, `expected_config_dir`, and
  `expected_data_dir`.
- The explicit runtime-path acceptance RED test has no direct analog in the
  community-handoff suite but is useful. Expected RED state is `TypeError`, then
  GREEN once kwargs land.
- Commit message `feat: pin external tool workflow paths` is acceptable.

Proceed to implementation.
