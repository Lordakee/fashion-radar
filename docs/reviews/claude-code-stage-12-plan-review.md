Not approved

- `Critical:` None.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`, Task 3 / Task 6 / Acceptance Criteria: strengthen the read-only boundary tests for `source-pack-lint`. The architecture correctly says the command must not create config/data/report directories or SQLite files, but the planned CLI test is named only `test_source_pack_lint_does_not_create_data_or_report_dirs`, and the installed-wheel smoke only checks `test ! -e "$tmpdir/data"`. Add explicit assertions that the command does not create:
  - default config directories,
  - default reports directories,
  - any `fashion-radar.sqlite` or other `*.sqlite*` files,
  - any collector/report artifacts.

  This matters because the Stage 12 boundary is specifically “local lint only,” and GitHub-ready tests should prove the CLI path cannot accidentally exercise the existing workflow paths that call `create_sqlite_engine()`, `initialize_schema()`, or directory creation.

- `Important:` `docs/superpowers/specs/2026-06-12-stage-12-source-pack-quality-design.md`, Non-Goals, and `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`, Scope Guard: mirror the full explicit out-of-scope list more completely. The current guard covers the main risky areas, but it omits or compresses several explicit exclusions from the review prompt, including:
  - official or unofficial social platform APIs,
  - platform search/export instructions,
  - raw comments, full post bodies, DMs, account IDs, follower lists, images, videos, downloads, reposting,
  - LLM scoring, embeddings, vector databases, image recognition, and paid-service requirements.

  The proposed implementation does not appear to add these, but the plan should make the boundary unambiguous before implementation and docs work begin.

- `Minor:` `src/fashion_radar/source_packs.py` planned boundary is appropriate. Keeping strict schema validation in `settings.py` / `load_source_config()` and putting advisory diagnostics in a new pure `source_packs.py` module is the right separation. It avoids turning schema validation into style/lint policy while still reusing the canonical config loader.

- `Minor:` Reading raw YAML before `load_source_config()` is justified. Pydantic defaults erase whether fields such as `weight` were omitted, so raw YAML inspection is necessary for `implicit_weight`. The plan should include a small implementation comment noting that raw YAML is intentionally read before typed validation for omitted-field diagnostics.

- `Minor:` Duplicate source names should remain errors. Existing collection/reporting code is source-identity oriented, and duplicate names would make source-keyed health/run-log interpretation ambiguous. The planned case/space normalization is appropriate.

- `Minor:` Duplicate RSS/RSSHub targets and duplicate GDELT queries as warnings are appropriate. They can double-count signals, but they may sometimes be intentional lane overlap or temporary experimentation, so warning-by-default plus `--strict` is a good balance.

- `Minor:` Missing tags as warnings are appropriate. Tags improve interpretation and tuning but should not make a structurally valid local pack unusable.

- `Minor:` The flat Typer command is the right interface. `fashion-radar source-pack-lint PATH` fits the existing CLI style better than introducing a nested command group for one diagnostic.

- `Minor:` The bounded GDELT public-pack expansion is reasonable. Adding configured GDELT lanes with `lookback_hours: 24`, `max_records: 100`, and `rate_limit_per_second: 1.0` improves starter-pack coverage without adding new source types, new live RSS endpoints, scraping, social extraction, or network behavior during linting.

- `Minor:` Consider making duplicate finding output deterministic and complete by reporting every member of a collision group, not only the second occurrence. This makes CI output easier to understand when three or more sources share a normalized name, URL, or query.

- `Minor:` In the URL normalization tests, include examples for lowercased scheme/host, stripped fragment, and trailing slash trimming. If query strings are preserved, document that choice so users understand when two feed URLs are considered distinct.

- `Minor:` For `article_extraction_enabled`, keep it informational only and make docs clear that it is a local-pack quality reminder, not a compliance/policy check and not a runtime fetch.
