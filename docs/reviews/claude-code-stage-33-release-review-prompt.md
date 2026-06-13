# Claude Code Stage 33 Release Review Prompt

You are reviewing the completed Stage 33 CI fresh runner sync fix for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release/code review only; do not edit files.
- Treat Critical and Important findings as blockers for commit and push.

## Goal

Fix the GitHub Actions CI failure from Stage 32 by ensuring
`uv sync --locked --dev --check` runs only after a fresh runner has created the
project environment with `uv sync --locked --dev`.

## Root Cause Evidence

GitHub Actions run `27481885536` for commit
`ad2116df6763cb1b2bab3e7e1c34d9c046c6bac0` failed in job `81230982347`, step
`Public lockfile check`.

The job log showed:

```text
UV_NO_CONFIG=1 uv sync --locked --dev --check
Would create project environment at: .venv
The environment is outdated; run `uv sync` to update the environment
Process completed with exit code 1.
```

Local Stage 32 verification passed because the local repository already had a
synchronized `.venv`; the GitHub runner was fresh and had no project
environment.

## Approved Plan Evidence

- Stage 33 design:
  `docs/superpowers/specs/2026-06-14-stage-33-ci-fresh-runner-sync-design.md`
- Stage 33 plan:
  `docs/superpowers/plans/2026-06-14-stage-33-ci-fresh-runner-sync-plan.md`
- Stage 33 plan approval:
  `docs/reviews/claude-code-stage-33-plan-review.md`

The plan review contains:

```text
APPROVED FOR STAGE 33 CI FRESH RUNNER FIX
```

## Files To Review

- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- `docs/superpowers/specs/2026-06-14-stage-33-ci-fresh-runner-sync-design.md`
- `docs/superpowers/plans/2026-06-14-stage-33-ci-fresh-runner-sync-plan.md`
- `docs/reviews/claude-code-stage-33-*.md`

## Review Checklist

Check that:

- CI pre-install `Public lockfile check` runs `UV_NO_CONFIG=1 uv lock --check`.
- CI pre-install lockfile gate keeps the mirror/index marker scan.
- CI install step runs `UV_NO_CONFIG=1 uv sync --locked --dev` first.
- CI install step runs `UV_NO_CONFIG=1 uv sync --locked --dev --check` only
  after the locked sync creates or updates `.venv`.
- CI still uses temp build artifacts and does not rely on repository
  `dist/*.whl`.
- Contributor docs, PR template, agent instructions, dependency mirror docs, and
  upload checklist no longer tell fresh environments to run `uv sync --check`
  before locked sync.
- Mirror-backed local installs remain `UV_DEFAULT_INDEX=... uv sync --frozen`
  and do not rewrite `uv.lock`.
- No `uv.lock`, dependency, runtime code, test code, data, report, generated
  artifact, source connector, scraping, crawling, platform automation, watcher,
  scheduler, source acquisition, source ranking, demand proof, platform
  coverage verification, or social-platform functionality changes are present.
- No secrets or tokens are included in the diff.

## Verification Evidence

Focused checks exited `0`:

```bash
rg -n 'Public lockfile check|Install dependencies|UV_NO_CONFIG=1 uv lock --check|UV_NO_CONFIG=1 uv sync --locked --dev$|UV_NO_CONFIG=1 uv sync --locked --dev --check|dist/\*\.whl' .github/workflows/ci.yml
rg -n 'UV_NO_CONFIG=1 uv lock --check|UV_NO_CONFIG=1 uv sync --locked --dev$|UV_NO_CONFIG=1 uv sync --locked --dev --check|sync --check runs after|environment exists|fresh' AGENTS.md CONTRIBUTING.md .github/pull_request_template.md docs/dependency-mirrors.md docs/github-upload-checklist.md CHANGELOG.md
git diff --check
git diff --cached --check
git diff --name-only -- uv.lock pyproject.toml src tests data reports
```

Fresh-environment sequence exited `0` with an isolated
`UV_PROJECT_ENVIRONMENT` that did not reuse repository `.venv`:

```bash
tmp_project_env="$(mktemp -d)/venv"
UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
  exit 1
fi
UV_PROJECT_ENVIRONMENT="$tmp_project_env" UV_NO_CONFIG=1 uv sync --locked --dev
UV_PROJECT_ENVIRONMENT="$tmp_project_env" UV_NO_CONFIG=1 uv sync --locked --dev --check
"$tmp_project_env/bin/python" -c "import fashion_radar; print('public fresh env ok')"
```

Before the package cache was warmed, the same public-index fresh-env sequence
timed out during dependency download. A mirror-backed frozen fresh install was
used to complete the missing package download without rewriting the public
lockfile, and the public sequence passed afterward:

```bash
UV_PROJECT_ENVIRONMENT="$tmp_project_env" UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
UV_PROJECT_ENVIRONMENT="$tmp_project_env" UV_NO_CONFIG=1 uv sync --locked --dev --check
```

Full local verification exited `0`:

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

Test result:

```text
572 passed
```

The Stage 32 CI-equivalent build/install/dashboard smoke also exited `0`.

Diff-scoped boundary scan matched only existing negative boundary language in
`AGENTS.md`. Diff-scoped secret scan returned no matches. Runtime/dependency
diff checks returned no files.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 33 COMMIT AND PUSH
```
