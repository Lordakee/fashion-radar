# Stage 33 CI Fresh Runner Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development or superpowers:executing-plans to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Fix the GitHub Actions CI failure caused by running
`uv sync --locked --dev --check` before `.venv` exists on a fresh runner.

**Architecture:** Docs/CI-only fix. Split public lockfile validation from
environment synchronization. CI validates `uv.lock`, installs from the locked
file, then runs a post-install sync check.

**Tech Stack:** GitHub Actions YAML, Markdown docs/templates, uv, pytest, ruff,
GitHub Actions API status check. No dependency or runtime code changes.

---

## Boundaries

In scope:

- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- Stage 33 plan/review artifacts.

Out of scope:

- Runtime code changes.
- Dependency or `uv.lock` changes.
- Source connectors, scraping, crawling, platform automation, browser
  automation, login/cookie flows, watchers, schedulers, source acquisition,
  source ranking, demand proof, platform coverage verification, or social
  platform functionality.
- PyPI publishing or artifact uploads.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Add: `docs/reviews/claude-code-stage-33-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-33-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create a plan review prompt that includes:

- GitHub Actions run `27481885536` failed at `Public lockfile check`.
- Job `81230982347` log showed `UV_NO_CONFIG=1 uv sync --locked --dev --check`
  would create `.venv` and exited `1`.
- The proposed fix is to run `uv sync --check` only after
  `UV_NO_CONFIG=1 uv sync --locked --dev`.
- Stage 33 must remain docs/CI-only.

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-33-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-33-plan-review.md
```

Expected approval phrase:

```text
APPROVED FOR STAGE 33 CI FRESH RUNNER FIX
```

Fix Critical/Important plan findings before Task 1.

## Task 1: CI Fresh Runner Fix

**Files:**

- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Move sync check after install**

Change the public lockfile step so it no longer runs
`uv sync --locked --dev --check` before the environment exists:

```yaml
      - name: Public lockfile check
        run: |
          UV_NO_CONFIG=1 uv lock --check
          if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
            exit 1
          fi
      - name: Install dependencies
        run: |
          UV_NO_CONFIG=1 uv sync --locked --dev
          UV_NO_CONFIG=1 uv sync --locked --dev --check
```

- [ ] **Step 2: Verify CI YAML**

Run:

```bash
sed -n '1,80p' .github/workflows/ci.yml
rg -n 'Public lockfile check|Install dependencies|UV_NO_CONFIG=1 uv lock --check|UV_NO_CONFIG=1 uv sync --locked --dev$|UV_NO_CONFIG=1 uv sync --locked --dev --check|dist/\*\.whl' .github/workflows/ci.yml
```

Expected:

- pre-install step has `uv lock --check` and mirror-marker scan;
- install step runs locked sync, then sync check;
- no `dist/*.whl` references.

## Task 2: Docs And Template Alignment

**Files:**

- Modify: `CONTRIBUTING.md`
- Modify: `.github/pull_request_template.md`
- Modify: `AGENTS.md`
- Modify: `docs/dependency-mirrors.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update contributor/PR verification**

In `CONTRIBUTING.md`, make the verification block fresh-env safe:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

In `.github/pull_request_template.md`, change the sync checkbox to:

```markdown
- [ ] `UV_NO_CONFIG=1 uv sync --locked --dev`
- [ ] `UV_NO_CONFIG=1 uv sync --locked --dev --check`
```

Keep the existing `UV_NO_CONFIG=1 uv lock --check` checkbox.

- [ ] **Step 2: Update agent and mirror guidance**

In `AGENTS.md` and `docs/dependency-mirrors.md`, state:

- use `UV_NO_CONFIG=1 uv lock --check` for public lockfile validation;
- use `UV_NO_CONFIG=1 uv sync --locked --dev` for fresh CI/release installs;
- run `UV_NO_CONFIG=1 uv sync --locked --dev --check` only after the project
  environment exists or after the locked sync step.

- [ ] **Step 3: Update upload checklist**

In `docs/github-upload-checklist.md`, make both pre-upload verification blocks
fresh-env safe by placing:

```bash
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

after `UV_NO_CONFIG=1 uv lock --check`.

- [ ] **Step 4: Update changelog**

Add an Unreleased `Changed` bullet:

```markdown
- Adjusted CI and contributor verification so `uv sync --check` runs after a
  fresh locked environment install instead of before `.venv` exists.
```

## Task 3: Verification

**Files:**

- No runtime files.

- [ ] **Step 1: Fresh-env CI sequence smoke**

Run a local isolated-env version of the CI sequence:

```bash
tmp_project_env="$(mktemp -d)/venv"
UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
  exit 1
fi
UV_PROJECT_ENVIRONMENT="$tmp_project_env" UV_NO_CONFIG=1 uv sync --locked --dev
UV_PROJECT_ENVIRONMENT="$tmp_project_env" UV_NO_CONFIG=1 uv sync --locked --dev --check
```

Expected: exits `0`; it does not reuse the repository `.venv`.

- [ ] **Step 2: Full local verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
git diff --cached --check
```

- [ ] **Step 3: Build smoke**

Run the Stage 32 CI-equivalent build/install/dashboard smoke from
`docs/superpowers/plans/2026-06-14-stage-32-ci-release-hygiene-plan.md`.

- [ ] **Step 4: Boundary and secret scans**

Run diff-scoped scans for prohibited platform/source-acquisition implications,
secrets, `uv.lock`, dependency, runtime, data, report, and build artifact
changes.

## Task 4: Claude Code Release Review

**Files:**

- Add: `docs/reviews/claude-code-stage-33-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-33-release-review.md`

- [ ] **Step 1: Request release review**

Ask Claude Code to review the Stage 33 diff, root-cause evidence, verification
evidence, and scope boundaries.

Required approval phrase:

```text
APPROVED FOR STAGE 33 COMMIT AND PUSH
```

Fix Critical/Important findings before commit.

## Task 5: Commit, Push, And GitHub Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 33 files**

Run:

```bash
git add .github/workflows/ci.yml .github/pull_request_template.md AGENTS.md CONTRIBUTING.md CHANGELOG.md docs/dependency-mirrors.md docs/github-upload-checklist.md docs/superpowers/specs/2026-06-14-stage-33-ci-fresh-runner-sync-design.md docs/superpowers/plans/2026-06-14-stage-33-ci-fresh-runner-sync-plan.md docs/reviews/claude-code-stage-33-*.md
git diff --cached --name-only
git diff --cached -- uv.lock pyproject.toml src tests data reports
git diff --cached --check
```

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Fix CI fresh runner sync check"
```

Push with a one-shot HTTP extraheader. Do not persist the GitHub token.

- [ ] **Step 3: Confirm GitHub Actions**

Query the latest GitHub Actions run for the pushed commit. If it is queued or in
progress, wait and poll until it completes. If it fails, return to systematic
debugging with the job logs.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- GitHub Actions result;
- uncommitted files;
- next step.
