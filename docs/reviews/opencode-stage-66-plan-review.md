I'll review the Stage 66 spec and plan. Let me read the target files and related existing code to assess conflicts.
Let me examine the existing modules the plan depends on, to verify its assumptions.
Now let me verify the CLI option constants, command signatures the generated steps reference, and the smoke/docs test structure.
Let me verify the `import-signals-dir` option flag names, since the plan's step 7 and the existing workflow module both use `--format` for it.
Let me check the precedent for `execution_mode` literals and the smoke/docs test infrastructure.
Let me examine the docs drift test structure and the AGENTS.md boundary phrasing to check for phrase mismatches.
Let me verify the smoke test structure, confirm no existing readiness references, and validate import paths.
I have enough to deliver concrete findings. Verifying the one subtle but critical assumption about default-arg binding before finalizing.

The plan's builder signature is `which: Callable[[str], str | None] = shutil.which` (plan line 280). Default argument values are evaluated once at function-definition time, so the default is bound to the original `shutil.which` object at import. The unit tests monkeypatch `readiness_module.shutil.which` (plan line 71, 585) — i.e. they rebind the `shutil` module's `which` attribute — which does **not** update the already-captured default. Confirmed blocking.

---

## Stage 66 Review — Critical / Important findings

### Affirmation on the headline question
`local_read_only` is **correct**; do not downgrade to `print_only`. `shutil.which` performs a real local `$PATH` read (stats binaries), so `print_only` would be inaccurate. The literal already has precedent at `src/fashion_radar/community_handoff_check.py:35` and `src/fashion_radar/heat_movers.py:12`. The trio is `print_only` only because they do zero local reads. No conflict with the trio or `community-handoff-check-dir`: readiness reuses `build_external_tool_adapter_registry` and only *prints* those commands as next-steps (mirroring `external_tool_workflow.py`). Scope stays local-only and free-first.

### Critical
**C1 — `which` injection is defeated by default-arg binding; core unit tests will fail.**
`build_external_tool_readiness(..., which: Callable = shutil.which)` (plan line 280) captures `shutil.which` at definition time. The tests then do `monkeypatch.setattr(readiness_module.shutil, "which", ...)` (plan lines 71, 585, 611, 650, 695) without passing `which=`. The rebinding is invisible to the captured default, so the real `shutil.which` runs:
- `test_readiness_has_stable_instaloader_contract_and_keys` asserts `status == "found"` / `path == "/usr/bin/instaloader"` → fails in CI (no `instaloader` on PATH).
- `test_readiness_reports_missing_and_not_applicable_commands` asserts `status == "missing"` → passes only on machines without `instaloader` (flaky/portability hazard).
- The CLI tests pass only because their assertions are tolerant (`status in {"found","missing"}`, plan line 798) or skip `which` entirely (`generic_community_export`, plan line 952).

Fix: resolve lazily — `which: Callable[[str], str | None] | None = None`, then `effective_which = which if which is not None else shutil.which` inside the body (live attribute read). This is the single change that unblocks Task 1 Step 4.

### Important
**I1 — Step 7 drops `--imported-at`, diverging from the trio and breaking determinism.**
`_readiness_steps` step 7 (plan lines 538-557) emits `import-signals-dir ... --dry-run` without `--imported-at`. The established pattern includes it even for dry-run: `external_tool_workflow.py:347` and `external_tool_adapters.py:433`. Omitting it makes the suggested command fall back to `datetime.now(UTC)` (`cli.py:1132`), undermining the "copyable deterministic command" goal. Add `--imported-at`, `as_of_text`.

**I2 — Task 3 Step 1 conflates the smoke script with the upload-checklist help loop (CI-drift risk).**
The `--help` line belongs in the `docs/github-upload-checklist.md` help loop (asserted by `test_upload_checklist_help_loop_matches_documented_commands`, `tests/test_cli_docs.py:432`, and auto-required once the command is public via `_public_cli_commands()`). The JSON validation belongs in `run_first_run_flow` (`scripts/check_first_run_smoke.py:775`). The plan's wording ("In `check_first_run_smoke.py`, add ... `--help`", plan line 1136-1141) mis-locates `--help`, and nothing in Task 3 explicitly says to add the `run_cli(... "external-tool-readiness" ...)` + `validate_external_tool_readiness(...)` call into `run_first_run_flow`. **No existing test guards that the new command is wired into the smoke flow**, so forgetting it = silent coverage gap.

**I3 — AGENTS.md canonical boundary bullet is unspecified.**
`AGENTS.md` "Scope Boundaries" currently has precise bullets for the trio (e.g. "must keep `external-tool-adapters` as a local, print-only ..."), but none for `external-tool-readiness`, and the plan only lists AGENTS.md in the File Map without the exact text. Because this command is `local_read_only` (not `print_only` like the trio), the bullet must explicitly distinguish it or the canonical boundary source drifts. Supply the exact bullet (mirroring the spec's required language at plan lines 260-270).

**I4 — Docs-drift test structure is underspecified vs. the trio's pattern.**
Task 3 Step 2 says "add a docs test requiring [phrases]" but does not pin the doc tuple (must mirror `EXTERNAL_TOOL_WORKFLOW_DOCS`, the 9-doc tuple at `tests/test_cli_docs.py:226`) nor the per-doc iteration pattern (`test_external_tool_workflow_docs_are_linked_and_bounded`, `tests/test_cli_docs.py:1124`). Without pinning, phrase coverage will be incomplete or inconsistent, and the `casefold()`-normalized exact-phrase matches (e.g. `"no account/session/cookie/token behavior"`) will fail on any wording variance.

### Test gaps that block execution
- **C1** (the `which` binding) — blocks Task 1 Step 4 outright.
- Add an explicit assertion that `external-tool-readiness` is invoked inside `run_first_run_flow` (or a command-coverage test) — otherwise per **I2** the smoke can ship without actually exercising the new command, and no test will catch it.

Minor (non-blocking, functionally equivalent but stylistically divergent from the trio): `_shell_command` uses `" ".join(shlex.quote(...))` (plan line 561) instead of `shlex.join` (`external_tool_adapters.py:468`); `_table_cell` drops the explicit `\r`/`\n` replace (plan line 565) that neighbors keep (`external_tool_adapters.py:472`).
