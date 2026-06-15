# Stage 43 Claude Review Protocol Restore Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore Claude Code with `--effort max` as the active review authority
and add a guard test so active workflow docs do not drift back to opencode.

**Architecture:** This is a documentation and docs-test node. It updates the two
active workflow entry points that still name opencode, leaves historical audit
records untouched, and adds a small pytest guard over active workflow docs.

**Tech Stack:** Markdown docs, Python 3.11, pytest, `uv`, `ruff`, `rg`, local
Claude Code CLI with `--effort max`. No runtime, source acquisition, connector,
scraping, platform automation, dependency, lockfile, CI, database, or dashboard
changes.

---

## Boundaries

In scope:

- Modify: `AGENTS.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify if release review exposes command-form drift:
  `docs/github-upload-checklist.md`
- Modify if review exposes active command drift: `docs/github-upload-checklist.md`
- Create: `tests/test_review_protocol_docs.py`
- Add: `docs/reviews/claude-code-stage-43-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-43-plan-review.md`
- Add if needed: `docs/reviews/claude-code-stage-43-plan-rereview*.md`
- Add: `docs/reviews/claude-code-stage-43-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-43-release-review.md`
- Maintain/update: this Stage 43 spec and plan.

Out of scope:

- Modifying historical `docs/reviews/opencode-stage-40-*` records.
- Modifying historical staged specs/plans solely because they mention opencode
  or Claude Code as prior audit history.
- Modifying `docs/github-upload-checklist.md` beyond active Claude Code command
  alignment if the guard or review exposes a current-review inconsistency.
- Source code, package metadata, `uv.lock`, CI YAML, database schema, runtime
  behavior, generated reports/data, dashboards, config templates, or schedules.
- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, watchers,
  monitors, or external services.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Create: `docs/reviews/claude-code-stage-43-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-43-plan-review.md`

- [ ] **Step 1: Write plan review prompt**

Create `docs/reviews/claude-code-stage-43-plan-review-prompt.md`:

````markdown
# Claude Code Stage 43 Plan Review Prompt

You are reviewing the Stage 43 Claude review protocol restore plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## User Rule Change

The user canceled the temporary local opencode/GLM 5.2 review rule and asked to
return review work to local Claude Code.

## Goal

Restore Claude Code with `--effort max` as the active plan and code/release
review authority, while preserving historical opencode records as audit history.

## Proposed Technical Approach

- Update `AGENTS.md` active review gate instructions from local opencode/GLM 5.2
  to local Claude Code with `--effort max`.
- Update `docs/REVIEW_PROTOCOL.md` active review process, command examples, and
  review record naming from `opencode-stage-N-*` to `claude-code-stage-N-*`.
- Keep `docs/github-upload-checklist.md` unchanged unless a real inconsistency
  is found; it already points to Claude Code in Final Review.
- Add `tests/test_review_protocol_docs.py` to assert active workflow docs do not
  contain active opencode authority terms such as `local opencode`,
  `opencode run`, `zhipuai-coding-plan/glm-5.2`, `GLM 5.2`, or
  `docs/reviews/opencode-stage-N`, and do contain the expected Claude Code
  command/naming terms.
- Allow the narrow historical note that older `opencode-*` review records under
  `docs/reviews/` are audit records and do not need rewriting.
- Scope the guard to active workflow docs only:
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/github-upload-checklist.md`
- Do not rewrite historical review artifacts, prior stage specs/plans, runtime
  behavior, package metadata, lockfiles, CI, databases, dashboards, scraping,
  crawling, platform automation, source acquisition, schedulers, watchers,
  monitors, or external services.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-43-claude-review-protocol-restore-design.md`
- `docs/superpowers/plans/2026-06-15-stage-43-claude-review-protocol-restore-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 43 CLAUDE REVIEW PROTOCOL RESTORE
```
````

- [ ] **Step 2: Request Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-43-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-43-plan-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 43 CLAUDE REVIEW PROTOCOL RESTORE`. Fix blockers before
Task 1. If fixes are needed, store each follow-up prompt/result as
`docs/reviews/claude-code-stage-43-plan-rereview*.md`.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm only Stage 43 planning files are dirty**

Run:

```bash
git status --short --branch
```

Expected before implementation: modified or untracked files are limited to the
Stage 43 spec, plan, and Claude Code Stage 43 plan review prompt/result files.
If unrelated files appear, stop and investigate before editing.

## Task 1: Add Active Review Protocol Drift Guard

**Files:**

- Create: `tests/test_review_protocol_docs.py`

- [ ] **Step 1: Write failing guard test**

Create `tests/test_review_protocol_docs.py`:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
REVIEW_PROTOCOL = ROOT / "docs" / "REVIEW_PROTOCOL.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"

ACTIVE_REVIEW_DOCS = [
    AGENTS,
    REVIEW_PROTOCOL,
    UPLOAD_CHECKLIST,
]

