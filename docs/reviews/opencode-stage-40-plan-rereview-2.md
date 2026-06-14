# Opencode Stage 40 Plan Rereview 2

Review model: GLM 5.2 via local opencode (`zhipuai-coding-plan/glm-5.2`).
Mode: plan rereview, read-only. No files were edited by this review.

## Scope Reviewed

- `docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md`
- `docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md`

Supporting evidence was gathered from the live repository (read-only `rg`/`glob`)
to validate scope completeness and the verification guards against the actual
state of the active review-gate references.

## Confirmation Of Previous Rereview Fixes

All five previously raised Important blockers are resolved in the revised plan:

1. The stale phrase guard was narrowed away from brittle wording and toward a
   case-sensitive `Claude Code` scan over the three active workflow docs.
2. New review record naming is explicitly covered by `opencode-stage-N-*`
   examples while older `claude-code-*` records remain historical.
3. The plan enumerates each active file and section that must be updated.
4. `AGENTS.md` is included in the active update scope.
5. The rereview prompt/result artifacts are listed in the Stage 40 file scope.

Scope completeness was checked against the live repo. Active review-gate
references are limited to `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and
`docs/github-upload-checklist.md`; every other `Claude Code` mention is
historical or descriptive context outside the active review workflow.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

M1. Active-phrase guard has a confirmed false-negative. The guard

    ```
    rg -qn "Ask Claude Code|Claude Code review|Claude Code for final|When invoking Claude Code"
    ```

    does not match `AGENTS.md:11` ("...plan to Claude Code for review."), because
    the literal substring `Claude Code review` is broken by ` for ` between
    `Code` and `review`, and the wording is `for review`, not `for final`. The
    line is explicitly enumerated for replacement in Task 1 Step 1, so faithful
    execution still updates it; the automated guard alone would not catch a miss.
    Recommendation: widen the active-files scan to a case-sensitive `Claude Code`
    over `AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md`.
    Case-sensitive matching preserves the lowercase `claude-code` legacy path
    tokens that legitimately remain in the Review Record Naming section. Cheap,
    high-value, non-blocking.

M2. The history guard covers `docs/superpowers/plans/` but not
    `docs/superpowers/specs/`. There are 36 historical spec files under
    `docs/superpowers/specs/` besides the Stage 40 spec, so an accidental edit to
    any of them would not be caught. Recommendation: mirror the plans/ guard for
    specs/, allowing only the Stage 40 spec path. Non-blocking.

M3. The in-scope manifest lists `opencode-stage-40-plan-rereview*.md` and the
    rereview-2 artifacts as "Add", while Task -1 describes rereview artifacts as
    conditional ("If fixes are needed"). In practice the rereviews are running, so
    the manifest is satisfied; just note the manifest presupposes rereviews occur.
    Cosmetic.

M4. Task 3 Step 2 runs `git diff --cached --check` before Task 4 stages anything,
    so it is a no-op at that point. The staged whitespace check is more
    meaningful inside Task 4 after staging. Harmless. Cosmetic.

M5. The release-review prompt (Task 3 Step 3) is underspecified compared to the
    plan-review prompt, which has a full template. Consider adding a short
    release-review prompt template for consistency. Minor.

## Verdict

The revised plan is documentation-only, correctly scoped, preserves all
historical records, keeps the review-gated structure intact, switches the active
gates to local opencode with GLM 5.2, and carries sound verification plus
release checks. All previously raised Important blockers are resolved. The
remaining findings are Minor and non-blocking; M1 and M2 are cheap, high-value
improvements that can be folded into Task 1 / Task 3 during execution without
changing the plan's intent.

APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW
