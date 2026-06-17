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
- [examples/community-tool-handoff.example.csv](../examples/community-tool-handoff.example.csv)
- [examples/community-tool-handoff.example.json](../examples/community-tool-handoff.example.json)
- [examples/community-tool-handoff-directory.example/README.md](../examples/community-tool-handoff-directory.example/README.md)
- [examples/community-tool-handoff-directory.example/csv/community-tool-a.csv](../examples/community-tool-handoff-directory.example/csv/community-tool-a.csv)
- [examples/community-tool-handoff-directory.example/csv/community-tool-b.csv](../examples/community-tool-handoff-directory.example/csv/community-tool-b.csv)
- [examples/community-tool-handoff-directory.example/json/community-tool-a.json](../examples/community-tool-handoff-directory.example/json/community-tool-a.json)
- [examples/community-tool-handoff-directory.example/json/community-tool-b.json](../examples/community-tool-handoff-directory.example/json/community-tool-b.json)
- `schemas/community-signals.schema.json`

The single-file examples are importable templates. The directory examples show
a local CSV/JSON export directory layout; their child CSV/JSON files are
importable handoff samples. The schema documents the strict JSON handoff
contract for tools that can validate JSON before writing a file for Fashion
Radar.

JSON producers can validate against `schemas/community-signals.schema.json`.
CSV producers should emit only the same allowed columns because JSON Schema does
not validate CSV. The runtime importer may ignore unknown fields for
backward-compatible manual imports, but this community contract asks external
tools to omit unknown, raw, private, media, account, cookie, session, and token
fields.

Use `community-signal-lint` or `community-signal-lint-dir` when you want
Fashion Radar to enforce the strict community handoff contract before
dry-run/import. Use `community-handoff-check-dir` when you want one local-only
handoff readiness report before import.
Use `external-tool-adapters` when a local upstream producer needs the
external social/community tool adapter registry and local producer-discovery
registry before choosing a sanitized CSV/JSON local file handoff shape.
Use `external-tool-template` when a local upstream producer needs
adapter-specific template rows for a sanitized CSV/JSON local file handoff
shape before writing its own export file.

## External Tool Handoff Templates

The external tool handoff templates are sanitized CSV/JSON local file handoff
templates for user-controlled external/community tools:
[examples/community-tool-handoff.example.csv](../examples/community-tool-handoff.example.csv)
and
[examples/community-tool-handoff.example.json](../examples/community-tool-handoff.example.json).
They are example file shapes for a user-controlled external tool to write
locally before Fashion Radar lint, preview, dry-run, import, and review steps.
They are not platform collection and do not add connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, source acquisition, demand
proof, ranking, or coverage verification.

## External Tool Export Directory Examples

The external community tool export directory examples are sanitized CSV/JSON
local export directory examples for user-controlled external/community tools:
[examples/community-tool-handoff-directory.example/README.md](../examples/community-tool-handoff-directory.example/README.md),
[examples/community-tool-handoff-directory.example/csv/community-tool-a.csv](../examples/community-tool-handoff-directory.example/csv/community-tool-a.csv),
[examples/community-tool-handoff-directory.example/csv/community-tool-b.csv](../examples/community-tool-handoff-directory.example/csv/community-tool-b.csv),
[examples/community-tool-handoff-directory.example/json/community-tool-a.json](../examples/community-tool-handoff-directory.example/json/community-tool-a.json),
and
[examples/community-tool-handoff-directory.example/json/community-tool-b.json](../examples/community-tool-handoff-directory.example/json/community-tool-b.json).
The checked-in `csv/` and `json/` directories are separate non-recursive
examples because each directory command takes one input format and one matched
filename pattern per run. Machine-readable `directory_example_paths` carries
these directory-layout pointers in `community-signal-profile --format json` and
`community-handoff-manifest --format json`, while `example_paths` remains the
single-file import examples.

```bash
uv run fashion-radar community-signal-lint-dir examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --strict
uv run fashion-radar import-signals-dir examples/community-tool-handoff-directory.example/json --format json --pattern "*.json" --source-name "External Community Tool" --data-dir "$PWD/data" --dry-run --output-format json
```

They are not platform collection and do not add connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, source acquisition, demand
proof, ranking, or coverage verification.

## External Tool Adapter Registry

