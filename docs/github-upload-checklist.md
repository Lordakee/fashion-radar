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

If `uv.lock` was changed by mirror-backed local operations before upload,
restore it before staging. See
[Recover A Mirror-Rewritten Lockfile](dependency-mirrors.md#recover-a-mirror-rewritten-lockfile)
for the recovery path.

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
      `community-handoff-check-dir`, `import-signals-dir --dry-run`,
      `import-signals-dir`, and `imported-review-workflow`; named steps
      `lint_handoff_directory`, `preview_candidate_phrases`,
      `review_handoff_readiness`, `dry_run_directory_import`,
      `import_directory_signals`, and `print_post_import_review`; the
      `review_handoff_readiness` step as the `community-handoff-check-dir`
      local-only handoff readiness report before importing rows; does not
      execute commands, read directories, validate files, import rows, open or
      write SQLite, fetch URLs, log in, download media, browser automation,
      scrape/crawl, monitor/watch, schedule, add source/platform connectors,
      perform source acquisition, prove demand, provide coverage verification,
      rank sources, write reports, update dashboards, generate configs,
      generate entity files, or add compliance, policy, authorization, or
      safety-review product features; and intentional printing of supplied
      directory/config/data paths inside copyable local commands, unlike
      aggregate candidate preview output.

Stage 41 docs freshness check:

- [ ] README links `docs/cli-reference.md`.
- [ ] Import/review examples that use `$PWD/data` pass `--data-dir "$PWD/data"`
      consistently.
- [ ] Installed-wheel help smoke covers every documented command, including
      the Stage 57 `heat-movers` entry.
- [ ] Stage 57 `heat-movers` docs describe local observed heat movement for
      one configured source set, compare configured sources and imported local
      signals, say output needs review, and say there is no demand proof or
      no platform coverage verification.
- [ ] Stage 58 `imported-review-workflow` docs describe the final read-only
      `heat-movers` handoff for local observed heat movement from configured
      sources and imported local signals, and say there is no demand proof or
      no platform coverage verification.
- [ ] Stage 60 `imported-review-workflow` docs describe the read-only
      imported-candidates step for candidate phrase review before the final
      read-only heat-movers step for local observed heat movement from
      configured sources and imported local signals, and say there is no demand
      proof and no platform coverage verification.
- [ ] Stage 65 `imported-entity-evidence` docs describe a local read-only,
      imported-only, privacy-safe drilldown over retained local rows with source
      type `manual_import`; include the `review_imported_entity_evidence`
      imported review workflow step; and state no scraping, no browser
      automation, no platform APIs, and no account or cookie work.
- [ ] `community-signal-profile` remains a print-only local producer contract
      for user-controlled tools, not source acquisition, platform monitoring,
      or compliance review.

Stage 52 docs check:

- [ ] `community-handoff-manifest` docs describe a local print-only producer
      manifest for one directory, including directory, pattern, suggested
      filename, producer profile/schema/example pointers,
      `directory_example_paths`, storage note, and workflow commands; no
      command execution, directory reads, file
      validation, row import, SQLite open/write, URL fetching, login, platform
      APIs, monitoring, scheduling, source/platform connectors, demand proof,
      platform coverage verification, source ranking, report writing,
      dashboard updates, config generation, or entity file generation.
- [ ] Saved manifest guidance says to keep the manifest outside the matched
      export directory or use a filename excluded by the handoff pattern,
      especially for JSON export directories using `--pattern "*.json"`.

Stage 56 docs check:

- [ ] `community-handoff-check-dir` docs describe a local-only handoff
      readiness report that reads matched local regular files and local config;
      no import rows, no SQLite, no config/data/report/dashboard/digest
      artifacts, no fetch URLs/login/platform APIs/download media/browser
      automation/scrape/crawl/monitor/watch/schedule/connectors/source
      acquisition/demand proof/ranking/coverage verification/entity generation/
      compliance/policy/authorization/safety-review features.

External tool handoff template docs check:

- [ ] Docs link
      [examples/community-tool-handoff.example.csv](../examples/community-tool-handoff.example.csv)
      and
      [examples/community-tool-handoff.example.json](../examples/community-tool-handoff.example.json)
      as sanitized CSV/JSON local file handoff templates for user-controlled
      external/community tools.
- [ ] Boundary text says the external tool handoff template is not
      platform collection and does not add connectors, scraping, browser
      automation, platform APIs, monitoring, scheduling, source acquisition,
      demand proof, ranking, or coverage verification.

External community tool export directory examples docs check:

- [ ] Docs link
      [examples/community-tool-handoff-directory.example/README.md](../examples/community-tool-handoff-directory.example/README.md),
      [examples/community-tool-handoff-directory.example/csv/community-tool-a.csv](../examples/community-tool-handoff-directory.example/csv/community-tool-a.csv),
      [examples/community-tool-handoff-directory.example/csv/community-tool-b.csv](../examples/community-tool-handoff-directory.example/csv/community-tool-b.csv),
      [examples/community-tool-handoff-directory.example/json/community-tool-a.json](../examples/community-tool-handoff-directory.example/json/community-tool-a.json),
      and
      [examples/community-tool-handoff-directory.example/json/community-tool-b.json](../examples/community-tool-handoff-directory.example/json/community-tool-b.json)
      as sanitized CSV/JSON local export directory examples for
      user-controlled external/community tools.
- [ ] Boundary text says the external community tool export directory examples
      are not platform collection and do not add connectors, scraping, browser
      automation, platform APIs, monitoring, scheduling, source acquisition,
      demand proof, ranking, or coverage verification.
- [ ] `community-signal-profile --format json` and
      `community-handoff-manifest --format json` docs expose those checked-in
      directory layout pointers as `directory_example_paths`.
- [ ] Package archive checks require the directory README plus the two CSV and
      two JSON handoff files.
- [ ] Package archive checks require the optional watchlist sample
      [examples/community-signals.watchlist.example.csv](../examples/community-signals.watchlist.example.csv)
      as a sanitized synthetic local community-signal file for exercising the
      optional entity pack. It adds no fetching URLs, no platform data
      collection, no connectors, no demand proof, no ranking, and no platform
      coverage verification.

External social/community tool adapter registry docs check:

- [ ] Docs describe `external-tool-adapters` as a local, print-only external
      social/community tool adapter registry and local producer-discovery
      registry for sanitized CSV/JSON local file handoff by user-controlled
      external/community tools.
- [ ] Boundary text says the registry is not platform collection and has no
      connectors, no scraping, no browser automation, no platform APIs, no
      monitoring, no scheduling, no source acquisition, no demand proof, no
      ranking, and no coverage verification.
- [ ] Each adapter command list includes `external-tool-readiness` as an
      optional local read-only preflight command, while
      `external-tool-adapters` itself remains print-only and does not run
      readiness or perform PATH lookup.
- [ ] CLI reference and installed-wheel smoke include `fashion-radar
      external-tool-adapters --format table` and `fashion-radar
      external-tool-adapters --format json`.

      ```bash
      fashion-radar external-tool-adapters --format table
      fashion-radar external-tool-adapters --format json
      ```

External tool template rows docs check:

- [ ] Docs describe `external-tool-template` as a local, print-only command
      that prints adapter-specific template rows for user-controlled
      external/community tools that need sanitized CSV/JSON local file handoff
      examples.
- [ ] Boundary text says the template command is not platform collection and
      has no connectors, no scraping, no browser automation, no platform APIs,
      no monitoring, no scheduling, no source acquisition, no demand proof, no
      ranking, and no coverage verification.
- [ ] JSON/CSV handoff rows remain importable row output only, while
      table/model guidance can include the same adapter recommended command
      list.
- [ ] CLI reference and installed-wheel smoke include `fashion-radar
      external-tool-template --adapter instaloader --format table`,
      `fashion-radar external-tool-template --adapter instaloader --format
      json`, and `fashion-radar external-tool-template --adapter instaloader
      --format csv`.

      ```bash
      fashion-radar external-tool-template --adapter instaloader --format table
      fashion-radar external-tool-template --adapter instaloader --format json
      fashion-radar external-tool-template --adapter instaloader --format csv
      ```

External tool workflow docs check:

- [ ] Docs describe `external-tool-workflow` as a local, print-only command
      that prints workflow metadata for user-controlled external/community
      tools that need a producer-facing wrapper around existing local commands
      before writing sanitized CSV/JSON local file handoff rows.
- [ ] Boundary text says the workflow command is not platform collection and
      has no connectors, no scraping, no browser automation, no platform APIs,
      no monitoring, no scheduling, no source acquisition, no demand proof, no
      ranking, and no coverage verification.
- [ ] Boundary text says the workflow command does not inspect directories,
      read handoff files, import rows, open SQLite, or create artifacts.
- [ ] JSON output is workflow metadata, not importable handoff rows.
- [ ] Workflow output includes `check_external_tool_readiness`, an optional
      preflight command that points to `external-tool-readiness` for local
      command availability guidance before sanitized handoff rows are prepared,
      while `external-tool-workflow` itself remains print-only.
- [ ] CLI reference and installed-wheel smoke include `fashion-radar
      external-tool-workflow --adapter instaloader --format table` and
      `fashion-radar external-tool-workflow --adapter instaloader --format
      json`.

      ```bash
      fashion-radar external-tool-workflow --adapter instaloader --format table
      fashion-radar external-tool-workflow --adapter instaloader --format json
      ```

External tool readiness docs check:

- [ ] Docs describe `external-tool-readiness` as local read-only, not
      print-only, because it performs command availability only with local PATH
      lookup (`shutil.which`) for known free external/community tools such as
      Rednote MCP, Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, and
      X/search exports.
- [ ] Boundary text says the readiness command prints readiness guidance,
      mirror-friendly install hints, and Fashion Radar next-step handoff
      commands for user-controlled external/community tools producing
      sanitized CSV/JSON local file handoff rows, but does not install
      dependencies automatically, does not run adapters, does not run upstream
      tools, does not inspect directories, does not read handoff files, import
      rows, open/write SQLite, or create config/data/report/dashboard/workflow/
      handoff artifacts.
- [ ] Boundary text says the readiness command is not a scraper/connector and
      has no scraping, no browser automation, no platform APIs, no
      account/session/cookie/token behavior, no monitoring, no scheduling, no
      source acquisition, no demand proof, no ranking, no coverage
      verification, and no compliance-review product feature.
- [ ] CLI reference and installed-wheel smoke include `fashion-radar
      external-tool-readiness --adapter instaloader --format table` and
      `fashion-radar external-tool-readiness --adapter instaloader --format
      json`.

      ```bash
      fashion-radar external-tool-readiness --adapter instaloader --format table
      fashion-radar external-tool-readiness --adapter instaloader --format json
      ```

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

Both first-run smokes use checked-in sample files and temporary config, data,
report, and export directories only. They do not run `collect`, `run`,
`dashboard`, scheduler/monitoring commands, scraping/crawling, browser
automation, account login, cookies/sessions, source/platform connectors,
platform automation, or external services. A successful source-checkout or
installed-wheel first-run smoke prints `First-run sample smoke passed.`.
The smoke also validates sample rows, matched starter entities, report content,
trend deltas, empty untracked candidates, and directory handoff dry-run counts.

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
  community-signal-profile \
  external-tool-adapters external-tool-template external-tool-workflow external-tool-readiness \
  community-signal-lint community-signal-lint-dir \
  community-candidates community-candidates-dir \
  community-handoff-manifest community-handoff-workflow \
  community-handoff-check-dir \
  import-signals import-signals-dir imported-signals imported-signals-summary \
  imported-entity-deltas imported-entity-evidence imported-candidates imported-candidate-evidence \
  imported-review-workflow collect match report candidates trends heat-movers \
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
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-candidates --help
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --help
"$tmp_env/venv/bin/fashion-radar" community-handoff-manifest --help
"$tmp_env/venv/bin/fashion-radar" community-handoff-workflow --help
"$tmp_env/venv/bin/fashion-radar" community-handoff-check-dir --help
"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --help
"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --format json
"$tmp_env/venv/bin/fashion-radar" external-tool-template --help
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format table
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format json
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format csv
"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --help
"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --adapter instaloader --format table
"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --adapter instaloader --format json
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --help
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format table
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format json
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter rednote_mcp --format json
"$tmp_env/venv/bin/fashion-radar" imported-signals --data-dir "$tmp_run/data" --as-of "2026-06-12T12:00:00Z" --format json
"$tmp_env/venv/bin/fashion-radar" imported-candidates --data-dir "$tmp_run/data" --config-dir "$tmp_run/config" --as-of "2026-06-13T12:00:00Z" --format json
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence --data-dir "$tmp_run/data" --as-of "2026-06-13T12:00:00Z" --entity-name "The Row" --entity-type brand --format json
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --data-dir "$tmp_run/data" --config-dir "$tmp_run/config" --as-of "2026-06-13T12:00:00Z" --phrase "Le Teckel bag" --format json
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --data-dir "$tmp_run/data ? # & %" --config-dir "$tmp_run/config ? # & %" --as-of "2026-06-13T12:00:00Z" --format json > "$tmp_run/imported-review-workflow.json"
"$tmp_env/venv/bin/fashion-radar" community-handoff-manifest "$tmp_run/missing ? # & %" --input-format csv --pattern "*.csv" --config-dir "$tmp_run/config ? # & %" --data-dir "$tmp_run/data ? # & %" --as-of "2026-06-13T12:00:00Z" --format json
"$tmp_env/venv/bin/fashion-radar" community-handoff-workflow "$tmp_run/missing ? # & %" --input-format csv --pattern "*.csv" --config-dir "$tmp_run/config ? # & %" --data-dir "$tmp_run/data ? # & %" --as-of "2026-06-13T12:00:00Z" --format json > "$tmp_run/community-handoff-workflow.json"
"$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
```

Check the installed-wheel community handoff workflow JSON shape. The checklist
expectation is `step_count == 6`, `review_handoff_readiness`, and a
`community-handoff-check-dir` local-only handoff readiness report before
importing rows:

```bash
"$tmp_env/venv/bin/python" - "$tmp_run/community-handoff-workflow.json" <<'PY'
import json
import sys
from pathlib import Path

workflow_json = Path(sys.argv[1]).read_text(encoding="utf-8")
payload = json.loads(workflow_json)
assert payload["execution_mode"] == "print_only"
assert payload["step_count"] == 6
assert [step["name"] for step in payload["steps"]] == [
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert payload["steps"][2]["name"] == "review_handoff_readiness"
assert "community-handoff-check-dir" in payload["steps"][2]["command"]
PY
```

Check the installed-wheel workflow JSON shape after the command above. The
checklist expectation is `step_count == 7`,
`review_imported_entity_evidence`, `review_imported_candidate_phrases`, and
final `review_local_heat_movers`:

```bash
"$tmp_env/venv/bin/python" - "$tmp_run/imported-review-workflow.json" <<'PY'
import json
import sys
from pathlib import Path

workflow_json = Path(sys.argv[1]).read_text(encoding="utf-8")
payload = json.loads(workflow_json)
assert payload["step_count"] == 7
assert payload["steps"][3]["name"] == "review_imported_entity_evidence"
assert payload["steps"][4]["name"] == "review_imported_candidate_phrases"
assert payload["steps"][-1]["name"] == "review_local_heat_movers"
PY
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