FORBIDDEN_ACTIVE_REVIEW_TERMS = (
    "local opencode",
    "opencode run",
    "zhipuai-coding-plan/glm-5.2",
    "GLM 5.2",
    "docs/reviews/opencode-stage-N",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_active_review_docs_use_claude_code_not_opencode() -> None:
    failures: list[str] = []

    for path in ACTIVE_REVIEW_DOCS:
        text = _read(path)
        for term in FORBIDDEN_ACTIVE_REVIEW_TERMS:
            if term in text:
                failures.append(f"{path.relative_to(ROOT)} still contains {term!r}")

    assert not failures, "\n".join(failures)


def test_active_review_protocol_documents_claude_code_gate() -> None:
    agents_text = _read(AGENTS)
    protocol_text = _read(REVIEW_PROTOCOL)
    checklist_text = _read(UPLOAD_CHECKLIST)

    assert "Claude Code" in agents_text
    assert "--effort max" in agents_text
    assert "claude --effort max --permission-mode plan --no-session-persistence" in protocol_text
    assert "claude-code-stage-N-plan-review.md" in protocol_text
    assert "claude-code-stage-N-release-review.md" in protocol_text
    assert "claude --effort max --permission-mode plan --no-session-persistence" in checklist_text
```

- [ ] **Step 2: Run the focused test**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py -q
```

Expected before Task 2 docs edits: FAIL because `AGENTS.md` and
`docs/REVIEW_PROTOCOL.md` still contain active opencode authority language.
Expected after Task 2 docs edits: PASS.

- [ ] **Step 3: Run style checks**

Run:

```bash
UV_NO_CONFIG=1 uv run ruff check tests/test_review_protocol_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_review_protocol_docs.py
```

Expected: both commands pass.

## Task 2: Restore Active Review Workflow Docs

**Files:**

- Modify: `AGENTS.md`
- Modify: `docs/REVIEW_PROTOCOL.md`

- [ ] **Step 1: Update `AGENTS.md` review gates**

Replace the active opencode review gate wording with Claude Code wording:

```markdown
## Review Gates

- Follow the staged review workflow in `docs/REVIEW_PROTOCOL.md`.
- Before starting a new stage, submit the objective, architecture, tech stack,
  implementation method, and plan to local Claude Code with `--effort max` for
  review.
- After completing a development node, run fresh verification and request local
  Claude Code review of the new code before moving to the next stage.
- Fix critical and important review findings before continuing.
```

- [ ] **Step 2: Update `AGENTS.md` runtime settings**

Replace the active opencode model instructions with:

````markdown
## Agent Runtime Settings

- When spawning Codex subagents for this project, set the subagent reasoning
  effort to `xhigh`.
- When invoking local Claude Code for plan or code review, use `--effort max`
  and read-only plan mode:

  ```bash
  claude --effort max --permission-mode plan --no-session-persistence \
    --tools Read,Grep,Glob,LS,Bash \
    -p "review prompt..."
  ```
````

- [ ] **Step 3: Update `docs/REVIEW_PROTOCOL.md` active process**

Use this full content for `docs/REVIEW_PROTOCOL.md`:

````markdown
# Review Protocol

This project follows a review-gated workflow.

## Before Coding

1. Write the objective, architecture, technical stack, implementation method, and staged plan.
2. Ask local Claude Code with `--effort max` to review the plan.
3. Record the review in `docs/reviews/`.
4. Fix critical and important planning issues.
5. Start implementation only after the plan is acceptable.

Use this command form for plan reviews:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

## During Development

Each implementation stage must end with:

1. Fresh tests and lint checks.
2. Local Claude Code review of newly added code.
3. Fixes for critical and important findings.
4. Local Claude Code review of the next-stage plan.

## Before GitHub Upload

Before pushing to GitHub:

1. Run the full test suite.
2. Run linting.
3. Run lockfile, package build, installed-wheel, packaged-resource, and optional
   dashboard extra smoke checks.
4. Check for secrets, cookies, tokens, private data, generated reports, local
   SQLite databases, SQLite sidecars, build artifacts, and CodeGraph DB files.
5. Ask local Claude Code with `--effort max` for final code and documentation review.
6. Fix critical and important findings.
7. Let the user create or choose the GitHub remote.

Use the same local Claude Code command form for release reviews:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

## Review Record Naming

Use this convention:

```text
docs/reviews/claude-code-stage-N-plan-review.md
docs/reviews/claude-code-stage-N-release-review.md
```

For follow-up reviews after fixes:

```text
docs/reviews/claude-code-stage-N-plan-rereview.md
docs/reviews/claude-code-stage-N-release-rereview.md
```

Older `opencode-*` records under `docs/reviews/` are historical audit records
and do not need rewriting.
````

- [ ] **Step 4: Align `docs/github-upload-checklist.md` if needed**

If review or verification shows the checklist's final Claude Code command is
shorter than the active protocol command, use this command form:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

- [ ] **Step 5: Run the guard after docs edits**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py -q
```

Expected: PASS.

## Task 3: Verification And Claude Code Release Review

**Files:**

- Create: `docs/reviews/claude-code-stage-43-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-43-release-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_review_protocol_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_review_protocol_docs.py
rg -n "local opencode|opencode run|zhipuai-coding-plan/glm-5.2|GLM 5.2|docs/reviews/opencode-stage-N" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
rg -n "Claude Code|claude --effort max|claude-code-stage-N" AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md
git diff --check
```

Expected: pytest and ruff pass; active-opencode-authority `rg` returns no
matches with exit 1; Claude Code `rg` finds the restored active protocol terms;
diff check passes.

- [ ] **Step 2: Run release verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py -q
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Expected: all commands pass.

- [ ] **Step 3: Write Claude Code release review prompt**

Create `docs/reviews/claude-code-stage-43-release-review-prompt.md`:

````markdown
# Claude Code Stage 43 Release Review Prompt

You are reviewing Stage 43 before commit and push.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a read-only release/code/docs review; do not edit files.
- Treat Critical and Important findings as blockers.

## User Rule Change

The user canceled the temporary opencode/GLM 5.2 review rule and asked to return
review work to local Claude Code.

## Expected Scope

- Active docs should restore Claude Code with `--effort max` as the plan and
  code/release review authority.
- `AGENTS.md` and `docs/REVIEW_PROTOCOL.md` should no longer require opencode or
  GLM 5.2.
- `docs/github-upload-checklist.md` should remain aligned with Claude Code final
  review instructions.
- `tests/test_review_protocol_docs.py` should guard only active workflow docs,
  not historical audit records.
- Historical `docs/reviews/opencode-stage-40-*` records and old staged specs/plans
  should remain untouched.
- No runtime, source acquisition, scraping/crawling/platform automation, package,
  lockfile, CI, database, dashboard, or generated-data behavior should change.

## Review Inputs

- Base commit: fill in with `git rev-parse HEAD`
- Working tree diff: inspect `git diff -- AGENTS.md docs/REVIEW_PROTOCOL.md tests/test_review_protocol_docs.py docs/superpowers/specs/2026-06-15-stage-43-claude-review-protocol-restore-design.md docs/superpowers/plans/2026-06-15-stage-43-claude-review-protocol-restore-plan.md docs/reviews/claude-code-stage-43-plan-review-prompt.md docs/reviews/claude-code-stage-43-plan-review.md`
- Verification output recorded by the agent before this review.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if Stage 43 is acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 43 COMMIT AND PUSH
```
````

- [ ] **Step 4: Request Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-43-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-43-release-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 43 COMMIT AND PUSH`. Fix blockers and rerun review before
commit.

## Task 4: Commit, Push, CI, And Handoff

**Files:**

- Git only.

This task is authorized only in the current active thread, where the user has
already provided the GitHub remote, authorized non-persistent token use for
pushes, and repeatedly asked that each completed node be reviewed, committed,
pushed, checked in GitHub Actions, and handed off. In a fresh session without
that user authorization, stop after release review with a Handoff Summary and
ask the user before committing or pushing.

Claude Code is a read-only reviewer in this workflow. The commit is performed by
Codex, so do not add a Claude Code co-author trailer unless the user or repo
instructions explicitly require one.

- [ ] **Step 1: Inspect status and staged diff**

Run:

```bash
git status --short --branch
git diff --stat
git diff --check
```

Expected: dirty files are Stage 43 docs, review artifacts, and
`tests/test_review_protocol_docs.py`; diff check passes.

- [ ] **Step 2: Commit Stage 43**

Run:

```bash
git add AGENTS.md docs/REVIEW_PROTOCOL.md tests/test_review_protocol_docs.py docs/superpowers/specs/2026-06-15-stage-43-claude-review-protocol-restore-design.md docs/superpowers/plans/2026-06-15-stage-43-claude-review-protocol-restore-plan.md docs/reviews/claude-code-stage-43-*.md
git commit -m "Restore Claude Code review protocol"
```

Expected: commit succeeds.

- [ ] **Step 3: Push with non-persistent credentials if needed**

Run normal push first:

```bash
git push origin main
```

If credentials are required, use the previously authorized one-shot
`http.extraheader` pattern without storing the token in Git config or remotes.

- [ ] **Step 4: Confirm GitHub Actions**

Run:

```bash
gh run list --branch main --limit 3
```

If a new run appears, wait until it completes:

```bash
gh run watch <run-id> --exit-status
```

Expected: the pushed commit's GitHub Actions run completes successfully.

- [ ] **Step 5: Handoff Summary and pause**

Write a concise Handoff Summary with:

- repo status;
- commit hash and push status;
- verified commands;
- unsubmitted/uncommitted files;
- next step.

Pause after this node because the user previously requested pausing when the
current node ends.
