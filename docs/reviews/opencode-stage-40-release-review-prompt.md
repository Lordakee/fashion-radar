# Opencode Stage 40 Release Review Prompt

You are reviewing the Stage 40 release candidate for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- This is a release review only; do not edit files.
- Treat Critical and Important findings as blockers.
- The review model must be GLM 5.2 via local opencode.

## Goal

Update the active repository review workflow docs so future plan and release
audit gates use local `opencode` with the GLM 5.2 model.

## Expected Technical Approach

- Update `AGENTS.md` so the active project instructions require local opencode
  with GLM 5.2 for plan/code review gates.
- Update `docs/REVIEW_PROTOCOL.md` so Before Coding, During Development,
  Before GitHub Upload, and Review Record Naming describe local opencode with
  GLM 5.2 instead of the prior review workflow.
- Update `docs/github-upload-checklist.md` so the Final Review section uses
  local opencode with GLM 5.2.
- Keep historical `claude-code-*` records as audit history and do not rewrite
  them.
- Keep this stage documentation-only.

The documented local opencode command form should be:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

## Files Changed Or Added In This Stage

- Modified: `AGENTS.md`
- Modified: `docs/REVIEW_PROTOCOL.md`
- Modified: `docs/github-upload-checklist.md`
- Added: `docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md`
- Added: `docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md`
- Added: `docs/reviews/opencode-stage-40-plan-review-prompt.md`
- Added: `docs/reviews/opencode-stage-40-plan-review.md`
- Added: `docs/reviews/opencode-stage-40-plan-rereview-prompt.md`
- Added: `docs/reviews/opencode-stage-40-plan-rereview.md`
- Added: `docs/reviews/opencode-stage-40-plan-rereview-2-prompt.md`
- Added: `docs/reviews/opencode-stage-40-plan-rereview-2.md`
- Added: `docs/reviews/opencode-stage-40-release-review-prompt.md`
- Added after this prompt runs: `docs/reviews/opencode-stage-40-release-review.md`

## Verification Evidence Already Run

```bash
rg -n "opencode|zhipuai-coding-plan/glm-5.2|GLM 5.2" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
if rg -qn "Claude Code" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md; then
  echo "FAIL: active Claude Code review requirements remain"
  exit 1
fi
rg -n "opencode-stage-N|opencode-stage-40" docs/REVIEW_PROTOCOL.md docs/reviews/opencode-stage-40-*.md
if git diff HEAD --name-only | rg '^docs/reviews/claude-code'; then
  echo "FAIL: historical Claude Code review records changed"
  exit 1
fi
if git diff HEAD --name-only | rg '^docs/superpowers/plans/' | rg -v '^docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md$'; then
  echo "FAIL: unrelated historical plan files changed"
  exit 1
fi
if git diff HEAD --name-only | rg '^docs/superpowers/specs/' | rg -v '^docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md$'; then
  echo "FAIL: unrelated historical spec files changed"
  exit 1
fi
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Observed result: all commands exited 0. `uv.lock` was not modified.

## Review Questions

1. Do the active workflow docs consistently point future plan, code, and release
   reviews to local opencode with GLM 5.2?
2. Are the review record naming instructions internally consistent with the new
   `opencode-stage-N-*` convention while preserving historical audit records?
3. Does this stage avoid product behavior changes, dependency changes,
   lockfile changes, CI changes, scraping/crawling/platform automation, source
   acquisition, schedulers, watchers, and monitors?
4. Are there any Critical or Important issues that should block commit and push?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if this release candidate is acceptable to commit and push, include
this exact phrase:

```text
APPROVED FOR STAGE 40 COMMIT AND PUSH
```
