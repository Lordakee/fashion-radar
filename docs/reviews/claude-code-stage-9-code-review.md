Approved for Stage 9 commit and GitHub sync

- `Critical:` None.

- `Important:` None.

- `Minor:`
  - `src/fashion_radar/importers/manual_signals.py:103-110`: CSV header validation only checks that some header row exists. An empty CSV with non-required headers like `foo,bar\n` would validate as zero rows. Consider requiring CSV headers to include `url`, `title`, and `published_at` even when there are no data rows, so “empty CSV with headers” means valid import headers.
  - `src/fashion_radar/importers/manual_signals.py:124-150`: Duplicate normalized URLs intentionally reuse the existing `ItemRepository.upsert_item()` behavior and are tested, but the semantics overwrite an existing collected item’s source metadata with `manual_import`. This is safe from a duplication/database-integrity perspective and covered by `test_store_manual_signal_rows_preserves_existing_normalized_url_upsert`, but it may be worth documenting that manual imports can update existing normalized URLs rather than creating separate provenance records.
  - `src/fashion_radar/cli.py:358-364`: The import command creates an engine and writes successfully after validation; consider disposing the engine after import for consistency with read-only commands. This is not blocking for correctness.
  - Working tree note: the added Stage 9 files are currently untracked in `git status` (`docs/manual-signal-import.md`, `src/fashion_radar/importers/`, `tests/test_manual_signal_import.py`, plus review docs). Ensure the intended added files are included when committing.

The core safety requirements look satisfied: CLI validation happens before database creation/write, `manual_import` is rejected from configured sources and absent from default collector dispatch, persistence uses only the conservative item fields, dry-run/invalid paths avoid data directory creation, candidate/report/dashboard wording remains bounded, and tests cover the key importer, CLI, config rejection, duplicate URL, and privacy-field behavior.
