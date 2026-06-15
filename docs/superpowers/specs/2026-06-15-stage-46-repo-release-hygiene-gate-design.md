# Stage 46 Repo Release Hygiene Gate Design

## Goal

Add a local, dependency-free release hygiene gate that catches accidental
publication of local runtime files, secrets, generated data, generated configs,
and private exports before the repository is pushed or packaged for GitHub.

## Scope

In scope:

- Add `scripts/check_release_hygiene.py`, a no-network checker for tracked
  paths, selected high-risk untracked files, persistent git remote/config
  leaks, and high-confidence secret-like content in tracked text files.
- Extend `scripts/check_package_archives.py` so built wheels and sdists reject
  forbidden archive members such as `.env.local`, generated SQLite files,
  generated reports, generated runtime configs, CodeGraph runtime databases,
  cookie/session files, private exports, caches, and bytecode.
- Add pytest coverage for the release hygiene script and archive denylist.
- Update `.gitignore` with narrow local artifact, session, token, and private
  export patterns while keeping publishable examples and docs visible.
- Update CI and `docs/github-upload-checklist.md` to run the same release
  hygiene gate before package smoke.
- Update GitHub Actions checkout to use `persist-credentials: false` so the
  hygiene gate does not fail on credentials injected by the runner checkout
  step.
- Extend docs drift tests so CI and the upload checklist cannot silently drop
  either release hygiene or package archive checks.
- Record Stage 46 Claude Code plan and release review artifacts.

Out of scope:

- Any source acquisition, scraping, crawling, browser automation, login,
  cookie/session use, CAPTCHA/proxy handling, account automation, source
  connectors, social platform APIs, media download, scheduling, watching, or
  external service integration.
- Any product compliance-review feature. This node is repository release
  hygiene only.
- Broad low-confidence content scanning. The repository intentionally documents
  terms such as token, cookie, session, and secret, so content checks should be
  high-confidence and redact values.
- Dependency additions, dependency upgrades, lockfile changes, runtime CLI
  behavior changes, database schema changes, dashboard changes, generated data,
  generated reports, or publishing to PyPI/GitHub Releases. The
  user-authorized node completion process may still commit, push with a
  non-persistent auth header, and confirm CI after local verification and
  Claude Code release review.

## Design

Create `scripts/check_release_hygiene.py` with only Python standard library
dependencies. The script should accept `--repo-root`, defaulting to the current
directory, and exit `1` after printing redacted findings to stderr when it
detects a release blocker. A clean run should print:

```text
Release hygiene checks passed.
```

The script should run local git commands only:

- `git ls-files` to inspect tracked repository paths.
- `git ls-files --others --exclude-standard` to inspect unignored local paths
  and fail only for high-risk artifact names, not every untracked scratch file.
  Ignored files are intentionally not reported because they are not normal git
  publication candidates; `.gitignore` is tightened in the same node to keep
  common local artifacts ignored.
- `git remote -v` and
  `git config --get-regexp '^http\\..*\\.extraheader$'` to detect persistent
  token-like remote URLs or saved authorization headers without printing their
  values.

Tracked path policy should reject:

- `.env` and `.env.*`, except `.env.example`.
- Virtual environments, build outputs, caches, bytecode, and egg-info.
- `.codegraph/*`, except `.codegraph/.gitignore`.
- `data/**`, except `data/README.md`.
- `reports/**`, except `reports/README.md`.
- Generated runtime configs: `configs/sources.yaml`,
  `configs/entities.yaml`, and `configs/scoring.yaml`.
- SQLite/database files and sidecars anywhere:
  `*.sqlite`, `*.sqlite-*`, `*.sqlite3`, `*.sqlite3-*`, `*.db`, and `*.db-*`.
- Cookie, session, browser profile, private export, local credential, and key
  material names.
- Local credential/config filenames: `.pypirc`, `pip.conf`, `pip.ini`,
  `uv.toml`, `.netrc`, and `.npmrc`.

Untracked path policy should be narrower: fail only when an unignored file or
directory looks like a high-risk local artifact. Examples include `.env.local`,
`cookies.txt`, `session.json`, `storage-state.json`, `browser-profiles/`,
`private-source-export.csv`, `exports/`, `private-exports/`, generated
`configs/*.yaml`, `data/*.sqlite`, `reports/latest.json`, local credential
config files such as `.pypirc`, `pip.conf`, `pip.ini`, `uv.toml`, `.netrc`,
and `.npmrc`, `*.pem`, and `*.key`.

Content scanning should inspect tracked text files only. It should skip binary
files and redacts values in findings. The patterns should be intentionally
high-confidence:

- GitHub personal access tokens with length-aware valid-looking patterns, such
  as `ghp_` followed by 36 token characters or `github_pat_` followed by a
  multi-part token shape. Prefix examples in docs/tests must not be enough to
  trigger a finding.
- PEM private key blocks.
- Persistent HTTP authorization headers in git config output.

Do not add a generic keyword scanner for words such as `token`, `secret`,
`cookie`, or `session`.

Extend `scripts/check_package_archives.py` with a shared forbidden-member
classifier used by both wheel and sdist validation. For sdists, reuse the
existing normalized path set after removing the top-level source directory. For
wheels, inspect member paths as written. Error messages should include the
archive label and offending member path, for example:

```text
sdist archive contains forbidden release member: .env.local
```

Allow these specific paths if present:

- `.env.example`
- `.codegraph/.gitignore`
- `data/README.md`
- `reports/README.md`

Update `.gitignore` with narrow local ignore patterns for env variants, local
Python packaging config, cookies/session/browser state, private exports,
generated local config variants, and key material. Keep all example files,
fixtures, templates, and docs publishable.

Update `.github/workflows/ci.yml` to run:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
```

after dependency installation and before lint/test/build steps. Also update
the checkout step:

```yaml
- uses: actions/checkout@v4
  with:
    persist-credentials: false
```

Update the upload checklist to include the same command under the pre-upload
checks.

If the checker is run outside a git repository, it should fail cleanly with a
short error instead of raising a traceback.

## Verification

Focused checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_release_hygiene.py tests/test_package_archives.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
```

Package smoke:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
```

Release checks:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```
