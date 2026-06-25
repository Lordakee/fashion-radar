# Stage 198 Plan Review Prompt

Review the Stage 198 plan:

`docs/superpowers/plans/2026-06-25-stage-198-deterministic-entity-watchlist-coverage-plan.md`

Context:

- The user wants a free-first fashion-intelligence tool that can evolve toward
  daily fashion news, celebrity style, designer brands, emerging labels, hot
  products, bags, shoes, and heat-change analysis.
- Current active review engine is local OpenCode with
  `zhipuai-coding-plan/glm-5.2 --variant max`.
- Recent full-project reviews redirected the project toward curated public
  source coverage using liveness evidence and deterministic matching quality.
- Stage 197 expanded the optional public source pack. Stage 198 should improve
  deterministic matching quality only.
- The user explicitly does not want compliance-review product features.
- Social/Xiaohongshu/Instagram/TikTok/X connectors remain future opt-in
  surfaces and must not be implemented in this stage.

Plan intent:

- Update only the optional `configs/entity-packs/fashion-watchlist.example.yaml`
  and its synthetic local sample workflow.
- Add two emerging designer brands (`Savette`, `Aeyde`) and two
  parent-brand-gated products (`Savette Symmetry Bag`,
  `Aeyde Uma Mary Jane`).
- Preserve the compact starter entity config and packaged template unchanged.
- Preserve local-only matching boundaries: no sources, scraping, connectors,
  platform APIs, ranking, demand proof, platform coverage verification, or
  compliance-review features.

Review questions:

1. Does the plan close a real core product gap in the collect -> match -> report
   pipeline without expanding frozen external/community/imported surfaces?
2. Are the four planned entities reasonable and precise under the current
   matcher semantics?
3. Are product aliases sufficiently guarded by `parent_brand` and
   `context_terms`, and does the plan avoid risky bare aliases such as
   `Symmetry` or `Uma`?
4. Are the planned tests sufficient for entity presence, parent-brand product
   safety, broad-alias rejection, sample workflow row counts, docs parity, and
   local-only boundaries?
5. Does the plan correctly regenerate `docs/entity-pack-quality.md` from lint
   output instead of hardcoding stale counts?
6. Does the plan preserve dependency/lockfile/mirror and review-artifact hygiene
   rules?
7. Are there Critical or Important fixes required before implementation?

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Concrete fixes required before implementation
