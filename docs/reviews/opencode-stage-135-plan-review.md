# Stage 135 Plan Review

I traced the three planned RED tests against the current substring validators in `scripts/check_first_run_smoke.py:1090-1137` and `:1252-1276`, verified the planned `validate_expected_external_tool_command()` helper against the existing `shlex.split(str(command))` pattern already used in `validate_external_tool_adapters()` at `scripts/check_first_run_smoke.py:855`, and confirmed each planned expected-argv list matches the static payload fixtures in `tests/test_first_run_smoke.py:919-1223`.

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **RED test coverage is asymmetric but acceptable.** The plan replaces substring checks for 4 steps in `validate_external_tool_workflow()` (registry, readiness, template, lint) but only adds one RED test (readiness extra flag). The design's "Risks" section explicitly scopes this stage to "command checks already present," and the existing valid-payload GREEN tests (`test_external_tool_workflow_requires_print_only_workflow_contract` at `tests/test_first_run_smoke.py:1884`) prove the three un-RED'd replacements accept valid commands. No change required; flagging in case future stages want negative tests for the registry/template/lint replacements.

2. **`match=` regexes are substring searches, not anchor checks.** `pytest.raises(..., match="readiness command")` matches anywhere in the `SmokeError` message. The planned `assert_equal` label `f"{command_name} {label} command"` yields `"external-tool-workflow readiness command expected [...]"` so the substring is present, and the `ValueError` branch yields `"... readiness command is not shell-parseable: ..."` which also matches. Confirmed correct; just noting the regex is permissive by design.

3. **`object` type for the `command` parameter matches existing style.** The helper's `command: object` + `str(command)` mirrors the existing pattern at `scripts/check_first_run_smoke.py:855`. Call sites pass `step.get("command", "")`, which returns `""` for missing keys (parses to `[]`, fails the argv comparison cleanly) and `None` for explicit nulls (parses to `["None"]`, also fails cleanly). No gap.

4. **Payload-derived value reads happen after existing assertions.** The plan's `adapter_id = str(payload["adapter_id"])` etc. is inserted after the existing `assert_equal(...)` checks at `scripts/check_first_run_smoke.py:1034-1044` and `:1179-1189`, so bracket access is safe and the values are already validated. The runtime `build_external_tool_workflow()` / `build_external_tool_readiness()` in `src/fashion_radar/external_tool_workflow.py` and `src/fashion_radar/external_tool_readiness.py` emit commands from the same payload fields, so deriving expected argv from the payload keeps temporary first-run directories valid. Confirmed.

5. **Scope discipline is clean.** The plan replaces only the substring loops already present in the two named validators; it does not add new command checks for the unchecked workflow steps (print_signal_profile, print_handoff_manifest, print_handoff_workflow, preview_candidate_phrases, review_handoff_readiness, import_directory_signals, print_post_import_review). No docs wording, CLI runtime, package/archive checker, dependency, `uv.lock`, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, PATH lookup, import, SQLite, file-read, artifact creation, or compliance/audit behavior changes. Confirmed against AGENTS.md scope boundaries.

## Verification command adequacy
The focused verification block (`docs/.../plan.md:364-372`) runs the targeted pytest slice, the contract parity suite, ruff check + format, the live `check_first_run_smoke.py` invocation, and `git diff --check`. The release gate (`plan.md:463-472`) adds full pytest, repo-wide ruff, `uv lock --check` with `UV_NO_CONFIG=1`-equivalent env stripping, `uv.lock` diff, whitespace check, and the two GitHub-credential guards. Sufficient.

## RED test specificity
- Test 1 (`--verbose` suffix) preserves every current substring anchor at `scripts/check_first_run_smoke.py:1102-1113`, so it passes today and fails after wiring. Proves the weakness.
- Test 2 (`--format json` instead of `table`) preserves `fashion-radar external-tool-workflow`, `--adapter`, `rednote_mcp`, and `--format`; the current loop at `:1256-1261` only checks for `--format` presence, not its value, so it passes today. Proves the weakness.
- Test 3 (`--format csv` instead of `json`) preserves `fashion-radar import-signals-dir`, `--data-dir`, `--imported-at`, `--dry-run`; the current loop at `:1269-1274` does not inspect `--format` at all, so it passes today. Proves the weakness.

All three are specific enough.

## `shlex.split()` + exact argv comparison
The helper parses with `shlex.split(str(command))` and compares the resulting list to `["fashion-radar", *parts]` via `assert_equal`. It does not compare joined strings, so `'*.json'` vs `"*.json"` quoting differences remain acceptable. Correct.

## Path derivation from payload
Every path argument (`directory`, `config_dir`, `data_dir`, `as_of`, `input_format`, `pattern`, `source_name`, `adapter_id`) comes from `payload[...]` in both validators. No hardcoded `"exports"`, `"configs"`, or `"data"` appears in the planned expected-argv lists (the test fixture's `external_tool_command()` calls in RED tests 2 and 3 use fixture literals, which is fine because those tests construct drift payloads). Correct.

---

**No Critical or Important blockers before implementation.** The plan may proceed to Task 1 (RED tests).
