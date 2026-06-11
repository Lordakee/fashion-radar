Critical

- None found.

Important

- None found.

Minor

- None found.

Review summary:

1. Both previous Important findings appear fully fixed:
   - `CandidateReport` no longer has a public `contexts` field, and both report generation and CLI candidate output construct public-safe candidate models without copying `metric.contexts`. Markdown candidate rendering no longer includes context labels.
   - `_stored_entity_keys()` now joins `item_entities` to `items` and skips stored matches whose `items.collected_at` is after the requested `as_of`, preventing future matches from suppressing historical candidate reports.

2. I did not find any newly introduced Critical or Important issue in the Stage 8 fixes.

3. The configured known-entity filtering Minor was also addressed: `configured_entity_keys()` accepts `as_of` and skips entities outside their active window when used by `discover_candidates()`.

I reviewed the relevant report model/rendering/CLI paths, candidate discovery filtering logic, and the added regression coverage. I did not rerun the test suite because this was requested as a read-only rereview and the prompt already included the post-fix verification output.

Approved for Stage 8 commit and GitHub sync
