# Stage 204 Plan Review

## Verdict

No Critical findings. No Important findings. The plan is accurate, well-scoped,
and consistent with the project's contract-first, offline, deterministic
conventions. Implementation may proceed after the non-blocking minor notes.

## Critical

None.

## Important

None.

## Verification Performed

- The planned `EXPECTED_PUBLIC_SOURCE_COMPOSITION` matches
  `configs/source-packs/fashion-public.example.yaml`: 10 RSS sources followed by
  10 GDELT sources in the same names, order, and types.
- The planned 10-entry `CANONICAL_PUBLIC_RSS_URLS` map matches all current RSS
  `url` values in the YAML.
- The raw YAML boundary assertions hold for the current file: every RSS source
  has `article.enabled: false`, `url`, and no `query`; every GDELT source has
  `query`, no `url`, and explicit `lookback_hours: 24`, `max_records: 100`, and
  `rate_limit_per_second: 1.0`.
- `SourcePackLintResult` exposes `error_count`, `warning_count`, and
  `info_count`; `type_counts` is sorted and will be `{"gdelt": 10, "rss": 10}`.
- The docs helpers can parse a new `## RSS Feeds` section placed before
  `## Check Pack Quality` when each bullet contains exactly one backticked
  source name.

## Question-By-Question Findings

1. Reasonable next stage after Stage 203: yes. Stage 204 hardens the optional
   public source-pack content contract before later matching/report work.

2. Exact composition tests: appropriate. This public pack is a curated,
   reviewable baseline, so add/remove/rename/reorder changes should force a
   deliberate contract update.

3. Expanding RSS URL map to all 10 sources and asserting exact equality:
   appropriate. It closes the current gap where only 5 of 10 RSS URLs are
   pinned and extra RSS sources would be ignored.

4. Raw YAML boundary test: correct. It proves explicit YAML fields instead of
   relying on Pydantic defaults.

5. `## RSS Feeds` docs section plus docs-sync test: right minimal docs change.
   It mirrors the existing GDELT inventory pattern.

6. Scope cleanliness: acceptable. The plan avoids live liveness gates, source
   expansion, connectors, scraping, demand proof, platform coverage
   verification, dependency changes, and compliance-review behavior.

7. Verification set: sufficient for a test/docs-only source-pack contract
   stage.

## Minor

1. The plan duplicated the composition and URL constants in two sections.
   Keeping one canonical block reduces transcription risk.

2. `public_pack_raw_sources()` uses direct `data["sources"]` access while
   sibling helpers use `.get()` plus assertions. Either is safe; aligning is
   stylistic.

3. The existing `test_public_fashion_source_pack_loads()` count floor becomes
   redundant after adding the exact 20-source test, though it still covers
   uniqueness and tag presence.

4. Only the RSS docs test is genuinely RED-to-GREEN. The YAML/config/lint
   contract tests will pass immediately because they codify existing intended
   repository state. Do not force RED by temporarily editing the YAML.
