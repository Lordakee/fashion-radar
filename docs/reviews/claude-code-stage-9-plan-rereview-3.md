Approved for Stage 9 implementation

- `Critical:` None.

- `Important:` None.

- `Minor:`
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 4: Consider clarifying write atomicity. The plan guarantees all validation happens before opening the database and prevents validation-error partial imports, which satisfies the stated goal. However, `store_manual_signal_rows()` uses `ItemRepository.upsert_item()` row-by-row, each in its own transaction. If a database/runtime failure occurs mid-store, prior rows may remain. Either explicitly document that "atomic" means validation atomicity only, or add a repository/batch transaction helper if full write atomicity is desired.
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 3: Add one test for an empty-but-headered CSV file, e.g. `url,title,published_at\n`, to lock down whether zero-row imports are allowed and what count is printed.
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 3: Add one test for malformed CSV rows with extra cells, since `csv.DictReader` can emit a `None` key for overflow columns. This would ensure accidental pasted/exported fields are either ignored safely or reported clearly.
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 3 / Task 5: Consider normalizing `default_source_name` inside `load_manual_signal_rows()` as defensive behavior, not only in the CLI. The CLI requirement is precise, but direct importer use in tests or future code could otherwise pass whitespace.
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 5: Add a CLI test for JSON import, not just CSV. Parser tests cover JSON, but a CLI-level JSON smoke test would protect Typer option wiring and output behavior.
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 5: The dry-run semantics are precise and correctly require parsing `--imported-at`, validating rows, and returning before engine/schema initialization. The proposed tests directly assert no `data_dir` creation for dry-run, invalid input, invalid timestamp, and unsupported format.
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 6: Safe wording is strong. One optional addition is to explicitly ban "instructions for obtaining exports from social platforms" in `docs/manual-signal-import.md`, matching the review prompt's out-of-scope list. The current plan says local user-provided files and no platform collection, which is safe, but this would make the boundary harder to regress.
  - `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 7: Verification is sufficient before code review and publication. The wheel smoke test is especially useful because it checks `import-signals --help`, dry-run no-directory creation, and invalid-file no-directory creation from an installed package.
