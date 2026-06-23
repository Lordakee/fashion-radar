# Stage 175 Plan Review

## Summary

Stage 175 is a well-scoped, docs/test-only node that keeps
`docs/entity-pack-quality.md` synchronized with current `entity-pack-lint`
output for the checked-in starter watchlist pack. The spec and plan correctly
identify the drift: abbreviated `tag_counts` / `category_tag_counts`, a stale
representative finding, and missing "abbreviated excerpt" prose. The proposed
parity tests follow the established Stage 168 `tests/test_source_packs_docs.py`
pattern. Runtime claims in the plan were verified: `entity_count=28`,
`alias_count=45`, `type_counts`, all 16 `tag_counts`, all 9
`category_tag_counts`, the four matcher-gate counters, the `0 errors / 16
warnings / 61 info` finding counts, and the first finding
(`context_terms_no_effect` / `Boat Shoes`) match the proposed JSON sample.

Boundary discipline is sound: no runtime, CLI, matcher, scoring, payload-shape,
install-hint, mirror-hint, dependency, or lockfile changes are introduced. One
important test-design defect must be fixed before implementation: the table
parity test uses an absolute path that makes the rendered first line disagree
with the documented relative-path sample.

## Findings

### Critical

None.

### Important

1. Table parity test cannot pass as written due to absolute-path mismatch.
   The plan defines `WATCHLIST_ENTITY_PACK = ROOT / "configs" / "entity-packs" /
   "fashion-watchlist.example.yaml"`, which is absolute.
   `render_entity_pack_lint_table` renders line 0 as
   `Entity pack: {result.path}`, and `result.path = str(path)`. With an
   absolute input, line 0 becomes
   `Entity pack: /home/ubuntu/fashion-radar/configs/entity-packs/fashion-watchlist.example.yaml`,
   but the documented table sample uses the relative form
   `configs/entity-packs/fashion-watchlist.example.yaml`. Recommended fix: in
   the table test, call `lint_entity_pack(WATCHLIST_ENTITY_PACK.relative_to(ROOT))`
   while keeping the absolute constant for locating the file in the JSON test.

### Minor

1. Spec/plan helper signature disagreement. The design spec describes
   `_json_ready_first_finding(result)` as a helper that accepts the lint result,
   but the plan implements `_json_ready_first_finding()` with no parameter and
   recomputes `lint_entity_pack(WATCHLIST_ENTITY_PACK)` internally. Align the
   two documents.
2. RED-step description is JSON-only. Task 1 Step 5 documents expected failure
   reasons only for the JSON parity test. The second command runs the whole
   file, which should show the table test passing and the JSON test failing
   after fixing the path issue. The plan should say that explicitly.

## Plan Assessment

- Scope safety: the node touches only `tests/test_entity_pack_quality_docs.py`,
  `docs/entity-pack-quality.md`, and review/spec/plan artifacts. No source,
  config, CLI, matcher, scoring, install-hint, mirror-hint, dependency, or
  lockfile files are modified.
- Boundary compliance: the plan respects the project scope boundaries. There is
  no source acquisition, connector, scraping, browser automation, platform API,
  monitoring, scheduling, demand-proof, ranking, coverage-verification, or
  compliance-review behavior.
- Test usefulness vs. brittleness: the two new parity tests are well-targeted.
  The table prefix comparison guards renderer/summary drift without coupling to
  the full 77-finding list. The JSON test pins every stable scalar and count-map
  field plus exactly one representative first finding, and separately requires
  the "abbreviated representative excerpt" / "not the full findings list" prose.
- Abbreviation tradeoff: testing exact counts plus one first finding keeps the
  docs honest about stable fields while avoiding a noisy full-finding dump.
- Factual accuracy: runtime numbers, count maps, finding counts, and the first
  finding in the proposed JSON sample match live `lint_entity_pack` output for
  `configs/entity-packs/fashion-watchlist.example.yaml`.
- Out-of-scope behavior: none detected in the plan. The review/release gate
  commands use the project-standard `uv --no-config run --frozen`,
  `UV_NO_CONFIG=1 uv lock --check`, secret scan, and extraheader checks.

## Verdict

Approve with one important fix required before implementation. Fix the table
parity test's path handling so it uses a relative path matching the documented
CLI invocation and table sample; without this, Task 2 Step 3 cannot reach
GREEN. The two minor items (spec/plan helper signature alignment, RED-step
description clarity) can be addressed during implementation but are not
blocking. Once the path fix is applied, the plan is safe to implement.
