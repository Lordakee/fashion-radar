Approved for Stage 9 commit and GitHub sync

- `Critical:` None.

- `Important:` None.

- `Minor:`
  - The new `ManualSignalRow.normalize_published_at()` behavior correctly rejects `None` and blank values before calling `parse_datetime_utc()`, so JSON `published_at: null` and short CSV rows with a missing `published_at` cell now become Pydantic validation failures and are wrapped by `load_manual_signal_rows()` as `ManualSignalImportError("row ...")`.
  - The `TypeError` conversion in both `published_at` and `collected_at` validators is appropriate. It preserves valid string/datetime parsing, keeps optional `collected_at` semantics intact (`None`/blank still means absent), and prevents raw `dateutil` `TypeError` from escaping the importer wrapper.
  - The CLI still validates before opening the write path: `load_manual_signal_rows()` runs before `create_sqlite_engine(default_database_path(data_dir))`, and `create_sqlite_engine()` is the code path that creates the data directory. The new CLI regression test covers the key invalid JSON path and asserts no traceback, no data directory, and no SQLite database.
  - I did not find unintended side effects on valid CSV/JSON imports, source weight defaulting/validation, source name fallback/override behavior, or collected-at defaulting.
  - Stage 9 remains within the local-only safety boundary. The implementation adds a local CSV/JSON importer only; I did not find platform collection, scraping/browser automation, social API integration, credential/session handling, export-acquisition instructions, private/raw field persistence, or overbroad social-listening claims in the reviewed changes.
  - Optional cleanup only: importer CLI errors currently include Pydantic’s full validation text after `row N`; if desired later, those could be shortened for readability, but the current behavior is clean, non-tracebacking, and acceptable.
