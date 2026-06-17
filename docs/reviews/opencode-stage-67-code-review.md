I'll review Stage 67's implementation. Let me start by reading the spec, plan, and key implementation files.
Now let me check the test files, the readiness command, and key docs in parallel.
Let me check the rest of the smoke tests and verify the readiness command was untouched, plus review docs.
The changes are uncommitted. Let me verify the workflow module doesn't import or call the readiness builder, and check the docs/cli test plus key docs.
Let me verify the actual diff of the implementation file, the AGENTS.md boundary, and the cli.py command.
Let me check the CLI test diff and the CLI command to confirm the command wrapper is unchanged.
Let me look at the CLI command and verify one more edge case - the no-artifact behavior of the workflow command.
## Review Complete — Stage 67

**No Critical findings. No Important findings. No blocking test gaps.**

### Verification of scope boundaries (the key risk area)

`src/fashion_radar/external_tool_workflow.py` remains strictly print-only:
- No new imports of `external_tool_readiness`, `shutil`, `subprocess`, or any SQLite/IO module — `"external-tool-readiness"` appears only as a string literal inside `_shell_command(...)` at `external_tool_workflow.py:202`.
- The new `check_external_tool_readiness` step (`external_tool_workflow.py:193-223`) only emits a copyable command string via `shlex.join`; it does not invoke the readiness builder or perform PATH lookup.
- `external_tool_readiness.py` is **not in the diff** — Stage 66 semantics are unchanged.
- `cli.py` is **not in the diff** — the `external-tool-workflow` CLI wrapper (`cli.py:757-799`) still just calls `build_external_tool_workflow` + renderer; the `not directory.exists()`/`not config_dir.exists()`/`not data_dir.exists()` no-artifact assertions in `tests/test_cli.py:849-851` still pass.

### Consistency checks

- **Workflow code**: clean insertion at `order=2`, correct `suggested_effect="read_only"` (PATH-lookup-only when manually run), all later steps renumbered 3→12.
- **Tests** (`test_external_tool_workflow.py`, `test_cli.py`, `test_first_run_smoke.py`, `test_cli_docs.py`): `step_count=12`, new step at index 1, effects list updated, readiness command assertions cover adapter/directory/config-dir/data-dir/as-of/input-format/pattern/source-name/`--format table`, source-name override now checked at indices 1 and 4, negative `executable_import` test correctly retargeted to `steps[10]`.
- **Smoke validator** (`scripts/check_first_run_smoke.py:519-660`): `EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS` has 12 entries, validator pins `step_count=12`, the 12-element effects list, validates `readiness_step = steps[1]` command tokens, and reindexes `template_step=steps[2]`, `lint_step=steps[6]`, `import_step=steps[10]`.
- **Docs/AGENTS.md**: `AGENTS.md`, `docs/source-boundaries.md`, `docs/community-signal-quality.md`, README, cli-reference, architecture, upload-checklist, CHANGELOG all add the preflight sentence while preserving every existing boundary clause (no connectors/scraping/browser automation/platform APIs/monitoring/scheduling/source acquisition/demand proof/ranking/coverage verification).
- **Circular guidance** (readiness↔workflow) is explicitly bounded by the new AGENTS.md wording: *"may print `check_external_tool_readiness` as an optional preflight command ... but it must not run that command."*

All verification commands listed in the prompt already pass (420 targeted, 9 docs drift, 3 smoke, 1098 full suite, ruff check/format, release hygiene, `git diff --check`). The implementation precisely matches the design spec and plan.
