# Stage 204 Plan Review Prompt

Review the Stage 204 implementation plan in
`docs/superpowers/plans/2026-06-25-stage-204-public-source-pack-composition-contracts-plan.md`.

Goal: turn the optional public fashion source pack's current offline
composition into an explicit test/docs contract: 20 enabled sources, 10 RSS
feeds, 10 bounded GDELT lanes, RSS article extraction disabled by default, and
docs that list both RSS and GDELT inventories in pack order.

Context:

- Stage 197 expanded the optional public source pack with additional public RSS
  feeds.
- Stage 201 normalized several direct RSS endpoints after source-liveness
  planning.
- Stage 203 added release hygiene for mirror-free public lockfiles.
- The current public pack has 10 RSS entries followed by 10 GDELT entries, all
  enabled. Existing tests only loosely require RSS/GDELT presence and minimum
  counts.
- This stage must remain offline and deterministic. It must not run live
  liveness checks as CI/release gates.
- This stage must not add/remove/change sources, RSS URLs, GDELT queries, tags,
  weights, collectors, scoring, reports, dashboard behavior, social/platform
  connectors, scraping, browser automation, source acquisition, demand proof,
  platform coverage verification, compliance-review product features,
  dependency files, `uv.lock`, or `pyproject.toml`.

Please review:

1. Is this a reasonable next core source-quality stage after Stage 203?
2. Are exact composition tests appropriate for the optional public pack, or are
   they too brittle?
3. Should the RSS URL map be expanded to all 10 RSS sources and asserted by
   exact equality?
4. Is the raw YAML boundary test the right way to prove RSS `article.enabled:
   false` and explicit GDELT bounds rather than relying on Pydantic defaults?
5. Is adding a `## RSS Feeds` docs section plus a docs-sync test the right
   minimal docs change?
6. Does the plan avoid live network checks, source expansion, connectors,
   scraping, demand proof, platform coverage verification, dependency changes,
   and compliance-review behavior?
7. Is the verification set sufficient for a test/docs-only source-pack
   contract stage?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
