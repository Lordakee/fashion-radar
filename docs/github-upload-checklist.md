# GitHub Upload Checklist

The repository can be prepared locally by an agent, but the user controls remote
creation, pushing to GitHub, PyPI publishing, and artifact uploads.

Do not create a public GitHub repository, add/push a remote, publish a package,
or upload build artifacts unless the user explicitly asks for that action.

## Before Upload

Run:

```bash
git status --short --untracked-files=all
git status --ignored --short
git diff --check
uv lock --check
uv sync --locked --dev --check
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Mirror install check:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

Check the public lockfile has no mirror URLs:

```bash
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
```

## Exclude

Do not commit or upload:

- `.venv/`
- `.pytest_cache/`
- `.ruff_cache/`
- `build/`
- `dist/`
- local SQLite databases or sidecars such as `*.sqlite`, `*.sqlite-wal`,
  `*.sqlite-shm`, `*.db`, `*.db-wal`, and `*.db-shm`
- generated reports under `reports/`
- `.codegraph` database, WAL/SHM, sockets, logs, or PID files
- cookies
- secrets
- API tokens
- browser profiles
- account/session files
- private source exports
- user-specific local config containing sensitive paths or credentials

`.codegraph/.gitignore` intentionally keeps CodeGraph runtime files out of git
while allowing the ignore rule itself to be tracked.

## Tooling Files

These files are intentionally publishable when they contain no secrets or local
absolute paths:

- `AGENTS.md`
- `.mcp.json`
- `.claude/settings.json`
- `.codegraph/.gitignore`

`.mcp.json` should use a relative project path for CodeGraph. The current
project config uses `"--path", "."`.

## Package Smoke

Use `/tmp` for build artifacts:

```bash
tmp_build="$(mktemp -d)"
uv build --out-dir "$tmp_build"
python -m zipfile -l "$tmp_build"/*.whl | rg 'fashion_radar/templates/(daily_report.md|configs/(sources|entities|scoring)\.example\.yaml)'
```

Installed-wheel smoke:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
```

Dashboard extra smoke:

```bash
tmp_dash="$(mktemp -d)"
uv venv "$tmp_dash/venv"
wheel_path="$(ls "$tmp_build"/*.whl | head -n 1)"
uv pip install --python "$tmp_dash/venv/bin/python" "${wheel_path}[dashboard]"
"$tmp_dash/venv/bin/python" -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
```

## Final Review

Before upload:

1. Run full verification.
2. Sync and check CodeGraph if it is being used.
3. Ask Claude Code for final docs/code review.
4. Fix all Critical and Important findings.
5. Let the user choose or create the GitHub remote and push.
