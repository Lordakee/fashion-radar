Approved for Stage 14 implementation

- `Critical:` None.

- `Important:`
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 3 / docs command examples: the proposed copy command writes the pack to repo-local `configs/entities.yaml`, but the shown CLI commands do not pass `--config-dir "$PWD/configs"` or set `FASHION_RADAR_CONFIG_DIR`. Existing CLI defaults use the platform user config directory, so `uv run fashion-radar doctor`, `match`, `report`, `candidates`, and `trends` may validate or use a different user config instead of the copied watchlist pack. Update the plan/docs examples to explicitly target the config directory that receives the pack, for example:
    ```bash
    cp configs/entity-packs/fashion-watchlist.example.yaml configs/entities.yaml
    uv run fashion-radar doctor --config-dir "$PWD/configs"
    ```
    and likewise include `--config-dir "$PWD/configs"` on the workflow commands, or instruct users to export:
    ```bash
    export FASHION_RADAR_CONFIG_DIR="$PWD/configs"
    ```
    before running the commands.

- `Minor:`
  - The optional entity watchlist pack is the right next stage after the community import contract: it broadens local matching coverage without adding new source acquisition, connector, collector, scoring, report, dashboard, or DB behavior.
  - Keeping the default starter config unchanged is the right boundary. The small starter remains useful for smoke tests and first runs, while the broader pack stays opt-in.
  - The proposed pack contents are useful as a seed watchlist as long as docs and YAML comments continue to frame it as a configurable local watchlist, not a hot-list, ranking, current-hotness claim, platform-wide signal, or market-wide demand proof.
  - The alias/context/parent-brand plan is aligned with the existing matcher: `EntityConfig.validate_aliases()` already validates unsafe single/common aliases and `parent_brand` references, while `evaluate_entity_matches()` already applies context gates for products with `parent_brand`, single-word aliases, and unsafe/common aliases. The plan correctly warns that `context_terms` are not universal phrase-level disambiguation for all multi-word category/trend aliases.
  - The proposed tests cover the right core areas: loading through `load_entity_config()`, type mix, expected examples, parent-brand references, broad alias protection, generic false-positive rejection, positive matching with parent/fashion context, and unchanged packaged starter config.
  - In `docs/entity-packs.md`, keep the negative boundary language immediately beside `match`, `report`, `candidates`, and `trends` examples so users do not infer that the pack adds collection, source setup, scraping, social/platform monitoring, source acquisition, or ranking semantics.
  - Keep `docs/reviews/` prompts/outputs and staged review files clearly labeled as process metadata, not product/runtime behavior or package functionality.
  - Verification is sufficient for GitHub upload after the Important config-dir docs fix: focused entity-pack tests, full pytest, ruff check, ruff format check, git diff check, CodeGraph status, and max-effort Claude Code review are appropriate for this static YAML/docs/tests stage.