`external-tool-adapters` prints the external social/community tool adapter
registry. It is a local producer-discovery registry for user-controlled
external/community tools that already produce sanitized CSV/JSON local file
handoff rows or need copyable commands for that handoff.

```bash
uv run fashion-radar external-tool-adapters --format table
uv run fashion-radar external-tool-adapters --format json
```

The registry describes built-in producer categories such as Rednote/Xiaohongshu
exports, Instaloader, TikTok-Api, yt-dlp metadata exports, X search exports, and
generic community exports. Each entry maps to the existing community signal
fields, a local provenance `platform` label, a suggested `source_name`, a
recommended CSV/JSON pattern, and the same local profile, manifest, workflow,
lint, readiness, dry-run, import, and review commands used elsewhere in this
guide.

The command is local and print-only. It does not run adapters, inspect
directories, read handoff files, validate files, import rows, open SQLite, or
create artifacts. It is not platform collection and has no connectors, no
scraping, no browser automation, no platform APIs, no monitoring, no
scheduling, no source acquisition, no demand proof, no ranking, and no
coverage verification.

## External Tool Template Rows

`external-tool-template` prints adapter-specific template rows for
user-controlled external/community tools that need sanitized CSV/JSON local
file handoff examples. JSON and CSV output are importable community handoff
rows only; table output may include local metadata, field mappings, boundaries,
and copyable local commands.

```bash
uv run fashion-radar external-tool-template --adapter instaloader --format table
uv run fashion-radar external-tool-template --adapter instaloader --format json
uv run fashion-radar external-tool-template --adapter instaloader --format csv
```

Omit `--adapter` to print two synthetic rows for every known adapter. The rows
use only the community handoff fields `url`, `title`, `published_at`,
`summary`, `source_name`, `platform`, `source_weight`, and `collected_at`.
They do not include raw/private/account/media/cookie/session/token fields.

The command is local and print-only. It does not write files, run adapters,
inspect directories, read handoff files, validate files, import rows, open
SQLite, or create artifacts. It is not platform collection and has no
connectors, no scraping, no browser automation, no platform APIs, no
monitoring, no scheduling, no source acquisition, no demand proof, no ranking,
and no coverage verification.

## Producer Profile

External user-controlled tools can print the local producer contract before
writing handoff files:

```bash
uv run fashion-radar community-signal-profile
uv run fashion-radar community-signal-profile --format json
```

The profile includes the contract version, supported input formats, canonical
CSV header, required fields, optional fields, allowed fields, excluded fields,
accepted JSON envelope shapes, field notes, source-weight bounds,
`directory_example_paths`, unsupported capabilities, and the recommended local
lint/preview/dry-run/import/review command sequence. A checked-in example is
available at
`examples/community-signal-profile.example.json`. It prints the contract only
and does not read handoff files or directories, create config/data/report
directories, open SQLite, fetch URLs, search platforms, log in, store cookies,
automate browsers, call platform APIs, monitor communities, rank sources,
verify platform coverage, perform source acquisition, or provide a
compliance-review workflow.

The JSON profile's `recommended_commands` list is the exact producer-facing
sequence. Prose examples in this guide may add `uv run` and temporary paths for
source-checkout smoke tests, but they should preserve the same lint, preview,
dry-run import, import, and review order. The profile recommendations remain
producer-facing and do not include `community-handoff-check-dir`;
`community-handoff-workflow` adds `review_handoff_readiness` when printing the
local operator sequence with a local-only handoff readiness report before
importing rows.

## Directory Manifest

External user-controlled tools that write a directory of community handoff
files can print a local directory manifest before creating export files:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar community-handoff-manifest ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
```

Print JSON when an external tool needs a stable machine-readable manifest:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar community-handoff-manifest ./exports --input-format json --pattern "*.json" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
```

Example JSON fields:

