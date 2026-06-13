## Critical

None found.

## Important

1. **Deterministic ordering tests still do not cover all required tie-breakers.**
   The prior review asked for focused tests covering all change labels *and* ordering tie-breakers:
   - absolute movement ordering,
   - higher `current_count`,
   - `entity_type` ascending,
   - `entity_name` ascending.

   The updated plan adds `test_query_imported_entity_deltas_labels_and_orders_all_change_states`, but the described expected order only proves the primary `change_label` order. It does not force or verify tie cases within the same label group. Add direct tests where multiple entities share the same `change_label` and differ only by:
   - `abs(delta)`,
   - `current_count`,
   - `entity_type`,
   - `entity_name`.

2. **Source-count filter behavior is still only partially tested.**
   The plan now adds a good direct test for distinct per-window `source_name` label counts:
   - duplicate matches do not inflate source counts,
   - two current labels produce `current_source_count == 2`,
   - baseline label count and delta are checked.

   However, the prior review also requested proving `--source-name` filtering produces counts within the filtered local label set. The current filter test only asserts the filtered entity is returned; it does not assert `current_source_count`, `baseline_source_count`, or `source_count_delta` under a source-name filter. Add a direct assertion that filtering to one stored source label reduces the per-window source counts accordingly.

3. **Forbidden-output checks are broad for JSON but still narrow for table output.**
   The JSON CLI test now checks forbidden top-level and entity keys across all entities, which resolves most of the prior concern. The table test still only checks absence of one title and one URL. Because table output is also user-visible and the fixture stores `alias`, `confidence`, `reason`, and `context_terms`, add table assertions that none of these forbidden values/field names appear:
   - `alias`,
   - `confidence`,
   - `reason`,
   - `context_terms`,
   - stored context strings such as `margaux`, `baseline`, `flats`, `rss`,
   - any source/import file path fields if present in fixtures.

   This keeps the command firmly within aggregate stored-entity output.

## Minor

1. **Renderer populated test remains under-specified.**
   The prior minor finding asked to replace “Add a populated renderer test…” with the exact expected rendered row and sanitization expectation. The updated plan still leaves this as prose:

   > Add a populated renderer test with an entity name containing `|` and newline...

   This is not blocking, but making it concrete would better preserve the implementation contract.

2. **Documentation update list may still be broader than necessary.**
   The plan still proposes edits to many docs:
   - `README.md`
   - `docs/manual-signal-import.md`
   - `docs/community-signal-import.md`
   - `docs/community-signal-quality.md`
   - `docs/architecture.md`
   - `docs/source-boundaries.md`
   - `docs/github-upload-checklist.md`
   - `CHANGELOG.md`

   This is not inherently wrong, and the docs boundary scan helps. Still, Stage 23 is tightly scoped; implementation should keep docs edits minimal and local to imported/manual signal references.

## Rechecked Prior Important Findings

1. `current_matched_item_count` / `baseline_matched_item_count` with `--entity-type`: **Resolved.** Design and plan now both say matched item counts apply after source-name and entity-type filters.

2. Current/baseline row classification and boundary tests: **Resolved enough.** The plan explicitly classifies rows in Python using:
   - `baseline_start < collected_at <= current_start`
   - `current_start < collected_at <= as_of`

   It also includes boundary test guidance for exact `baseline_start`, `current_start`, `as_of`, and future rows.

3. Timestamp parsing / no lexical `collected_at` reliance: **Resolved.** Design and plan now explicitly parse `collected_at` with `parse_datetime_utc()` and avoid SQL timestamp range filtering.

4. Deterministic tests for all labels and ordering: **Partially resolved; still Important.** Labels are covered, but tie-breakers are not.

5. Direct tests for per-window stored `source_name` label counts: **Partially resolved; still Important.** Basic source counts are covered, but filtered source-count semantics are not.

6. Forbidden output fields checked broadly: **Partially resolved; still Important.** JSON is broad; table output remains narrow.

7. Explicit process gate: Claude Code plan approval before implementation: **Resolved.**

8. Direct-main commit/push constrained to user-authorized workflow and code-review completion: **Resolved.**

Not approved
