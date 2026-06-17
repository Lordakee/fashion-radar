Now let me verify each of the four fixes against the actual source code to confirm the plan instructions match reality.
Let me verify the surrounding context for each fix to confirm the plan instructions are accurate.
Let me verify the remaining details: the smoke script state, the readiness CLI flags, and check for any other stale index references the plan might miss.
Let me confirm two remaining items: whether `docs/community-signal-import.md` actually lists the step names (so the literal-token requirement is real), and check the REVIEW_PROTOCOL for review-artifact commit requirements.
Let me directly confirm `docs/community-signal-import.md` currently lists the step names (proving the literal-token requirement is real).
## Stage 67 Plan Re-Review

All four focus items from the first review are now addressed:

1. **`steps[9]` → `steps[10]` negative-test shift** — ✅ Plan Task 3 Step 6 (plan:406-423) explicitly rewrites `import_step = steps[9]` → `steps[10]` in `test_validate_external_tool_workflow_requires_print_only_workflow_contract`. Verified the target at `tests/test_first_run_smoke.py:1203`.
2. **Unconditional `EXTERNAL_TOOL_WORKFLOW_STEP_NAMES` + doc literal** — ✅ Plan Task 4 Step 4 (plan:505-513) is now unconditional. Verified tuple at `tests/test_cli_docs.py:187` + loop at `:1183-1184`, and confirmed `docs/community-signal-import.md` currently has 0 occurrences of `check_external_tool_readiness` (token addition is required, not optional).
3. **CLI step-key assertions preserved** — ✅ Plan Task 3 Step 1 (plan:274-284) now explicitly retains `assert list(payload["steps"][0]) == [...]`. Verified source at `tests/test_cli.py:783-789`.
4. **Plan-review artifacts gated before commit** — ✅ Plan Task 5 Step 5 (plan:598-600) adds `test -f` checks; all four files exist on disk.

### Remaining finding

**Important — commit omits the plan-rereview artifact pair.** Task 5 Step 5's `git add` (plan:601) and its preceding `test -f` guards (plan:599-600) cover only `opencode-stage-67-plan-review{,-prompt}.md` and the code-review pair, but not `docs/reviews/opencode-stage-67-plan-rereview{,-prompt}.md`, which already exist on disk (they are the output of this re-review cycle and follow the `*-plan-rereview.md` convention noted in `docs/REVIEW_PROTOCOL.md:64`). Executing the plan as written leaves both rereview files untracked after the commit. Add them to the `test -f` guards and the `git add` list for review-record completeness.

No Critical findings; no blocking test gaps remain.