```json
{
  "contract_version": "community-handoff-manifest/v1",
  "execution_mode": "print_only",
  "directory": "./exports",
  "input_format": "json",
  "pattern": "*.json",
  "producer_profile_command": "fashion-radar community-signal-profile --format json",
  "producer_contract_version": "community-signals/v1",
  "supported_input_formats": ["csv", "json"],
  "suggested_filename": "community-signals.json",
  "matched_file_rule": "Downstream lint, preview, and import commands treat matching regular files directly under the supplied directory as handoff files; they do not recurse into subdirectories.",
  "manifest_storage_note": "Do not save this manifest as a matched handoff file. For example, when using --pattern \"*.json\", do not save the manifest as a .json file inside the handoff directory; save it outside the directory or use an excluded filename/pattern.",
  "schema_path": "schemas/community-signals.schema.json",
  "example_paths": [
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "examples/community-tool-handoff.example.csv",
    "examples/community-tool-handoff.example.json"
  ],
  "directory_example_paths": [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json"
  ],
  "required_fields": ["url", "title", "published_at"],
  "optional_fields": ["summary", "source_name", "platform", "source_weight", "collected_at"],
  "prohibited_fields": [
    "account_id",
    "author_handle",
    "cookie",
    "direct_message",
    "follower_count",
    "full_post_body",
    "image_url",
    "profile_url",
    "raw_comment",
    "session",
    "token",
    "video_url"
  ],
  "workflow": {
    "execution_mode": "print_only",
    "step_count": 6,
    "steps": [
      {
        "order": 1,
        "name": "lint_handoff_directory",
        "command": "fashion-radar community-signal-lint-dir ./exports --input-format json --pattern \"*.json\" --source-name \"Community Tool Export\" --strict",
        "suggested_effect": "read_only"
      },
      {
        "order": 2,
        "name": "preview_candidate_phrases",
        "command": "fashion-radar community-candidates-dir ./exports --input-format json --pattern \"*.json\" --config-dir ./configs --as-of 2026-06-13T12:00:00+00:00 --source-name \"Community Tool Export\"",
        "suggested_effect": "read_only"
      },
      {
        "order": 3,
        "name": "review_handoff_readiness",
        "command": "fashion-radar community-handoff-check-dir ./exports --input-format json --pattern \"*.json\" --config-dir ./configs --as-of 2026-06-13T12:00:00+00:00 --source-name \"Community Tool Export\" --strict",
        "suggested_effect": "read_only"
      },
      {
        "order": 4,
        "name": "dry_run_directory_import",
        "command": "fashion-radar import-signals-dir ./exports --format json --pattern \"*.json\" --data-dir ./data --source-name \"Community Tool Export\" --imported-at 2026-06-13T12:00:00+00:00 --dry-run",
        "suggested_effect": "read_only"
      },
      {
        "order": 5,
        "name": "import_directory_signals",
        "command": "fashion-radar import-signals-dir ./exports --format json --pattern \"*.json\" --data-dir ./data --source-name \"Community Tool Export\" --imported-at 2026-06-13T12:00:00+00:00",
        "suggested_effect": "updates_local_imports"
      },
      {
        "order": 6,
        "name": "print_post_import_review",
        "command": "fashion-radar imported-review-workflow --config-dir ./configs --data-dir ./data --as-of 2026-06-13T12:00:00+00:00 --source-name \"Community Tool Export\"",
        "suggested_effect": "print_only"
      }
    ]
  }
}
```

The manifest describes the target directory, matched file pattern, suggested
filename (`community-signals.csv` or `community-signals.json`), producer profile
fields and pointers, schema/example paths, `directory_example_paths`, field
notes and rules, prohibited fields, unsupported capabilities, storage guidance,
and workflow commands. The workflow includes `review_handoff_readiness`, which
prints the `community-handoff-check-dir` local-only handoff readiness report
before importing rows. It is local and print-only: it does not execute commands,
read the supplied directory, validate files, import rows, open SQLite, create
artifacts, fetch URLs, log in, call platform APIs, monitor communities,
schedule work, add source/platform connectors, prove demand, verify platform
coverage, or rank sources.

Do not save this manifest as a matched handoff file. If saved, keep it outside the matched export directory or use an excluded filename/pattern, especially
for JSON export directories using `--pattern "*.json"`. Otherwise
`community-signal-lint-dir`, `community-candidates-dir`, or
`import-signals-dir` may treat the manifest JSON as a signal file.

## Required Fields

- `url`: source URL or stable reference URL for the observed item.
- `title`: short observed text, headline, or normalized signal phrase.
- `published_at`: ISO 8601-compatible publication or observation timestamp.

## Optional Fields

