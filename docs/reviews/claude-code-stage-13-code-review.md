Approved for Stage 13 commit/push

- `Critical:` None.
- `Important:` None.
- `Minor:`
  - `tests/test_community_signal_import_contract.py:48` checks the schema shape but does not validate the example JSON against the schema with a JSON Schema validator. This is acceptable for Stage 13 because no JSON Schema dependency was added and the static assertions cover the approved contract requirements, but a future dev-only schema validation check could catch malformed schema/example drift more directly.
  - `.gitignore` appears to ignore generated data/report/build/cache artifacts under the expected project paths, but the review environment did not allow `git status`/`git ls-files` without approval, so I could not independently confirm the exact staged/untracked set. Before commit, run `git status --short` and ensure only the Stage 13 source/docs/test/example/schema/review files are staged.

Review summary:

- The implementation matches the approved Stage 13 design: it adds docs, importable examples, a strict static JSON schema, and focused tests around the existing `import-signals`/`load_manual_signal_rows()` path.
- No production Python module, collector, source model, DB schema, dashboard, report renderer, dependency declaration, lockfile, or source pack change was observed in the reviewed files.
- The schema/runtime distinction is clear:
  - `schemas/community-signals.schema.json` is strict for external JSON producers (`additionalProperties: false`, required `url`/`title`/`published_at`, `(0, 5]` `source_weight`).
  - Runtime importer remains backward-compatible with `ManualSignalRow.model_config = ConfigDict(extra="ignore")`.
- CSV and JSON examples use only the allowed public contract fields and load through the real manual importer.
- Dry-run tests cover both examples through the Typer CLI and assert no config/data/report dirs, SQLite files, report files, latest artifacts, or report index are created.
- Docs consistently frame community import as a local sanitized handoff contract, not a connector, scraper, platform acquisition guide, compliance workflow, or social monitoring system.
- Reviewed docs avoid platform-wide/market-wide/verified-demand/top-social-trend claims except as negative boundary language.
- No token, cookie, credential, session/account artifact, SQLite DB, build artifact, `.venv`, `.codegraph`, or generated report content was found in the reviewed Stage 13 files.
