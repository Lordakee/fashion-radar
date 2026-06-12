Not approved

- `Critical:`
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 4, lines 541-575: release verification still includes `uv lock`, `uv sync`, alternate-index sync, package build, temp venv creation, and wheel install. Even though lines 38-44 correctly label these as development/release operations rather than Stage 14 architecture, Task 4 still makes them part of the plan flow before GitHub upload. This conflicts with the requested static-pack boundary and risks network/dependency/package work outside the Stage 14 implementation scope.
    **Needed change:** Move these commands to a clearly separate “Optional downstream release operations, not part of Stage 14 implementation or acceptance” section, or remove them from the Stage 14 implementation plan. GitHub-upload readiness for this stage should be framed as static repo readiness: pack/docs/tests present, no runtime/dependency/schema/collector changes, default starter unchanged, and wording/source-boundary checks clean.

- `Important:`
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, docs workflow lines 481-489: including `uv run fashion-radar collect` is acceptable only if the docs explicitly say this uses existing configured sources and does not add sources, source acquisition, platform/community ingestion, scraping, social monitoring, or current-hotness detection.
    **Needed change:** Add boundary wording to `docs/entity-packs.md` instructions: “The entity pack only changes local entity matching. `collect` uses only existing configured sources and existing collector behavior.”
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, tests lines 134-182: the broad-alias tests cover good representative cases, but they are not exhaustive over all potentially broad aliases in the proposed pack.
    **Needed change:** Either broaden the test to iterate all aliases and require every single-word/common alias to have `safe_single_word` or `context_terms`, or state the current matcher tests are representative regression coverage for high-risk aliases.
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, test lines 185-193: `assert len(root_config.entities) == 7` is brittle. It matches the current unchanged-starter contract, but it encodes a magic count rather than the actual preservation requirement.
    **Needed change:** Prefer asserting root and packaged templates are identical, plus expected starter entity names/content, or clearly document that the exact seven-entity starter is intentionally frozen for Stage 14.
  - `docs/superpowers/specs/2026-06-12-stage-14-entity-watchlist-pack-design.md`, Files lines 101-108 vs. implementation plan Task 4 lines 523-528: the design names Stage 14 plan-review artifacts, while the implementation plan creates code-review artifacts. This is not conceptually wrong, but it expands the “static pack, tests, docs” stage with process files.
    **Needed change:** Clarify these review files are optional/release-process artifacts, or remove them from implementation scope.

- `Minor:`
  - The overall stage choice is sound: an optional static entity watchlist pack is a reasonable next step after the community import contract because it improves local matching coverage without changing ingestion, scoring, schema, or runtime behavior.
  - Keeping `configs/entities.example.yaml` and the packaged init template unchanged is the right boundary. It preserves the small first-run/smoke-test starter while giving advanced users an explicit opt-in pack.
  - The proposed pack contents are useful as a seed watchlist if the docs keep the current framing: local observation only, not current hotness, market-wide demand, platform-wide ranking, or verified external trend proof.
  - Alias/context/parent-brand strategy is directionally safe for the existing matcher: generic or broad terms such as `Coach`, `Mary Jane`, `boat shoes`, `Margaux`, and `Arcadie` are planned with context terms and/or product parent brands.
  - The wording guard in plan lines 510-520 is good, but reviewers should classify negative boundary matches such as “not a hot-list” or “not a ranking” as allowed rather than treating every match as failure.
  - Add docs guidance for reverting to the starter config after trying the pack, e.g. copy back from `src/fashion_radar/templates/configs/entities.example.yaml` or restore from git, so optionality is obvious.
