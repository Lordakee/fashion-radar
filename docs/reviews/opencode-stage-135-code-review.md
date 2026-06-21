# Stage 135 Code Review

I traced the helper, both validators, the three RED tests, the static payload fixtures, the runtime command emitters in `src/fashion_radar/external_tool_workflow.py:160-389` and `src/fashion_radar/external_tool_readiness.py:310-440`, and the focused verification output.

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **RED coverage is asymmetric but matches the plan's explicit scope.** Six substring loops were replaced (registry, readiness, template, lint in `validate_external_tool_workflow()` at `scripts/check_first_run_smoke.py:1118-1203`; workflow and dry-run in `validate_external_tool_readiness()` at `:1329-1374`), but only three RED tests were added (workflow readiness extra flag, readiness workflow `--format json`, readiness dry-run `--format csv`). The three un-RED'd replacements are still exercised as GREEN by `test_validate_external_tool_workflow_requires_print_only_workflow_contract` at `tests/test_first_run_smoke.py:1884-1916` and `test_validate_external_tool_readiness_requires_local_read_only_contract` near `:1990`, so valid payloads provably pass. This was already flagged in the Stage 135 plan review and accepted by the design's "command checks already present" scope. No change required; flagging in case a future stage wants negative tests for the registry/template/lint replacements.

2. **`match=` regexes are substring anchors by design.** `pytest.raises(..., match="readiness command")` matches anywhere in the `SmokeError` message. The helper's label `f"{command_name} {label} command"` yields `"external-tool-workflow readiness command expected [...]"`, and the `ValueError` branch yields `"... readiness command is not shell-parseable: ..."`. Both match. Already noted in the plan review; no change required.

3. **`object` typing for `command` mirrors existing style.** `validate_expected_external_tool_command(command_name, label, command: object, *parts)` plus `str(command)` mirrors the existing `expected_external_tool_command` pattern. Call sites pass `step.get("command", "")`, which yields `""` for missing keys (`shlex.split("")` → `[]`, fails argv cleanly) and `None` for explicit nulls (`shlex.split("None")` → `["None"]`, also fails cleanly). No gap.

4. **Payload-derived value reads happen only after scalar validation.** The `adapter_id = str(payload["adapter_id"])` block at `scripts/check_first_run_smoke.py:1062-1069` and `:1256-1263` runs after the `assert_equal(...)` pins at `:1051-1056` and `:1245-1250` and the populated-string loop at `:1058-1061` / `:1252-1255`. Bracket access is therefore safe, and the runtime `_shell_command(...)` emitters in `external_tool_workflow.py:175-381` and `external_tool_readiness.py:315-440` emit commands from the same payload fields, so deriving expected argv from the payload keeps temporary first-run directories valid. Confirmed.

5. **Scope discipline is clean.** Only `scripts/check_first_run_smoke.py` (+172/-37 lines, helper + 6 substring-loop replacements + payload-derived local strings) and `tests/test_first_run_smoke.py` (+70 lines, 3 RED tests) are modified. `git diff --stat` confirms no other source changes; `git diff --exit-code -- uv.lock` is clean. No CLI runtime, docs wording, package/archive checker, dependency, `uv.lock`, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, generated command execution, PATH lookup, import, SQLite, file-read, artifact creation, or compliance/audit behavior changes. Confirmed against AGENTS.md scope boundaries.

## RED test specificity
- **Test 1** (`--verbose` suffix on workflow readiness command) preserves every original substring anchor (`fashion-radar external-tool-readiness`, `--adapter`, `rednote_mcp`, `--input-format`, `json`, `--pattern`, `*.json`, `--source-name`, `--format`, `table`); passes the old loop, fails the new exact argv check. Proves the weakness.
- **Test 2** (`--format json` instead of `--format table` on readiness workflow command) preserves `fashion-radar external-tool-workflow`, `--adapter`, `rednote_mcp`, and the bare `--format` token the old loop checked; passes the old loop, fails the new exact argv check. Proves the weakness.
- **Test 3** (`--format csv` instead of `--format json` on readiness dry-run command) preserves `fashion-radar import-signals-dir`, `--data-dir`, `data`, `--imported-at`, `--dry-run`; the old loop never inspected `--format`; passes the old loop, fails the new exact argv check. Proves the weakness.

## `shlex.split()` + exact argv comparison
The helper at `scripts/check_first_run_smoke.py:376-390` parses with `shlex.split(str(command))` and compares the resulting list to `["fashion-radar", *parts]` via `assert_equal`. It does not compare joined strings, so `'*.json'` vs `"*.json"` quoting differences remain acceptable. On `ValueError` it raises a `SmokeError` with the `{command_name} {label} command is not shell-parseable: ...` label, which the `match=` regexes also anchor. Correct.

## Path derivation from payload
Every path argument (`directory`, `config_dir`, `data_dir`, `as_of`, `input_format`, `pattern`, `source_name`, `adapter_id`) comes from `payload[...]` in both validators at `scripts/check_first_run_smoke.py:1062-1069` and `:1256-1263`. No hardcoded `"exports"`, `"configs"`, or `"data"` literals appear in the validator-side expected argv lists. The RED tests' use of fixture literals in their drift payloads is fine because those tests construct drift fixtures, not real first-run smoke runs. Correct.

## Verification confirmation
- Targeted RED tests: 3 passed.
- Focused `external_tool_workflow or external_tool_readiness or external_tool_adapters`: 21 passed.
- `tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py`: 76 passed.
- `ruff check` and `ruff format --check` on the two changed files: clean.
- Live `python scripts/check_first_run_smoke.py --repo-root .`: "First-run sample smoke passed."
- `git diff --check`: clean.
- Full pytest sweep (run independently): 1230 passed.
- `uv.lock` unchanged.

---

**No Critical or Important blockers before release.** The implementation matches the Stage 135 design and plan, the RED tests prove the prior substring checks were too weak, the helper uses `shlex.split()` with exact argv comparison, expected path arguments are derived from payload fields, and the stage introduces no runtime CLI, docs, dependency, lockfile, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, PATH lookup, import, SQLite, file-read, artifact creation, or compliance/audit behavior changes.