- `summary`: short sanitized note for local review.
- `source_name`: display name for the external tool or local file.
- `platform`: short local provenance label. When present, it is preserved on
  retained `manual_import` rows in SQLite and may appear in imported review
  output. It is not platform coverage, source acquisition, demand proof, or a
  claim of complete platform/community visibility.
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

Check a local directory of files produced by another tool. For a deterministic
repository sample, create a temporary export directory from the checked-in CSV
first:

```bash
AS_OF="2026-06-13T12:00:00Z"
tmp_run="$(mktemp -d)"
mkdir -p "$tmp_run/exports"
cp examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"
uv run fashion-radar community-signal-lint-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --source-name "Community Tool Export" --strict
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
```

Continuing from the same temporary export directory, print a copyable directory
handoff workflow without running it:

```bash
uv run fashion-radar community-handoff-manifest "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar community-handoff-workflow "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
```

`community-handoff-manifest` prints a producer-facing manifest for the supplied
directory, pattern, suggested filename, profile/schema/example pointers,
`directory_example_paths`, storage note, and workflow command list. It does not
read the directory or execute any workflow step.

`community-handoff-workflow` prints the local sequence
`community-signal-lint-dir`, `community-candidates-dir`,
`community-handoff-check-dir`, `import-signals-dir --dry-run`,
`import-signals-dir`, and `imported-review-workflow`. Its named workflow steps
are `lint_handoff_directory`, `preview_candidate_phrases`,
`review_handoff_readiness`, `dry_run_directory_import`,
`import_directory_signals`, and `print_post_import_review`. The
`review_handoff_readiness` step prints the `community-handoff-check-dir`
local-only handoff readiness report before importing rows. It does not execute
commands, read the supplied directory, validate files, import rows, open or
write SQLite, fetch URLs, log in, download media, automate browsers, scrape,
monitor, watch folders, schedule work, add source/platform connectors, prove
demand, verify platform coverage, rank sources, write reports, update
dashboards, generate configs, or generate entity files. It intentionally prints
the supplied directory/config/data paths inside copyable local commands, unlike
aggregate candidate preview output.

Run one aggregate local readiness report for the same deterministic temporary
export directory before import:

```bash
uv run fashion-radar community-handoff-check-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
```

For your own JSON export directory, use the same local review timestamp:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar community-handoff-check-dir ./exports --input-format json --pattern "*.json" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
```

`community-handoff-check-dir` is a local-only handoff readiness report for
user-controlled community signal directories. It reads only matched local
regular files and local config. It does not import rows, uses no SQLite,
creates no config/data/report/dashboard/digest artifacts, and has no fetch URLs/login/platform
APIs/download media/browser automation/scrape/crawl/monitor/watch/schedule/connectors/source
acquisition/demand proof/ranking/coverage verification/entity generation/compliance/policy/
authorization/safety-review features.

Preview aggregate candidate phrases from the checked-in sample before import:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
```

For your own local JSON handoff file, use your current review timestamp:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar community-candidates ./community-signals.json --input-format json --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
```

`community-candidates` reads one local handoff file and local config, then
prints aggregate-only candidate phrase metrics before import. It does not
import rows, open SQLite, recurse directories, fetch URLs, or expose the
supplied input file path, row URLs, row titles, summaries, raw text, normalized
keys, candidate contexts, or representative item details.

Continuing from the deterministic temporary export directory, preview aggregate
candidate phrases from a local directory batch before import:

```bash
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
```

For your own JSON export directory, use a timestamp for the local review run:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar community-candidates-dir ./exports --input-format json --pattern "*.json" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
```

`community-candidates-dir` reads matched regular files directly under one local
directory and local config, then prints aggregate-only candidate phrase metrics
before import. It does not recurse, import rows, open SQLite, fetch URLs, print
the supplied directory path, expose matched file paths, expose matched file
names, or expose row URLs, row titles, summaries, raw text, normalized keys,
candidate contexts, raw validation findings, account/private fields, or
representative item details.

Then validate the same deterministic temporary export directory through the
importer model without writing rows:

```bash
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
```

For your own JSON export directory, dry-run through the same importer model:

```bash
uv run fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run --output-format json
```

After the importer-model dry run succeeds, import the same deterministic
temporary export directory:

```bash
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
```

For your own JSON export directory, pass the timestamp you want stored on the
imported rows:

