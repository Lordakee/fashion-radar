# Stage 32 CI Release Hygiene Design

## Goal

Align public GitHub CI, contributor verification docs, and upload smoke commands
with the Stage 31 release-gate findings.

## Scope

Stage 32 is a CI/docs hygiene node. It does not add runtime features.

In scope:

- Add public lockfile checks to CI with user-level uv config disabled.
- Add a CI check that `uv.lock` contains no mirror/index URL markers.
- Keep CI build artifacts in a temporary directory instead of repository
  `dist/`.
- Update contributor-facing verification commands to use `UV_NO_CONFIG=1` for
  public lockfile checks.
- Update agent-facing dependency guidance to use `UV_NO_CONFIG=1` for committed
  lockfile checks.
- Link release/mirror docs from the README documentation index.
- Complete the Stage 31 review artifact summary by referencing the full
  `docs/reviews/claude-code-stage-31-*.md` artifact set.
- Update dependency mirror docs to explain the difference between mirror-backed
  local installs and public lockfile validation.
- Update package smoke docs to avoid relying on a bare `python` executable.
- Add Stage 32 plan/review artifacts.

Out of scope:

- Runtime command behavior changes.
- New collectors, source connectors, social-platform integrations, scraping,
  crawling, browser automation, login/cookie workflows, watchers, schedulers,
  source acquisition, source ranking, demand proof, or platform coverage
  verification.
- Dependency changes or `uv.lock` changes.
- Publishing a PyPI package or uploading build artifacts.

## Design

### CI Lockfile Gate

GitHub CI should verify the public lockfile before install:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

This keeps CI aligned with Stage 31 and protects contributors who have a
user-level `~/.config/uv/uv.toml` mirror default from accidentally treating the
public lockfile as stale.

CI should also reject mirror/index URL markers in `uv.lock`:

```bash
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
  exit 1
fi
```

### CI Build Smoke

The build smoke should write sdist/wheel artifacts to a temp directory:

```bash
tmp_build="$(mktemp -d)"
uv build --out-dir "$tmp_build"
```

Installed-wheel and dashboard extra smoke should live in the same GitHub Actions
step as the build, so the `tmp_build` shell variable is still in scope. The
step should install from `"$tmp_build"/*.whl` instead of `dist/*.whl`, so a
local copy-paste of the CI block does not dirty the repo.

### Docs Alignment

Update these docs and templates:

- `CONTRIBUTING.md`
- `AGENTS.md`
- `README.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- `docs/release-gate-stage31.md`
- `CHANGELOG.md`

The docs should distinguish:

- local mirror-backed installs: `UV_DEFAULT_INDEX=... uv sync --frozen ...`;
- public lockfile validation: `UV_NO_CONFIG=1 uv lock --check` and
  `UV_NO_CONFIG=1 uv sync --locked --dev --check`.

`docs/github-upload-checklist.md` package smoke should use `uv run python` or a
known temp-venv interpreter instead of bare `python`, because some environments
do not provide a `python` binary.

## Verification

Required local checks:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
git diff --cached --check
```

CI smoke syntax should be checked with shell execution where possible by running
the same build/install block locally against `/tmp`.

Boundary scan should confirm Stage 32 changes do not introduce positive claims
about prohibited platform/source-acquisition functionality.
