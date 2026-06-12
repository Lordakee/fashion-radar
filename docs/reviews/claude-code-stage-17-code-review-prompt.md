# Claude Code Stage 17 Code Review Prompt

You are reviewing `/home/ubuntu/fashion-radar` in read-only mode. Do not edit
files. Use maximum reasoning.

## Goal

Stage 17 adds a local, read-only directory batch diagnostics command:

```bash
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv"
fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json" --format json
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --strict
```

The command should lint multiple already-sanitized, user-provided local
community signal CSV/JSON handoff files in one directory before any single-file
`import-signals --dry-run` or import step.

## Architecture And Tech Stack

- Python 3.11+, Typer CLI, Pydantic v2, pytest, ruff.
- No new dependencies and no lockfile changes.
- `src/fashion_radar/community_signals.py` adds:
  - `CommunitySignalDirectoryLintResult`
  - `lint_community_signal_directory(...)`
  - `render_community_signal_directory_lint_table(...)`
- Directory lint is a wrapper around existing `lint_community_signal_file()`.
  It must not duplicate row parsing/validation.
- File matching must be non-recursive:
  - enumerate `directory.iterdir()`
  - filter `path.is_file()`
  - match `fnmatch.fnmatch(path.name, pattern)`
  - sort by `str(path)`
- `Path.glob()` / `rglob()` must not be used for matching because `**/*.csv`
  must not recurse.
- CLI adds a flat `community-signal-lint-dir` command near
  `community-signal-lint`.
- Directory JSON output must serialize aggregate fields:
  - `directory`
  - `input_format`
  - `pattern`
  - `file_count`
  - `row_count`
  - `valid_row_count`
  - `error_count`
  - `warning_count`
  - `info_count`
  - `field_counts`
  - `source_name_counts`
  - `platform_counts`
  - `files`
  - `findings`
- Top-level directory `findings` are only directory-level findings. Per-file
  findings stay in each `files[]` entry.
- CLI must print table/JSON before exit handling.
- CLI exit logic must use aggregate `result.error_count` and
  `result.warning_count`, not only top-level `result.findings`.

## Scope Guard

This stage must remain local-only and read-only. It must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, MCP platform
  scraping servers, platform APIs, account automation, login cookies, browser
  profiles, proxies, CAPTCHA/rate-limit/access-control bypass, or source export
  acquisition instructions;
- collectors, source types, background jobs, watch folders, schedulers, multi-file
  import, multi-file dry-run, SQLite writes, migrations, matching/scoring/report
  changes, dashboard changes, or digest changes;
- product-facing compliance/audit/approval/policy workflow features.

## Files To Review

Production:

- `src/fashion_radar/community_signals.py`
- `src/fashion_radar/cli.py`

Tests:

- `tests/test_community_signal_lint.py`
- `tests/test_cli.py`

Docs:

- `docs/community-signal-quality.md`
- `docs/community-signal-import.md`
- `README.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`

Planning/review artifacts:

- `docs/superpowers/specs/2026-06-12-stage-17-community-signal-directory-lint-design.md`
- `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`
- `docs/reviews/claude-code-stage-17-plan-review*.md`
- `docs/reviews/claude-code-stage-17-plan-rereview*.md`
- this prompt and the resulting review file.

## Verification Already Run

```text
.venv/bin/python -m pytest tests/test_community_signal_lint.py -q -k directory_lint
10 passed, 13 deselected

.venv/bin/python -m pytest tests/test_cli.py -q -k community_signal_lint_dir
12 passed, 68 deselected

.venv/bin/python -m pytest tests/test_community_signal_lint.py tests/test_cli.py -q -k "community_signal_lint_dir or directory_lint"
22 passed, 81 deselected

git diff --check
exit 0

.venv/bin/python -m pytest -q
366 passed

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
78 files already formatted

codegraph status
Files indexed: 92; Total nodes: 1457; Total edges: 3907
```

Docs boundary scan was also run:

```bash
rg -n "community-signal-lint-dir|platform-wide|market-wide|current-hotness|source acquisition|source-acquisition|platform search|social monitoring|exports|ranking|demand proof|compliance|audit|authorization" README.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md CHANGELOG.md
```

Hits should be reviewed as command examples or explicit negative/boundary
contexts only.

## Review Request

Please review the current working-tree diff, not just committed code:

```bash
git diff -- src/fashion_radar/community_signals.py src/fashion_radar/cli.py tests/test_community_signal_lint.py tests/test_cli.py docs/community-signal-quality.md docs/community-signal-import.md README.md docs/architecture.md docs/source-boundaries.md CHANGELOG.md
```

Find issues by severity:

- Critical: correctness, data loss, non-local side effects, security/secrets,
  scope violations, or broken command behavior.
- Important: missing required tests, unstable JSON shape, wrong exit behavior,
  recursive matching, docs that could mislead users, deterministic ordering
  issues, or no-artifact gaps.
- Minor: wording, maintainability, or polish.

Explicitly answer:

1. Does the implementation preserve non-recursive direct-child matching?
2. Does invalid/unreadable directory handling return stable directory-level
   findings without tracebacks?
3. Does no-match return `no_matching_files` as an error?
4. Do aggregate severity counts include per-file findings?
5. Does CLI strict/non-strict exit behavior match the plan?
6. Do tests cover JSON success and failure shape, sorted file order, warning-only
   behavior, and no-artifact behavior?
7. Do docs avoid adding social/platform acquisition, scraping, account
   automation, platform coverage, authorization verification, compliance/audit,
   or policy workflow product features?
8. Is the code ready for release checks, commit, and push after fixing any
   Critical/Important findings?

## Next Stage Plan After Approval

If you approve Stage 17 code:

1. Run release checks:
   - `uv lock --check --default-index https://pypi.org/simple`
   - `uv sync --locked --dev --check --default-index https://pypi.org/simple`
   - `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
   - `uv build --out-dir /tmp/fashion-radar-dist-stage17`
   - installed-wheel smoke for `fashion-radar community-signal-lint-dir --help`
     and one JSON run from a temporary venv, installing via the Tsinghua mirror.
2. Run secret and generated-artifact scans.
3. Ensure the Git remote URL remains token-free.
4. Commit as `Add community signal directory diagnostics`.
5. Push to `origin main`, using only a temporary `GIT_ASKPASS` if credentials are
   needed, then delete it.

Please return an approval status plus findings. Do not modify files.
