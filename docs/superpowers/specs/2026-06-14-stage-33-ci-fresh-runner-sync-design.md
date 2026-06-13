# Stage 33 CI Fresh Runner Sync Design

## Goal

Fix the GitHub Actions CI failure introduced by Stage 32 while preserving the
public lockfile and mirror hygiene goals.

## Root Cause

The Stage 32 CI workflow runs this command in a fresh GitHub Actions runner
before any project environment exists:

```bash
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

`uv sync --check` checks whether the Python environment is already synchronized
with the project. On a fresh runner, `.venv` does not exist, so uv correctly
reports that it would create the project environment and exits with status `1`.

Local Stage 32 verification passed because the local repository already had a
synchronized `.venv`.

## Scope

Stage 33 is a CI/docs hygiene fix. It does not add runtime features.

In scope:

- Move the CI synchronization check after the locked install.
- Keep the pre-install public lockfile gate as `UV_NO_CONFIG=1 uv lock --check`
  plus the mirror-marker scan.
- Update contributor, PR, agent, mirror, and GitHub upload docs so fresh
  environments run locked sync before optional `--check` verification.
- Add Stage 33 plan/review artifacts.
- Check the GitHub Actions run after pushing the fix.

Out of scope:

- Runtime command changes.
- Dependency or `uv.lock` changes.
- Source connectors, scraping, crawling, browser automation, login/cookie
  flows, watchers, schedulers, source acquisition, source ranking, demand proof,
  or platform coverage verification.
- PyPI publishing or artifact uploads.

## Design

### CI Sequence

The CI sequence should distinguish lockfile validation from environment
synchronization:

```bash
UV_NO_CONFIG=1 uv lock --check
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

The first two checks validate the public lockfile without creating `.venv`.
The install step creates the fresh runner environment from the committed
lockfile. The post-install `--check` confirms the environment is synchronized
after creation.

### Docs Alignment

Docs should avoid telling users or CI to run `uv sync --check` before an
environment exists. For fresh environments, use:

```bash
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

For public lockfile validation independent of user-level mirror config, keep:

```bash
UV_NO_CONFIG=1 uv lock --check
```

Mirror-backed local installs still use `UV_DEFAULT_INDEX=... uv sync --frozen`
and should not rewrite or commit `uv.lock`.

## Verification

Local verification should include:

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

CI-like fresh environment verification should run the same lock/install/check
sequence with an isolated project environment path so it cannot reuse the local
`.venv`.

After push, query the GitHub Actions run for the new commit and confirm CI
completes successfully.
