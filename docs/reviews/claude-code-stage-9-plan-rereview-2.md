Not approved

- `Critical:` None.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 6 / Files list: the plan does not include the actual user-facing report/dashboard wording that currently says candidate signals are from "configured sources." Existing code has hardcoded wording in `src/fashion_radar/reports.py` (`_render_candidate_sections`) and `src/fashion_radar/dashboard/app.py` candidate-tab caption. Because Stage 9 imports local manual rows into the same item store, those outputs would become inaccurate after import. Add explicit implementation and tests/docs checks to update this wording to "configured sources and imported local signals" or equivalent safe phrasing that does not imply complete platform coverage.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 4 tests: the storage tests do not directly verify the key normalized-URL upsert requirement. Add a test where an imported row has the same normalized URL as an existing item, verifying no duplicate row is created, `items_added` reflects only net new items, and the existing upsert semantics are preserved.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 5 CLI tests: `test_import_signals_command_imports_csv` only checks CLI output. Add assertions that the SQLite database was created only for the real import and that the stored item has `source_type == "manual_import"`, the expected `source_name`, sanitized fields, and no private/extra metadata. Otherwise the CLI wiring could regress while the lower-level storage test still passes.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 3 parser tests: the public JSON interface says JSON may be either a list of objects or an object with an `items` list, but the positive tests only cover the `{"items": [...]}` shape. Add a positive JSON top-level-list test to drive that supported format.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 4/5: the plan says Stage 9 must not create source health or collector run history records, but there is no explicit regression test for that. Add a storage or CLI import test that inspects `collector_runs` and `source_health` after import and verifies they remain empty.

- `Minor:` `docs/superpowers/specs/2026-06-12-stage-9-manual-signal-import-design.md`, Privacy And Storage: the phrase "platform export" is not an instruction for obtaining platform exports, but it is close to the out-of-scope boundary. Safer wording would be "If users want to preserve a note from their local file, they should put a short sanitized note in `summary`."

- `Minor:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 5: clarify whether `--dry-run --imported-at not-a-date` should fail. The current implementation sketch parses `--imported-at` before dry-run even though dry-run does not use the import timestamp. Either document that all CLI options are validated during dry-run, or skip timestamp parsing until the real import path.

- `Minor:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 3: add a test for unsupported `--format`/`input_format` behavior or rely explicitly on Typer/Literal validation. This is not central, but it would make the parser/CLI contract clearer.
