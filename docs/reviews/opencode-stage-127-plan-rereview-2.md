I'll re-review the Stage 127 plan after the changes. Let me read the relevant artifacts.
Now let me verify the current working-tree state to ground the re-review.
Let me verify the focused `-k` filter now collects the marker tests by name, and confirm the partial working-tree state matches the plan's assumptions.
Let me confirm the expected artifact name and check the design's verification block alignment.
I have everything needed. Both prior Important blockers are resolved (plan lines 165/231 use the corrected filter; plan lines 38-42 plus conditional Task 1/Task 2 steps handle the partial working tree). The working tree confirms: helper + call + 3 rejection tests present, no marker tests yet, no allowlist clause yet — matching the plan's "continue from current tree" delta. The revised filter collects the new marker test names (both contain `gitignore`, verified via collect-only). Let me write the re-review artifact.
Re-review complete and saved to `docs/reviews/opencode-stage-127-plan-rereview-2.md`.

**Critical findings:** None.

**Important findings:** None. Both round-1 blockers are fixed:
- Filter at plan:165/231 is now `-k "unexpected_direct or build_directory or gitignore"`; verified via `--collect-only` that both new marker test names match the `gitignore` disjunct, so they run in the RED/GREEN loop.
- Task 1 Steps 2-4 are guarded "If not already present", and Task 2 Steps 2-3 say "amend/keep existing" — matching the verified working tree (helper + call + 3 rejection tests present; no marker tests / allowlist clause yet). No duplicate-definition risk.

**Minor findings:**
1. Design verification block at `design.md:106` still uses the old filter (without `or gitignore`); mitigated by its next line running the full file, and the plan is authoritative. Doc drift only.
2. Design Expected Behavior doesn't list the combined `.gitignore` + unexpected-child scenario, though Task 1 Step 5 tests it.
3. Carried: test writes `*\n` vs real 1-byte `*` marker; moot under by-name matching.

**Final statement:** There are **no Critical or Important blockers** before continuing implementation.
