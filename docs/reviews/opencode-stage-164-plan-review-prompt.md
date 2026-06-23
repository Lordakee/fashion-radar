# Stage 164 Plan Review Prompt

Review the Stage 164 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 164 Plan Review
```

Objective:

Make human-readable lint table finding-count labels consistent across
source-pack, entity-pack, and community-signal lint surfaces.

Read these files:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-164-cross-lint-finding-count-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-164-cross-lint-finding-count-grammar-plan.md`
- `src/fashion_radar/source_packs.py`
- `src/fashion_radar/entity_packs.py`
- `src/fashion_radar/community_signals.py`
- `tests/test_source_packs.py`
- `tests/test_entity_pack_lint.py`
- `tests/test_community_signal_lint.py`
- `docs/community-signal-quality.md`

Review questions:

1. Is Stage 164 correctly scoped to human-readable lint finding-count labels?
2. Is moving the Stage 162 source-pack helper into a shared internal
   `lint_formatting.py` module appropriate, or should this stage keep local
   helpers?
3. Do the planned RED tests prove the entity/community singular-count gaps
   while preserving plural/non-one wording?
4. Does the plan cover community-signal directory aggregate and per-file
   finding-count output without drifting into row-count grammar?
5. Are verification, docs, code-review, release-review, release-hygiene,
   commit, and push steps complete enough?
6. Are there any critical or important findings before implementation?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
