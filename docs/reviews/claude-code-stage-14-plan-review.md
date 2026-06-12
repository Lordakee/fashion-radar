Not approved

- `Critical:` None.

- `Important:`
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 1, `test_default_packaged_entity_config_stays_small_and_loadable` lines 131-140: the test is too weak for the stated “default starter config unchanged” boundary. It compares only entity names and length, so aliases, context terms, tags, weights, match confidence, and active windows could change undetected. Change this to compare the full validated config/model dump for the root and packaged `entities.example.yaml`, while still asserting the expected small starter count if desired.
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 1 broad-alias test lines 122-129 and proposed YAML around lines 233-237, 277-301, 332-363: matcher safety coverage is structural, not behavioral. Checking that `context_terms` exist does not prove the existing matcher rejects generic prose or accepts parent-brand/narrow-context mentions. Add focused matcher tests using the existing matching system for cases such as plain “coach” as a person, “Mary Jane” as a name, generic “boat shoes” prose, and single-product aliases like `Margaux`/`Arcadie`, plus positive cases with parent brand or narrow fashion context.
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 3 workflow commands lines 428-436: the design requires docs for existing `collect`, `import-signals`, `match`, `report`, `candidates`, and `trends` commands, but the plan omits a `candidates` command example. Add the existing safe candidate-discovery CLI command to the docs plan.
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 4 lines 507-529: commit/push is not part of the Stage 14 entity-pack architecture or acceptance criteria and introduces process risk. Make commit/push explicitly conditional on separate user authorization in the implementation session, or move it out of the implementation plan.

- `Minor:`
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 2 YAML line 208: change “ASCII form of Alaa” to “ASCII form of Alaïa.”
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 1 lines 122-129: make the broad-alias test explicitly assert that the alias `Mary Janes` exists and is protected, not only that the `Mary Jane Shoes` entity has context terms.
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 3 wording guard lines 456-465: clarify that negative boundary wording such as “not a hot-list/ranking” is expected and allowed, so implementers do not treat every `rg` hit as a failure.
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 4 installed-wheel smoke lines 489-495: provide exact commands and include relevant existing CLI help checks from outside the source checkout.
