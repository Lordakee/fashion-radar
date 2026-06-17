I'll review Stage 68 changes. Let me start by examining the current state and the diff.
Let me verify the actual `external-tool-readiness` command's argument interface matches what's being recommended.
Let me check the `--format` option name on `external-tool-readiness` to confirm the recommended flag name is correct.
Flag interface verified. Now let me examine the tests.
Now let me check the docs changes and remaining files in scope.
Let me check `external_tool_template.py` to verify the boundary that JSON/CSV handoff rows do not include the readiness command guidance.
Let me verify `external-tool-workflow` wasn't unintentionally affected.
Let me verify the test claims by running the actual tests.
Let me look at the smoke test fixture in full to understand prior context.
Let me check for any tests that may pin the count of recommended_commands or specific indices that could break.
Let me see the complete test for the instaloader adapter command order.
Let me run the full test suite to confirm no regressions.
## Stage 68 Code Review

### Summary

The change adds the `external-tool-readiness` command to every adapter's `recommended_commands` list in `external-tool-adapters`. The implementation is purely additive string formatting; no executable behavior was introduced or modified. All boundaries specified in the stage goal are respected.

### Verification Performed

- Confirmed position: `_recommended_commands` emits readiness at index 1, immediately after `community-signal-profile` (`src/fashion_radar/external_tool_adapters.py:357-380`).
- Confirmed all 10 required flag/value pairs are present and ordered correctly.
- Cross-checked every recommended flag against the live CLI signature at `src/fashion_radar/cli.py:802-817` — all of `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`, `--input-format`, `--pattern`, `--source-name`, and `--format table` are accepted by `external-tool-readiness`.
- Confirmed the shell-quoting helper `_shell_command` (`shlex.join`) is the same one used by every other recommended command.
- Confirmed `external-tool-template`'s JSON/CSV renderers still emit only `{"items": ...}` (`external_tool_templates.py:155-173`); the new test `test_template_command_guidance_includes_external_tool_readiness` asserts both inclusion in `recommended_commands` and exclusion from JSON/CSV.
- Confirmed `external_tool_readiness.py` and `external_tool_workflow.py` are untouched.
- Re-ran: `pytest -q` (1099 passed), `ruff check` + `ruff format --check` (passed), `scripts/check_release_hygiene.py` (passed), `git diff --check` (passed).

### Findings

**No Critical or Important issues.**

**Minor**

1. `tests/test_external_tool_adapters.py:88-97` — The new readiness-value assertions cover `--adapter`, `--directory`, `--input-format`, `--pattern`, `--source-name`, `--as-of`, and `--format`, but omit direct value checks for `--config-dir` and `--data-dir`. Coverage is recovered indirectly by `test_registry_quotes_paths_pattern_and_source_names` (lines 166-169), which asserts the quoted config/data paths appear in `recommended_commands[1]`. No correctness risk; only a small explicitness gap.

2. `scripts/check_first_run_smoke.py:495-497` — The readiness validator uses plain substring matching (`if expected not in readiness_command`) and only inspects the first adapter (`rednote_mcp`). This is consistent with the file's existing style and scope, but means a malformed readiness command in any other adapter would not be caught by the smoke. Low impact given all adapters share the same `_recommended_commands` generator.

3. `tests/test_first_run_smoke.py:1173` — The `missing_token` negative case only verifies detection of one missing token (`--input-format`). The smoke loop short-circuits on the first missing token, so a regression that broke only the `--format`/`table` check would not be caught by this specific test. Low risk.

### Residual Risk / Test Gaps

- Low overall. The change is additive to a `print_only` registry; no execution paths were touched.
- No test enumerates the readiness command for every adapter — only `instaloader` (unit) and `rednote_mcp` (smoke). Since all adapters share `_recommended_commands`, the structural risk is minimal, but a per-adapter smoke loop would be the natural place to harden this if desired.
- Docs changes are consistent across AGENTS.md, README.md, CHANGELOG.md, cli-reference.md, source-boundaries.md, architecture.md, community-signal-import.md, community-signal-quality.md, and github-upload-checklist.md; no drift detected.
