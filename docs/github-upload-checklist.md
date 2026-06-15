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
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Mirror install check:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

Do not stage `uv.lock` if mirror-backed local operations changed it. Regenerate
the lockfile only against the default PyPI registry before publishing.

If a user-level uv config sets a mirror as the default index, keep release
lockfile checks isolated from that config:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

Check the public lockfile has no mirror URLs:

```bash
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
```

Historical boundary checks:

Stage 27B docs check:

- [ ] `community-candidates` docs describe one-file local pre-import preview,
      aggregate-only output, no SQLite writes, no URL fetching, and no supplied
      input file path, row URL, row title, summary, raw text, normalized key,
      candidate context, or representative item detail exposure.

Stage 29 docs check:

- [ ] `community-candidates-dir` docs describe local non-recursive directory
      preview, aggregate-only output, no SQLite writes, no URL fetching, and no
      supplied directory path, matched file path, matched file name, row URL,
      row title, summary, raw text, normalized key, candidate context, raw
      validation finding, account/private field, or representative item detail
      exposure.

Stage 30 docs check:

- [ ] `community-handoff-workflow` docs describe a local print-only directory
      workflow for `community-signal-lint-dir`, `community-candidates-dir`,
      `import-signals-dir --dry-run`, `import-signals-dir`, and
      `imported-review-workflow`; no command execution, directory reads, file
      validation, row import, SQLite open/write, URL fetching, login, media
      download, browser automation, scraping, monitoring, folder watching,
      scheduling, source/platform connectors, demand proof, platform coverage
      verification, source ranking, report writing, dashboard updates, config
      generation, or entity file generation; and intentional printing of
      supplied directory/config/data paths inside copyable local commands,
      unlike aggregate candidate preview output.

Stage 41 docs freshness check:

- [ ] README links `docs/cli-reference.md`.
- [ ] Import/review examples that use `$PWD/data` pass `--data-dir "$PWD/data"`
      consistently.
- [ ] Installed-wheel help smoke covers every current public command.

## Exclude

Do not commit or upload:

- `.venv/`
- `.env.local` or other `.env.*` local environment files
- `.pytest_cache/`
- `.ruff_cache/`
- `build/`
- `dist/`
- local SQLite databases or sidecars such as `*.sqlite`, `*.sqlite-wal`,
  `*.sqlite-shm`, `*.db`, `*.db-wal`, and `*.db-shm`
- generated reports under `reports/`
- generated runtime configs such as `configs/sources.yaml`,
  `configs/entities.yaml`, and `configs/scoring.yaml`
- `.codegraph` database, WAL/SHM, sockets, logs, or PID files
- cookies
- secrets
- API tokens
- browser profiles
- account/session files
- private source exports
- local credential config files such as `.pypirc`, `pip.conf`, `pip.ini`,
  `uv.toml`, `.netrc`, and `.npmrc`
- key material such as `*.pem` and `*.key`
- user-specific local config containing sensitive paths or credentials

`.codegraph/.gitignore` intentionally keeps CodeGraph runtime files out of git
while allowing the ignore rule itself to be tracked.

The release hygiene script checks tracked files and unignored untracked files.
Ignored local artifacts are kept out of normal git publication by `.gitignore`
rather than reported on every run.

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

Run the release hygiene gate before building archives:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
```

Run the deterministic first-run sample smoke. It uses checked-in community
signal examples and temporary config/data/report directories; it does not run
live collection or launch the dashboard server:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Use `/tmp` for build artifacts:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
```

Installed-wheel smoke:

The installed-wheel first-run smoke uses the built wheel Python environment,
does not prepend the checkout `src/` directory to `PYTHONPATH`, and fails if it
imports `fashion_radar` from the source tree.

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
for cmd in \
  init migrate-db doctor source-pack-lint entity-pack-lint \
  community-signal-lint community-signal-lint-dir \
  community-candidates community-candidates-dir community-handoff-workflow \
  import-signals import-signals-dir imported-signals imported-signals-summary \
  imported-entity-deltas imported-candidates imported-candidate-evidence \
  imported-review-workflow collect match report candidates trends \
  schedule-example dashboard clean-old-data run
do
  "$tmp_env/venv/bin/fashion-radar" "$cmd" --help
done
tmp_run="$(mktemp -d)"
mkdir -p "$tmp_run/exports"
mkdir -p "$tmp_run/config"
printf 'version: 1\nscoring: {}\ncandidate_discovery:\n  min_current_mentions: 1\n  review_min_current_mentions: 1\n' > "$tmp_run/config/scoring.yaml"
printf 'url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n' > "$tmp_run/exports/signals.csv"
"$tmp_env/venv/bin/fashion-radar" import-signals-dir --help
"$tmp_env/venv/bin/fashion-radar" import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --dry-run
"$tmp_env/venv/bin/fashion-radar" import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --data-dir "$tmp_run/data"
"$tmp_env/venv/bin/fashion-radar" imported-signals --help
"$tmp_env/venv/bin/fashion-radar" imported-signals-summary --help
"$tmp_env/venv/bin/fashion-radar" imported-entity-deltas --help
"$tmp_env/venv/bin/fashion-radar" imported-candidates --help
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --help
"$tmp_env/venv/bin/fashion-radar" community-handoff-workflow --help
"$tmp_env/venv/bin/fashion-radar" imported-signals --data-dir "$tmp_run/data" --as-of "2026-06-12T12:00:00Z" --format json
"$tmp_env/venv/bin/fashion-radar" imported-candidates --data-dir "$tmp_run/data" --config-dir "$tmp_run/config" --as-of "2026-06-13T12:00:00Z" --format json
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --data-dir "$tmp_run/data" --config-dir "$tmp_run/config" --as-of "2026-06-13T12:00:00Z" --phrase "Le Teckel bag" --format json
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --data-dir "$tmp_run/data ? # & %" --config-dir "$tmp_run/config ? # & %" --as-of "2026-06-13T12:00:00Z" --format json
"$tmp_env/venv/bin/fashion-radar" community-handoff-workflow "$tmp_run/missing ? # & %" --input-format csv --pattern "*.csv" --config-dir "$tmp_run/config ? # & %" --data-dir "$tmp_run/data ? # & %" --as-of "2026-06-13T12:00:00Z" --format json
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
3. Run a final local Claude Code code and documentation review with
   `--effort max`.
4. Fix all Critical and Important findings.
5. Let the user choose or create the GitHub remote and push.

Use this command form:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```
