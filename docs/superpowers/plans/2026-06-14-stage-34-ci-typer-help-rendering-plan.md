# Stage 34 CI Typer Help Rendering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development or superpowers:executing-plans to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Fix the GitHub Actions pytest failure caused by Typer/Rich help output
being ANSI-split under `GITHUB_ACTIONS=true`.

**Architecture:** CI-only test environment fix. Set
`_TYPER_FORCE_DISABLE_TERMINAL=1` for the pytest step so Typer does not force
Rich terminal rendering under GitHub Actions. Runtime CLI behavior is unchanged.

**Tech Stack:** GitHub Actions YAML, Markdown plan/review artifacts, uv,
pytest, ruff. No dependency or runtime code changes.

---

## Boundaries

In scope:

- `.github/workflows/ci.yml`
- `CHANGELOG.md`
- Stage 34 plan/review artifacts.

Out of scope:

- Runtime code changes.
- Test assertion rewrites.
- Dependency or `uv.lock` changes.
- Source connectors, scraping, crawling, platform automation, browser
  automation, login/cookie flows, watchers, schedulers, source acquisition,
  source ranking, demand proof, platform coverage verification, or social
  platform functionality.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Add: `docs/reviews/claude-code-stage-34-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-34-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create a plan review prompt with:

- GitHub Actions run `27482498492` failed in `Tests` after Stage 33 fixed
  lockfile/install order.
- Local reproduction:
  `CI=true GITHUB_ACTIONS=true uv run pytest tests/test_cli.py::test_dashboard_command_help_lists_config_dir -q`
  fails because Typer/Rich inserts ANSI escape sequences inside option strings.
- Local verification:
  `CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest tests/test_cli.py -q`
  passes with `189 passed`.
- Proposed fix:
  set `_TYPER_FORCE_DISABLE_TERMINAL=1` only on the GitHub Actions pytest step.

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-34-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-34-plan-review.md
```

Expected approval phrase:

```text
APPROVED FOR STAGE 34 CI TYPER HELP FIX
```

Fix Critical/Important plan findings before Task 1.

## Task 1: CI Test Environment Fix

**Files:**

- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Add Typer terminal override to pytest step**

Change:

```yaml
      - name: Tests
        run: uv run pytest
```

to:

```yaml
      - name: Tests
        env:
          _TYPER_FORCE_DISABLE_TERMINAL: "1"
        run: uv run pytest
```

- [ ] **Step 2: Verify CI YAML**

Run:

```bash
rg -n 'name: Tests|_TYPER_FORCE_DISABLE_TERMINAL|uv run pytest' .github/workflows/ci.yml
```

Expected: the env var appears only in the Tests step.

## Task 2: Changelog

**Files:**

- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add Changed bullet**

Add:

```markdown
- Stabilized GitHub Actions CLI help tests by disabling Typer forced terminal
  rendering in the pytest step.
```

## Task 3: Verification

**Files:**

- No runtime files.

- [ ] **Step 1: Reproduce and verify CI-specific test behavior**

Run:

```bash
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest tests/test_cli.py -q
```

Expected: exits `0`.

- [ ] **Step 2: Full local verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
```

- [ ] **Step 3: Boundary and secret scans**

Run diff-scoped scans for prohibited platform/source-acquisition implications,
secrets, `uv.lock`, dependency, runtime, data, report, and build artifact
changes.

## Task 4: Claude Code Release Review

**Files:**

- Add: `docs/reviews/claude-code-stage-34-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-34-release-review.md`

- [ ] **Step 1: Request release review**

Ask Claude Code to review the Stage 34 diff, root-cause evidence, verification
evidence, and scope boundaries.

Required approval phrase:

```text
APPROVED FOR STAGE 34 COMMIT AND PUSH
```

Fix Critical/Important findings before commit.

## Task 5: Commit, Push, And GitHub Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 34 files**

Run:

```bash
git add .github/workflows/ci.yml CHANGELOG.md docs/superpowers/specs/2026-06-14-stage-34-ci-typer-help-rendering-design.md docs/superpowers/plans/2026-06-14-stage-34-ci-typer-help-rendering-plan.md docs/reviews/claude-code-stage-34-*.md
git diff --cached --name-only
git diff --cached -- uv.lock pyproject.toml src tests data reports
git diff --cached --check
```

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Stabilize CI Typer help tests"
```

Push with a one-shot HTTP extraheader. Do not persist the GitHub token.

- [ ] **Step 3: Confirm GitHub Actions**

Poll the latest GitHub Actions run for the pushed commit until it completes.
If it fails, return to systematic debugging with job logs.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- GitHub Actions result;
- uncommitted files;
- next step.
