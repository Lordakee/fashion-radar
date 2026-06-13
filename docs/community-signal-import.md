# Community Signal Import

Community signal import is a local handoff contract for sanitized CSV/JSON rows
created by tools the user controls. It uses the existing
`fashion-radar import-signals` command and stores accepted rows as
`manual_import`.

This is a template layer over manual signal import. It is not a connector,
source-acquisition guide, platform collector, account workflow, or monitoring
service.

## Contract Files

- `examples/community-signals.example.csv`
- `examples/community-signals.example.json`
- `schemas/community-signals.schema.json`

The examples are importable templates. The schema documents the strict JSON
handoff contract for tools that can validate JSON before writing a file for
Fashion Radar.

JSON producers can validate against `schemas/community-signals.schema.json`.
CSV producers should emit only the same allowed columns because JSON Schema does
not validate CSV. The runtime importer may ignore unknown fields for
backward-compatible manual imports, but this community contract asks external
tools to omit unknown, raw, private, media, account, cookie, session, and token
fields.

Use `community-signal-lint` or `community-signal-lint-dir` when you want
Fashion Radar to enforce the strict community handoff contract before
dry-run/import.

## Required Fields

- `url`: source URL or stable reference URL for the observed item.
- `title`: short observed text, headline, or normalized signal phrase.
- `published_at`: ISO 8601-compatible publication or observation timestamp.

## Optional Fields

- `summary`: short sanitized note for local review.
- `source_name`: display name for the external tool or local file.
- `platform`: short provenance label. It is not stored as platform coverage and
  does not imply complete visibility.
- `source_weight`: local score weight in `(0, 5]`.
- `collected_at`: timestamp for when the external tool produced the row.

Do not include raw comments, full post bodies, private messages, author handles,
account IDs, follower lists, profile URLs, images, videos, cookies, sessions,
tokens, or other account/private material in community import files. Keep
context in `summary` short and sanitized.

## Preflight Lint

Check repository examples without importing rows:

```bash
uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-signal-lint examples/community-signals.example.json --input-format json --source-name "Community Tool Export"
```

Check a local file produced by another tool:

```bash
uv run fashion-radar community-signal-lint ./community-signals.csv --input-format csv --source-name "Community Tool Export" --strict
```

Check a local directory of files produced by another tool:

```bash
uv run fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --source-name "Community Tool Export" --strict
uv run fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json" --source-name "Community Tool Export" --strict
```

Then validate the same local directory through the importer model without
writing rows:

```bash
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --dry-run
uv run fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --source-name "Community Tool Export" --dry-run --output-format json
```

After the importer-model dry run succeeds, import the same local directory:

```bash
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data"
uv run fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --source-name "Community Tool Export" --imported-at "2026-06-12T12:00:00Z" --data-dir "$PWD/data"
```

The linters validate allowed columns/fields, excluded raw/private fields,
import-readiness, duplicate URLs, missing provenance, and implicit defaults.
`community-signal-lint` reads one local file. `community-signal-lint-dir` reads
matched regular files directly under one local directory and does not recurse.
They do not create config/data/report directories, open SQLite, import rows,
fetch URLs, collect sources, verify authorization, provide platform/community
data acquisition steps, or run matching/scoring.

`import-signals-dir --dry-run` is the importer-model directory check. It reads
matched regular files directly under one local directory, does not recurse, and
does not open SQLite or import rows. It is less strict than
`community-signal-lint-dir` because the manual importer remains
backward-compatible with extra columns. Use the same `--source-name` across
lint, directory dry run, and import when you want source summaries to align.
`import-signals-dir` without `--dry-run` imports only after every matched local
file validates; a validation failure imports nothing.

See [community-signal-quality.md](community-signal-quality.md).

## Dry Run

Validate the repository examples without writing rows:

```bash
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --dry-run
uv run fashion-radar import-signals examples/community-signals.example.json --format json --source-name "Community Tool Export" --dry-run
```

Validate a local file produced by another tool:

```bash
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export" --dry-run
```

Dry-run validation uses the same parser/import model as the write path. It does
not create the local SQLite database or import rows.

## Import

After a dry run succeeds, import the local file:

```bash
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export"
```

JSON imports use the same command with `--format json`:

```bash
uv run fashion-radar import-signals ./community-signals.json --format json --source-name "Community Tool Export"
```

Imported rows use the existing manual-import storage path. If a row's normalized
URL already exists in the local database, the existing item upsert behavior
applies.

## Review After Import

Run the normal local review workflow after importing:

```bash
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export" --unmatched-only
uv run fashion-radar match
uv run fashion-radar report --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

`imported-signals-summary` reads the same retained local rows and groups counts
by stored `source_name`.

`imported-signals` reads retained imported rows from local SQLite only. It does
not import rows, run matching/scoring, generate reports, fetch URLs, monitor
directories, or infer platform/community coverage.

Results remain local observed signals from configured sources and imported
local files. They do not prove demand outside the configured source set.

## Boundary

Fashion Radar reads only the local CSV/JSON file passed to `import-signals`.
It does not fetch the URLs in the file, log in to services, download media, or
provide instructions for obtaining platform or community data.

`community-signal-lint` reads only the local CSV/JSON file passed to it.
`community-signal-lint-dir` reads only matched regular files directly under the
local directory passed to it. They report contract findings. They do not fetch
URLs, log in, recurse, download media, verify authorization, or provide
instructions for obtaining platform/community data.

`import-signals-dir --dry-run` reads only matched regular files directly under
the local directory passed to it and validates them through the importer model.
It does not fetch URLs, log in, recurse, download media, open SQLite, import
rows, verify authorization, or provide instructions for obtaining
platform/community data.

`imported-signals` opens an existing local SQLite database in read-only mode and
reviews retained `manual_import` rows. It does not acquire source files, fetch
URLs, run matching/scoring, write reports, or create dashboard/report
artifacts.

Users are responsible for importing only rows they are authorized to process.
