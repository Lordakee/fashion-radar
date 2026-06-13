# Stage 28 Community Candidate Directory Preview Design

## Goal

Add `fashion-radar community-candidates-dir`, a local read-only command that
previews aggregate candidate phrases from a non-recursive directory of
user-supplied community signal CSV/JSON handoff files before import.

The command helps an external local community tool validate a batch export by
answering: "which untracked candidate phrases would this local batch surface if
I imported it?"

## Stage Boundary

Stage 28 is implementation plus focused tests only:

- add directory preview support to the existing in-memory community candidate
  preview module;
- add the CLI command;
- add module and CLI tests;
- update no broad user docs in this node;
- do not commit or push in this node.

Docs updates, final release verification, Claude Code code review, commit, and
push belong to follow-up nodes after Stage 28 implementation is reviewed.

## Scope

The command reads regular files directly under one supplied local directory,
using a user-supplied glob pattern. It also reads local config from
`--config-dir`. It does not:

- recurse through subdirectories;
- watch folders;
- schedule scans;
- fetch URLs;
- call platform APIs;
- log in to services;
- download media;
- import rows;
- open or write SQLite;
- write config, data, report, or dashboard artifacts;
- generate entity YAML;
- create candidate approval state.

The preview is not proof of demand or broad platform visibility. Counts are
local observations from the supplied files only.

## Command

```text
fashion-radar community-candidates-dir DIRECTORY [OPTIONS]
```

Options:

- `DIRECTORY`: local directory containing sanitized CSV/JSON handoff files.
  The value is used only for reading and is never emitted in JSON or table
  output.
- `--input-format [csv|json]`: format selector, default `csv`.
- `--pattern TEXT`: direct-child filename glob, default `*.csv`.
- `--config-dir PATH`: existing config directory.
- `--as-of TEXT`: required UTC preview timestamp.
- `--source-name TEXT`: fallback source name for rows that omit `source_name`,
  default `Community Tool Export`.
- `--limit INTEGER`: maximum candidates to print, default `50`, minimum `0`.
- `--format [table|json]`: output format, default `table`.

Blank `--source-name` is normalized to `Community Tool Export`.

Validation order:

1. Typer rejects invalid `--input-format` and negative `--limit` before the
   command body runs.
2. The command parses `--as-of` before loading config or reading the directory.
3. The command loads scoring config and optional entity config before reading
   the directory.
4. Only after valid `--as-of` and valid config does the command read directory
   children and matched files.

## Data Flow

1. CLI parses `--as-of` and loads local scoring/entity config.
2. The directory preview helper loads rows through
   `load_manual_signal_directory_rows()` so CSV/JSON row validation and
   non-recursive direct-child file matching reuse the manual import path.
3. The helper treats any directory-level or file-level load error as a failed
   preview and raises a generic `ManualSignalImportError` that does not include
   directory paths, file paths, file names, row values, or raw diagnostics.
4. Rows missing `collected_at` use the requested `as_of` value as their preview
   collected timestamp. This mirrors importing at that timestamp.
5. Candidate text is built from `title` and sanitized `summary`.
6. Candidate extraction uses `extract_candidate_phrases()` with configured
   entity keys from `entities.yaml` so config-known names are suppressed.
7. Stored SQLite matches are intentionally not consulted because this is a
   pre-import directory preview that never opens SQLite. Entities known only
   through stored DB matches may still appear.
8. Each row contributes at most one mention per candidate normalized key.
9. Mentions are filtered to
   `baseline_window_start < collected_at <= as_of`.
10. Candidate groups are filtered with existing candidate discovery thresholds:
    review minimum current mentions, review minimum distinct current sources,
    and single-token minimums.
11. Scores use weighted current mentions, source diversity bonus, and growth
    bonus.
12. Results are sorted by score descending, current mentions descending,
    distinct sources descending, then phrase.

## Output Model

Top-level JSON keys:

```text
input_format
as_of
current_window_start
baseline_window_start
current_days
baseline_days
source_name
file_count
row_count
candidate_count
limit
candidates
```

Candidate row keys match `community-candidates`:

```text
phrase
candidate_type
label
score
current_mentions
baseline_mentions
distinct_sources
growth_ratio
first_seen_at
```

`candidate_count` is the pre-limit candidate count. With `--limit 0`,
`candidates` is empty while `candidate_count`, `file_count`, and `row_count` are
preserved.

The command intentionally does not output local directory paths, file paths,
file names, row URLs, row titles, summaries, raw text, private fields,
normalized keys, candidate contexts, source files, import paths, account fields,
representative item details, or raw validation findings. The output is
aggregate only.

Table output follows the same boundary. It does not print `DIRECTORY`, matched
file paths, matched file names, or the pattern.

## Error Handling

- Invalid `--as-of`: exit `1`; no config load or directory read.
- Invalid `--input-format`: Typer exits before command body; no config load or
  directory read.
- Negative `--limit`: Typer exits before command body; no config load or
  directory read.
- Invalid config: exit `1`; no directory read.
- Invalid directory, no matching files, invalid file, or invalid row: exit `1`
  with a clean generic community-candidate-directory error. CLI output must not
  echo the supplied local directory path, matched file names, row values, raw
  validation diagnostics, or traceback.
- `candidate_discovery.enabled: false`: returns zero candidates while still
  reporting validated file and row counts.

## Tests

Stage 28 implementation tests must cover:

- current and baseline windows aggregated across multiple direct-child files;
- direct child matching only, with nested files ignored;
- `--pattern` selecting regular files without recursive traversal;
- rows without `collected_at` use `as_of`;
- configured entity names are suppressed;
- source-name fallback and blank fallback are normalized;
- each row contributes one mention per candidate normalized key;
- review thresholds and single-token thresholds filter candidates;
- `candidate_discovery.enabled: false` returns file and row counts with zero
  candidates;
- `limit=0` preserves pre-limit `candidate_count`, `file_count`, and
  `row_count`;
- JSON and table output do not leak directory paths, file paths, file names,
  row URLs, row titles, summaries, raw text, normalized keys, contexts, source
  paths, raw validation findings, or representative item fields;
- CLI help lists `community-candidates-dir`;
- CLI JSON output has stable keys;
- CLI table output is readable and aggregate-only;
- invalid `--as-of`, invalid `--input-format`, and negative `--limit` do not
  read the directory;
- invalid config does not read the directory and exits cleanly;
- invalid directory, no matching files, and invalid file content exit cleanly
  without traceback, paths, filenames, or row-value echoes;
- command does not create data, report, SQLite, or dashboard artifacts.
