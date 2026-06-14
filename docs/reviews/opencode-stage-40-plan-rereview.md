I'll perform the Stage 40 plan rereview. Let me first gather non-mutating evidence to ground my findings — verifying the load-bearing claims (opencode CLI syntax, current doc state, AGENTS.md consistency, commit style, existing review files).
I have enough evidence. The `opencode run` syntax in the plan is verified correct (`-m/--model`, repeated `-f/--file` array, message positionals first). The current `docs/REVIEW_PROTOCOL.md` and `docs/github-upload-checklist.md` confirm where the active Claude Code language lives, and `AGENTS.md` still mandates Claude Code at lines 11, 13, 20. Here is my rereview.

---

# Opencode Stage 40 Plan Rereview

## Critical Findings

None.

## Important Findings

**I-1. The "Claude Code removed" guard cannot fail (`|| true` defeats it).**
Both `docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md:57` and `docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md:201` use:

```bash
rg -n "Ask Claude Code|Claude Code review|Claude Code for final" docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md || true
```

The `|| true` means this check always exits 0, so it provides **zero enforcement** that the active Claude Code phrases were actually removed. These patterns are well-targeted (they match `REVIEW_PROTOCOL.md:8,18,20,32` and `github-upload-checklist.md:174` and are case-sensitive, so they will not collide with the historical hyphenated `claude-code` filename tokens). Make it a real gate:

```bash
if rg -qn "Ask Claude Code|Claude Code review|Claude Code for final" docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md; then
  echo "FAIL: active Claude Code review requirements remain"
  exit 1
fi
```

Given the first review explicitly asked for verification hardening, shipping a guard that cannot fail is a regression of that very point.

**I-2. `REVIEW_PROTOCOL.md` "Review Record Naming" section is out of Task 1 scope.**
`docs/REVIEW_PROTOCOL.md:36-55` prescribes the naming convention for **new** review records as `docs/reviews/YYYY-MM-DD-stage-N-claude-code-review.md` and `docs/reviews/claude-code-plan-review.md`. The plan's Task 1 ("Replace active reviewer language" / "Preserve blocker policy" / "Do not rewrite history") never addresses this section. After Stage 40 the protocol will still tell contributors to name *new* records with the `claude-code` token while the project is actually producing `opencode-stage-40-*.md` records. The active doc becomes self-contradictory. Task 1 must extend the naming convention to the `opencode-...` form (while preserving the historical `claude-code-...` examples as accepted legacy names).

**I-3. Task 1 "intro and gate sections" is ambiguous and risks an incomplete edit.**
Task 1 Step 1 says update "the intro and gate sections." `REVIEW_PROTOCOL.md` has Claude Code references in three distinct gates — Before Coding (`:8`), During Development (`:18,:20`), and Before GitHub Upload (`:32`) — plus the naming section from I-2. "Gate sections" could be read to exclude "During Development" or the naming block. Combined with I-1 (the only verification that would catch a missed section cannot fail), there is real risk of shipping a half-migrated protocol. Task 1 should enumerate every Claude Code location to replace, or reference a single source-of-truth list.

**I-4. `AGENTS.md` is left contradicting the new active policy.**
`AGENTS.md:11` ("submit ... to Claude Code for review"), `:13` ("Claude Code review of the new code"), and `:20` ("When invoking Claude Code for plan or code review, pass `--effort max`") directly mandate Claude Code. The Stage 40 goal is "future plan and release reviews use local opencode with GLM 5.2, matching the user's current rule." `AGENTS.md` is listed as a publishable active tooling file in `docs/github-upload-checklist.md:108`, not historical record. Leaving it stale means the project's highest-priority instruction document contradicts `REVIEW_PROTOCOL.md` after this stage. The spec never decides this: either expand scope to update `AGENTS.md`'s three review-gate lines, or add an explicit "deferred with rationale" note. Silence is not acceptable for a stated goal of "matching the user's current rule."

**I-5. Plan "In scope" artifact list does not match execution.**
`docs/reviews/` already contains `opencode-stage-40-plan-rereview.md` and `opencode-stage-40-plan-rereview-prompt.md`, but the plan's Boundaries → In scope list (`plan:19-23`) only names the four first-pass review files. The fix loop in Task -1 ("Fix blockers before Task 1") naturally produces rereview artifacts, but the executable plan's file manifest omits them, creating audit drift between "what the plan says it will create" and "what actually lands." Either add the rereview prompt/result to the in-scope list, or add one line noting that the Task -1 fix loop may emit additional `opencode-stage-40-plan-rereview*.md` artifacts.

## Minor Findings

**M-1. No verification that review records exist and contain the required approval phrase.** The whole point of the gate is the review record, yet Task 3 verifies only the two active docs. Consider adding `rg -l "APPROVED FOR STAGE 40" docs/reviews/opencode-stage-40-*-review.md` (and the release equivalent) so a missing/failed review is caught.

**M-2. `git diff --quiet -- uv.lock` (`plan:228`, `spec:77`) checks only unstaged changes and is redundant with `uv lock --check`.** Harmless, but it can be dropped or complemented with `--cached`.

**M-3. History guards use `git diff --name-only` (unstaged only).** A *staged* modification to a `docs/reviews/claude-code-*` file would slip past `plan:202`. Low likelihood here, but `git diff HEAD --name-only` would cover both staged and unstaged.

**M-4. Spec design section does not mention the rereview/fix loop.** Acceptable as an operational detail, but a one-line note ("a plan review may require one or more fix/rereview cycles before Task 1") would align the spec with how the gate actually runs.

## Verdict

The fixes applied since the first review are genuine improvements and are verified correct: the Markdown `ruff format --check` removal is right, the history guards are present, the `opencode run -m zhipuai-coding-plan/glm-5.2 "<prompt>" --file ... --file ...` syntax matches the actual CLI (`-m/--model`, `-f/--file` array, message positionals first), the pre-flight task is added, and the commit message style (`Document opencode review workflow`) matches repo convention.

However, the rereview is not yet clean. I-1 means the headline verification (Claude Code removal) is non-enforcing. I-2 and I-3 mean the most likely execution outcome is a `REVIEW_PROTOCOL.md` that still prescribes `claude-code` naming for new records and may keep stale Claude Code phrases in the "During Development" gate. I-4 leaves the project's top-priority instruction doc (`AGENTS.md`) directly contradicting the new policy — which is exactly the kind of inconsistency a "review workflow" stage must not introduce. I-5 is an audit-fidelity gap between the plan and the artifacts already on disk.

Per the blocking policy ("Treat Critical and Important findings as blockers"), these must be resolved before execution. The approval phrase is therefore withheld.

**Required changes before approval:**
1. Convert the `|| true` Claude Code removal check into a failing guard (I-1), in both spec and plan.
2. Extend Task 1 to update the "Review Record Naming" section to the `opencode-...` convention for new records (I-2).
3. Enumerate every Claude Code location in `REVIEW_PROTOCOL.md` that Task 1 must replace (I-3).
4. Decide `AGENTS.md`: either bring its three review-gate lines into scope, or explicitly document the deferral (I-4).
5. Reconcile the plan's in-scope file manifest with the rereview artifacts already being produced (I-5).

Approval phrase: **not issued** (5 Important blockers remain).
