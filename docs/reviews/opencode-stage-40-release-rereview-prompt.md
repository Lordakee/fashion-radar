# Opencode Stage 40 Release Rereview Prompt

You are rereviewing the Stage 40 release candidate for the `fashion-radar`
repository after one Important blocker was fixed.

Required review mode:

- Think carefully.
- This is a release rereview only; do not edit files.
- Treat Critical and Important findings as blockers.
- The review model must be GLM 5.2 via local opencode.

## Original Release Review Blocker

`docs/reviews/opencode-stage-40-release-review.md` withheld approval because
`docs/reviews/opencode-stage-40-plan-rereview-2.md` contained corrupted capture
text, duplicate verdicts, and duplicate approval phrases.

## Fix Applied

- Cleaned `docs/reviews/opencode-stage-40-plan-rereview-2.md` so it has one
  coherent review body.
- Confirmed it contains exactly one
  `APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW` phrase.
- Confirmed it contains no `Wrote` capture artifact and no orphaned
  `the next stage.` fragment.
- Updated the Stage 40 plan manifest to include release rereview artifacts if
  needed.

## Active Docs Still Expected To Be Correct

- `AGENTS.md` should require local opencode with GLM 5.2 for plan/code review.
- `docs/REVIEW_PROTOCOL.md` should route plan, code, next-stage, and release
  review gates to local opencode with GLM 5.2 and use `opencode-stage-N-*`
  naming for new records.
- `docs/github-upload-checklist.md` should require local opencode with GLM 5.2
  for final docs/code review.

The command form should remain:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

## Verification Evidence Re-run After The Fix

```bash
rg -n "Wrote|APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW|the next stage\\." docs/reviews/opencode-stage-40-plan-rereview-2.md
count=$(rg -c "APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW" docs/reviews/opencode-stage-40-plan-rereview-2.md)
if [ "$count" != "1" ]; then
  echo "FAIL: expected exactly one plan approval phrase, got $count"
  exit 1
fi
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

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if this release candidate is acceptable to commit and push, include
this exact phrase:

```text
APPROVED FOR STAGE 40 COMMIT AND PUSH
```