```bash
IMPORTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --source-name "Community Tool Export" --imported-at "$IMPORTED_AT" --data-dir "$PWD/data"
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

Use `community-handoff-workflow` when you want Fashion Radar to print that
directory order without running any step. It may print supplied
directory/config/data paths because its output is a copyable local checklist;
that is different from `community-candidates-dir`, which suppresses paths and
row details in aggregate preview output. The order includes
`review_handoff_readiness`, the `community-handoff-check-dir` local-only
handoff readiness report before importing rows, and the workflow does not
execute commands.

See [community-signal-quality.md](community-signal-quality.md).

## Dry Run

Validate the repository examples without writing rows:

```bash
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals examples/community-signals.example.json --format json --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
```

Validate a local file produced by another tool:

```bash
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
```

Dry-run validation uses the same parser/import model as the write path. It does
not create the local SQLite database or import rows.

## Import

After a dry run succeeds, import the checked-in sample or a local file:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data"
```

JSON imports use the same command with `--format json`:

```bash
uv run fashion-radar import-signals ./community-signals.json --format json --source-name "Community Tool Export" --imported-at "2026-06-12T12:00:00Z" --data-dir "$PWD/data"
```

Imported rows use the existing manual-import storage path. If a row's normalized
URL already exists in the local database, the existing item upsert behavior
applies.
Accepted `platform` values follow the same manual-import storage path as local
provenance metadata only; they do not create connectors, acquire sources, prove
demand, or establish platform/community coverage.

## Review After Import

Run the normal local review workflow after importing:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --phrase "Le Teckel bag"
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --phrase "Le Teckel bag" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --unmatched-only
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$AS_OF"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar heat-movers --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF"
```

Retained-row review commands can be narrowed with `--source-name`,
`--lookback-days`, and `--limit` where supported. Entity-delta review uses
`--current-days`, `--baseline-days`, and `--entity-type` where supported. Use
`--format json` when you need machine-readable output.

`imported-review-workflow` prints a copyable sequence for existing local review
commands after import. The workflow includes a read-only imported-candidates
step for candidate phrase review and still ends with the final read-only
heat-movers step for local observed heat movement from configured sources and
imported local signals. Those review outputs need review and provide no demand
proof and no platform coverage verification. The workflow does not execute
those commands, open SQLite, read configs, import rows, run matching, score
signals, generate reports, or create artifacts.

`imported-signals-summary` reads the same retained local rows and groups counts
by stored `source_name`. Stored `platform` values, when present, are local
provenance labels for review output only.

`imported-entity-deltas` reads retained local rows with stored matches and
compares aggregate entity counts across collected-at windows.

`imported-candidates` reads retained local rows and surfaces observed candidate
phrases from `manual_import` rows only. It is local and read-only, and the
phrases need review before any entity config change.

`imported-candidate-evidence` reads retained local rows and shows the local
evidence rows behind one requested candidate phrase. It is local and read-only.

`imported-signals` reads retained imported rows from local SQLite only and may
show stored `platform` provenance labels from imported rows. It does not import
rows, run matching/scoring, generate reports, fetch URLs, monitor directories,
acquire source files, or infer platform/community coverage.

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

`community-handoff-workflow` does not execute commands, read the supplied
directory, validate files, import rows, open or write SQLite, fetch URLs, log in,
download media, automate browsers, scrape, monitor, watch folders, schedule work,
add source/platform connectors, prove demand, verify platform coverage, rank
sources, write reports, update dashboards, generate configs, or generate entity
files. It only prints copyable local commands and may echo supplied
directory/config/data paths inside those commands. Its
`review_handoff_readiness` step is the `community-handoff-check-dir`
local-only handoff readiness report before importing rows.

`community-handoff-check-dir` is a local-only handoff readiness report. It
reads only matched local regular files and local config. It does not import
rows, uses no SQLite, creates no config/data/report/dashboard/digest artifacts,
and has no fetch URLs/login/platform APIs/download media/browser automation/scrape/crawl/monitor/
watch/schedule/connectors/source acquisition/demand proof/ranking/coverage verification/entity
generation/compliance/policy/authorization/safety-review features.

`community-candidates-dir` reads only matched regular files directly under the
local directory passed to it plus local config. It does not recurse, import
rows, open SQLite, fetch URLs, log in, download media, expose matched file paths
or matched file names, expose account/private fields, or provide instructions
for obtaining platform/community data.

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
