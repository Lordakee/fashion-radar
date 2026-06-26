# Stage 208 Plan Rereview

**I-1 status: RESOLVED.** I verified the plan now quotes the real Stage 207 baseline in both places:

- "Example current warning shape" (plan lines 23–26) matches `src/fashion_radar/entity_packs.py:498-502` exactly.
- Task 2 Step 3 "from" snippet (plan lines 233–237) matches the same source exactly.

A literal `edit`-tool replacement will now succeed. The scope (lines 5, 18, 31–33) and the new message (lines 244–249) also correctly acknowledge that the alias is newly introduced into the message body — the secondary point of I-1. The `_sort_findings(...)` tie-breaker note (lines 253–255) is accurate — I confirmed `finding.message` is the final sort key at `entity_packs.py:695`. The docs-parity guard (lines 256–259) addresses initial M-1. No further action on I-1.

I also independently verified the implementation is behaviorally sound: `_context_display_by_key` produces an identical `context_keys` set (the helper's `if context_key` guard is equivalent to the comprehension's `if term.strip() and normalize_alias_key(term)`, since a truthy `normalize_alias_key` implies a truthy `term.strip()`), and the deterministic test's expectation (`mary jane` selected over `shoes` via `sorted(context_keys)`) is correct per `_context_term_contained_in_alias` at `entity_packs.py:660`.

## Critical
None.

## Important

**I-2. The Task 2 Step 2 "from" snippet for `context_keys` does not match the actual code (execution blocker, same class as the original I-1).**

The plan (lines 214–219) instructs the implementer to change FROM:
```python
context_keys = {
    normalize_alias_key(context_term)
    for context_term in entity.context_terms
    if normalize_alias_key(context_term)
}
```
But the **actual** current code at `src/fashion_radar/entity_packs.py:444-448` is:
```python
context_keys = {
    normalize_alias_key(term)
    for term in entity.context_terms
    if term.strip() and normalize_alias_key(term)
}
```
Two differences: the loop variable is `term` (not `context_term`), and the guard is `term.strip() and normalize_alias_key(term)` (not bare `normalize_alias_key(context_term)`). A literal `edit`-tool replacement will fail with "oldString not found." This is behaviorally benign — I verified the proposed helper yields the same key set — but the quoted text must match the source for the prescribed edit, exactly as I-1 required for the message. This was missed by the initial review; it should be fixed now while correcting baseline quotes.

**Fix:** quote the real comprehension (variable `term`, full guard) in the Task 2 Step 2 "from" block.

## Minor
None beyond the initially-filed M-1/M-2, both now addressed by the plan update.

**Recommendation:** I-1 is resolved. Fix I-2 (correct the `context_keys` "from" snippet to quote the real source) before Task 1. No other Critical or Important blockers remain.
