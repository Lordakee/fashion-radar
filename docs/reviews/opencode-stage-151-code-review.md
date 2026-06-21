## Stage 151 Code Review Findings

**No blocking issues.** Stage 151 is sound, verified RED→GREEN, and safe to merge.

### RED case proof ✅
I reverted `scripts/check_first_run_smoke.py` to base and re-ran the 3 new tests — all failed with `DID NOT RAISE`, then passed with the smoke change restored. The prior validator only inspected `name` and `command`, so populated `order` / `purpose` / `suggested_effect` drift was genuinely accepted. True RED cases.

- `tests/test_first_run_smoke.py:1916` order drift
- `tests/test_first_run_smoke.py:1926` purpose drift (note the drift string also doubles as a scope-canary — it describes browser/live collection, which the AGENTS.md scope boundaries forbid)
- `tests/test_first_run_smoke.py:1936` suggested_effect drift (`updates_local_matches` → `read_only` is a real semantic change)

### Exact metadata equality ✅
`validate_imported_review_workflow()` at `scripts/check_first_run_smoke.py:983-999` now extracts `{order, name, purpose, suggested_effect}` per step and compares against `EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEP_METADATA` (`scripts/check_first_run_smoke.py:102-148`) via `assert_equal(...)` with the label `"step metadata"` (matches the tests' regex). The defensive `isinstance(step, dict)` pre-check at `scripts/check_first_run_smoke.py:983-985` closes a latent gap where the older `names = [...if isinstance(step, dict)]` comprehension would silently skip non-dict entries.

### Command drift tests still use command-specific labels ✅
The metadata keys deliberately exclude `command`, so:
- Parametrized `test_validate_imported_review_workflow_rejects_command_argv_drift` (`tests/test_first_run_smoke.py:1946`) still surfaces labels like `summary command`, `match refresh command`, etc.
- `test_validate_imported_review_workflow_rejects_coordinated_metadata_command_drift` (`tests/test_first_run_smoke.py:2027`) only mutates date/source/day fragments inside `command` plus top-level scalars, so it falls through to `source_name|as_of|lookback_days|current_days|baseline_days` — not `step metadata`.
- The new metadata check is layered *after* the step-name list check, so `rejects_heat_movers_not_final` (`tests/test_first_run_smoke.py:1906`) still surfaces via `"step names"` for order swaps. Full suite (1281 tests) confirms no label regressions.

### Runtime behavior unchanged ✅
Only `scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py` are touched. The pre-existing parity test `test_imported_review_workflow_payload_matches_real_builder` (`tests/test_first_run_smoke.py:1378-1388`) does whole-payload equality between the fixture and `build_imported_review_workflow()`, so the pinned metadata is transitively bound to the runtime builder. Full suite: `1281 passed`.

### Verification coverage ✅
I ran the focused gates from `docs/superpowers/specs/2026-06-22-stage-151-imported-review-step-metadata-exactness-design.md:167-186`:
- `pytest tests/test_first_run_smoke.py -q` → 115 passed
- Full `pytest -q` → 1281 passed
- `ruff check` + `ruff format --check` on both files → clean
- `git diff --check` → clean

### Non-blocking nits
- **Low** — `design.md:40` and `plan.md:150` say "Add an expected metadata **tuple**" but the constant is a `list` (correct, since ordering matters). Wording-only; no behavior impact.
- **Low** — `plan.md:35` lists `src/fashion_radar/imported_review_workflow.py` under "Relevant files" for the plan review, but the implementation correctly never edits it. Worth keeping since it's the parity anchor the reviewer should read.

### Verdict
Proceed to commit, push, and poll CI.
