# Stage 197 Plan Review Prompt

Review the Stage 197 plan:

`docs/superpowers/plans/2026-06-25-stage-197-public-rss-pack-expansion-plan.md`

Context:

- The user wants continuous development toward a free fashion-intelligence
  tool, but the core must avoid social/platform scraping/connectors for now.
- Current roadmap focus is curated public-source coverage using source-liveness
  evidence and deterministic matching quality.
- The default `configs/sources.example.yaml` should remain compact; this stage
  targets only the optional broader public source pack.
- Public RSS candidates were checked during planning on 2026-06-25. Live
  source-liveness should remain advisory and non-blocking.

Review questions:

1. Does the plan improve the core collect -> match -> report product direction
   without expanding frozen external/community/imported surfaces?
2. Are the chosen RSS feeds and tags reasonable for a small optional public-pack
   expansion?
3. Does the plan preserve source-boundary constraints: no social scraping,
   browser automation, platform APIs, access bypass, demand proof, source
   ranking, platform coverage verification, or compliance-review product
   features?
4. Are docs and tests sufficient, especially `docs/source-packs.md`,
   `docs/source-pack-quality.md`, and source-pack docs guards?
5. Is live liveness correctly treated as advisory rather than release-blocking?
6. Are there Critical or Important fixes required before implementation?

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Concrete fixes required before implementation
