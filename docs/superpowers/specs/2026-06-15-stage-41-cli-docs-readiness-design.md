# Stage 41 CLI Docs Readiness Design

## Goal

Refresh the public documentation for the current command-line surface so users
can follow one local workspace consistently and contributors have a compact
command map for release checks.

## Scope

In scope:

- Add a compact CLI reference document for the current public commands, path
  flags, output flags, and read/write behavior.
- Update README documentation links and examples so local import/review flows
  consistently use the same `--config-dir`, `--data-dir`, and `--reports-dir`
  paths where relevant.
- Update manual/community signal import docs so single-file and directory
  import examples show current `--data-dir` and `--imported-at` flags.
- Update source pack usage docs so copying a pack into a repo-local config
  directory is paired with explicit `--config-dir` examples.
- Update trend delta examples so `match` and `trends` read the same local data
  directory used by import/review commands.
- Update dashboard and data-retention examples to surface current `--host`,
  `--port`, and `--data-dir` behavior.
- Update candidate discovery, daily digest, scheduling, and entity pack examples
  when they show the same operational commands with path defaults that would
  mix repo-local config and platform-default data/report directories.
- Update the GitHub upload checklist smoke commands so help coverage matches
  the current public command surface.
- Record Stage 41 Claude Code plan/release review artifacts under
  `docs/reviews/`.

Out of scope:

- Source code, tests, dependencies, `uv.lock`, CI workflow behavior, database
  schema, runtime behavior, dashboards, reports, packaging behavior, generated
  artifacts, and config templates.
- Rewriting historical review records or historical release-gate records.
- Adding source connectors, scraping, crawling, browser automation,
  login/cookie/account/proxy/CAPTCHA flows, platform APIs, source acquisition,
  schedulers, watchers, monitors, or external services.

## Design

Create `docs/cli-reference.md` as the compact current command map. It should be
short enough to audit, grouped by task area, and should explicitly call out:

- `--config-dir`, `--data-dir`, and `--reports-dir` are dynamic defaults unless
  environment variables are set.
- `import-signals` uses `--format` for input format and supports
  `--data-dir`, `--source-name`, `--imported-at`, and `--dry-run`.
- `import-signals-dir` uses required `--format` and `--pattern`, with separate
  `--output-format`.
- Review commands use `--format` for table/JSON output.
- `clean-old-data` is the cleanup command name.
- Dashboard defaults to `127.0.0.1:8501` and supports `--host` and `--port`.

Update user-facing docs by editing examples rather than adding new behavior.
The primary consistency rule is: if an example imports into `$PWD/data`, all
follow-up review/match/trend commands in that sequence must also pass
`--data-dir "$PWD/data"`. If an example copies config to `$PWD/configs`, the
follow-up command must pass `--config-dir "$PWD/configs"` unless the text
explicitly tells the user to export `FASHION_RADAR_CONFIG_DIR`.

Keep `docs/release-gate-stage31.md` as historical evidence. Do not rewrite it.
Instead, stop presenting it in README as the current release/readiness document;
the current reusable upload gate remains `docs/github-upload-checklist.md`.

## Verification

Focused documentation checks:

```bash
rg -n "docs/cli-reference.md|CLI Reference|Command Reference" README.md docs/cli-reference.md
rg -n "import-signals .*--data-dir|import-signals-dir .*--data-dir|--imported-at" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md
rg -n "trends .*--data-dir|match .*--data-dir" docs/trend-deltas.md README.md docs/architecture.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md
rg -n "dashboard .*--host|dashboard .*--port|clean-old-data .*--data-dir|source-pack-lint .*--strict" README.md docs/dashboard.md docs/data-retention.md docs/source-packs.md
if rg -qn "release-gate-stage31" README.md; then
  echo "FAIL: README still presents Stage 31 release gate as current docs"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md | rg -v -- "--data-dir"; then
  echo "FAIL: repo-local review tail command without --data-dir"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md | rg -v -- "--config-dir"; then
  echo "FAIL: repo-local review tail command without --config-dir"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " README.md | rg -v -- "--help" | rg -v -- "--data-dir"; then
  echo "FAIL: README review command without --data-dir"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " README.md | rg -v -- "--help" | rg -v -- "--config-dir"; then
  echo "FAIL: README review command without --config-dir"
  exit 1
fi
scoped_docs=(
  README.md
  docs/cli-reference.md
  docs/manual-signal-import.md
  docs/community-signal-import.md
  docs/community-signal-quality.md
  docs/architecture.md
  docs/source-packs.md
  docs/trend-deltas.md
  docs/dashboard.md
  docs/data-retention.md
  docs/candidate-discovery.md
  docs/daily-digest.md
  docs/scheduling.md
  docs/entity-packs.md
  docs/github-upload-checklist.md
)
if rg -n "fashion-radar (report|candidates|trends|run) [^\\\\]*$" "${scoped_docs[@]}" | rg -v -- "--as-of|--help"; then
  echo "FAIL: one-line command requiring --as-of is documented without --as-of"
  exit 1
fi
rg -n -C 3 "fashion-radar (report|candidates|trends|run)( |$| \\\\)" "${scoped_docs[@]}"
rg -n "claude-code-stage-41" docs/reviews/claude-code-stage-41-*.md
git diff --check
```

Release checks:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar --help
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar collect --help
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar import-signals --help
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar import-signals-dir --help
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar trends --help
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar dashboard --help
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar clean-old-data --help
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```
