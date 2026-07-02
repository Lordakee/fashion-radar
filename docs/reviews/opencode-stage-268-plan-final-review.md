## Stage 268 Plan Final Review

### Critical
None.

### Important
None — all five blocking findings are resolved.

### Verification of the five required fixes

1. **`tests/test_scheduling.py` in scope + three renderer tests updated — FIXED.**
   Files list (plan:25-26) includes it. Task 2 Step 1 (plan:120-126) names all three tests, which I confirmed exist: `test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log` (`test_scheduling.py:100`), `test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron` (`:137`), `test_render_row_one_systemd_uses_one_timestamp_and_output_env` (`:185`). They're run in Task 2 Steps 2/5 and Task 4 Steps 1/3.

2. **`test_row_one_scheduling_docs_keep_two_step_refresh_order` explicitly updated — FIXED.**
   Task 3 Step 6 (plan:242) rewrites it to require `row-one refresh`, `"single refresh command"`, and the overlap warning, dropping `"two-step refresh"` and the `run` → `build --latest-only` order. Confirmed it exists at `test_row_one_docs.py:214` (currently pins `--latest-only` at `:221`).

3. **Exact schedule comment emitted by renderer — FIXED.**
   Task 2 Step 3 (plan:146-150) instructs the renderer to emit `# ROW ONE scheduled refresh runs the single refresh command.`; Task 3 Step 3 (plan:197-198) smoke-asserts the substring `ROW ONE scheduled refresh runs the single refresh command.` The current renderer already prints a comment sentence at `scheduling.py:110` surfaced via `row-one schedule`, and substring match tolerates the `# ` prefix. Prior I1 closed.

4. **`assert_output_contains_text` + matching negative helper — FIXED.**
   Plan uses `assert_output_contains_text(command_name, output, tuple)` (plan:194-203), matching the real signature at `check_first_run_smoke.py:1064-1068`. Plan:211 adds `assert_output_not_contains_text` (none exists today) and uses it (plan:204-208). Prior I3 closed.

5. **Lingering `--latest-only` expectations reconciled — FIXED.**
   - `test_scheduling.py:119,158,198` → removed per Task 2 Step 1 (plan:126).
   - `test_row_one_cli.py:401` → dropped via the rename in Task 2 Step 1 (plan:105-111).
   - `check_first_run_smoke.py:1078,1082,1086` → replaced by the rewritten `validate_row_one_schedule_output` (Task 3 Step 3).
   - `check_first_run_smoke.py:2951` (local-ops) → still passes without edits because `--latest-only` survives in local-ops output via the preserved preview command (`ops.py:50`) and Storage prose (`ops.py:85`), which Task 2 Step 4 does not touch.
   - `test_row_one_docs.py:60,84,205` and `row-one.md` cleanup language → intentionally preserved (plan:236).
   The earlier-mentioned `--latest-only` in `test_row_one_cli.py:99,133,238` and `test_first_run_smoke.py:1866` belong to the still-existing `build`/`preview` commands and correctly stay.

### Minor
- **M1 — Comment prefix implicit.** Task 2 Step 3 emits the sentence with a `# ` prefix while the smoke assertion is the bare substring. It works via substring matching, but the plan could state this explicitly to avoid an implementer "fixing" the mismatch.
- **M2 — Local-ops `--latest-only` is silent.** Task 3 Step 3 (plan:213) lists new local-ops expectations but doesn't mention that the existing `--latest-only` entry at `check_first_run_smoke.py:2951` remains valid (via preview/prose). An implementer trimming the tuple is safe either way; spelling it out removes doubt.
- **M3 — Systemd comment not specified.** Task 2 Step 3's "update the human-readable schedule comment" most naturally targets the cron renderer; no test/smoke pins a systemd comment, so non-blocking.

### Verdict
**Proceed to implementation.** All five blocking findings (prior C1, C2, I1, I2, I3) are resolved, the scope is internally consistent, and the verified-positive points from the prior rereview (command ordering, helper reuse, clean scope) still hold. The Minor items are clarification-only and non-blocking.
