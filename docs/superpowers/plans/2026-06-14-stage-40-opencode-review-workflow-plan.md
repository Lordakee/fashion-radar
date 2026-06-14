# Stage 40 Opencode Review Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update active repository review docs so future audit gates use local opencode with GLM 5.2.

**Architecture:** This is a documentation-only workflow update. Keep historical Claude Code records untouched, and update only the active process docs and project agent instructions that future agents and contributors should follow.

**Tech Stack:** Markdown docs, `opencode run -m zhipuai-coding-plan/glm-5.2`, `rg`, `uv`, `git`. No Python source, dependency, lockfile, schema, connector, scraping, platform automation, scheduler, watcher, monitor, or CI behavior changes.

---

## Boundaries

In scope:

- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Add: `docs/reviews/opencode-stage-40-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-40-plan-review.md`
- Add: `docs/reviews/opencode-stage-40-plan-rereview-prompt.md`
- Add: `docs/reviews/opencode-stage-40-plan-rereview.md`
- Add: `docs/reviews/opencode-stage-40-plan-rereview-2-prompt.md`
- Add: `docs/reviews/opencode-stage-40-plan-rereview-2.md`
- Add: `docs/reviews/opencode-stage-40-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-40-release-review.md`
- Add if needed: `docs/reviews/opencode-stage-40-release-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-40-release-rereview.md`
- Add: this Stage 40 spec and plan

Out of scope:

- Rewriting historical `docs/reviews/claude-code-*` records.
- Rewriting historical `docs/superpowers/plans/*` references to Claude Code.
- Editing source code, tests, workflow YAML, package metadata, `uv.lock`, data,
  reports, generated artifacts, or config templates.
- Adding source connectors, scraping, crawling, browser automation,
  login/cookie/account/proxy/CAPTCHA flows, source acquisition, platform APIs,
  schedulers, watchers, monitors, or external services.

## Task -1: Opencode Plan Review Gate

**Files:**

- Create: `docs/reviews/opencode-stage-40-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-40-plan-review.md`

- [ ] **Step 1: Write plan review prompt**

Create `docs/reviews/opencode-stage-40-plan-review-prompt.md`:

```markdown
# Opencode Stage 40 Plan Review Prompt

You are reviewing the Stage 40 opencode review workflow documentation plan for
the `fashion-radar` repository.

Required review mode:

- Think carefully.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.
- The review model must be GLM 5.2 via local opencode.

## Goal

Update the active repository review workflow docs so future audit gates use
local `opencode` with the GLM 5.2 model.

## Proposed Technical Approach

- Update `docs/REVIEW_PROTOCOL.md` to replace active Claude Code review gates
  with local opencode review gates.
- Use this local model ID in examples:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

- Update `docs/github-upload-checklist.md` final review language to require
  local opencode with GLM 5.2 before upload.
- Keep historical Claude Code records and old staged plans untouched.
- Keep the change documentation-only.
- Do not change product code, tests, dependencies, lockfiles, CI, database
  schema, commands, scraping/crawling/platform automation, source acquisition,
  schedulers, watchers, or monitors.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md`
- `docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW
```
```

- [ ] **Step 2: Request opencode plan review**

Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 \
  "$(cat docs/reviews/opencode-stage-40-plan-review-prompt.md)" \
  --file docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md \
  --file docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md \
  > docs/reviews/opencode-stage-40-plan-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW`. Fix blockers before Task 1.
If fixes are needed, store each follow-up prompt/result as
`docs/reviews/opencode-stage-40-plan-rereview*.md`.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm worktree contains only Stage 40 planning files**

Run:

```bash
git status --short --branch
```

Expected before editing active docs: modified or untracked files are limited to
Stage 40 spec, plan, and opencode review prompt/result files. If unrelated files
appear, stop and investigate before editing.

## Task 1: Update Active Agent Instructions And Review Protocol

**Files:**

- Modify: `AGENTS.md`
- Modify: `docs/REVIEW_PROTOCOL.md`

- [ ] **Step 1: Replace active reviewer language in `AGENTS.md`**

Replace the active Claude Code review requirements in `AGENTS.md`:

- line requiring objective/architecture/technical stack/implementation method
  and plan submission to Claude Code;
- line requiring Claude Code review of newly added code;
- line requiring `--effort max` when invoking Claude Code.

The new instructions should say reviews use local opencode with GLM 5.2:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

- [ ] **Step 2: Replace active reviewer language in `docs/REVIEW_PROTOCOL.md`**

Update every active Claude Code review reference in these sections:

- Before Coding;
- During Development;
- Before GitHub Upload;
- Review Record Naming.

The key command to document is:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

Explain that `zhipuai-coding-plan/glm-5.2` is the local opencode model ID for
GLM 5.2.

- [ ] **Step 3: Preserve blocker policy**

Keep the current workflow structure:

- plan review before coding;
- fresh documentation checks and release verification before release review;
- Critical and Important findings block progress;
- review artifacts are recorded in `docs/reviews/`.

- [ ] **Step 4: Update new review record naming without rewriting history**

New records should use names like:

```text
docs/reviews/opencode-stage-N-plan-review.md
docs/reviews/opencode-stage-N-release-review.md
```

Add one sentence stating that older `claude-code-*` review files remain
historical records and do not need rewriting.

## Task 2: Update GitHub Upload Checklist

**Files:**

- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Update Final Review section**

Change the final review step that currently asks Claude Code for review so it
requires local opencode with GLM 5.2 instead:

```text
Run a final local opencode code and documentation review with GLM 5.2.
```

Include the command form:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

- [ ] **Step 2: Keep upload exclusions and verification commands unchanged**

Do not alter dependency, smoke-test, package, artifact-exclusion, token,
SQLite, CodeGraph, or generated-report checklist items.

## Task 3: Verification And Opencode Release Review

**Files:**

- Create: `docs/reviews/opencode-stage-40-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-40-release-review.md`

- [ ] **Step 1: Documentation checks**

Run:

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
```

Expected: the first command finds the new active opencode language; the second
check fails if active Claude Code review requirements remain. The history
guards confirm Stage 40 did not rewrite historical Claude Code review artifacts
or unrelated historical plans/specs.

- [ ] **Step 2: Release verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

- [ ] **Step 3: Opencode release review**

Create `docs/reviews/opencode-stage-40-release-review-prompt.md` with the diff
summary, verification evidence, and next-stage recommendation. Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 \
  "$(cat docs/reviews/opencode-stage-40-release-review-prompt.md)" \
  --file AGENTS.md \
  --file docs/REVIEW_PROTOCOL.md \
  --file docs/github-upload-checklist.md \
  > docs/reviews/opencode-stage-40-release-review.md
```

Required approval phrase:

```text
APPROVED FOR STAGE 40 COMMIT AND PUSH
```

Fix all Critical and Important findings before commit.
If fixes are needed, store each follow-up release prompt/result as
`docs/reviews/opencode-stage-40-release-rereview*.md`.

## Task 4: Commit, Push, And Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 40 files**

Confirm that no source code, dependency files, lockfiles, generated data,
reports, build artifacts, tokens, or unrelated files are staged.

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Document opencode review workflow"
```

Push with a token-free remote and one-shot auth only if needed. Do not persist
GitHub tokens in remote URLs or git config.

- [ ] **Step 3: Confirm GitHub Actions**

Confirm the latest pushed commit reaches GitHub and CI completes successfully.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- review artifacts produced;
- GitHub Actions result;
- uncommitted files;
- next step.
