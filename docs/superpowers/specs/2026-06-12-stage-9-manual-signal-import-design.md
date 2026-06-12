# Stage 9 Manual Signal Import Design

## Goal

Add a safe local import path for user-provided fashion signals from local
CSV/JSON files. The feature lets users bring rows they already have permission
to process into Fashion Radar without adding social-platform scraping,
account automation, browser automation, cookies, proxies, CAPTCHA bypass,
private data collection, paid API requirements, LLMs, or embeddings.

Imported rows become normal local items, so existing entity matching,
candidate discovery, reports, and dashboard views can reuse them.

## Non-Goals

Stage 9 does not implement:

- Platform search or automated collection.
- Crawlers, scrapers, browser automation, Playwright, MCP scraping servers, or
  account automation.
- Login cookies, account/session files, proxy pools, fingerprint evasion,
  CAPTCHA bypass, access-control bypass, paywall bypass, or private data
  collection.
- Official or unofficial APIs for social platforms.
- Engagement scraping or external popularity claims.
- Storage of raw comments, full post bodies, author profiles, account IDs,
  follower lists, images, or videos.

## Recommended Approach

Implement a local importer for normalized CSV/JSON files:

```bash
fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export"
fashion-radar import-signals ./signals.json --format json --source-name "Manual Export"
fashion-radar import-signals ./signals.csv --dry-run
```

The command intentionally writes to the local database when it is not run with
`--dry-run`, unlike `fashion-radar candidates`. It initializes the local schema
only for real imports because dry-run should validate without database writes.

The importer first validates local rows without opening any database path. A
separate storage helper then stores already validated rows as `CollectedItem`
objects using the existing item repository upsert semantics and a new source
type value:

```text
manual_import
```

This is not a collector source. It is a provenance label for rows the user
already has permission to import.

`manual_import` must be rejected in `sources.yaml`. It is import-only and must
not appear in configured source collection, source packs, source health, or
collector run history.

## Input Format

CSV and JSON use the same logical fields.

Required fields:

- `url`
- `title`
- `published_at`

Optional fields:

- `summary`
- `source_name`
- `platform`
- `source_weight`
- `collected_at`

JSON may be either a list of objects or an object with an `items` list.

The command-level `--source-name` is used when a row omits `source_name`.
If both row `source_name` and command `--source-name` are missing, the command
uses `Manual Import`.
An all-whitespace `--source-name` is treated as missing and normalized to
`Manual Import`.

`platform` is accepted only as a short provenance label. It is not stored in a
new schema field, is discarded after validation, and must not be interpreted as
full platform coverage.

`source_weight` defaults to `1.0` and is bounded to the same practical range as
configured sources: greater than `0` and less than or equal to `5`.

`collected_at` defaults to the import run timestamp.

Unknown CSV columns or JSON object keys are ignored. The importer stores only
the fields listed above. This lets users export from varied tools without
committing accidental private fields.

## Privacy And Storage

The importer stores only:

- source name
- source type `manual_import`
- URL
- title
- short summary
- publication timestamp
- source weight
- collection timestamp

It does not store author handles, comments, account IDs, follower counts, raw
engagement counts, full post bodies, images, videos, profile URLs, or cookies.

If users want to preserve a note from their local file, they should put a short
sanitized note in `summary`.

## Validation

Validation is strict and atomic before any write path opens:

- If any row is invalid, the command exits non-zero and writes no rows.
- `--dry-run` validates and reports counts without initializing the database or
  writing rows.
- `url`, `title`, and `published_at` must be non-empty.
- `published_at` and `collected_at` must parse with the existing UTC date
  parser.
- `source_weight` must parse as a number in `(0, 5]`.
- CSV must have headers.
- JSON must be a list of objects or an object with an `items` list.

Atomic validation avoids partial imports when a user provides a malformed file.
Database/runtime failures after validation use the existing per-row upsert
behavior and are not a full transactional batch guarantee in Stage 9.

## Data Flow

```text
CSV/JSON file
  -> parse rows with standard library csv/json
  -> validate into ManualSignalRow objects
  -> open database only after validation succeeds
  -> convert to CollectedItem(source_type=manual_import)
  -> item repository upsert semantics
  -> existing match/report/candidates/dashboard commands
```

The feature does not call the network. It does not read source config files.
It only reads the provided local file and writes to the configured local data
directory.

The local item table keeps one row per normalized URL. If an imported file uses
a URL already in the database, Stage 9 follows existing upsert behavior and
updates that item instead of creating a duplicate. The CLI output reports new
items added separately from rows imported. The new-item count is a local
single-process CLI count intended for normal local use.

## CLI Output

Successful import prints:

```text
Validated N manual signal rows
Imported N manual signal rows
Items added: X
```

Dry run prints:

```text
Validated N manual signal rows
Dry run: no rows imported
```

Invalid files print a concise row-numbered error and exit non-zero.

## Integration With Existing Features

After import, users can run:

```bash
fashion-radar match
fashion-radar report --as-of 2026-06-12T00:00:00Z
fashion-radar candidates --as-of 2026-06-12T00:00:00Z
```

Imported items participate in:

- deterministic entity matching
- entity heat scoring
- candidate discovery
- report representative items
- dashboard mention summaries

The dashboard and reports must continue to frame outputs as configured-source
or imported local signals that need review. They must not claim that imported
rows represent complete platform coverage.

## Files

Create:

- `src/fashion_radar/importers/__init__.py`
- `src/fashion_radar/importers/manual_signals.py`
- `tests/test_manual_signal_import.py`
- `docs/manual-signal-import.md`

Modify:

- `src/fashion_radar/models/source.py`
- `src/fashion_radar/cli.py`
- `README.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/dashboard.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

## Verification

Required verification before Stage 9 code review:

- Focused import parser/workflow/CLI tests.
- Full `pytest`.
- `ruff check .`.
- `ruff format --check .`.
- `uv lock --check`.
- `uv sync --locked --dev --check`.
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`.
- Wheel/sdist build.
- Installed-wheel CLI/resource smoke.
- CodeGraph status.
- Claude Code code review with `--effort max`.
