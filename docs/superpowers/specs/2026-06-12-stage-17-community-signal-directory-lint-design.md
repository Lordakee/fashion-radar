# Stage 17 Community Signal Directory Lint Design

## Goal

Add a local, read-only directory-level diagnostics command for folders of
community signal CSV/JSON handoff files. This helps external tools controlled by
the user write multiple sanitized files into a local folder and preflight them
in one command before any `import-signals --dry-run` or import step.

Stage 17 improves local batch handoff ergonomics. It does not add collection,
platform connectors, platform search, scraping, browser automation, account
automation, platform APIs, source acquisition, bulk import, background
monitoring, ranking claims, authorization verification, or policy workflow
features.

## Recommended Approach

Extend `src/fashion_radar/community_signals.py` with a small batch wrapper around
the existing single-file linter:

```python
class CommunitySignalDirectoryLintResult(BaseModel): ...

def lint_community_signal_directory(
    directory: Path,
    *,
    input_format: ManualSignalFormat,
    pattern: str,
    default_source_name: str = "Community Signal Import",
) -> CommunitySignalDirectoryLintResult: ...

def render_community_signal_directory_lint_table(
    result: CommunitySignalDirectoryLintResult,
) -> list[str]: ...
```

Add a flat Typer command:

```bash
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv"
fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json"
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --format json
fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json" --strict
```

Command behavior:

- `DIRECTORY` is a local directory path supplied by the user.
- `--input-format csv|json` is required. The command does not infer platform,
  source, semantics, or file type from filenames.
- `--pattern TEXT` is required. Examples are `*.csv` and `*.json`.
- matching is non-recursive in Stage 17.
- only regular files directly under `DIRECTORY` are linted. Implementation
  should enumerate direct children with `directory.iterdir()` and match
  `path.name` with `fnmatch.fnmatch()`, not `Path.glob()`, so patterns such as
  `**/*.csv` cannot recurse.
- paths are sorted deterministically by path string.
- the command reuses `lint_community_signal_file()` for every matched file.
- output is printed before exit handling.
- errors always exit non-zero.
- `--strict` exits non-zero when warnings are present.
- warning-only directories exit zero without `--strict`.
- the command has no `--config-dir`, `--data-dir`, or `--reports-dir`.
- the command does not create config/data/report directories, open SQLite,
  import rows, collect sources, fetch URLs, match entities, score, generate
  reports, package digests, touch dashboard state, or run platform tooling.

## Result Shape

JSON output should be stable:

```json
{
  "directory": "exports",
  "input_format": "csv",
  "pattern": "*.csv",
  "file_count": 2,
  "row_count": 3,
  "valid_row_count": 2,
  "error_count": 1,
  "warning_count": 3,
  "info_count": 2,
  "field_counts": {
    "platform": 2,
    "published_at": 3,
    "source_name": 2,
    "title": 3,
    "url": 3
  },
  "source_name_counts": {
    "Community Tool Export": 2
  },
  "platform_counts": {
    "community": 2
  },
  "files": [
    {
      "path": "exports/a.csv",
      "input_format": "csv",
      "row_count": 2,
      "valid_row_count": 2,
      "field_counts": {},
      "source_name_counts": {},
      "platform_counts": {},
      "findings": []
    }
  ],
  "findings": []
}
```

The `files` entries should be the existing `CommunitySignalLintResult` shape.
The directory-level `findings` list is reserved for directory-level errors or
warnings such as invalid directory or no matching files. Per-file row findings
remain inside the corresponding file result.

Table output should show aggregate summary first, followed by one line per file
and finding details:

```text
Community signal directory: exports
Input format: csv
Pattern: *.csv
Files: 2
Rows: 3 total, 2 import-ready
Fields: platform=2, published_at=3, source_name=2, title=3, url=3
Sources: Community Tool Export=2
Platforms: community=2
Findings: 1 errors, 3 warnings, 2 info
Files:
- exports/a.csv: 2 rows, 2 import-ready, 0 errors, 0 warnings, 0 info
- exports/b.csv: 1 rows, 0 import-ready, 1 errors, 3 warnings, 2 info
Severity | File | Code | Row | Field | Message
error | exports/b.csv | invalid_row | 2 | row | Row is not import-ready: ...
```

## Directory Findings

Errors:

- `invalid_directory`: directory cannot be read or is not a directory.
- `no_matching_files`: pattern matched zero regular files.

Directory-level findings should be sorted deterministically. No recursive
scanning is included in Stage 17, so nested files are ignored rather than
reported.

## Files

Modify:

- `src/fashion_radar/community_signals.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_signal_lint.py`
- `tests/test_cli.py`
- `docs/community-signal-quality.md`
- `docs/community-signal-import.md`
- `README.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`

Process artifacts:

- `docs/superpowers/specs/2026-06-12-stage-17-community-signal-directory-lint-design.md`
- `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`
- `docs/reviews/claude-code-stage-17-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-17-plan-review.md`
- later Stage 17 code review prompts/results.

## Non-Goals

Stage 17 does not implement or document:

- social-platform connectors, platform search, remote community ingestion, or
  automated social collection;
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or source-acquisition
  workflows;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- official or unofficial social platform APIs;
- instructions for obtaining platform/community exports;
- raw comments, full post bodies, private messages, author handles, account IDs,
  follower lists, profile URLs, images, videos, media downloading, reposting, or
  archive redistribution;
- recursive directory scanning, watch folders, background jobs, schedulers, or
  automatic imports;
- multi-file import, multi-file dry-run, DB migrations, collector changes,
  source-health changes, dashboard changes, report semantics changes, matcher
  behavior changes, persistent adapter tables, or scoring algorithm changes;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, authorization verification, policy checklist, or legal review feature.

## Testing

Focused tests should prove:

- directory lint runs existing single-file lint results in deterministic sorted
  path order;
- aggregate counts include file count, row counts, valid row counts,
  severities, field counts, source counts, and platform counts;
- a bad file does not hide clean-file results;
- invalid directory and no matching files are directory-level errors;
- nested files are ignored by non-recursive matching;
- fallback source-name behavior flows through to the existing single-file
  linter;
- table and JSON output shapes are stable;
- CLI help, table output, JSON output, strict mode, warning-only non-strict
  exit behavior, invalid directory behavior, and no-artifact behavior are
  covered.

No test should call the network, run collectors, invoke platform/social tooling,
open SQLite, create config/data/report directories, or require external account
data.

## Documentation

Update `docs/community-signal-quality.md` with a directory batch lint section.
Docs should say batch lint reads matched regular files directly under one local
directory, does not recurse, does not import rows, does not fetch URLs, and does
not verify authorization or platform coverage.

Update `docs/community-signal-import.md`, `README.md`,
`docs/architecture.md`, `docs/source-boundaries.md`, and `CHANGELOG.md` with
short Stage 17 notes.

## Verification

Required before Stage 17 code review:

- focused community-signal lint tests;
- focused CLI tests;
- full `pytest -q`;
- `ruff check .`;
- `ruff format --check .`;
- `git diff --check`;
- CodeGraph status;
- Claude Code code review with `--effort max`.

Post-approval release/upload checks:

- `uv lock --check --default-index https://pypi.org/simple`;
- `uv sync --locked --dev --check --default-index https://pypi.org/simple`;
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`;
- package build;
- installed-wheel smoke checks;
- secret/generated-artifact scans before GitHub upload.
