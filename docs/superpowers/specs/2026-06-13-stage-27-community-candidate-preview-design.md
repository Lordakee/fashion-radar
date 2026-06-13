# Stage 27A Community Candidate Preview Design

## Goal

Add `fashion-radar community-candidates`, a local read-only command that previews
aggregate candidate phrases from one user-supplied community signal CSV/JSON
handoff file before import.

The command helps an external local tool validate its sanitized Fashion Radar
handoff file by answering: "which untracked candidate phrases would this one
file surface if I imported it?"

## Stage Boundary

Stage 27A is implementation plus focused tests only:

- add the in-memory preview module;
- add the CLI command;
- add module and CLI tests;
- update no broad user docs in this node;
- do not commit or push in this node.

Docs updates, final release verification, Claude Code code review, commit, and
push belong to follow-up nodes after Stage 27A implementation is reviewed.

## Scope

The command reads exactly one local file supplied by the user and local config
from `--config-dir`. It does not:

- recurse through directories;
- watch folders;
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
local observations from the supplied file only.

## Command

```text
fashion-radar community-candidates PATH [OPTIONS]
```

Options:

- `PATH`: local CSV/JSON handoff file. The value is used only for reading and is
  never emitted in JSON or table output.
- `--input-format [csv|json]`: format selector, default `csv`.
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
2. The command parses `--as-of` before loading config or reading the input file.
3. The command loads scoring config and optional entity config before reading
   the input file.
4. Only after valid `--as-of` and valid config does the command read the input
   file.

## Data Flow

1. CLI parses `--as-of` and loads local scoring/entity config.
2. The preview helper loads rows through `load_manual_signal_rows()` so CSV/JSON
   row validation matches the manual import path.
3. Rows missing `collected_at` use the requested `as_of` value as their preview
   collected timestamp. This mirrors importing at that timestamp.
4. Candidate text is built from `title` and sanitized `summary`.
5. Candidate extraction uses `extract_candidate_phrases()` with configured
   entity keys from `entities.yaml` so config-known names are suppressed.
6. Stored SQLite matches are intentionally not consulted because this is a
   pre-import file preview that never opens SQLite. Entities known only through
   stored DB matches may still appear.
7. Each row contributes at most one mention per candidate normalized key.
8. Mentions are filtered to
   `baseline_window_start < collected_at <= as_of`.
9. Candidate groups are filtered with existing candidate discovery thresholds:
   review minimum current mentions, review minimum distinct current sources, and
   single-token minimums.
10. Scores use weighted current mentions, source diversity bonus, and growth
    bonus.
11. Results are sorted by score descending, current mentions descending,
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
row_count
candidate_count
limit
candidates
```

Candidate row keys:

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

`candidate_count` is the pre-limit candidate count. With `--limit 0`, `candidates`
is empty while `candidate_count` and `row_count` are preserved.

The command intentionally does not output local file paths, row titles, URLs,
summaries, raw text, private fields, normalized keys, candidate contexts, source
files, import paths, account fields, or representative item details. The output
is aggregate only.

Table output follows the same boundary. It does not print `PATH` or any source
file/import path.

`label` uses a small local preview vocabulary:

- `new`: current mentions exist and baseline mentions are zero.
- `rising`: current and baseline mentions exist and growth ratio meets
  `candidate_discovery.rising_growth_ratio`.
- `observed`: current mentions pass review thresholds but do not meet the
  previous labels.

## Error Handling

- Invalid `--as-of`: exit `1`; no config load or file read.
- Invalid `--input-format`: Typer exits before command body; no config load or
  file read.
- Negative `--limit`: Typer exits before command body; no config load or file
  read.
- Invalid config: exit `1`; no input file read.
- Invalid file path, format, or row shape: exit `1` with a clean generic
  community-candidate error. CLI output must not echo the supplied local file
  path.
- `candidate_discovery.enabled: false`: returns zero candidates while still
  reporting validated row count.

## Tests

Stage 27A implementation tests must cover:

- current and baseline windows from one local CSV fixture;
- rows without `collected_at` use `as_of`;
- configured entity names are suppressed;
- source-name fallback and blank fallback are normalized;
- each row contributes one mention per candidate normalized key;
- review thresholds filter candidates;
- single-token thresholds filter candidates;
- `candidate_discovery.enabled: false` returns row count with zero candidates;
- `limit=0` preserves pre-limit `candidate_count` and `row_count`;
- recursive JSON string checks prevent leaking URLs, titles, summaries, raw
  text, normalized keys, contexts, source paths, and representative item fields;
- table output does not leak the same forbidden values;
- table rendering sanitizes pipes and newlines;
- CLI help lists `community-candidates`;
- CLI JSON output has stable keys;
- CLI table output is readable;
- invalid `--as-of`, invalid `--input-format`, and negative `--limit` do not
  read the file;
- invalid config does not read the file and exits cleanly;
- invalid input file exits cleanly without traceback or local path echo;
- command does not create data, report, SQLite, or dashboard artifacts.
