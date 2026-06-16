I'll review the Stage 60 plan. Let me first gather the relevant context.
Now let me examine the actual source files to verify the plan aligns with reality.
Let me verify the actual `imported-candidates` command signature to ensure the printed command flags are valid.
Let me check the existing CLI tests and first-run smoke infrastructure to validate the plan's test assertions.
The smoke script's `run_first_run_flow` doesn't currently invoke `imported-review-workflow` and there's no `run_cli_json` helper. Let me check how the smoke test is structured and the CLI test details.
Now let me read the relevant CLI test sections and the docs test to verify the plan's assertions match the existing test fixtures.
Let me check the docs drift test and the CLI `imported-review-workflow` command implementation to confirm print-only behavior.
Let me check the existing docs test constants and the relevant docs to verify the docs drift approach.
Let me verify whether `test_community_handoff_manifest.py` and `test_community_handoff_workflow.py` use the real workflow builder (which would break when step_count changes to 6).
The community handoff workflow only *prints* the `imported-review-workflow` command string and doesn't call the builder, so its `step_count == 5` is unaffected. Let me do a final sweep for any other references to the imported review workflow's 5-step shape that the plan might miss.
I have completed a thorough review. Let me verify one final detail about the existing render-table test and whether the plan's guidance there is necessary.
## Verdict: APPROVED FOR STAGE 60 PLAN

I verified the plan against the actual sources: `imported_candidates_command` signature (cli.py:1417-1425 confirms `--config-dir/--data-dir/--as-of/--source-name` are all valid and `--limit/--format` have defaults, so omitting them is correct), the print-only builder (imported_review_workflow.py:38-153 uses only `_shell_command`/`shlex.join` with no data access), the print-only CLI command (cli.py:1463-1503 only renders), and confirmed the community-handoff workflow only *prints* the workflow string (community_handoff_workflow.py step 5) so its `step_count==5` tests are unaffected.

### Critical
None.

### Important
None blocking. Two implementation-clarity items a subagent could stumble on (both self-correcting via the TDD red-green cycle, so non-blocking):
1. **Smoke helper name mismatch (plan 2.4, line 354):** The snippet calls `run_cli_json(...)`, but `scripts/check_first_run_smoke.py` has no such helper — only `run_cli` + `validate_json_output`. The plan's trailing "Adapt the exact helper call style…" note covers it, but the literal snippet would fail if copied. Recommend showing the real `validate_json_output("…", run_cli(context, …).stdout)` pattern.
2. **Smoke test index/sequence shift (plan 2.2):** Adding `imported-review-workflow` after `match` (currently `captured[7]`) shifts the export-dir assertions at `captured[13]–[16]` → `[14]–[17]` and requires inserting the name in the exact 17→18 element list (test_first_run_smoke.py:967). The plan states this, but should also tell the implementer to add `"imported-review-workflow"` to the `--config-dir/--data-dir/--source-name/AS_OF` conditional coverage sets (test_first_run_smoke.py:996-1037) so the smoke actually verifies invocation flags rather than silently skipping them.

### Minor
1. **Generic docs phrase:** Required phrase `"final"` (plan 3.1, line 426) is too generic and may match incidentally; prefer `"final read-only heat-movers step"`.
2. **Render-table fixture guidance (plan 1.1, line 131):** Ambiguous ("Steps: 4 or use six rows"). The existing `test_render_imported_review_workflow_table` builds a synthetic `step_count=3` model and tests the renderer in isolation — it passes unchanged. Clarify this is optional enrichment, not required.
3. **Docs phrase coverage:** The 9-doc drift list (incl. CHANGELOG, github-upload-checklist) requires `"read-only imported-candidates step"` and `"candidate phrase review"` in every file; Task 3.3 only explicitly assigns those phrases to README/community-signal-import/cli-reference. The red-green loop forces the rest, but sharper guidance would help.
4. **Docs test refactor:** Plan says "update the existing imported-review docs test" but the current test `test_imported_review_workflow_docs_link_to_heat_movers_review` (test_cli_docs.py:386) uses `IMPORTED_REVIEW_HEAT_*`. Clarify whether the constants are renamed/replaced or a second test is added, and note that `"local observed heat movement"` coverage is dropped in the new constant set.

### Rationale
The design and plan fully satisfy the Stage 60 objective with correct step placement (`review_imported_candidate_phrases` at order 4, `review_local_heat_movers` retained as final at order 6), correct command flags, no out-of-scope behavior (no new CLI command/option, no runtime data access in the builder, no schema/dependency/connector changes), and strong verification gates (direct + CLI + docs-drift + source/installed first-run smoke + full pytest + ruff + lock/mirror hygiene + package-archive + installed-wheel smoke + opencode release review). `--source-name` handling mirrors the existing `imported-entity-deltas`/`imported-signals` steps and is correctly omitted from the final heat-movers step.

### Recommended implementation split
Follow the plan's sequential 3-task split exactly — it is safe:
- **Task 1:** `src/fashion_radar/imported_review_workflow.py` + `tests/test_imported_review_workflow.py` (produces the 6-step model everything else depends on).
- **Task 2 (after Task 1):** `tests/test_cli.py` + `scripts/check_first_run_smoke.py` + `tests/test_first_run_smoke.py`.
- **Task 3 (after Task 1):** `tests/test_cli_docs.py` + the 9 docs/CHANGELOG.

No file overlaps between tasks; run strictly sequentially (not parallel), then Task 4 verification/commit.
