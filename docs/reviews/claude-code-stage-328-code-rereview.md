**Critical**

None.

---

**Important**

None.

---

**Medium**

None. The prior finding is resolved. `_referenced_paragraph_indices` already returns `tuple[object, ...]` (reusable), so the double-iteration risk was low in practice, but the explicit `tuple(paragraph_indices)` materialization in `_support_excerpt` closes it correctly and makes the contract explicit regardless of future callers.

---

**Minor**

`_strict_valid_saved_signal_paragraph_indices` is now called twice on the same `referenced_paragraph_indices` - once in `_add_story_signal_supports` (for `paragraph_links`) and once inside `_paragraph_excerpt`. The function is idempotent so the results are consistent, but the redundant validation pass is mildly wasteful. Not worth changing unless this path becomes hot.

`_support_excerpt` also materializes `items` into a `tuple` defensively. At the call site `items` is a `list[...]`, so that materialization is unnecessary - harmless, but slightly inconsistent signaling (materializing something that doesn't need it alongside something that does).

---

**Verdict**

**Correct - safe to merge.** The follow-up change properly addresses the prior finding. `Sequence[object]` is the right annotation for `_paragraph_excerpt` (it must be multi-iterable), `_support_excerpt` materializes both arguments before use, and the excerpt/paragraph-link index derivation stays in sync. No new issues introduced.
