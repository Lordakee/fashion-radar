I'll review the two Stage 58 planning artifacts against the stated objective and boundaries.
Now let me verify the plan's accuracy against the actual codebase. I'll check the existing workflow builder, heat-movers CLI, and test files in parallel.
Let me verify the heat-movers CLI signature and the docs drift test helpers.
Let me examine the heat-movers CLI command signature and the docs drift test helpers to verify the plan's claims.
Let me verify the CLI test patterns for `imported-review-workflow` and check the `--config-dir`/`--as-of` option definitions.
Let me read the key CLI tests to verify the plan's CLI test instructions align with existing patterns.
Let me verify the `_normalized_text` helper to ensure the docs drift phrases will actually match, and check the existing release-check scripts exist.
Let me check for any other places that assume the 4-step workflow (to ensure the plan's coverage is complete), and confirm the heat-movers output-format option doesn't interfere.
Verification complete. I cross-checked every claim in the plan against the actual source: the builder (`src/fashion_radar/imported_review_workflow.py`), the `heat-movers` CLI signature (`src/fashion_radar/cli.py:1276`), the existing tests, and the docs-drift helpers. All factual claims hold.

---

## Stage 58 Plan Review

### Critical findings
None.

### Important findings
None.

### Minor findings

1. **Render-fixture update is under-specified (plan Task 1, Step 1).** The instruction to add a third step to `test_render_imported_review_workflow_table()` shows only the new `ImportedReviewWorkflowStep(...)` object. It omits the three corollary edits the same test needs: bumping `step_count=2` → `3` (`tests/test_imported_review_workflow.py:100`), changing the expected `"Steps: 2"` line → `"Steps: 3"` (`tests/test_imported_review_workflow.py:132`), and appending the corresponding expected rendered row to the assertion list. A TDD implementer will hit these via the red phase, but spelling them out would match the precision of the other steps.

2. **CLI JSON test update is shown as additive only (plan Task 2, Step 1).** The existing `tests/test_cli.py:3500` asserts `payload["step_count"] == 4`. The plan says "Add assertions that: `assert payload['step_count'] == 5`" but does not explicitly call out removing/replacing the existing `== 4` line. Trivial, but worth a one-line note for parity with Task 1's explicitness.

3. **No-artifact coverage is described vaguely (plan Task 2, Step 1).** The plan says "add an assertion that the heat-movers command is printed without creating a database." The existing `test_imported_review_workflow_command_creates_no_artifacts` (`tests/test_cli.py:4556`) and `test_..._does_not_access_data_or_execute` (`:4595`) already patch `subprocess.run`, `create_sqlite_engine`, `initialize_schema`, etc., and these automatically cover the new printed step since it is just a string. Recommend the plan say "reuse the existing no-artifact/no-data-access tests; no new patch targets are needed" instead of implying a new assertion, to avoid a redundant/ambiguous test.

4. **Docs-drift phrase set is heavy for CHANGELOG (plan Task 3, Step 1).** The required phrases (`"local observed heat movement"`, `"read-only"`, `"no demand proof"`, `"no platform coverage verification"`) must appear in all seven docs including `CHANGELOG.md`. `_normalized_doc_text` (`tests/test_cli_docs.py:148`) only collapses whitespace and `casefold()`s — it preserves hyphens, so docs prose must literally contain `read-only` (hyphen) even though the JSON field is `read_only` (underscore). This is consistent with the project's boundary-preservation norm, but the CHANGELOG entry will be unusually verbose; flagging so the author isn't surprised.

### Verification of review questions

1. **Scoped to one small feature, no duplication.** ✅ Single new `ImportedReviewWorkflowStep`; `Do not modify` list explicitly protects `community_signal_profile.py`, `community_handoff_manifest.py`, `community_handoff_workflow.py`, `community_handoff_check.py` (plan:55-58). Docs note says `community-handoff-check-dir` stays pre-import (plan:301).
2. **TDD with concrete files/tests/commands/expected failures.** ✅ Each task is red→green with explicit files, failing-command snippets, and "Expected: failures..." notes.
3. **`imported-review-workflow` stays print-only.** ✅ `execution_mode` stays `"print_only"`; no `subprocess` calls added; existing no-execution/no-data-access tests retained.
4. **Heat step uses existing `heat-movers` CLI, no new DB I/O in builder.** ✅ Verified `heat-movers` accepts `--config-dir/--data-dir/--as-of` (`cli.py:1278-1280`) and has no `--source-name`; builder only appends a command string; `heat_movers.py` is in the do-not-modify list.
5. **Test coverage adequate.** ✅ Direct builder output, CLI JSON (`step_count==5`, last step name/effect/command), CLI table (`review_local_heat_movers`, `fashion-radar heat-movers`), docs drift across 7 docs, no `--source-name` leakage (two tests), no-artifact/no-data-access (existing tests remain valid).
6. **Docs preserve local-only / no demand proof / no coverage-verification wording.** ✅ Drift test enforces all three phrases; existing docs already use this exact wording.
7. **Release checks complete.** ✅ Full pytest, `ruff check .`, `ruff format --check .`, `uv lock --check`, `uv sync --locked --dev --check`, mirror sync + `rg` leak guard, `git diff --exit-code -- uv.lock pyproject.toml`, `check_release_hygiene.py`, `check_first_run_smoke.py`, installed-wheel smoke (validates `step_count: 5` + `fashion-radar heat-movers`), and opencode release review.

### Final verdict

```text
APPROVED FOR STAGE 58 PLAN
```
