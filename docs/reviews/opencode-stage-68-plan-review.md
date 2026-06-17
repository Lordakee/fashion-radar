Let me verify a few final details before reporting findings.
I've completed a thorough review of the spec and plan against the current codebase. Here are the concrete findings.

---

## Stage 68 Spec & Plan Review

### Scope & Boundary Verdict

**Scope is appropriate and well-bounded.** Adding one printed `external-tool-readiness` command to each adapter registry entry's `recommended_commands` is a natural, narrow next-stage follow-up to Stage 67's workflow preflight. `external-tool-adapters` correctly remains `execution_mode="print_only"` — the registry only *prints* the readiness command string; it does not call readiness, perform PATH lookup, inspect directories, read handoff files, or open SQLite. The plan avoids all prohibited features (no connectors, scraping, browser automation, platform APIs, account/cookie/token behavior, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review product feature). The "print-only registry printing a local read-only command for the user to optionally run manually" distinction is preserved correctly.

---

### IMPORTANT-1: Plan misses `tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths` (silent semantic drift / blocking test gap)

`tests/test_cli.py:582` reads:
```python
command = payload["adapters"][0]["recommended_commands"][1]
assert "'exports ? # & %'" in command
assert "'config ? # & %'" in command
assert "'data ? # & %'" in command
assert "--source-name 'Instaloader Export'" in command
```

After Stage 68, `recommended_commands[1]` is the **new readiness command**, not the manifest command the test was written to validate. The four assertions **happen to keep passing** because the readiness command also emits `--directory`, `--config-dir`, `--data-dir`, and `--source-name 'Instaloader Export'`. The plan never mentions this test.

This is silent semantic drift: a test named `..._filters_adapter_and_quotes_paths` will now be quoting-checking the readiness command instead of the manifest. Stage 67 explicitly handled the analogous shift in `external-tool-workflow` by adding parallel readiness assertions *and* updating shifted indexes (see `docs/superpowers/plans/2026-06-17-stage-67-...-plan.md` Task 1 Steps 2–3). Stage 68 should do the same.

**Fix before implementation:** Either change `[1]` → `[2]` to keep validating the manifest, or add a parallel readiness assertion at `[1]` and a manifest assertion at `[2]`, and update the test name/comment to reflect both. The plan's Task 3 Step 1 must be amended to call this out.

---

### IMPORTANT-2: Plan Task 1 Step 3 quoting-test instructions are ambiguous (likely-redundant assertions)

`tests/test_external_tool_adapters.py:151-154` already asserts on `adapter.recommended_commands[1]` for `x_search_export`. After Stage 68, `[1]` becomes the readiness command (which also quotes the same paths/source-name). The plan's Task 1 Step 3 provides 8 assertions covering both `[1]` and `[2]` without saying whether the existing 4 lines on `[1]` should be *replaced*, *kept*, or *augmented*. An executor following literally would either duplicate the `[1]` block or accidentally drop the manifest `[2]` check.

The first 4 lines of the proposed block are byte-identical to the existing test, so the executor needs to know the intent is "the existing `[1]` block now happens to validate readiness quoting; add a parallel `[2]` block for manifest quoting." Tighten the wording to make this explicit, mirroring how Stage 67 Task 1 Step 2 framed the parallel-check addition.

---

### IMPORTANT-3: Spec/plan's Risks section under-enumerates order-locking tests

The spec's Risks section says "Tests intentionally lock the command order, so update focused tests and smoke fixtures together," but the plan only enumerates `tests/test_external_tool_adapters.py` and `tests/test_cli.py::test_external_tool_adapters_command_prints_json`. It omits:
- `tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths` (see IMPORTANT-1),
- `tests/test_first_run_smoke.py::external_tool_adapters_payload` (referenced in 3+ tests at lines 1122, 1133, 1138, 1759),
- the real-CLI smoke invocation in `scripts/check_first_run_smoke.py:1016-1020`.

Recommend adding an explicit enumeration to the spec's Risks section so reviewers and the future executor can verify coverage is complete.

---

### Minor / pre-existing (not blocking, but worth noting)

- **M1:** `external_tool_adapters_payload` in `tests/test_first_run_smoke.py:405` uses adapter keys `"platform"` and `"source_name"` rather than the real model's `platform_label` / `suggested_source_name`. The plan adds `recommended_commands` to this fixture without addressing the pre-existing key drift. Not blocking — `validate_external_tool_adapters` doesn't check those keys — but it is existing tech debt the plan inherits silently.
- **M2:** The docs drift test `test_external_tool_adapter_registry_docs_are_linked_and_bounded` (`tests/test_cli_docs.py:1022`) does not assert anything about `recommended_commands` content or count, so the plan's docs phrase insertion is unverified by tests. If you want the docs update to be enforceable, add a docs-drift assertion that the adapter registry section of each listed doc mentions `external-tool-readiness` as a printed preflight.
- **M3:** Plan Task 3 Step 3 applies the *same* paragraph to all 9 docs, but `docs/community-signal-import.md` and `docs/community-signal-quality.md` have separate `external-tool-adapters` / `-workflow` / `-readiness` subsections; the executor may need slight rewording per doc to fit the existing section voice. Worth a one-line note in the plan.

---

### Verified correct

- Command-flag set in the readiness command string (`--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`, `--input-format`, `--pattern`, `--source-name`, `--format table`) matches the actual `external-tool-readiness` CLI signature at `src/fashion_radar/cli.py:802-816`.
- Insertion position (after `community-signal-profile`, before `community-handoff-manifest`) is consistent between spec and plan.
- Index-shift math in Task 1 Step 2 (manifest `[1]→[2]`, dry-run `[5]→[6]`, non-dry-run `[6]→[7]`) is correct against the post-change 9-command ordering.
- `_adapter(...)` already receives `adapter_id` and only needs to forward it into `_recommended_commands`; no signature risk.
- Plan keeps `external-tool-adapters`, `external-tool-readiness`, and `external-tool-workflow` semantics unchanged.
- No CI risk from lockfile or mirror config: plan uses `uv --no-config run --frozen` consistently.

---

### Recommendation

**Approve with required plan revisions** before implementation:
1. Add explicit handling for `tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths` (IMPORTANT-1).
2. Clarify Task 1 Step 3 quoting-test intent — replace vs. augment (IMPORTANT-2).
3. Expand the spec's Risks section to enumerate every order-locking test (IMPORTANT-3).

After those three revisions the plan is safe to execute.
