# Claude Code Stage 9 Code Review Prompt

You are reviewing the Stage 9 implementation for Fashion Radar. Run this as a
read-only code review. Do not edit files, do not run collectors, do not call the
network, and do not execute platform/social tooling.

Use maximum reasoning effort. The invoking command must be:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-9-code-review-prompt.md
```

## Review Base

Review the uncommitted implementation changes on top of:

```text
862d9821d7d56ec136eee31e3f16a06dc7ac5f5d docs: add stage 9 manual import plan
```

## Goal

Stage 9 adds optional offline import of user-provided local CSV/JSON signal
files. The import path must validate rows before opening any database write
path, store only conservative item metadata, and allow imported rows to flow
through existing match, report, candidate, and dashboard workflows.

## Implemented Behavior To Review

- Adds `SourceType.MANUAL_IMPORT = "manual_import"`.
- Rejects `manual_import` in configured source definitions and `sources.yaml`.
- Keeps `manual_import` out of default collector dispatch.
- Adds `src/fashion_radar/importers/manual_signals.py`.
- Parses local CSV/JSON using standard-library `csv`/`json`.
- Validates required fields `url`, `title`, `published_at`.
- Accepts optional `summary`, `source_name`, `platform`, `source_weight`,
  `collected_at`.
- Ignores unknown/private fields and does not persist them.
- Rejects malformed CSV rows with extra cells.
- Allows empty CSV files with headers as zero rows.
- Normalizes empty optional fields and default source names.
- Adds `store_manual_signal_rows()` for already validated rows.
- Adds `fashion-radar import-signals PATH --format csv|json`.
- Ensures dry-run, invalid files, invalid `--imported-at`, and unsupported
  formats do not create `data_dir` or the SQLite database.
- Updates report/dashboard candidate wording to mention configured sources and
  imported local signals.
- Adds docs for manual local imports without acquisition instructions.

## Explicit Out Of Scope

The implementation must not add or document:

- platform search or automated social collection
- crawlers, scrapers, browser automation, Playwright, Selenium, MCP platform
  scraping servers, or account automation
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining exports from Instagram, TikTok, X/Twitter,
  Xiaohongshu, or similar platforms
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile internals, images, videos, media downloading, or reposting
- claims of complete social listening, complete platform coverage, verified
  demand, market-wide trend proof, or real-time social monitoring

## Files Changed

Modified:

- `CHANGELOG.md`
- `README.md`
- `docs/architecture.md`
- `docs/candidate-discovery.md`
- `docs/dashboard.md`
- `docs/scoring.md`
- `docs/source-boundaries.md`
- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/dashboard/app.py`
- `src/fashion_radar/models/source.py`
- `src/fashion_radar/reports.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- `tests/test_dashboard.py`
- `tests/test_models.py`
- `tests/test_reports.py`
- `tests/test_workflows.py`

Added:

- `docs/manual-signal-import.md`
- `src/fashion_radar/importers/__init__.py`
- `src/fashion_radar/importers/manual_signals.py`
- `tests/test_manual_signal_import.py`

## Verification Already Run

Fresh verification commands completed successfully:

```bash
.venv/bin/python -m pytest -q
# 200 passed

.venv/bin/python -m ruff check .
# All checks passed

.venv/bin/python -m ruff format --check .
# 65 files already formatted

uv lock --check
# Resolved 84 packages

uv sync --locked --dev --check
# Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
# Would make no changes
```

Package smoke also completed successfully:

```bash
uv build --out-dir /tmp/fashion-radar-dist-stage9
uv venv "$tmpdir/venv"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmpdir/venv/bin/python" "$wheel"
"$tmpdir/venv/bin/fashion-radar" import-signals --help
"$tmpdir/venv/bin/fashion-radar" import-signals "$tmpdir/signals.csv" --format csv --dry-run --data-dir "$tmpdir/data"
test ! -e "$tmpdir/data"
"$tmpdir/venv/bin/fashion-radar" import-signals "$tmpdir/invalid-signals.csv" --format csv --data-dir "$tmpdir/invalid-data"
test ! -e "$tmpdir/invalid-data"
```

CodeGraph status after implementation:

```text
Files indexed: 78
Total nodes: 948
Total edges: 2455
```

Safety grep results were reviewed. Matches were negative boundary wording only:

- `access-control bypass` exclusions in README, changelog, and source boundary
  docs.
- `cookies` in the manual import privacy boundary saying not to import them.

## Review Questions

Please focus on:

1. Correctness of validate-before-write ordering in CLI and importer APIs.
2. Whether `manual_import` can accidentally enter collector execution.
3. Whether imported rows persist only allowed metadata.
4. Whether duplicate normalized URL behavior is safe and tested.
5. Whether dry-run and invalid-input paths avoid data directory/database
   creation.
6. Whether candidate/report/dashboard/docs wording remains safe and accurate.
7. Whether tests cover the key behavior and privacy boundaries.

## Response Format

Start with one of:

- `Approved for Stage 9 commit and GitHub sync`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before commit.
- `Important:` issues that should be fixed before commit.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
