Approved for Stage 14 release handoff

- `Critical:` None.

- `Important:` None.

- `Minor:`
  - `.gitignore` now covers `.codegraph/`, `.venv/`, local SQLite/data outputs, reports, caches, and build artifacts. It does not explicitly ignore possible token/cookie/session/browser-profile filenames such as `cookies.txt`, `session.json`, `tokens.json`, or browser profile directories. Stage 14 did not add those artifacts or workflows, so this is not blocking, but adding explicit patterns later would further reduce accidental-commit risk.
  - Consider adding accented aliases such as `Alaïa` / `Alaïa Le Teckel` alongside the current ASCII aliases if broader practical matching is desired. The current pack is valid and conservative as-is.
  - Consider adding carefully context-guarded product-form aliases such as `Arcadie bag`, `Le Teckel bag`, or `Puzzle bag` only if they remain specific enough for retained local corpora.

Review summary:

- The Stage 14 implementation matches the approved plan: it adds a static optional entity watchlist pack, docs, tests, and process metadata without changing production runtime behavior.
- `configs/entity-packs/fashion-watchlist.example.yaml` is shaped as a valid `EntityConfig`, and product entries reference existing parent brands.
- The default starter config and packaged init template remain unchanged, with test coverage enforcing equality and the expected small starter entity list.
- `tests/test_entity_packs.py` exercises actual loader and matcher behavior, including generic rejection for broad aliases and contextual/parent-brand acceptance, without assuming universal `context_terms` gating for every multi-word category or trend alias.
- `docs/entity-packs.md` scopes usage to copying the pack, validating with `doctor`, and running local review commands only after signals already exist. It does not introduce `fashion-radar collect`, source-acquisition guidance, platform/community ingestion, scraping, monitoring, ranking, or current-hotness claims.
- Existing README/architecture references to `collect` describe the project’s pre-existing core workflow, not new Stage 14 entity-pack behavior. I did not treat those existing product docs as Stage 14 adding source acquisition or platform/community ingestion.
- No production Python modules, dependencies, lockfiles, DB schema, collectors, reports, dashboard, scoring logic, source packs, or packaged templates appear to have been changed accidentally.
- Generated-file coverage is materially improved with root `.codegraph/` ignore coverage.
