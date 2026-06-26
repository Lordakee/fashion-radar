# Stage 208 Plan Second Rereview

**I-2 status: RESOLVED.**

The Task 2 Step 2 "from" block (plan lines 214–220) now reads:

```python
context_keys = {
    normalize_alias_key(term)
    for term in entity.context_terms
    if term.strip() and normalize_alias_key(term)
}
```

I confirmed this matches the actual source at `src/fashion_radar/entity_packs.py:444-448` byte-for-byte (loop variable `term`, full `term.strip() and normalize_alias_key(term)` guard). A literal `edit`-tool replacement will now succeed. The earlier I-1 quotes ("Example current warning shape" lines 23–26 and Task 2 Step 3 "from" lines 233–238) still match the source at `entity_packs.py:498-502`, so all three quoted baselines are now accurate.

I also re-verified the implementation is behaviorally sound beyond the quote fix:

- **Key-set equivalence holds.** `normalize_alias_key(...)` ends in `.strip()` (`extract/text.py:45`), so a truthy normalized key implies a non-whitespace source term, which implies a truthy `term.strip()`. Therefore the helper's `if context_key` guard yields the identical key set as the original `if term.strip() and normalize_alias_key(term)` guard. No divergence.
- **Deterministic test (Step 3) is correct.** For `context_terms: [shoes, mary jane, runway]` against alias `Mary Jane shoes`, `sorted(context_keys)` iterates `mary jane` first; `_context_term_contained_in_alias` (`entity_packs.py:660`) matches token slice `["mary","jane"]` and `break`s before `shoes`. Display term `"mary jane"` is the original YAML spelling, so `"'mary jane'" in message` and `"'shoes'" not in message` both hold.
- **RED assertions (Steps 1–2) match fixtures.** Existing tests use lowercase context-term spelling (`shoes`, `mary jane`) and alias `Mary Jane shoes`; the new message interpolates original-text `alias.value` and `context_display_by_key[...]`, so `"'shoes'"`, `"'mary jane'"`, and `"'Mary Jane shoes'"` all resolve as asserted.

## Critical
None.

## Important
None.

## Minor
None beyond the previously-filed M-1/M-2 (both already addressed).

**No Critical or Important planning blockers remain.** I-2 is resolved; the plan is clear to proceed to Task 1.
