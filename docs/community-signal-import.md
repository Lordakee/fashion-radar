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

Dry-run validation does not create the local SQLite database or import rows.

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
uv run fashion-radar match
uv run fashion-radar report --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Results remain local observed signals from configured sources and imported
local files. They do not prove demand outside the configured source set.

## Boundary

Fashion Radar reads only the local CSV/JSON file passed to `import-signals`.
It does not fetch the URLs in the file, log in to services, download media, or
provide instructions for obtaining platform or community data.

Users are responsible for importing only rows they are authorized to process.
