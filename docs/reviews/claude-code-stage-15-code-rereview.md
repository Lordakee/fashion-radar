Approved for Stage 15 upload

- `Critical:` None.
- `Important:` None.
- `Minor:` None.

The previous Important finding is resolved: `README.md:174-177` now accurately distinguishes single-word/common aliases from ordinary multi-word aliases and matches the current matcher behavior documented and implemented in `entity_packs.py`.

The prior Minor wording issues are also resolved without introducing new problems:

- `docs/entity-pack-quality.md:3-4` now correctly frames `entity-pack-lint` as checking YAML before using it in matching workflows, not as participating in matching.
- `README.md:153-158` now explicitly says the dashboard’s `Trend Deltas` local SQLite read does not create trend tables or write database state.

I did not run verification commands per the read-only/no-execution constraints, but the reported post-fix results are sufficient and consistent with the reviewed changes.
