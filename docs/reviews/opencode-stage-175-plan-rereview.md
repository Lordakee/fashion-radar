# Stage 175 Plan Rereview

## Summary

The Stage 175 plan rereview confirms that the important path-handling defect and
both minor alignment issues from the first plan review have been fixed in the
design spec and implementation plan. The table parity test now feeds a relative
path into `lint_entity_pack(...)` so the rendered first line matches the
documented CLI/table sample; the design and plan now agree that
`_json_ready_first_finding(result)` receives the already-computed lint result;
and the RED-step description now states that the table parity test should pass
while the JSON parity test fails before docs updates.

Runtime verification against `configs/entity-packs/fashion-watchlist.example.yaml`
confirms every field the GREEN JSON sample pins: `entity_count=28`,
`alias_count=45`, the six `type_counts` lanes, all 16 `tag_counts` lanes, all 9
`category_tag_counts` lanes, the four matcher-gate counters (`22` / `4` / `7` /
`12`), the `0 errors / 16 warnings / 61 info` finding counts, and the first
sorted finding (`context_terms_no_effect` / `Boat Shoes` / `alias=None` /
`field=context_terms`). The relative-path table render reproduces the documented
five-line summary prefix exactly. The current checked-in docs JSON sample is
genuinely RED: abbreviated count maps, a stale first finding, and no
`abbreviated representative excerpt` wording.

## Findings

### Critical

None.

### Important

None. The prior important finding (absolute-path mismatch in the table parity
test) is resolved.

### Minor

None blocking. One optional, non-blocking observation: the helper signature
`_json_ready_first_finding(result: object)` annotates the parameter as `object`
and then accesses `result.findings` after an `hasattr` guard. Static type
checkers that do not narrow on `hasattr` could flag this, but the project
release gate runs Ruff only, so it does not affect configured checks. No change
required.

## Fix Assessment

- Important fix (path handling): applied in both documents. The design now
  states the table parity test must pass
  `WATCHLIST_ENTITY_PACK.relative_to(ROOT)` into `lint_entity_pack(...)`. The
  plan computes `relative_pack_path = WATCHLIST_ENTITY_PACK.relative_to(ROOT)`
  and calls `render_entity_pack_lint_table(lint_entity_pack(relative_pack_path))`.
  Runtime confirmation shows the rendered first line is
  `Entity pack: configs/entity-packs/fashion-watchlist.example.yaml`, matching
  `docs/entity-pack-quality.md`.
- Minor fix 1 (helper signature alignment): applied. The design describes
  `_json_ready_first_finding(result)` as receiving the already-computed lint
  result; the plan defines the helper with a result parameter and passes the
  shared result into it instead of recomputing lint.
- Minor fix 2 (RED-step clarity): applied. The plan now states the table parity
  test should pass because the current table summary is in sync, while the JSON
  parity test fails on abbreviated count maps, a stale first finding, and
  missing excerpt wording.

Implementability: the RED/GREEN path is credible and verified. Against current
docs, the table prefix test passes and the JSON parity test fails on
`tag_counts`, `category_tag_counts`, the first finding, and the excerpt prose.
After Task 2, the proposed JSON sample matches `lint_entity_pack` output
field-for-field, and the new prose sentence contains both required phrases.

Scope discipline: unchanged and sound. The node still touches only
`tests/test_entity_pack_quality_docs.py`, `docs/entity-pack-quality.md`, and
review/spec/plan artifacts. No runtime lint behavior, entity config loading,
matcher behavior, scoring behavior, CLI behavior, payload shape, renderer
behavior, exit behavior, install hints, mirror hints, dependency manifests, or
`uv.lock` changes. No source acquisition, connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, demand proof, ranking,
coverage verification, or compliance-review product feature.

## Verdict

Approve. All first-review findings are resolved, the RED/GREEN path is verified
against live lint output, and no critical or important issues remain. The plan is
safe to implement.
