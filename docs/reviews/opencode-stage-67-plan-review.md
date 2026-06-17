I'll review the Stage 67 spec and plan. Let me start by reading both files and gathering relevant context.
Let me verify the plan against the actual current codebase. I'll examine the implementation, tests, smoke scripts, and the existing readiness command in parallel.
Now let me verify the readiness command's actual CLI signature, the smoke script, and the AGENTS.md boundaries in parallel.
I found a key risk to verify: whether the `external-tool-readiness` CLI actually accepts the `--input-format`, `--pattern`, `--source-name`, and `--format table` flags the new printed command uses. Let me check the CLI definitions, the deterministic smoke fixture, the CLI tests, and docs drift tests in parallel.
Now let me read the CLI readiness command signature, the deterministic workflow payload fixture, and the CLI workflow tests to verify the plan's command string matches real CLI behavior.
Let me read the CLI workflow tests, the docs drift tests, and the negative payload tests to check for any breakage from the new step.
I found a likely blocking test gap. Let me verify the remaining CLI/docs tests and the negative test that references `steps[9]` for the import step, plus check the docs step-name tuple and the AGENTS.md scope boundary text.
I've found the key issues. Let me do a final sweep for any other references to the old step indexes/counts that the plan might miss, and confirm the AGENTS.md boundary and the readiness format option include "table".
Let me confirm line 1035 of `test_first_run_smoke.py` (`del steps[3]`) belongs to a different workflow's negative test, not the external workflow.
## Stage 67 Review Findings

### Blocking test gap (Critical)

**`tests/test_first_run_smoke.py:1203` is not covered by the plan and will break.** `test_validate_external_tool_workflow_requires_print_only_workflow_contract` does `import_step = steps[9]` then sets `suggested_effect = "read_only"` expecting `"import step effect"`. After the 11→12 shift, index 9 is `dry_run_directory_import` (already `read_only`), so no error is raised and `pytest.raises(..., match="import step effect")` fails. Plan Task 3 (Step 5 only updates the fixture dict) must add: change `steps[9]` → `steps[10]` in the `executable_import` branch of that test. I verified no other stray `steps[9]`/`step_count==11` references are missed by the plan (the `del steps[3]` at line 1035 and the `steps[3]` refs in `test_community_handoff_*`/`test_imported_review_workflow` belong to other workflows).

### Important

1. **`tests/test_cli_docs.py:187` `EXTERNAL_TOOL_WORKFLOW_STEP_NAMES` is unconditional, not optional.** Plan Task 4 Step 4 phrases the tuple edit as "if … has a step-name tuple." It does, and `test_external_tool_workflow_docs_include_examples_and_steps` (line 1183) asserts every name appears verbatim in `docs/community-signal-import.md`. Both the tuple update and adding the literal `check_external_tool_readiness` token to `community-signal-import.md` are required, not conditional.

2. **Plan Task 3 Step 1 "from" block drifts from the real source.** It omits the `assert list(payload["steps"][0]) == ["order","name","purpose","command","suggested_effect"]` block at `tests/test_cli.py:783-789`. A literal block-replace by a subagent will fail to match; the implementer must preserve that assertion. The "to" assertions (steps[1] read_only, steps[10] import, steps[4] directory) are correct.

3. **Commit step references review artifacts no task creates.** Task 5 Step 5 `git add`s `docs/reviews/opencode-stage-67-plan-review-prompt.md` and `opencode-stage-67-plan-review.md`, but this plan only creates the `*-code-review-*` pair (Task 5 Steps 4–5). The plan-review files must pre-exist from the staged plan review; if they don't, `git add` errors out. Confirm they exist at those exact paths before commit, or remove them from the `git add` list.

### On the focus questions

- **Scope:** Adding a printed `check_external_tool_readiness` step is the right, minimal next stage — a pure print-only integration of the existing Stage 66 command.
- **Print-only:** Correctly preserved. `suggested_effect="read_only"` legitimately describes the printed command's runtime behavior, matching the existing `lint_export_directory` / `review_handoff_readiness` convention (the workflow itself never executes it).
- **Boundaries:** Clean. No connectors/scraping/browser automation/platform APIs/monitoring/scheduling/source acquisition/demand proof/ranking/coverage/compliance-review. The printed command is valid: `external-tool-readiness` CLI accepts `--input-format`, `--pattern`, `--source-name`, and `--format table` (`ExternalToolReadinessOutputFormat = Literal["table","json"]`, cli.py:225).
- **Circular guidance:** Acceptable; the new step is framed as optional preflight. Minor pre-existing asymmetry: readiness's `print_external_tool_workflow` step purpose is not labeled optional — out of scope here.
- **CI:** No dependency changes, so `uv --frozen` is safe; no lockfile/`UV_NO_CONFIG` risk beyond existing norms.

Fix the Critical item (#1) before implementation; address Important #1–#3 during implementation.
