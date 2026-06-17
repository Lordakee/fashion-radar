I'll review the new test against the implementation contract.
## Verdict: PASS

## Critical findings
None. The test correctly exercises the contract.

## Important findings
None. Traced against `query_imported_entity_evidence` and `_query_evidence_rows` (src/fashion_radar/imported_entity_evidence.py:112, :205-212):
- Window classification is right: `newest_id` (AS_OF−5min) and the older item (AS_OF−1h) fall in `(current_window_start, as_of]` → current; the AS_OF−10d item falls in `(baseline_window_start, current_window_start]` → baseline.
- Sort key `(window, -collected_at, -id)` puts `newest_id` first; `evidence[:1]` then yields `[newest_id]`. Assertions `row_count==1`, `total_count==3`, `current_mentions==2`, `baseline_mentions==1`, `[newest_id]` all hold.
- Timestamps are distinct (5min/1h/10d), so no tie-break flakiness; URLs are distinct so `upsert_item` returns fresh ids. Not flaky.

## Test gaps
- The test's stated intent ("limit applies *after* sorting") is only weakly distinguished from a buggy "limit pushed into SQL" regression. Because the first-inserted item (lowest `id`) happens to also be the one that sorts first (most recent `collected_at` in the current window), an incorrect `ORDER BY items.c.id LIMIT 1` would return the same `newest_id`. Swapping insertion order so the lowest-id row is *not* the top-sorted row (e.g., insert the AS_OF−1h item first, then `newest_id`) would make this test genuinely guard against that regression. Non-blocking; current behavior is correct and covered.
