# Stage 190 Code Review

## Critical

No critical findings. The implementation satisfies the approved Stage 190 goal:
read-only `source-liveness` probing is correctly scoped, network probes are
bounded to enabled RSS/RSSHub/GDELT sources, disabled sources are skipped
without network calls, schema-invalid disabled sources surface as
`invalid_config`, RSS bytes are parsed via `BytesIO` so `feedparser` cannot
dereference path/URL strings, GDELT uses `GDELT_DOC_API` +
`gdelt_http_settings(source)` + `timespan=<lookback_hours>h` + `maxrecords=1`,
the CLI prints before evaluating the exit code, and tests inject fake clients
with a module-level `FashionHttpClient` guard.

## Important

No important findings. All focused verification commands pass
(`tests/test_source_liveness.py` + `tests/test_cli.py`: 37 passed;
docs tests: 82 passed; full suite: 1428 passed; ruff check/format clean;
release hygiene clean; `git diff --check` clean). Exit semantics match the
spec: errors exit 1, warnings exit 1 only with `--strict`, and invalid
`--format` values are rejected by Typer's `Literal` choice parsing before the
builder is invoked (`src/fashion_radar/cli.py:652-668`,
`tests/test_cli.py:9349`).

## Minor

- `docs/source-packs.md:45-60` — The new `## Check Source Liveness` section is
  inserted directly between the `source-pack-lint --format json` command
  (line 42) and the unqualified `Example JSON shape:` heading (line 60). The
  JSON block that follows is the `source-pack-lint` shape (no
  `contract_version`/`execution_mode`/`probed_count`/`live_count`), but because
  the liveness `--format json` example (line 53) now immediately precedes it, a
  reader may assume it documents `source-liveness` output. Consider relocating
  the liveness section after the existing JSON-shape block, or relabeling the
  heading to `Example source-pack-lint JSON shape:`.

- `src/fashion_radar/source_liveness.py:539-541` — `_record_label` duplicates
  the logic of `lint_formatting.format_count_label`
  (`src/fashion_radar/lint_formatting.py:4-6`). Reusing the shared helper would
  keep pluralization behavior consistent across modules.

## Verdict

Approve. Stage 190 is read-only, boundary-correct, and fully tested with no
live network access. The two Minor items are documentation/DRY polish and do
not block the stage.
