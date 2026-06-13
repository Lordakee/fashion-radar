## Critical

None found.

## Important

1. **`current_matched_item_count` / `baseline_matched_item_count` semantics are inconsistent when `--entity-type` is used.**
   - Design says these counts are distinct manual-import items with at least one stored match “after optional source-name filtering” only.
   - Plan says item counts come from distinct item IDs “after filters,” which appears to include `entity_type`.
   - This affects the top-level JSON contract. Fix by explicitly choosing one behavior:
     - If entity-type should affect matched item counts, update the design wording.
     - If not, update the plan to compute matched item counts independently from entity-type-filtered entity rows.

2. **Window boundary/classification logic needs to be specified more concretely in the implementation plan.**
   The design clearly defines:
   - baseline: `baseline_start < collected_at <= current_start`
   - current: `current_start < collected_at <= as_of`
   But the plan only shows a broad SQL range query and does not spell out the per-row classification condition. Add explicit implementation guidance and tests for boundary rows exactly at `baseline_start`, `current_start`, and `as_of`.

3. **The plan relies on SQL string comparison for `collected_at` window filtering without addressing timestamp normalization assumptions.**
   Existing repository writes UTC ISO strings, but if retained rows contain equivalent timestamps with different offset spellings, lexical comparison can misclassify rows. The plan should either:
   - state that stored `collected_at` values are already normalized by existing ingestion/repository paths and this command relies on that invariant, or
   - fetch a safe superset and classify via `parse_datetime_utc()` in Python.

4. **Test coverage is not concrete enough for all deterministic change labels and ordering.**
   The design defines labels and order for `new_in_current`, `increased`, `dropped_from_current`, `decreased`, and `unchanged`, plus tie-breakers. The plan’s example tests cover only `new_in_current` and `unchanged`. Add focused tests for:
   - `increased`
   - `decreased`
   - `dropped_from_current`
   - absolute movement ordering
   - current-count tie-breaker
   - `entity_type` / `entity_name` ascending tie-breakers
   This is important because ordering must not imply external ranking and must stay deterministic.

5. **Source-count behavior needs direct tests.**
   The design says `current_source_count`, `baseline_source_count`, and `source_count_delta` are distinct stored local `source_name` label counts per entity/window. The plan does not include a concrete test with the same entity appearing across multiple local source-name labels. Add tests proving:
   - duplicate matches on the same item do not inflate source counts;
   - two different stored source labels in the same window produce source count `2`;
   - `source_count_delta` is exactly current minus baseline;
   - `--source-name` filtering produces counts within the filtered local label set.

6. **Forbidden-output checks are too narrow.**
   The design correctly excludes titles, URLs, summaries, raw item row IDs, reasons, context terms, source file paths, and confidence details. The CLI JSON test only asserts absence of `title` and `url` on the first entity. Add assertions, preferably over all top-level/entity keys, that forbidden fields are absent:
   - `id`
   - `item_id`
   - `title`
   - `url`
   - `summary`
   - `reason`
   - `context_terms`
   - `confidence`
   - `alias`
   - source/import file path fields

7. **The process gate “Claude Code review before code” is not explicit enough in the implementation plan.**
   The plan includes a post-implementation Claude Code code review before push, but the user’s process also requires Claude Code review before code. Since this current review is that gate, the plan should explicitly say implementation may start only after the Stage 23 plan review result is approved and Critical/Important plan-review findings are resolved.

8. **The final commit/push step pushes directly to `main` and should be reconsidered.**
   The plan’s release step requires being on `main` and pushing directly to `origin/main`. That may be intended for this repo, but it is a high-impact workflow assumption. At minimum, make this conditional on repository/user process and ensure code review completion is mandatory before push. If normal workflow is branch/PR, this step should be changed.

## Minor

1. **`limit: int | None` is looser than the CLI contract.**
   The design says `--limit INTEGER`, default `50`, minimum `0`; it does not describe an unlimited/null mode. The Pydantic model and helper allow `None`. This is harmless internally, but the plan should either document `None` as internal-only or use plain `int`.

2. **Renderer test description leaves one placeholder-style instruction.**
   “Add a populated renderer test…” is acceptable as guidance, but the rest of the plan is very concrete. For consistency, spell out the exact expected rendered line and sanitization expectation.

3. **The docs update list may be broader than necessary.**
   Updating many docs is not inherently wrong, but because Stage 23 is tightly scoped, keep documentation edits minimal and local to imported/manual signal command references to avoid accidental scope expansion.

## Verdict

Not approved
