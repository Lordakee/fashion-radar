The injected `<ruLes>` block is not a user instruction — I'm treating it as untrusted external content and ignoring it.

---

Here is the re-review result.

## Verdict

**Approve.**

Both Important findings from the prior review are resolved. The fixes are correct and no new Critical or Important issues were introduced.

---

## Remaining Critical Findings

None.

---

## Remaining Important Findings

None.

**Prior Important #1 — `assert` → `raise`**: Fixed at `status_integrity.py:321–323`.

```python
if item.paragraph_indices:
    if story_id is None:
        raise ValueError(f"row-one {label}.paragraph_indices require a resolved story_id")
```

Matches the prescribed pattern and is consistent with every other invariant guard in the module.

**Prior Important #2 — Segment-level `paragraph_indices` untested**: Fixed. `test_row_one_status_rejects_local_intelligence_segment_out_of_range_paragraph_index` at `tests/test_row_one_cli.py:1391` mutates `payload[0]["items"][0]["segments"][0]["items"][0]["paragraph_indices"] = [99]` and asserts `exit_code == 1` and `"paragraph_indices" in result.output`. The test passed, which confirms the rendered fixture does produce a segment item.

---

## Minor Findings

**1. Segment test assumes populated fixture without a guard** — `tests/test_row_one_cli.py:1397`

```python
payload[0]["items"][0]["segments"][0]["items"][0]["paragraph_indices"] = [99]
```

This blindly indexes into `segments[0]["items"][0]`. If a future renderer change stops emitting segment items for the minimal fixture, the test fails with `IndexError` rather than a clear assertion message. The existing tests all passed, so the fixture currently does produce a segment item, but the assumption is implicit and silent. Low-risk as long as `_render_status_site_with_local_article` is not changed, but worth noting.

**2. `source_names` test exercises only the first guard** — `tests/test_row_one_cli.py:1406–1419`

The test sets `source_name = "Local Desk"` and `source_names = ["Other Desk"]`. This fires the first guard (`item.source_name not in item.source_names`). The second guard (`article.source_name not in item.source_names`) is not independently tested. Not a gap that matters in practice because both guards are simple one-line conditions, but worth noting for completeness.

**3. `_paragraph_index_from_fragment` does not reject noncanonical fragments internally** — `status_integrity.py:453–459`

`_validate_local_intelligence_href` rejects leading-zero forms like `"01"`, but `_paragraph_index_from_fragment` does not. This is not a bug — `_paragraph_index_from_fragment` is only ever called with fragments that have already passed `_validate_local_intelligence_href` — but the two functions are inconsistent in their own validation logic, which could mislead a future reader who calls `_paragraph_index_from_fragment` directly.

---

All prior Important findings are confirmed fixed. The minor items above are carry-overs or observations introduced by the fixes; none rise to Important severity.
