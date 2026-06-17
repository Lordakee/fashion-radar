Review these two Stage 65 planning files in /home/ubuntu/fashion-radar:

- docs/superpowers/specs/2026-06-17-stage-65-imported-entity-evidence-design.md
- docs/superpowers/plans/2026-06-17-stage-65-imported-entity-evidence-plan.md

Context:
- Stage 65 adds `fashion-radar imported-entity-evidence`.
- The command must be local, read-only, and imported-only.
- It should query retained `manual_import` rows joined to stored
  `item_entities` matches for one exact `entity_name` and `entity_type`.
- It must use the same current/baseline collected-at windows as
  `imported-entity-deltas`.
- It must deduplicate duplicate stored matches by item id.
- Output must be privacy-safe: no raw summaries, full post bodies, raw comments,
  handles, profile URLs, media URLs, account IDs, source file paths, match
  aliases, confidence, reasons, or context terms.
- It must not add scraping, browser automation, platform APIs, account/cookie
  behavior, media downloads, monitoring, scheduling, source acquisition, demand
  proof, ranking, coverage verification, schema migration, dashboard browser,
  or compliance-review product features.

Check only for Critical or Important issues before coding:
1. Objective/scope mismatch.
2. A test or implementation instruction that is clearly impossible against the
   existing repo patterns.
3. Missing boundary coverage that could allow platform collection, raw-data
   leakage, write side effects, or scoring/ranking confusion.
4. Contract ambiguity likely to break implementation, docs, smoke, or package
   checks.

Return exactly:
- Verdict: APPROVED FOR STAGE 65 IMPLEMENTATION or CHANGES REQUIRED
- Critical:
- Important:
- Minor:
- Rationale:
